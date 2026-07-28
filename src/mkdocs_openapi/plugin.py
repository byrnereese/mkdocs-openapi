"""MkDocs plugin entry point."""

from __future__ import annotations

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
        """Read the configured specification and add generated virtual files."""
        if config.nav is None:
            raise PluginError(
                "openapi: nav must contain an OpenAPI .json, .yaml, or .yml entry"
            )

        spec_uris = _find_spec_uris(config.nav)
        if not spec_uris:
            raise PluginError(
                "openapi: no OpenAPI .json, .yaml, or .yml entry was found in nav"
            )
        if len(spec_uris) > 1:
            joined = ", ".join(spec_uris)
            raise PluginError(
                "openapi: this version supports one specification per site; "
                f"found {joined}"
            )

        spec_uri = spec_uris[0]
        spec_file = files.get_file_from_path(spec_uri)
        if spec_file is None:
            raise PluginError(
                f"openapi: specification {spec_uri!r} was not found under docs_dir"
            )

        try:
            document = load_spec(spec_file.content_string, spec_uri)
            generated = generate_site(
                document,
                output_dir=self.config.output_dir,
                models_dir=self.config.models_dir,
                tag_nav=self.config.tag_nav,
                unlisted_tags=self.config.unlisted_tags,
            )
        except OpenAPIError as error:
            raise PluginError(f"openapi: {error}") from error

        files.remove(spec_file)
        model_page_uris = {model.source_uri for model in generated.models}
        for source_uri, content in generated.pages.items():
            existing = files.get_file_from_path(source_uri)
            if existing is not None:
                raise PluginError(
                    f"openapi: generated page {source_uri!r} conflicts with "
                    "an existing docs file"
                )
            inclusion = (
                InclusionLevel.NOT_IN_NAV
                if not self.config.models_in_nav
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

        config.nav = _replace_spec_nav(
            config.nav,
            spec_uri=spec_uri,
            api_nav=generated.api_nav,
            models_nav=generated.models_nav,
            models_title=self.config.models_title,
            models_in_nav=self.config.models_in_nav,
        )
        return files


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
    spec_uri: str,
    api_nav: list,
    models_nav: list,
    models_title: str,
    models_in_nav: bool,
) -> list:
    rewritten: list[Any] = []
    for item in nav:
        if not isinstance(item, dict):
            rewritten.append(item)
            continue
        for title, value in item.items():
            if value == spec_uri:
                rewritten.append({title: api_nav})
                if models_nav:
                    if models_in_nav:
                        rewritten.append({models_title: models_nav})
                    else:
                        models_index = next(iter(models_nav[0].values()))
                        rewritten.append({models_title: models_index})
            elif isinstance(value, list):
                rewritten.append(
                    {
                        title: _replace_spec_nav(
                            value,
                            spec_uri=spec_uri,
                            api_nav=api_nav,
                            models_nav=models_nav,
                            models_title=models_title,
                            models_in_nav=models_in_nav,
                        )
                    }
                )
            else:
                rewritten.append({title: value})
    return rewritten


def _clean_relative_dir(value: str, name: str) -> str:
    path = PurePosixPath(value.strip("/"))
    if not value.strip("/") or path.is_absolute() or ".." in path.parts:
        raise PluginError(
            f"openapi: {name} must be a non-empty relative directory"
        )
    return path.as_posix()
