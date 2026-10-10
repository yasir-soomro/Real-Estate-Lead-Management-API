# Implementation Tasks

Complete tasks in order. `R1`–`R7` refer to the numbered functional requirements in [specification.md](specification.md); component names refer to [plan.md](plan.md). The lead contract is approved as recorded in the specification.

## Phase 1: FastAPI Foundations

1. **Verify the application entry point**
	- **Maps to:** R1; `main.py`, `config.py`.
	- **Complete when:** The configured command imports and starts the FastAPI application under the supported Python version.
	- **Verify:** Import the app in the project environment and run the existing test suite.

2. **Verify centralized settings**
	- **Maps to:** R2; `config.py`, `dependencies.py`.
	- **Complete when:** App name, debug mode, host, and port are read through the central settings provider.
	- **Test:** Check defaults and environment overrides for those four settings.

3. **Verify the health API contract**
	- **Maps to:** R3, R5, R7; `main.py`, `routers/health.py`, `services/health.py`, `schemas/health.py`.
	- **Complete when:** `GET /health` returns HTTP `200` and exactly `{"status": "ok"}`.
	- **Test:** Call the route with FastAPI's test client and assert the status and JSON body.

4. **Establish a passing Phase 1 baseline**
	- **Maps to:** R1–R3, R7; `tests/`.
	- **Complete when:** The test suite runs with the project's test command and covers startup/configuration and the health contract.
	- **Test:** Run `uv run python -m unittest discover -s tests -v`.

## Phase 2: Production Architecture

5. **Resolve lead API decisions before implementation (complete)**
	- **Maps to:** R4, R5; `schemas/`, `routers/`, `services/`, `repositories/`.
	- **Complete when:** Lead fields, identifier, validation rules, duplicate behavior, update/delete semantics, list behavior, and response/error contracts are recorded in the specification.
	- **Verify:** Approved requirements are recorded in [specification.md](specification.md).

6. **Define and test lead schemas (complete)**
	- **Depends on:** Task 5 (complete).
	- **Maps to:** R5; `schemas/leads.py`, `tests/`.
	- **Complete when:** Pydantic models define the approved integer ID, required non-empty name/phone/city, positive integer PKR budget, and `new`/`contacted`/`qualified` status with `new` as the create default. PATCH models accept partial fields and reject empty updates.
	- **Test:** Cover valid create/default status, invalid or missing fields, unknown fields, non-positive/non-integer budgets, invalid statuses, response IDs, empty/null PATCH values, and invalid PATCH values.

7. **Define and implement in-memory repository operations (complete)**
	- **Depends on:** Tasks 5 and 6.
	- **Maps to:** R4, R6; `repositories/leads.py`, `tests/`.
	- **Complete when:** The repository supports approved CRUD operations without depending on FastAPI or response formatting, retains data in one process, and rejects duplicate phones after trimming surrounding whitespace.
	- **Test:** Focused repository tests cover CRUD, duplicate phone variants with surrounding whitespace, and absent-record behavior.

8. **Implement lead use cases in the service layer (complete)**
	- **Depends on:** Tasks 6 and 7.
	- **Maps to:** R4–R6; `services/leads.py`, `tests/`.
	- **Complete when:** Each approved lead operation delegates storage to the repository and applies only approved business rules.
	- **Test:** Service tests cover operation success, missing records, and duplicate-phone conflict translation.

9. **Wire shared dependencies (complete)**
	- **Depends on:** Tasks 7 and 8.
	- **Maps to:** R4, R6; `dependencies.py`, `main.py`.
	- **Complete when:** Each app instance owns one repository/service pair and exposes it through FastAPI dependencies; request contexts for the same app share the pair, while separately created apps have separate repositories.
	- **Test:** Resolve the dependencies for two request contexts on one app; assert they share the same instances and that a lead created through the first service is visible through the second. Task 10 covers this persistence through HTTP routes.

10. **Add approved lead routes (complete)**
	 - **Depends on:** Tasks 5–9.
	 - **Maps to:** R4, R5, R7; `routers/leads.py`, `schemas/leads.py`, `services/leads.py`.
	 - **Complete when:** Each approved route delegates to a service and returns the approved response model and status code; routers contain no storage logic.
	 - **Test:** API tests cover create (`201`), list/filter and limit validation, get/update (`200`), delete (`204`), duplicate (`409`), invalid request (`422`), missing lead (`404`), and persistence from a create request to a subsequent list or retrieve request.

11. **Run the full acceptance suite and scope check (complete)**
	 - **Depends on:** Tasks 1–10.
	 - **Maps to:** R1–R7; all components in `plan.md` and `tests/`.
	 - **Complete when:** All tests pass, approved behavior matches the specification, and data remains process-local and in-memory.
	 - **Test:** Run `uv run python -m unittest discover -s tests -v`; review that no database, authentication, AI agent, deployment setup, or out-of-scope feature was added.