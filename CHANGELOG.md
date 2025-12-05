# Changelog

All notable changes to this project will be documented in this file.

## [v1.0.2] - 2025-12-05

### Added
- MIT License file
- License section in README files

### Changed
- Translated test_server.sh to English

## [v1.0.1] - 2025-12-03

### Changed
- Translated all comments and messages to English
- Updated documentation (README.md) with English version
- Improved code documentation and docstrings

### Technical
- All source code comments now in English
- Logging messages in English
- Maintained French documentation in README_fr.md

## [v1.0.0] - 2025-12-03

### Added
- Initial working version of PmWiki MCP server
- SSE (Server-Sent Events) transport support
- Three main tools: `search_wiki`, `read_page`, `list_pages`
- Docker Hub support
- Complete documentation (French and English)
- Pylint configuration for development
- Test script

### Features
- Read PmWiki pages
- Search text across wiki
- List available pages with group filtering
- Expose pages as MCP resources
- Docker container with health check
- Support for remote connections via network

### Docker
- Published on Docker Hub: `kcofoni/pmwiki-mcp`
- Docker Compose configuration
- Volume mounting for wiki.d directory
