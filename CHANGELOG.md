# Changelog

All notable changes to `mkdocs-openapi` are documented here.

## 0.3.2 — 2026-10-09

### Added

- Operation endpoint bars with horizontally scrollable URLs and copy controls.
- Page action menus for copying generated Markdown or viewing it in a new tab.
  The menu uses a compact three-dot action button.
- Deprecated operations display a Material warning admonition.

### Changed

- Parameters render as wrapping-safe entries grouped into path, query, header,
  cookie, and request-body sections.
- Responses render as status-code tabs with schema properties expanded inline
  instead of linking response schemas to model pages.
- HTTP method pills are narrower, and `DELETE` pills use the compact `DEL`
  label.
- Generated content tabs use the site's normal Material/PyMdown styling rather
  than forcing the alternate tab style.

### Fixed

- HTTP method pills remain visible when their operation page is active in
  Material's primary navigation.
- Bullet lists in API overview descriptions render as lists when they directly
  follow introductory text.

## 0.3.0 — 2026-10-07

### Added

- A `models_mode: inline` option that renders each operation's reachable model
  graph on the operation page without generating standalone model pages or
  model navigation.

## 0.2.2 — 2026-07-29

### Added

- A `suppress_tag_overview` option for omitting tag overview links from
  generated navigation while continuing to generate the overview pages.
- A `suppress_method_badges` option for hiding HTTP method badges in Material's
  primary navigation.

## 0.2.1 — 2026-07-29

### Fixed

- External navigation links ending in `.json`, `.yaml`, or `.yml` are no
  longer mistaken for local OpenAPI specifications.

## 0.2.0 — 2026-07-29

### Added

- Support for generating multiple OpenAPI specifications in one MkDocs site.
- Per-specification output, model, navigation, and tag configuration through
  the new `specs` mapping.
- Validation for duplicate sources, generated directories, navigation entries,
  and cross-specification page collisions.
- A runnable multiple-API example.

### Changed

- OpenAPI documents are parsed and their generated paths are validated before
  MkDocs files or navigation are modified.
- Generation errors in multi-specification sites identify the owning
  specification.

### Compatibility

- Existing single-specification configuration and generated URLs are
  unchanged.

## 0.1.0 — 2026-07-28

- Initial release.
