## [0.1.3] - 2026-05-01

### Added
- Change password feature
- Secure password validation using Django validators
- Session-safe password update flow

### Security
- Added audit logging for password changes

## [0.1.4] - 2026-05-02

### Added

* Unified error handling system (`handle_error`) supporting 401, 403, 404, 429, and 423
* Pluggable error handlers via `DID_AUTH["ERROR_HANDLERS"]`
* Role-based access decorator (`@role_required`) with automatic dashboard redirection
* Customizable error templates (`did_auth/errors/*.html`)
* Centralized error logging integrated with audit system

### Improved

* Rate limiting decorator now properly enforces limits using `request.limited`
* Logging system hardened to avoid reserved LogRecord conflicts
* Error responses standardized across decorators, views, and flows
* Environment configuration clarity (`dev`, `local`, `prod`) for better deployment control

### Security

* Added structured logging for all error responses (403, 429, etc.)
* Improved rate limit handling with consistent blocking behavior
* Enhanced role-based access control enforcement

### Fixed

* Fixed rate limiting not triggering due to missing `request.limited` check
* Fixed logging crash (`KeyError: Attempt to overwrite 'message' in LogRecord`)
* Fixed inconsistent error handling across views and decorators
