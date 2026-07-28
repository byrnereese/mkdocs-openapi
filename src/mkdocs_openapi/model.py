"""Internal representation of generated documentation pages."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Operation:
    """An OpenAPI operation and its generated location."""

    method: str
    path: str
    operation_id: str
    title: str
    tags: tuple[str, ...]
    primary_tag: str
    source_uri: str
    data: dict
    path_parameters: tuple[dict, ...] = ()


@dataclass
class TagGroup:
    """Operations grouped under their primary OpenAPI tag."""

    name: str
    slug: str
    description: str = ""
    operations: list[Operation] = field(default_factory=list)

    @property
    def source_uri(self) -> str:
        """Return the source URI for this tag's overview page."""
        if not self.operations:
            raise ValueError("A tag group must contain an operation")
        return self.operations[0].source_uri.rsplit("/", 1)[0] + "/index.md"


@dataclass(frozen=True)
class ModelPage:
    """A reusable OpenAPI component schema."""

    name: str
    slug: str
    source_uri: str
    schema: dict


@dataclass
class GeneratedSite:
    """All virtual pages and navigation produced for one specification."""

    pages: dict[str, str]
    api_nav: list
    models_nav: list
    operations: list[Operation]
    models: list[ModelPage]

