"""Turn an OpenAPI document into virtual Markdown pages and navigation."""

from __future__ import annotations

from collections import OrderedDict
from collections.abc import Mapping

from .model import GeneratedSite, ModelPage, Operation, TagGroup
from .naming import UniqueSlugger, slugify
from .parser import resolve_local_ref
from .renderer import MarkdownRenderer


HTTP_METHODS = {
    "get",
    "put",
    "post",
    "delete",
    "patch",
    "head",
    "options",
    "trace",
}


def generate_site(
    document: dict,
    *,
    output_dir: str = "api-reference",
    models_dir: str = "models",
) -> GeneratedSite:
    """Generate Markdown pages and MkDocs navigation for an OpenAPI document."""
    output_dir = output_dir.strip("/")
    models_dir = models_dir.strip("/")

    tag_descriptions = {
        str(tag.get("name")): str(tag.get("description", ""))
        for tag in document.get("tags", [])
        if isinstance(tag, Mapping) and tag.get("name")
    }
    declared_tags = list(tag_descriptions)
    tag_slugger = UniqueSlugger()
    tag_slugs = {
        tag: tag_slugger.allocate(tag, fallback="untagged")
        for tag in declared_tags
    }
    operation_sluggers: dict[str, UniqueSlugger] = {}
    groups: OrderedDict[str, TagGroup] = OrderedDict()
    operations: list[Operation] = []

    for path, raw_path_item in document.get("paths", {}).items():
        path_item = resolve_local_ref(document, raw_path_item)
        if not isinstance(path_item, Mapping):
            continue
        path_parameters = tuple(
            item
            for item in path_item.get("parameters", [])
            if isinstance(item, dict)
        )

        for raw_method, raw_operation in path_item.items():
            method = str(raw_method).lower()
            if method not in HTTP_METHODS:
                continue
            operation_data = resolve_local_ref(document, raw_operation)
            if not isinstance(operation_data, Mapping):
                continue
            operation_data = dict(operation_data)

            tags = tuple(
                str(tag)
                for tag in operation_data.get("tags", [])
                if str(tag).strip()
            )
            if not tags:
                tags = ("Untagged",)
            primary_tag = tags[0]

            if primary_tag not in tag_slugs:
                tag_slugs[primary_tag] = tag_slugger.allocate(
                    primary_tag, fallback="untagged"
                )
            tag_slug = tag_slugs[primary_tag]
            if primary_tag not in groups:
                groups[primary_tag] = TagGroup(
                    name=primary_tag,
                    slug=tag_slug,
                    description=tag_descriptions.get(primary_tag, ""),
                )

            operation_id = str(operation_data.get("operationId", "")).strip()
            title = _operation_title(operation_data, method, str(path))
            slug_source = operation_id or title or f"{method}-{path}"
            operation_slugger = operation_sluggers.setdefault(
                primary_tag, UniqueSlugger()
            )
            operation_slug = operation_slugger.allocate(
                slug_source, fallback=slugify(f"{method}-{path}")
            )
            source_uri = (
                f"{output_dir}/{tag_slug}/"
                f"operation-{method}-{operation_slug}.md"
            )
            operation = Operation(
                method=method.upper(),
                path=str(path),
                operation_id=operation_id,
                title=title,
                tags=tags,
                primary_tag=primary_tag,
                source_uri=source_uri,
                data=operation_data,
                path_parameters=path_parameters,
            )
            groups[primary_tag].operations.append(operation)
            operations.append(operation)

    ordered_groups = _order_groups(groups, declared_tags)

    schemas = document.get("components", {}).get("schemas", {})
    if not isinstance(schemas, Mapping):
        schemas = {}
    model_slugger = UniqueSlugger()
    models: list[ModelPage] = []
    for name, schema in schemas.items():
        if not isinstance(schema, Mapping):
            continue
        model_name = str(name)
        model_slug = model_slugger.allocate(model_name, fallback="model")
        models.append(
            ModelPage(
                name=model_name,
                slug=model_slug,
                source_uri=f"{models_dir}/{model_slug}.md",
                schema=dict(schema),
            )
        )

    renderer = MarkdownRenderer(
        document,
        output_dir=output_dir,
        models_dir=models_dir,
        groups=ordered_groups,
        models=models,
    )
    pages: dict[str, str] = {
        f"{output_dir}/index.md": renderer.render_api_overview()
    }
    api_nav: list = [{"Overview": f"{output_dir}/index.md"}]

    for group in ordered_groups:
        pages[group.source_uri] = renderer.render_tag_overview(group)
        children: list = [{"Overview": group.source_uri}]
        for operation in group.operations:
            pages[operation.source_uri] = renderer.render_operation(operation)
            children.append({operation.title: operation.source_uri})
        api_nav.append({group.name: children})

    models_nav: list = []
    if models:
        models_index_uri = f"{models_dir}/index.md"
        pages[models_index_uri] = renderer.render_models_overview()
        models_nav.append({"Overview": models_index_uri})
        for model in models:
            pages[model.source_uri] = renderer.render_model(model)
            models_nav.append({model.name: model.source_uri})

    return GeneratedSite(
        pages=pages,
        api_nav=api_nav,
        models_nav=models_nav,
        operations=operations,
        models=models,
    )


def _operation_title(operation: Mapping, method: str, path: str) -> str:
    summary = str(operation.get("summary", "")).strip()
    if summary:
        return summary[:-1] if summary.endswith(".") else summary
    operation_id = str(operation.get("operationId", "")).strip()
    if operation_id:
        words = slugify(operation_id).replace("-", " ")
        return words[:1].upper() + words[1:]
    return f"{method.upper()} {path}"


def _order_groups(
    groups: OrderedDict[str, TagGroup], declared_tags: list[str]
) -> list[TagGroup]:
    ordered: list[TagGroup] = []
    for tag in declared_tags:
        if tag in groups:
            ordered.append(groups[tag])
    ordered.extend(group for name, group in groups.items() if name not in declared_tags)
    return ordered

