---
description: Generate comprehensive, well-documented unit tests for a Python file using pytest framework.
---

This workflow guides you through generating high-fidelity unit tests with `pytest`, enforcing strict project-standard organization and robust database isolation.

### 1. Parameters & Usage

Trigger this workflow using:
`/unit-tests-pytest target_file::"src/module.py" maximum_tests_limit::10 dependencies::"src/utils.py"`

| Parameter             | Description                                  | Default              |
| :-------------------- | :------------------------------------------- | :------------------- |
| `target_file`         | The Python file to test.                     | `{{ @CurrentFile }}` |
| `dependencies`        | Contextual files for imports/types (max 10). | -                    |
| `maximum_tests_limit` | Max test functions to generate.              | 10                   |
| `max_line_length`     | Maximum characters per documentation line.   | 120                  |
| `min_line_length`     | Minimum line length threshold.               | 80                   |

---

### 2. Task Definition - Step 1: Test Generation

Produce a complete `pytest` module for `{{{ target_file }}}` with no more than `{{{ maximum_tests_limit }}}` functions.

#### 1. STRICT Directory Mirroring

- **Location**: Test files **MUST** be created in a dedicated `tests/` folder at project root.
- **Mirroring**: Replicate the source directory structure within the tests folder.
- **Root Prefix**: Prefix the source root directory with `tests_`.
- **Packages**: Add `__init__.py` to ALL directories in the `tests/` tree.
- **Example**: `src/utils/db.py` -> `tests/tests_src/utils/test_db.py`.

#### 2. Implementation Standards

- **Mocking (CRITICAL)**: **NEVER** allow real database connections. All interactions MUST be mocked (fixture-based engines, sessions, connections).
- **Test Types**: Cover **Nominal behavior**, **Edge cases** (boundary values, empty inputs), and **Invalid inputs** (with `pytest.raises`).
- **Isolation**: Each test MUST be self-contained and deterministic. Mock all external side effects (time, filesystem, HTTP).
- **Naming**: Use descriptive names: `test_<function>_<scenario>`.

---

### 3. Task Definition - Step 2: Documentation Refinement

After the test logic is finalized, enhance its documentation by results of Stage 1:

1. **Refinement Command**: Invoke the documentation engine on the generated file:
   `/document-python-projects target_file_name::"<generated_test_path>" docstring_style::"Google" max_line_length::{{{ max_line_length }}} min_line_length::{{{ min_line_length }}}`
2. **Quality**: Ensure professional Google-style docstrings with accurate Parameter (fixture) and Return sections.

---

### 4. Constraints & Requirements (ASSERTIVE)

#### DATABASE MOCKING - CRITICAL

1.  **Connection Control**: Use `unittest.mock.patch` or `MagicMock` to stop all real DB calls.
2.  **Specific Patterns**:
    - **SQLAlchemy/SQLModel**: Mock `engine`, `Session`, and `Session.query`.
    - **Psycopg/SQLite**: Mock `connection` and `cursor` (e.g., `cursor.fetchall`).
    - **Mongo**: Mock `MongoClient` and collections.
3.  **Failure Scenarios**: Mock `OperationalError`, `ConnectionError`, and test transaction rollbacks.
4.  **Realistic Data**: Mock connections MUST return realistic data structures mimicking cursor behavior.

#### ORGANIZATIONAL RULES

5.  **Project Root**: The `tests/` folder must exist at the same level as the source root.
6.  **Mirror Examples**:
    - `app/api.py` -> `tests/tests_app/test_api.py`
    - `mylib/core/util.py` -> `tests/tests_mylib/core/test_util.py`
7.  **Package Integrity**: Ensure every folder in the test path has an `__init__.py`.

#### PYTEST BEST PRACTICES

8.  **AAA Pattern**: Follow Arrange-Act-Assert explicitly in test bodies.
9.  **Fixtures**: Extract shared setup into clear, reusable fixtures.
10. **Parametrize**: Use `@pytest.mark.parametrize` for testing multiple input states.
11. **Docstrings**: Provide a module summary and concise docstrings for every test function.
12. **Pure Functions**: Emphasize property-like tests and input/output contracts.
13. **Classes**: Test constructors, public methods, and state transitions.

#### DOCUMENTATION CONSTRAINTS

14. **Line Length**: Respect `{{{ max_line_length }}}`. Expand lines naturally if they exceed `{{{ min_line_length }}}`.
15. **Standard**: Use Google docstyle conventions ONLY.

### 5. Quality Checklist

- [x] Test file located in `tests/` mirroring the source structure.
- [x] Every directory in the test path contains `__init__.py`.
- [x] `test_` prefix added to filename.
- [x] DATABASE MOCKING is fully implemented; no real connections possible.
- [x] Fixtures and parametrization used correctly.
- [x] Scenarios cover: Nominal, Boundary, Error, and Side Effects.
- [x] Documentation refinement command (Step 2) applied to generated code.
- [x] All documentation line lengths within `{{{ max_line_length }}}`.
