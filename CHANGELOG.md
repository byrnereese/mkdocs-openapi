# Changelog

All notable changes to `mkdocs-openapi` are documented here.

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
