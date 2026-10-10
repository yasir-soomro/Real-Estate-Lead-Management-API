# Application Architecture Plan

## Phases

### Phase 1: FastAPI Foundations

Retain the existing app entry point, environment-backed settings, `GET /health`, Pydantic response schema, and test setup. Verify app startup and the health response through the API test client.

### Phase 2: Production Architecture

The lead-domain decisions are approved in [specification.md](specification.md). Implement the lead API through schemas, routers, services, and the in-memory repository, keeping each layer within its responsibility.

## Folder Structure

```text
src/real_estate_lead_api/
  __init__.py
  main.py                    # Build the FastAPI app and run it
  config.py                  # Central environment-backed settings
  dependencies.py            # Provide shared settings and app services
  routers/
    __init__.py
    health.py                # Existing GET /health route
    leads.py                 # Approved lead HTTP routes
  schemas/
    __init__.py
    health.py                # Existing health response model
    leads.py                 # Approved Pydantic lead request/response models
  services/
    __init__.py
    health.py                # Existing health behavior
    leads.py                 # Lead use cases and business rules
  repositories/
    __init__.py
    leads.py                 # Implemented in-memory lead storage
tests/
  test_main.py               # Existing health API test
  test_lead_schemas.py       # Lead request and response validation tests
  test_lead_repository.py    # In-memory storage tests
  test_lead_service.py       # Lead service behavior tests
  test_leads.py              # Lead API tests
```

This matches the current package layout. Health and configuration modules, lead schemas, the in-memory repository, lead services, and approved lead routes are implemented.

## Module Responsibilities

- **`main.py`** creates the FastAPI application, registers routers, and exposes the configured run entry point. It does not own lead rules or storage.
- **`config.py`** reads and exposes the existing app name, debug mode, host, and port settings. Other modules use settings through dependency injection rather than reading environment variables directly.
- **`dependencies.py`** supplies shared dependencies to route handlers, including the lead service and its repository. One in-memory repository instance is shared across requests handled by the same app process; it is not shared across processes and is lost when the process stops.
- **`routers/`** defines HTTP paths, accepts validated request models, calls services, and maps service outcomes to the approved HTTP status codes and response models.
- **`schemas/`** defines Pydantic API request and response models. Health and approved lead models are implemented.
- **`services/`** coordinates each approved use case and applies business rules without depending on FastAPI request objects or storing data itself. It translates repository outcomes into service-level outcomes for routes to map to HTTP.
- **`repositories/`** defines storage operations and implements them with in-memory data. It reports duplicate-phone conflicts without deciding HTTP response formats.
- **`tests/`** tests API behavior through FastAPI's test client and directly tests schema, repository, and service boundaries.

## Request Flow

For `GET /health`:

```text
HTTP request -> health router -> health service -> health response schema -> HTTP 200 response
```

For approved lead operations:

```text
HTTP request
  -> FastAPI router and Pydantic request validation
  -> injected lead service
  -> in-memory lead repository
  -> service result
  -> router response model and approved HTTP response
```

FastAPI returns its standard `422` response when request validation fails, before the service is called. The service reports missing leads and duplicate-phone conflicts without depending on HTTP; the router maps those outcomes to `404` and `409` respectively.

## Consistency and Constraints

- The health and lead contracts are specified in [specification.md](specification.md); route handlers map service outcomes to those status codes and response models.
- Repository lifetime must preserve data between requests to the same app process while honoring the specification's no-sharing-between-processes constraint.
- Lead fields, validation, duplicate handling, update/delete semantics, and listing behavior are approved and are enforced by schemas, repository operations, and services at their respective boundaries.
- No database, authentication, AI agent, deployment setup, or out-of-scope feature is included.