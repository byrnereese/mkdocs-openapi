"""MkDocs plugin entry point."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from importlib.resources import files as package_files
from pathlib import PurePosixPath
from typing import Any

from mkdocs import plugins
from mkdocs.config import base, config_options as c
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.exceptions import PluginError
from mkdocs.structure.files import File, Files, InclusionLevel

from .errors import OpenAPIError
from .generator import generate_site
from .model import GeneratedSite
from .parser import load_spec


ASSET_URI = "assets/mkdocs-openapi.css"
SPEC_SUFFIXES = {".json", ".yaml", ".yml"}
REQUIRED_MARKDOWN_EXTENSIONS = (
    "admonition",
    "attr_list",
    "tables",
    "pymdownx.superfences",
    "pymdownx.tabbed",
)


class OpenAPISpecConfig(base.Config):
    """Configuration for one specification in a multi-specification site."""

    source = c.Type(str)
    output_dir = c.Type(str)
    models_dir = c.Optional(c.Type(str))
    models_title = c.Optional(c.Type(str))
    models_in_nav = c.Optional(c.Type(bool))
    tag_nav = c.Optional(c.Type(list))
    unlisted_tags = c.Optional(c.Choice(("exclude", "append", "error")))


class OpenAPIPluginConfig(base.Config):
    """Configuration for the OpenAPI plugin."""

    output_dir = c.Type(str, default="api-reference")
    models_dir = c.Type(str, default="models")
    models_title = c.Type(str, default="Models")
    models_in_nav = c.Type(bool, default=True)
    tag_nav = c.Optional(c.Type(list))
    unlisted_tags = c.Choice(
        ("exclude", "append", "error"), default="exclude"
    )
    specs = c.Optional(c.DictOfItems(c.SubConfig(OpenAPISpecConfig)))


@dataclass(frozen=True)
class _ResolvedSpec:
    """Validated generation settings for one OpenAPI document."""

    spec_id: str
    source: str
    output_dir: str
    models_dir: str
    models_title: str
    models_in_nav: bool
    tag_nav: list[Any] | None
    unlisted_tags: str


@dataclass(frozen=True)
class _GeneratedSpec:
    """Generated output associated with its specification settings."""

    settings: _ResolvedSpec
    site: GeneratedSite


class OpenAPIPlugin(plugins.BasePlugin[OpenAPIPluginConfig]):
    """Generate in-memory Markdown pages from an OpenAPI nav entry."""

    def on_config(self, config: MkDocsConfig) -> MkDocsConfig:
        """Validate paths and register the bundled stylesheet."""
        output_dir = _clean_relative_dir(self.config.output_dir, "output_dir")
        models_dir = _clean_relative_dir(self.config.models_dir, "models_dir")
        if output_dir == models_dir:
            raise PluginError("openapi: output_dir and models_dir must differ")
        self.config.output_dir = output_dir
        self.config.models_dir = models_dir

        self._configured_specs = self._resolve_configured_specs()

        if ASSET_URI not in config.extra_css:
            config.extra_css.append(ASSET_URI)
        for extension in REQUIRED_MARKDOWN_EXTENSIONS:
            if extension not in config.markdown_extensions:
                config.markdown_extensions.append(extension)
        config.mdx_configs.setdefault("pymdownx.tabbed", {}).setdefault(
            "alternate_style", True
        )
        return config

    def on_files(self, files: Files, config: MkDocsConfig) -> Files:
        """Read configured specifications and add generated virtual files."""
        if config.nav is None:
            raise PluginError(
                "openapi: nav must contain an OpenAPI .json, .yaml, or .yml entry"
            )

        spec_uris = _find_spec_uris(config.nav)
        if not spec_uris:
            raise PluginError(
                "openapi: no OpenAPI .json, .yaml, or .yml entry was found in nav"
            )

        duplicates = [
            uri for uri, count in Counter(spec_uris).items() if count > 1
        ]
        if duplicates:
            joined = ", ".join(duplicates)
            raise PluginError(
                "openapi: each specification may appear in nav only once; "
                f"found duplicate entries for {joined}"
            )

        settings = self._settings_for_nav(spec_uris)
        source_files: dict[str, File] = {}
        for spec in settings:
            spec_file = files.get_file_from_path(spec.source)
            if spec_file is None:
                raise PluginError(
                    "openapi: specification "
                    f"{spec.source!r} was not found under docs_dir"
                )
            source_files[spec.source] = spec_file

        generated_specs: list[_GeneratedSpec] = []
        for spec in settings:
            spec_file = source_files[spec.source]
            try:
                document = load_spec(spec_file.content_string, spec.source)
                generated = generate_site(
                    document,
                    output_dir=spec.output_dir,
                    models_dir=spec.models_dir,
                    tag_nav=spec.tag_nav,
                    unlisted_tags=spec.unlisted_tags,
                )
            except OpenAPIError as error:
                if len(settings) == 1 and not self._configured_specs:
                    raise PluginError(f"openapi: {error}") from error
                raise PluginError(
                    f"openapi: specification {spec.spec_id!r} "
                    f"({spec.source}): {error}"
                ) from error
            generated_specs.append(_GeneratedSpec(spec, generated))

        page_owners: dict[str, _ResolvedSpec] = {}
        source_uris = set(source_files)
        for generated_spec in generated_specs:
            spec = generated_spec.settings
            for source_uri in generated_spec.site.pages:
                previous = page_owners.get(source_uri)
                if previous is not None:
                    raise PluginError(
                        f"openapi: specifications {previous.spec_id!r} and "
                        f"{spec.spec_id!r} both generate page {source_uri!r}"
                    )
                existing = files.get_file_from_path(source_uri)
                if existing is not None:
                    if source_uri in source_uris:
                        detail = "a source specification"
                    else:
                        detail = "an existing docs file"
                    raise PluginError(
                        f"openapi: specification {spec.spec_id!r} generates "
                        f"page {source_uri!r}, which conflicts with {detail}"
                    )
                page_owners[source_uri] = spec

        # Mutate MkDocs state only after every spec and generated URI validates.
        for spec_file in source_files.values():
            files.remove(spec_file)

        for generated_spec in generated_specs:
            spec = generated_spec.settings
            generated = generated_spec.site
            model_page_uris = {
                model.source_uri for model in generated.models
            }
            for source_uri, content in generated.pages.items():
                inclusion = (
                    InclusionLevel.NOT_IN_NAV
                    if not spec.models_in_nav
                    and source_uri in model_page_uris
                    else InclusionLevel.UNDEFINED
                )
                files.append(
                    File.generated(
                        config,
                        source_uri,
                        content=content,
                        inclusion=inclusion,
                    )
                )

        if files.get_file_from_path(ASSET_URI) is None:
            css = (
                package_files("mkdocs_openapi.assets")
                .joinpath("mkdocs-openapi.css")
                .read_text(encoding="utf-8")
            )
            files.append(File.generated(config, ASSET_URI, content=css))

        replacements = {
            generated_spec.settings.source: generated_spec
            for generated_spec in generated_specs
        }
        config.nav = _replace_spec_nav(config.nav, replacements=replacements)
        return files

    def _resolve_configured_specs(self) -> tuple[_ResolvedSpec, ...]:
        """Validate and normalize explicit multi-specification settings."""
        if not self.config.specs:
            return ()

        resolved: list[_ResolvedSpec] = []
        source_owners: dict[str, str] = {}
        directory_owners: dict[str, str] = {}
        for raw_spec_id, raw in self.config.specs.items():
            spec_id = raw_spec_id.strip()
            if not spec_id:
                raise PluginError(
                    "openapi: specification IDs must not be empty"
                )
            if spec_id != raw_spec_id:
                raise PluginError(
                    "openapi: specification IDs must not have leading or "
                    f"trailing whitespace: {raw_spec_id!r}"
                )
            source = _clean_spec_source(raw.source, spec_id)
            output_dir = _clean_relative_dir(
                raw.output_dir, f"specs.{spec_id}.output_dir"
            )
            models_dir = _clean_relative_dir(
                raw.models_dir or f"{output_dir}/models",
                f"specs.{spec_id}.models_dir",
            )
            if output_dir == models_dir:
                raise PluginError(
                    f"openapi: specs.{spec_id}.output_dir and models_dir "
                    "must differ"
                )

            previous_source = source_owners.get(source)
            if previous_source is not None:
                raise PluginError(
                    f"openapi: specifications {previous_source!r} and "
                    f"{spec_id!r} use the same source {source!r}"
                )
            source_owners[source] = spec_id

            for directory in (output_dir, models_dir):
                previous_directory = directory_owners.get(directory)
                if previous_directory is not None:
                    raise PluginError(
                        f"openapi: specifications {previous_directory!r} and "
                        f"{spec_id!r} use the same generated directory "
                        f"{directory!r}"
                    )
                directory_owners[directory] = spec_id

            resolved.append(
                _ResolvedSpec(
                    spec_id=spec_id,
                    source=source,
                    output_dir=output_dir,
                    models_dir=models_dir,
                    models_title=(
                        raw.models_title
                        if raw.models_title is not None
                        else self.config.models_title
                    ),
                    models_in_nav=(
                        raw.models_in_nav
                        if raw.models_in_nav is not None
                        else self.config.models_in_nav
                    ),
                    tag_nav=(
                        raw.tag_nav
                        if raw.tag_nav is not None
                        else self.config.tag_nav
                    ),
                    unlisted_tags=(
                        raw.unlisted_tags
                        if raw.unlisted_tags is not None
                        else self.config.unlisted_tags
                    ),
                )
            )
        return tuple(resolved)

    def _settings_for_nav(
        self, spec_uris: list[str]
    ) -> tuple[_ResolvedSpec, ...]:
        """Match nav entries to explicit settings or legacy single-spec mode."""
        if not self._configured_specs:
            if len(spec_uris) > 1:
                joined = ", ".join(spec_uris)
                raise PluginError(
                    "openapi: multiple specifications require the specs "
                    f"configuration; found {joined}"
                )
            return (
                _ResolvedSpec(
                    spec_id=spec_uris[0],
                    source=spec_uris[0],
                    output_dir=self.config.output_dir,
                    models_dir=self.config.models_dir,
                    models_title=self.config.models_title,
                    models_in_nav=self.config.models_in_nav,
                    tag_nav=self.config.tag_nav,
                    unlisted_tags=self.config.unlisted_tags,
                ),
            )

        configured_by_source = {
            spec.source: spec for spec in self._configured_specs
        }
        nav_sources = set(spec_uris)
        unconfigured = [
            uri for uri in spec_uris if uri not in configured_by_source
        ]
        if unconfigured:
            raise PluginError(
                "openapi: nav contains specifications not registered under "
                f"specs: {', '.join(unconfigured)}"
            )
        missing = [
            spec.source
            for spec in self._configured_specs
            if spec.source not in nav_sources
        ]
        if missing:
            raise PluginError(
                "openapi: configured specifications are missing from nav: "
                f"{', '.join(missing)}"
            )
        return tuple(configured_by_source[source] for source in spec_uris)


def _find_spec_uris(nav: list) -> list[str]:
    found: list[str] = []
    for item in nav:
        if not isinstance(item, dict):
            continue
        for value in item.values():
            if isinstance(value, str):
                if PurePosixPath(value).suffix.lower() in SPEC_SUFFIXES:
                    found.append(value)
            elif isinstance(value, list):
                found.extend(_find_spec_uris(value))
    return found


def _replace_spec_nav(
    nav: list,
    *,
    replacements: dict[str, _GeneratedSpec],
) -> list:
    """Replace every registered spec entry with its generated navigation."""
    rewritten: list[Any] = []
    for item in nav:
        if not isinstance(item, dict):
            rewritten.append(item)
            continue
        for title, value in item.items():
            replacement = (
                replacements.get(value) if isinstance(value, str) else None
            )
            if replacement is not None:
                spec = replacement.settings
                generated = replacement.site
                rewritten.append({title: generated.api_nav})
                models_nav = generated.models_nav
                if models_nav:
                    if spec.models_in_nav:
                        rewritten.append({spec.models_title: models_nav})
                    else:
                        models_index = next(iter(models_nav[0].values()))
                        rewritten.append(
                            {spec.models_title: models_index}
                        )
            elif isinstance(value, list):
                rewritten.append(
                    {
                        title: _replace_spec_nav(
                            value,
                            replacements=replacements,
                        )
                    }
                )
            else:
                rewritten.append({title: value})
    return rewritten


def _clean_spec_source(value: str, spec_id: str) -> str:
    """Validate and normalize a specification source URI."""
    source = _clean_relative_dir(value, f"specs.{spec_id}.source")
    if PurePosixPath(source).suffix.lower() not in SPEC_SUFFIXES:
        suffixes = ", ".join(sorted(SPEC_SUFFIXES))
        raise PluginError(
            f"openapi: specs.{spec_id}.source must end in one of: {suffixes}"
        )
    return source


def _clean_relative_dir(value: str, name: str) -> str:
    path = PurePosixPath(value.strip("/"))
    if not value.strip("/") or path.is_absolute() or ".." in path.parts:
        raise PluginError(
            f"openapi: {name} must be a non-empty relative directory"
        )
    return path.as_posix()
