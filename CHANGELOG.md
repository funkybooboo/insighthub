# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Changed
- Consolidated domain models, repositories, and storage into the shared package to provide a single source of truth.
- Moved contract tests to shared and added signature-based tests; server tests now focus on integration, not implementation details.
- Removed duplicate server copies of domain models/repositories and moved storage implementations to shared.
- Updated documentation to reflect contract-first testing and shared layout (lowercase file names).

### Removed
- Old server copies of domain models and repositories.
- Server-side storage implementations that duplicated shared storage code.

## [1.0.0] – 2025-11-18
- Initial release.
