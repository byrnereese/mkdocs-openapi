"""Render OpenAPI structures as Material-friendly Markdown."""

from __future__ import annotations

import json
import posixpath
from collections.abc import Mapping, Sequence
from typing import Any

import yaml

from .model import ModelPage, Operation, TagGroup
from .parser import resolve_local_ref


class MarkdownRenderer:
    """Render all page types for one OpenAPI document."""

    def __init__(
        self,
        document: dict,
        *,
        output_dir: str,
        models_dir: str,
        groups: list[TagGroup],
        models: list[ModelPage],
    ) -> None:
        self.document = document
        self.output_dir = output_dir
        self.models_dir = models_dir
        self.groups = groups
        self.models = models
        self.models_by_name = {model.name: model for model in models}
        self.security_schemes = (
            document.get("components", {}).get("securitySchemes", {})
        )

    def render_api_overview(self) -> str:
        """Render the API-level landing page."""
        info = self.document.get("info", {})
        title = str(info.get("title") or "API reference")
        lines = [f"# {title}", ""]
        description = str(info.get("description", "")).strip()
        if description:
            lines.extend([description, ""])

        metadata = []
        if info.get("version"):
            metadata.append(("Version", f"`{info['version']}`"))
        if self.document.get("openapi"):
            metadata.append(("OpenAPI", f"`{self.document['openapi']}`"))
        if metadata:
            lines.extend(["## About", "", "| Field | Value |", "| --- | --- |"])
            lines.extend(
                f"| {self._table(key)} | {self._table(value)} |"
                for key, value in metadata
            )
            lines.append("")

        servers = self.document.get("servers", [])
        if servers:
            lines.extend(
                ["## Servers", "", "| URL | Description |", "| --- | --- |"]
            )
            for server in servers:
                if not isinstance(server, Mapping):
                    continue
                lines.append(
                    f"| `{self._table(server.get('url', ''))}` "
                    f"| {self._table(server.get('description', '')) or '—'} |"
                )
            lines.append("")

        if self.groups:
            lines.extend(
                [
                    "## Resources",
                    "",
                    "| Resource | Description | Operations |",
                    "| --- | --- | ---: |",
                ]
            )
            from_uri = f"{self.output_dir}/index.md"
            for group in self.groups:
                link = self._link(group.name, from_uri, group.source_uri)
                lines.append(
                    f"| {link} | {self._table(group.description) or '—'} "
                    f"| {len(group.operations)} |"
                )
            lines.append("")

        if self.security_schemes:
            lines.extend(["## Authentication", ""])
            for name, raw_scheme in self.security_schemes.items():
                scheme = resolve_local_ref(self.document, raw_scheme)
                if not isinstance(scheme, Mapping):
                    continue
                lines.extend(
                    [
                        f"### {name}",
                        "",
                        self._security_scheme_description(scheme),
                        "",
                    ]
                )

        if self.models:
            models_uri = f"{self.models_dir}/index.md"
            link = self._link(
                "model reference", f"{self.output_dir}/index.md", models_uri
            )
            lines.extend(
                [
                    "## Data models",
                    "",
                    f"Reusable schemas are documented in the {link}.",
                    "",
                ]
            )

        return self._finish(lines)

    def render_tag_overview(self, group: TagGroup) -> str:
        """Render a tag landing page with links to its operations."""
        lines = [self._frontmatter([group.name]), f"# {group.name}", ""]
        if group.description:
            lines.extend([group.description.strip(), ""])
        lines.extend(["| Method | Operation |", "| --- | --- |"])
        for operation in group.operations:
            badge = self._method_badge(operation.method)
            link = self._link(
                operation.title, group.source_uri, operation.source_uri
            )
            lines.append(f"| {badge} | {link} |")
        lines.append("")
        return self._finish(lines)

    def render_operation(self, operation: Operation) -> str:
        """Render a single operation page."""
        tags = list(dict.fromkeys([*operation.tags, operation.method]))
        lines = [
            self._frontmatter(tags),
            f"# {operation.title}",
            "",
            f"{self._method_badge(operation.method)} "
            f"`{operation.path}`{{ .operation-path }}",
            "",
        ]

        description = str(operation.data.get("description", "")).strip()
        if description:
            lines.extend([description, ""])
        if operation.data.get("deprecated"):
            lines.extend(
                [
                    '!!! warning "Deprecated"',
                    "",
                    "    This operation is deprecated.",
                    "",
                ]
            )

        if operation.operation_id:
            lines.append(f"**Operation ID:** `{operation.operation_id}`  ")
        lines.extend(
            [
                f"**Authorization:** {self._security_for(operation.data)}",
                "",
            ]
        )

        parameters = self._operation_parameters(operation)
        if parameters:
            lines.extend(
                [
                    "## Parameters",
                    "",
                    "| Name | Location | Type | Required | Description |",
                    "| --- | --- | --- | --- | --- |",
                ]
            )
            for parameter in parameters:
                schema = parameter.get("schema", {})
                if not schema and isinstance(parameter.get("content"), Mapping):
                    first_media = next(iter(parameter["content"].values()), {})
                    schema = first_media.get("schema", {})
                required = bool(
                    parameter.get("required") or parameter.get("in") == "path"
                )
                lines.append(
                    "| `{name}` | {location} | {type_} | {required} | "
                    "{description} |".format(
                        name=self._table(parameter.get("name", "")),
                        location=self._table(parameter.get("in", "")),
                        type_=self._table(
                            self._schema_type(schema, operation.source_uri)
                        ),
                        required="**Yes**" if required else "No",
                        description=self._table(
                            parameter.get("description", "")
                        )
                        or "—",
                    )
                )
            lines.append("")

        raw_body = operation.data.get("requestBody")
        body = resolve_local_ref(self.document, raw_body)
        if isinstance(body, Mapping):
            lines.extend(self._render_request_body(body, operation.source_uri))

        responses = operation.data.get("responses", {})
        if isinstance(responses, Mapping) and responses:
            lines.extend(
                [
                    "## Responses",
                    "",
                    "| Status | Description | Body |",
                    "| --- | --- | --- |",
                ]
            )
            for status, raw_response in responses.items():
                response = resolve_local_ref(self.document, raw_response)
                if not isinstance(response, Mapping):
                    continue
                lines.append(
                    f"| `{self._table(status)}` "
                    f"| {self._table(response.get('description', '')) or '—'} "
                    f"| {self._response_body(response, operation.source_uri)} |"
                )
            lines.append("")

        external_docs = operation.data.get("externalDocs")
        if isinstance(external_docs, Mapping) and external_docs.get("url"):
            label = str(external_docs.get("description") or "External documentation")
            lines.extend(
                [
                    "## See also",
                    "",
                    f"[{label}]({external_docs['url']})",
                    "",
                ]
            )

        return self._finish(lines)

    def render_models_overview(self) -> str:
        """Render the model index."""
        source_uri = f"{self.models_dir}/index.md"
        lines = [
            self._frontmatter(["Model"]),
            "# Models",
            "",
            "Reusable component schemas are documented once and linked from "
            "every operation that uses them.",
            "",
            "| Model | Description |",
            "| --- | --- |",
        ]
        for model in self.models:
            link = self._link(model.name, source_uri, model.source_uri)
            lines.append(
                f"| {link} | {self._table(model.schema.get('description', '')) or '—'} |"
            )
        lines.append("")
        return self._finish(lines)

    def render_model(self, model: ModelPage) -> str:
        """Render one reusable component schema."""
        schema = model.schema
        lines = [self._frontmatter(["Model"]), f"# {model.name}", ""]
        if schema.get("description"):
            lines.extend([str(schema["description"]).strip(), ""])

        composition = self._composition(schema, model.source_uri)
        if composition:
            lines.extend(["## Composition", "", composition, ""])

        properties, required = self._model_properties(schema)
        if properties:
            lines.extend(
                [
                    "## Properties",
                    "",
                    "| Property | Type | Required | Description |",
                    "| --- | --- | --- | --- |",
                ]
            )
            for name, raw_property in properties.items():
                property_schema = (
                    raw_property if isinstance(raw_property, Mapping) else {}
                )
                details = self._schema_details(property_schema)
                lines.append(
                    f"| `{self._table(name)}` "
                    f"| {self._table(self._schema_type(property_schema, model.source_uri))} "
                    f"| {'**Yes**' if name in required else 'No'} "
                    f"| {self._table(details) or '—'} |"
                )
            lines.append("")
        else:
            lines.extend(
                [
                    "## Type",
                    "",
                    self._schema_type(schema, model.source_uri),
                    "",
                ]
            )

        example = self._sample_from_schema(schema)
        if example is not None:
            lines.extend(
                [
                    "## Example",
                    "",
                    "```json",
                    self._json_dump(example),
                    "```",
                    "",
                ]
            )
        return self._finish(lines)

    def _render_request_body(self, body: Mapping, source_uri: str) -> list[str]:
        lines = ["## Request body", ""]
        description = str(body.get("description", "")).strip()
        if description:
            lines.extend([description, ""])
        if body.get("required"):
            lines.extend(["**Required:** Yes", ""])

        content = body.get("content", {})
        if not isinstance(content, Mapping) or not content:
            return lines

        if len(content) == 1:
            media_type, media = next(iter(content.items()))
            lines.extend(
                self._render_media_type(str(media_type), media, source_uri)
            )
            return lines

        for media_type, media in content.items():
            lines.extend([f'=== "{media_type}"', ""])
            rendered = self._render_media_type(
                str(media_type), media, source_uri, include_label=False
            )
            lines.extend(self._indent(rendered, 4))
            lines.append("")
        return lines

    def _render_media_type(
        self,
        media_type: str,
        raw_media: object,
        source_uri: str,
        *,
        include_label: bool = True,
    ) -> list[str]:
        media = raw_media if isinstance(raw_media, Mapping) else {}
        schema = media.get("schema", {})
        lines: list[str] = []
        if include_label:
            lines.extend([f"**Content type:** `{media_type}`", ""])
        if schema:
            lines.extend(
                [f"**Schema:** {self._schema_type(schema, source_uri)}", ""]
            )

        example = self._media_example(media, schema)
        if example is not None and self._is_json_media_type(media_type):
            lines.extend(
                [
                    "```json",
                    self._json_dump(example),
                    "```",
                    "",
                ]
            )
        elif example is not None and isinstance(example, str):
            lines.extend(["```text", example, "```", ""])
        return lines

    def _operation_parameters(self, operation: Operation) -> list[Mapping]:
        combined: dict[tuple[str, str], Mapping] = {}
        for raw_parameter in [
            *operation.path_parameters,
            *operation.data.get("parameters", []),
        ]:
            parameter = resolve_local_ref(self.document, raw_parameter)
            if not isinstance(parameter, Mapping):
                continue
            key = (
                str(parameter.get("name", "")),
                str(parameter.get("in", "")),
            )
            combined[key] = parameter
        return list(combined.values())

    def _response_body(self, response: Mapping, source_uri: str) -> str:
        content = response.get("content", {})
        if not isinstance(content, Mapping) or not content:
            return "—"
        types: list[str] = []
        for media in content.values():
            if not isinstance(media, Mapping):
                continue
            schema = media.get("schema")
            rendered = (
                self._schema_type(schema, source_uri) if schema else "content"
            )
            if rendered not in types:
                types.append(rendered)
        return ", ".join(types) or "—"

    def _schema_type(self, raw_schema: object, source_uri: str) -> str:
        if not isinstance(raw_schema, Mapping):
            return "any"
        ref = raw_schema.get("$ref")
        if isinstance(ref, str) and ref.startswith("#/components/schemas/"):
            name = ref.removeprefix("#/components/schemas/")
            model = self.models_by_name.get(name)
            if model:
                return self._link(name, source_uri, model.source_uri)
            return name
        if isinstance(ref, str):
            return f"`{ref}`"

        for keyword, label in (
            ("oneOf", "one of"),
            ("anyOf", "any of"),
            ("allOf", "all of"),
        ):
            choices = raw_schema.get(keyword)
            if isinstance(choices, Sequence) and not isinstance(
                choices, (str, bytes)
            ):
                rendered = [
                    self._schema_type(choice, source_uri) for choice in choices
                ]
                return f"{label}: " + ", ".join(rendered)

        schema_type = raw_schema.get("type")
        if isinstance(schema_type, list):
            return " or ".join(str(item) for item in schema_type)
        if schema_type == "array":
            return (
                "array of "
                + self._schema_type(raw_schema.get("items", {}), source_uri)
            )
        if schema_type == "object" and raw_schema.get("additionalProperties"):
            additional = raw_schema["additionalProperties"]
            if additional is True:
                return "object of any"
            return "object of " + self._schema_type(additional, source_uri)
        if not schema_type:
            if raw_schema.get("properties"):
                schema_type = "object"
            elif raw_schema.get("enum"):
                schema_type = "string"
            else:
                schema_type = "any"
        schema_format = raw_schema.get("format")
        rendered = str(schema_type)
        if schema_format:
            rendered += f" · {schema_format}"
        if raw_schema.get("nullable"):
            rendered += " or null"
        return rendered

    def _schema_details(self, schema: Mapping) -> str:
        parts: list[str] = []
        if schema.get("description"):
            parts.append(str(schema["description"]).strip())
        if schema.get("enum"):
            values = ", ".join(f"`{value}`" for value in schema["enum"])
            parts.append(f"Allowed values: {values}.")
        if "default" in schema:
            parts.append(f"Default: `{schema['default']}`.")
        if "minimum" in schema:
            parts.append(f"Minimum: `{schema['minimum']}`.")
        if "maximum" in schema:
            parts.append(f"Maximum: `{schema['maximum']}`.")
        if "minLength" in schema:
            parts.append(f"Minimum length: `{schema['minLength']}`.")
        if "maxLength" in schema:
            parts.append(f"Maximum length: `{schema['maxLength']}`.")
        if schema.get("pattern"):
            parts.append(f"Pattern: `{schema['pattern']}`.")
        return " ".join(parts)

    def _model_properties(
        self, schema: Mapping
    ) -> tuple[dict[str, object], set[str]]:
        properties = dict(schema.get("properties", {}))
        required = set(schema.get("required", []))
        for member in schema.get("allOf", []):
            if not isinstance(member, Mapping) or "$ref" in member:
                continue
            properties.update(member.get("properties", {}))
            required.update(member.get("required", []))
        return properties, required

    def _composition(self, schema: Mapping, source_uri: str) -> str:
        for keyword, label in (
            ("allOf", "All of"),
            ("oneOf", "One of"),
            ("anyOf", "Any of"),
        ):
            members = schema.get(keyword)
            if isinstance(members, Sequence) and not isinstance(
                members, (str, bytes)
            ):
                return f"**{label}:** " + ", ".join(
                    self._schema_type(member, source_uri) for member in members
                )
        return ""

    def _media_example(self, media: Mapping, schema: object) -> Any:
        if "example" in media:
            return media["example"]
        examples = media.get("examples")
        if isinstance(examples, Mapping) and examples:
            first = resolve_local_ref(self.document, next(iter(examples.values())))
            if isinstance(first, Mapping) and "value" in first:
                return first["value"]
        return self._sample_from_schema(schema)

    def _sample_from_schema(
        self,
        raw_schema: object,
        *,
        depth: int = 0,
        seen_refs: frozenset[str] = frozenset(),
    ) -> Any:
        if depth > 6 or not isinstance(raw_schema, Mapping):
            return None
        if "example" in raw_schema:
            return raw_schema["example"]
        if "default" in raw_schema:
            return raw_schema["default"]
        if raw_schema.get("enum"):
            return raw_schema["enum"][0]

        ref = raw_schema.get("$ref")
        if isinstance(ref, str) and ref.startswith("#/"):
            if ref in seen_refs:
                return None
            resolved = resolve_local_ref(self.document, raw_schema)
            return self._sample_from_schema(
                resolved,
                depth=depth + 1,
                seen_refs=seen_refs | {ref},
            )

        if raw_schema.get("allOf"):
            merged: dict[str, Any] = {}
            for member in raw_schema["allOf"]:
                sample = self._sample_from_schema(
                    member, depth=depth + 1, seen_refs=seen_refs
                )
                if isinstance(sample, dict):
                    merged.update(sample)
            return merged or None
        for keyword in ("oneOf", "anyOf"):
            if raw_schema.get(keyword):
                return self._sample_from_schema(
                    raw_schema[keyword][0],
                    depth=depth + 1,
                    seen_refs=seen_refs,
                )

        schema_type = raw_schema.get("type")
        if not schema_type and raw_schema.get("properties"):
            schema_type = "object"
        if schema_type == "object":
            result: dict[str, Any] = {}
            for index, (name, child) in enumerate(
                raw_schema.get("properties", {}).items()
            ):
                if index >= 12:
                    break
                sample = self._sample_from_schema(
                    child, depth=depth + 1, seen_refs=seen_refs
                )
                if sample is not None:
                    result[str(name)] = sample
            return result
        if schema_type == "array":
            item = self._sample_from_schema(
                raw_schema.get("items", {}),
                depth=depth + 1,
                seen_refs=seen_refs,
            )
            return [item] if item is not None else []
        if schema_type == "string":
            return {
                "date": "2026-01-01",
                "date-time": "2026-01-01T00:00:00Z",
                "email": "user@example.com",
                "uuid": "00000000-0000-4000-8000-000000000000",
                "uri": "https://example.com",
                "binary": "<binary>",
            }.get(str(raw_schema.get("format")), "string")
        if schema_type == "integer":
            return int(raw_schema.get("minimum", 0))
        if schema_type == "number":
            return float(raw_schema.get("minimum", 0))
        if schema_type == "boolean":
            return False
        return None

    def _security_for(self, operation: Mapping) -> str:
        requirements = (
            operation["security"]
            if "security" in operation
            else self.document.get("security", [])
        )
        if not requirements:
            return "None"
        alternatives: list[str] = []
        for requirement in requirements:
            if not isinstance(requirement, Mapping):
                continue
            schemes: list[str] = []
            for name, scopes in requirement.items():
                scheme = resolve_local_ref(
                    self.document, self.security_schemes.get(name, {})
                )
                label = self._security_scheme_label(name, scheme)
                if scopes:
                    label += " (" + ", ".join(f"`{scope}`" for scope in scopes) + ")"
                schemes.append(label)
            if schemes:
                alternatives.append(" **and** ".join(schemes))
        return " **or** ".join(alternatives) or "None"

    def _security_scheme_label(self, name: str, scheme: object) -> str:
        if not isinstance(scheme, Mapping):
            return str(name)
        scheme_type = scheme.get("type")
        if scheme_type == "apiKey":
            return "API key"
        if scheme_type == "oauth2":
            return "OAuth 2.0"
        if scheme_type == "openIdConnect":
            return "OpenID Connect"
        if scheme_type == "http":
            value = str(scheme.get("scheme") or "HTTP")
            return value.upper() if value.lower() in {"basic", "bearer"} else value
        return str(name)

    def _security_scheme_description(self, scheme: Mapping) -> str:
        scheme_type = scheme.get("type")
        if scheme_type == "apiKey":
            return (
                f"Send the API key in the `{scheme.get('name', 'api_key')}` "
                f"{scheme.get('in', 'header')} value."
            )
        if scheme_type == "oauth2":
            scopes: dict[str, str] = {}
            for flow in scheme.get("flows", {}).values():
                if isinstance(flow, Mapping):
                    scopes.update(flow.get("scopes", {}))
            if not scopes:
                return "OAuth 2.0."
            lines = ["OAuth 2.0 scopes:", ""]
            lines.extend(f"- `{name}` — {description}" for name, description in scopes.items())
            return "\n".join(lines)
        if scheme_type == "http":
            return f"HTTP {scheme.get('scheme', 'authentication')}."
        return f"{scheme_type or 'Custom'} authentication."

    def _method_badge(self, method: str) -> str:
        lower = method.lower()
        return f"`{method.upper()}`{{ .http-method .{lower} }}"

    def _link(self, label: str, from_uri: str, to_uri: str) -> str:
        base = posixpath.dirname(from_uri) or "."
        target = posixpath.relpath(to_uri, base)
        return f"[{label}]({target})"

    def _frontmatter(self, tags: list[str]) -> str:
        data = yaml.safe_dump(
            {"tags": tags},
            sort_keys=False,
            allow_unicode=True,
        ).strip()
        return f"---\n{data}\n---"

    def _table(self, value: object) -> str:
        return (
            str(value)
            .strip()
            .replace("\n", " ")
            .replace("\r", " ")
            .replace("|", r"\|")
        )

    def _indent(self, lines: list[str], spaces: int) -> list[str]:
        prefix = " " * spaces
        indented: list[str] = []
        for line in lines:
            parts = line.splitlines() or [""]
            indented.extend(prefix + part if part else "" for part in parts)
        return indented

    def _is_json_media_type(self, value: str) -> bool:
        media_type = value.lower().split(";", 1)[0].strip()
        return media_type == "application/json" or media_type.endswith("+json")

    def _json_dump(self, value: object) -> str:
        return json.dumps(
            value,
            indent=2,
            ensure_ascii=False,
            default=lambda item: (
                item.isoformat() if hasattr(item, "isoformat") else str(item)
            ),
        )

    def _finish(self, lines: list[str]) -> str:
        while lines and not lines[-1]:
            lines.pop()
        return "\n".join(lines) + "\n"
