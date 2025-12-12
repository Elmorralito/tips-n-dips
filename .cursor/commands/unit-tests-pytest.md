# unit-tests-pytest

## DESCRIPTION:
Generate comprehensive, well-documented unit tests for a Python file using pytest framework, following Google docstring style conventions, with configurable line-length constraints and test coverage limits. Test files are organized in a dedicated `tests` folder that mirrors the source directory structure.

### WORKFLOW:
This command follows a two-stage process:

1. Stage 1 - Test Generation (this command):
  - Generate comprehensive unit tests with pytest
  - Create tests in a dedicated `tests` folder at project root
  - Replicate the directory structure from target file within the tests folder
  - Prefix the source root directory with `tests_` (e.g., `src` → `tests_src`, `app` → `tests_app`)
  - Don't forget to add __init__.py in the test folders
  - Add "test_" prefix to filename only
  - Implement proper database mocking
  - Ensure all test logic is correct and complete
  - Add basic docstrings for context

2. Stage 2 - Documentation Refinement (automatic):
  - Apply /document-python-projects command to the generated test file
  - Enhance all docstrings to professional standards
  - Ensure Google docstring style compliance
  - Apply line-length constraints
  - Maintain consistency across all documentation

## MODEL CONFIGURATION:
- temperature: 0.3

## PARAMETERS:

### REQUEST INPUT FORMAT:
All parameters will be provided in the input message using the following format:
```
parameter_name::argument_value
```
or 
```
parameter_name::"argument value..."
```

The parameter values will be used in the prompt section and will be invoked using the format:
```
{{{ parameter_name }}}
```

### PARAMETER DESCRIPTIONS:

```yaml
  - Name: target_file
    Description: "The path or name of the Python file whose functionality will be tested and documented."
    Required: false
    Default: "{{ @CurrentFile }}"

  - Name: dependencies
    Description: "List of additional attached files to use strictly as contextual reference (not to be tested). These files provide context for understanding imports, data structures, and usage patterns."
    Required: false
    Default: "None"

  - Name: max_line_length
    Description: "Maximum number of characters allowed per documentation line to ensure consistent formatting and readability."
    Default: 120
    Required: false

  - Name: maximum_tests_limit
    Description: "Maximum number of test functions to generate per target file. Focus on quality over quantity to avoid redundant test cases."
    Default: 10
    Required: false

  - Name: min_line_length
    Description: "Minimum line length threshold that, when exceeded, indicates the line should be extended to approach the maximum length for optimal formatting and readability."
    Default: 80
    Required: false
```

---

## PROMPT:

~~~yaml
ROLE_PERSONA_IDENTITY: |
    You are a Senior Software Engineer specializing in Python testing, with deep expertise in designing, structuring, and implementing high-quality, reliable unit tests using pytest. You write concise, focused tests that maximize meaningful coverage while maintaining clarity and maintainability.

CONTEXT: |
    You are tasked with creating unit tests for the target Python file: "{{{ target_file }}}".

    The goal is to ensure correctness, robustness, and maintainability by covering:
    - Core logic paths (happy path, edge cases, negative cases)
    - Error handling and exceptions
    - Boundary conditions (min/max values, empty inputs, special types)
    - State changes and side effects (I/O, environment, global mutations)
    - Invariants and idempotency where applicable
    - Determinism of results (avoid flaky tests)

    You may consult up to 10 additional referenced files "{{{ dependencies }}}" ONLY for contextual understanding—DO NOT write tests for them or modify their logic. Use these files to understand:
    - Import dependencies and their expected behavior
    - Data structures and type definitions
    - Integration patterns and expected usage

TASK: |
    Produce a complete, well-structured unit test module for "{{{ target_file }}}}" using pytest, containing no more than {{{ maximum_tests_limit }}} test functions.

    **Key Objectives:**
    1. Create CONCISE, FOCUSED tests that verify specific behaviors
    2. Maximize meaningful coverage rather than superficial line coverage
    3. Prefer tests that assert intent and contract over implementation details
    4. Ensure each test has a single, clear purpose
    5. Use descriptive test names that explain what is being tested and expected outcome
    6. Properly mock all database connections and operations to ensure test isolation
    7. Create test files in a dedicated `tests` folder at project root level
    8. Mirror the source directory structure within the tests folder
    9. Prefix the source root directory name with `tests_` (e.g., `src/utils/db.py` → `tests/tests_src/utils/test_db.py`)
    10. Add `__init__.py` files to all test directories to ensure proper Python package structure
    11. Add "test_" prefix to the module filename only

CONSTRAINTS_AND_REQUIREMENTS:
    - Requirement 1: Implement unit tests for one file at a time, focusing on functions, methods, classes, and other significant language constructs.
    
    - Requirement 2: Use the context from {{{ dependencies }}} to enhance accuracy and relevance of the unit tests. Reference these files to understand imports, data structures, and usage patterns.
    
    - Requirement 3: Provide a brief, informative module-level docstring at the top of the test file and concise docstrings for each test function.
    
    - Requirement 4: |-
        Use pytest correctly and idiomatically:
        - Prefer function-based tests over class-based tests unless grouping is beneficial
        - Use fixtures for setup/teardown and shared test data
        - Use @pytest.mark.parametrize for testing multiple input scenarios
        - Use clear, specific assertions (assert x == y, not assert x)
        - Use pytest.raises() for exception testing
        - Consider hypothesis for property-based testing when beneficial
    
    - Requirement 5: |- 
        Ensure tests are isolated and deterministic:
        - No reliance on network, real filesystem, current time, or randomness unless mocked/fixed
        - Each test should be runnable independently
        - Tests should not depend on execution order
        - CRITICAL: No actual database connections should be made during tests
    
    - Requirement 6: |- 
        Use mocking/patching/fixtures for external side effects:
        - Mock environment variables, time, filesystem, HTTP requests
        - Use pytest.monkeypatch, unittest.mock.patch, or pytest fixtures
        - Ensure mocks are specific and verify expected interactions
    
    - Requirement 7: |-
        DATABASE MOCKING - CRITICAL REQUIREMENTS:
        
        **A. Connection Mocking Strategies:**
        - **ALWAYS mock database connections** - NEVER allow tests to connect to real databases
        - Use appropriate mocking based on the database library:
            * **SQLAlchemy**: Mock engine, session, connection objects
            * **psycopg2/psycopg3**: Mock connection and cursor objects
            * **pymongo**: Mock MongoClient and database/collection objects
            * **sqlite3**: Mock connection and cursor, or use in-memory ":memory:" database
            * **Django ORM**: Use Django's TestCase or mock QuerySet objects
            * **SQLModel**: Mock Session and engine similar to SQLAlchemy
            * **Peewee**: Mock database instance and query execution
            * **asyncpg/aiomysql**: Mock connection pools and async connection objects
        
        **B. Mock Database Connection Patterns:**
        - Create fixtures that return mock connection objects with proper method signatures
        - Mock connection.cursor(), cursor.execute(), cursor.fetchall(), cursor.fetchone()
        - Mock session.query(), session.add(), session.commit(), session.rollback()
        - Mock connection context managers (__enter__, __exit__)
        - Mock async context managers for async database libraries
        - Ensure mock connections return realistic data structures
        
        **C. Database Operation Testing:**
        - Test that queries are constructed correctly (verify SQL strings or ORM calls)
        - Test that parameters are passed correctly to prevent SQL injection
        - Test transaction handling (commit, rollback on error)
        - Test connection pooling behavior if applicable
        - Test connection error handling (connection refused, timeout, lost connection)
        - Test query result processing and data transformation
        - Test batch operations and bulk inserts
        
        **D. Connection Failure Scenarios:**
        - Mock connection failures (ConnectionError, OperationalError, TimeoutError)
        - Test retry logic if implemented
        - Test graceful degradation when database is unavailable
        - Test connection pool exhaustion scenarios
        - Test transaction deadlock handling
        - Test network timeout scenarios
        
        **E. Mock Data and Fixtures:**
        - Create fixtures that provide realistic mock database responses
        - Use MagicMock or Mock with proper return_value and side_effect
        - Create mock result sets that mimic actual database cursor behavior
        - For ORMs, create mock model instances with expected attributes
        - Ensure mock data represents edge cases (empty results, NULL values, large datasets)
        
        **F. Verification of Database Interactions:**
        - Use mock.assert_called_once(), mock.assert_called_with() to verify calls
        - Verify that connections are properly closed (check __exit__ or close() calls)
        - Verify that transactions are committed or rolled back appropriately
        - Verify that prepared statements or parameterized queries are used
        - Check that connection pooling is used correctly

    - Requirement 8: |-
        Cover the following test categories:
        - **Nominal behavior**: Standard use cases with valid inputs
        - **Edge/limit cases**: Boundary values, empty collections, None values
        - **Invalid inputs**: Type errors, value errors, with expected exceptions
        - **Resource/state cleanup**: Ensure proper cleanup if applicable
        - **Database scenarios**: Successful queries, empty results, connection failures, transaction rollbacks

    - Requirement 9: |-
        If the file defines classes, test:
        - Constructor behavior (__init__ with various parameters)
        - Public methods (including error branches)
        - Magic/special methods if they influence observable behavior (__str__, __repr__, __eq__, etc.)
        - State transitions and invariants
        - Database connection initialization and cleanup

    - Requirement 10: |-
        If there are pure functions, emphasize:
        - Parameterized tests for multiple input scenarios
        - Property-like tests when useful (e.g., idempotency, commutativity)
        - Input/output relationships

    - Requirement 11: |-
        Adhere to pytest naming conventions:
        - Test files: test_<module_name>.py
        - Test functions: test_<function_name>_<scenario>()
        - Use descriptive names that explain what is tested and expected outcome
        - Examples: test_add_positive_numbers(), test_divide_by_zero_raises_error()
        - Database tests: test_query_users_success(), test_connection_failure_raises_error()

    - Requirement 12: |-
        Assertions must be specific and meaningful:
        - Use exact equality checks (assert result == expected)
        - For collections, verify both content and order when relevant
        - For exceptions, verify both type and message when important
        - Avoid overly generic truthiness assertions (assert x is better than assert x == True)
        - For database operations, verify both the result and the interaction with the mock

    - Requirement 13: |- 
        Favor readability with clear test structure:
        - Use Arrange-Act-Assert (AAA) pattern
        - Add brief comments for Given-When-Then semantics when helpful
        - Keep test bodies concise (typically 5-15 lines)
        - Extract complex setup into fixtures
        - Group related database mocking setup into reusable fixtures

    - Requirement 14: |-
        Documentation line length constraints:
        - Do not exceed {{{ max_line_length }}} characters in documentation lines
        - If a docstring line exceeds {{{ min_line_length }}} but is shorter than max, expand it naturally (without filler) to approach {{{ max_line_length }}} for improved consistency

    - Requirement 15: |-
        Include module-level docstrings:
        - Test module must have a clear module-level docstring
        - Explain what is being tested and the overall test strategy
        - Mention database mocking strategy if applicable

    - Requirement 16: |-
        Docstring format requirements:
        - Use concise first-line summaries followed by extended detail if needed
        - Do not fabricate behavior not inferable from the file
        - If ambiguity exists, note it with a TODO or NOTE comment
        - If the target file exposes constants/enums, test that dependent logic uses them correctly

    - Requirement 17: |-
        Style and quality standards:
        - Prefer explicit over implicit
        - Avoid excessive mocking—only where side effects or isolation require it
        - Keep test bodies minimal but expressive
        - Add brief inline comments only where clarity is improved
        - Use type hints in tests if they clarify intent (optional but recommended)
        - Follow PEP 8 style guidelines

    - Requirement 18: |-
        Be CONCISE and CONCRETE:
        - Each test should verify ONE specific behavior or scenario
        - Avoid redundant tests that verify the same logic
        - Focus on tests that would catch real bugs
        - Prioritize tests for complex logic, error handling, and edge cases
        - Avoid trivial tests (e.g., testing that a getter returns a value)

    - Requirement 19: |-
        TEST FOLDER STRUCTURE - CRITICAL REQUIREMENTS:
        - **Create a dedicated `tests` folder** at the project root level (same level as src, app, or library root)
        - **Mirror the source directory structure** within the tests folder
        - **Prefix the source root directory** with `tests_` inside the tests folder
        - **Add `__init__.py` files** to all test directories to ensure proper Python package structure
        - **Add "test_" prefix** to the module filename only
        - Examples of correct transformations:
            * `src/utils/database.py` → `tests/tests_src/utils/test_database.py`
            * `app/services/user_service.py` → `tests/tests_app/services/test_user_service.py`
            * `mylibrary/core/handlers/auth.py` → `tests/tests_mylibrary/core/handlers/test_auth.py`
            * `database_manager.py` (root level) → `tests/test_database_manager.py`
        - **Required `__init__.py` files** for the above examples:
            * `tests/__init__.py`
            * `tests/tests_src/__init__.py`
            * `tests/tests_src/utils/__init__.py`
            * `tests/tests_app/__init__.py`
            * `tests/tests_app/services/__init__.py`
            * `tests/tests_mylibrary/__init__.py`
            * `tests/tests_mylibrary/core/__init__.py`
            * `tests/tests_mylibrary/core/handlers/__init__.py`

    - Constraint 1: You may reference up to 10 additional files besides the target file for context. Ensure tests are self-contained and clear.

    - Constraint 2: Strictly adhere to pytest framework logic and guidelines when implementing test cases. DO NOT COMBINE TESTING FRAMEWORKS. ONLY USE pytest.

    - Constraint 3: Strictly adhere to Google docstring conventions and format when documenting test cases and the test module.

    - Constraint 4: Implement ONLY test cases for the target file, not any referenced files.

    - Constraint 5: The maximum length of lines within documentation is {{{ max_line_length }}} characters.

    - Constraint 6: If a documentation line surpasses {{{ min_line_length }}} characters, extend it naturally to approach {{{ max_line_length }}} characters to ensure better formatting and readability. Do not add filler text.

    - Constraint 7: DO NOT PROVIDE DOCUMENTATION FOR {{{ target_file }}} as it is not necessary. ONLY DOCUMENT the output test file.

    - Constraint 8: Limit the total number of test functions to {{{ maximum_tests_limit }}}. Focus on the most important and valuable tests.

    - Constraint 9: "**NEVER allow tests to make actual database connections**. All database interactions must be mocked."

    - Constraint 10: |-
        **The test file MUST be created in a dedicated `tests` folder** with the following structure:
        - Place tests folder at project root level
        - Mirror source directory structure inside tests folder
        - Prefix source root directory with `tests_` (e.g., `src` → `tests_src`)
        - Add `__init__.py` to all test directories
        - Add "test_" prefix to filename only
~~~

### OUTPUT_FORMAT:
Provide the following in your response:

1. **Brief Summary** (at the very top):
    - Concise description of what the target file does
    - Overview of what the test file covers
    - Key testing strategies employed
    - Database mocking approach (if applicable)
    - **Test file path** showing the preserved directory structure with "test_" prefix

2. **Test Module** (complete, ready-to-use):
    - **File path**: Follow the tests folder structure rules
      **Example**: If target is src/utils/database.py, test file is tests/tests_src/utils/test_database.py
    - Include all necessary imports (pytest, unittest.mock, database libraries)
    - Module-level docstring (basic structure only - will be refined in step 4)
    - All test functions with basic docstrings (will be refined in step 4)
    - Fixtures for database mocking (connections, cursors, sessions, etc.)
    - Working, executable pytest code
    - Proper database connection mocking with realistic behavior

3. **Required __init__.py Files:**
    - List all __init__.py files that need to be created for the test structure
    - Example for src/utils/database.py:
      * tests/__init__.py
      * tests/tests_src/__init__.py
      * tests/tests_src/utils/__init__.py

4. **Test Coverage Notes**:
    - Brief list of what scenarios are covered
    - Database-specific scenarios tested (connections, queries, failures)
    - Any assumptions made
    - Any limitations or areas not covered (if applicable)

5. **Documentation Refinement Instruction**:
    After generating the test module above, apply the /document-python-projects custom command to the generated test file with the following parameters:
    
    ```
    /document-python-projects target_file_name::"<full_path_to_test_file>" docstring_style::"Google" examples_in_docstrings::false max_line_length::{{{ max_line_length }}} min_line_length::{{{ min_line_length }}}
    ```
    
    Where `<full_path_to_test_file>` is the complete path including the directory structure and "test_" prefix.
    
    Example: If target file is `src/utils/database.py`, use:
    ```
    /document-python-projects target_file_name::"src/utils/test_database.py" docstring_style::"Google" examples_in_docstrings::false max_line_length::120 min_line_length::80
    ```

    This will ensure:
    - Professional, standards-compliant documentation following Google docstring style
    - Proper line-length constraints ({{{ max_line_length }}} max, {{{ min_line_length }}} min)
    - Comprehensive module-level and function-level docstrings
    - Consistent terminology and formatting across all test functions
    - Clear descriptions of test purpose, parameters (fixtures), and expected outcomes

    **IMPORTANT**: The /document-python-projects command should be applied AFTER the test cases have been:
     - Fully defined with correct pytest syntax
     - Validated for logical correctness and completeness
     - Refined to ensure they follow best practices and cover all required scenarios

    Only once the test logic is finalized should the documentation enhancement be performed.

### EXAMPLES:
#### Example 1: Basic parametrized test
pytest unit test examples demonstrating best practices:
```python
"""Test suite for arithmetic operations in calculator module."""
import pytest
from calculator import add, divide

@pytest.mark.parametrize(
    "a,b,expected",
    [
        (1, 2, 3),           # positive numbers
        (-1, 2, 1),          # negative and positive
        (0, 0, 0),           # zeros
        (100, -100, 0),      # large numbers
    ],
)
def test_add_various_inputs(a, b, expected):
    """Test addition with various numeric inputs including positive, negative, and zero values."""
    assert add(a, b) == expected

def test_add_type_error_with_string():
    """Test that add raises TypeError when given a string argument instead of a number."""
    with pytest.raises(TypeError, match="unsupported operand type"):
        add(1, "x")

def test_divide_by_zero_raises_value_error():
    """Test that divide raises ValueError when attempting to divide by zero."""
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        divide(10, 0)
```

#### Example 2: Using fixtures for setup
```python
"""Test suite for user management functionality."""

import pytest
from user_manager import UserManager, User

@pytest.fixture
def user_manager():
    """Provide a fresh UserManager instance for each test."""
    return UserManager()

@pytest.fixture
def sample_user():
    """Provide a sample user object with standard test data."""
    return User(name="John Doe", email="john@example.com", age=30)

def test_add_user_success(user_manager, sample_user):
    """Test that a valid user can be successfully added to the user manager."""
    # Arrange - fixtures provide setup
    # Act
    result = user_manager.add_user(sample_user)
    # Assert
    assert result is True
    assert len(user_manager.users) == 1
    assert user_manager.users[0].name == "John Doe"

def test_add_duplicate_user_raises_error(user_manager, sample_user):
    """Test that adding a duplicate user raises ValueError with appropriate message."""
    user_manager.add_user(sample_user)
    with pytest.raises(ValueError, match="User already exists"):
        user_manager.add_user(sample_user)
```

#### Example 3: Mocking external dependencies
```python
"""Test suite for file processor with mocked filesystem operations."""

import pytest
from unittest.mock import mock_open, patch
from file_processor import FileProcessor

def test_read_file_success():
    """Test that read_file correctly reads and returns file content when file exists."""
    mock_content = "test content\nline 2"
    with patch("builtins.open", mock_open(read_data=mock_content)):
        processor = FileProcessor()
        result = processor.read_file("test.txt")
        assert result == mock_content

def test_read_file_not_found_raises_error():
    """Test that read_file raises FileNotFoundError when attempting to read non-existent file."""
    with patch("builtins.open", side_effect=FileNotFoundError):
        processor = FileProcessor()
        with pytest.raises(FileNotFoundError):
            processor.read_file("nonexistent.txt")
```
#### Example 4: Mocking SQLAlchemy database connections
```python
"""Test suite for user repository with mocked SQLAlchemy database operations."""

import pytest
from unittest.mock import MagicMock, patch, call
from sqlalchemy.exc import OperationalError
from user_repository import UserRepository
from models import User

@pytest.fixture
def mock_session():
    """Provide a mocked SQLAlchemy session for database operations testing."""
    session = MagicMock()
    session.query.return_value = session
    session.filter.return_value = session
    session.first.return_value = None
    return session

@pytest.fixture
def mock_engine():
    """Provide a mocked SQLAlchemy engine for connection testing."""
    engine = MagicMock()
    return engine

@pytest.fixture
def user_repository(mock_session):
    """Provide a UserRepository instance with mocked database session."""
    return UserRepository(session=mock_session)

def test_get_user_by_id_success(user_repository, mock_session):
    """Test that get_user_by_id returns correct user when user exists in database."""
    # Arrange
    expected_user = User(id=1, name="John Doe", email="john@example.com")
    mock_session.query.return_value.filter.return_value.first.return_value = expected_user
    
    # Act
    result = user_repository.get_user_by_id(1)
    
    # Assert
    assert result == expected_user
    mock_session.query.assert_called_once_with(User)
    mock_session.query.return_value.filter.assert_called_once()

def test_get_user_by_id_not_found(user_repository, mock_session):
    """Test that get_user_by_id returns None when user does not exist in database."""
    # Arrange
    mock_session.query.return_value.filter.return_value.first.return_value = None
    
    # Act
    result = user_repository.get_user_by_id(999)
    
    # Assert
    assert result is None

def test_create_user_success(user_repository, mock_session):
    """Test that create_user successfully adds new user and commits transaction to database."""
    # Arrange
    user_data = {"name": "Jane Doe", "email": "jane@example.com"}
    
    # Act
    result = user_repository.create_user(**user_data)
    
    # Assert
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    assert result.name == user_data["name"]
    assert result.email == user_data["email"]

def test_create_user_rollback_on_error(user_repository, mock_session):
    """Test that create_user rolls back transaction when database commit fails."""
    # Arrange
    mock_session.commit.side_effect = OperationalError("Connection lost", None, None)
    user_data = {"name": "Jane Doe", "email": "jane@example.com"}
    
    # Act & Assert
    with pytest.raises(OperationalError):
        user_repository.create_user(**user_data)
    
    mock_session.rollback.assert_called_once()

def test_connection_failure_raises_operational_error(mock_engine):
    """Test that repository raises OperationalError when database connection fails."""
    # Arrange
    mock_engine.connect.side_effect = OperationalError("Cannot connect", None, None)
    
    # Act & Assert
    with pytest.raises(OperationalError, match="Cannot connect"):
        UserRepository.from_engine(mock_engine)
```

#### Example 5: Mocking psycopg2 database connections
```python
"""Test suite for PostgreSQL data access layer with mocked psycopg2 connections."""

import pytest
from unittest.mock import MagicMock, patch, call
import psycopg2
from data_access import DatabaseConnection, fetch_users, insert_user

@pytest.fixture
def mock_cursor():
    """Provide a mocked psycopg2 cursor for query execution testing."""
    cursor = MagicMock()
    cursor.fetchall.return_value = []
    cursor.fetchone.return_value = None
    cursor.rowcount = 0
    return cursor

@pytest.fixture
def mock_connection(mock_cursor):
    """Provide a mocked psycopg2 connection with cursor for database operations testing."""
    connection = MagicMock()
    connection.cursor.return_value = mock_cursor
    connection.__enter__.return_value = connection
    connection.__exit__.return_value = False
    return connection

@patch('psycopg2.connect')
def test_fetch_users_returns_all_users(mock_connect, mock_connection, mock_cursor):
    """Test that fetch_users returns all users from database when query executes successfully."""
    # Arrange
    mock_connect.return_value = mock_connection
    expected_users = [
        (1, "John Doe", "john@example.com"),
        (2, "Jane Smith", "jane@example.com")
    ]
    mock_cursor.fetchall.return_value = expected_users
    
    # Act
    result = fetch_users()
    
    # Assert
    assert result == expected_users
    mock_cursor.execute.assert_called_once_with("SELECT id, name, email FROM users")
    mock_connection.close.assert_called_once()

@patch('psycopg2.connect')
def test_fetch_users_empty_result(mock_connect, mock_connection, mock_cursor):
    """Test that fetch_users returns empty list when no users exist in database."""
    # Arrange
    mock_connect.return_value = mock_connection
    mock_cursor.fetchall.return_value = []
    
    # Act
    result = fetch_users()
    
    # Assert
    assert result == []
    assert len(result) == 0

@patch('psycopg2.connect')
def test_insert_user_commits_transaction(mock_connect, mock_connection, mock_cursor):
    """Test that insert_user executes parameterized query and commits transaction successfully."""
    # Arrange
    mock_connect.return_value = mock_connection
    mock_cursor.rowcount = 1
    user_data = ("John Doe", "john@example.com")
    
    # Act
    result = insert_user(*user_data)
    
    # Assert
    assert result is True
    mock_cursor.execute.assert_called_once_with(
        "INSERT INTO users (name, email) VALUES (%s, %s)",
        user_data
    )
    mock_connection.commit.assert_called_once()
    mock_connection.close.assert_called_once()

@patch('psycopg2.connect')
def test_insert_user_rollback_on_error(mock_connect, mock_connection, mock_cursor):
    """Test that insert_user rolls back transaction when database error occurs during commit."""
    # Arrange
    mock_connect.return_value = mock_connection
    mock_connection.commit.side_effect = psycopg2.DatabaseError("Constraint violation")
    user_data = ("John Doe", "john@example.com")
    
    # Act & Assert
    with pytest.raises(psycopg2.DatabaseError):
        insert_user(*user_data)
    
    mock_connection.rollback.assert_called_once()
    mock_connection.close.assert_called_once()

@patch('psycopg2.connect')
def test_connection_timeout_raises_operational_error(mock_connect):
    """Test that connection attempt raises OperationalError when database server times out."""
    # Arrange
    mock_connect.side_effect = psycopg2.OperationalError("Connection timeout")
    
    # Act & Assert
    with pytest.raises(psycopg2.OperationalError, match="Connection timeout"):
        DatabaseConnection.connect()

@patch('psycopg2.connect')
def test_connection_context_manager_closes_properly(mock_connect, mock_connection):
    """Test that database connection context manager properly closes connection on exit."""
    # Arrange
    mock_connect.return_value = mock_connection
    
    # Act
    with DatabaseConnection.get_connection() as conn:
        pass
    
    # Assert
    mock_connection.__exit__.assert_called_once()
    mock_connection.close.assert_called_once()
```

#### Example 6: Mocking MongoDB connections
```python
"""Test suite for MongoDB data access layer with mocked pymongo connections."""

import pytest
from unittest.mock import MagicMock, patch
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from mongo_repository import MongoUserRepository

@pytest.fixture
def mock_collection():
    """Provide a mocked MongoDB collection for document operations testing."""
    collection = MagicMock()
    collection.find.return_value = []
    collection.find_one.return_value = None
    collection.insert_one.return_value = MagicMock(inserted_id="507f1f77bcf86cd799439011")
    return collection

@pytest.fixture
def mock_database(mock_collection):
    """Provide a mocked MongoDB database with collection access for testing."""
    database = MagicMock()
    database.users = mock_collection
    return database

@pytest.fixture
def mock_client(mock_database):
    """Provide a mocked MongoDB client for connection and database operations testing."""
    client = MagicMock()
    client.__getitem__.return_value = mock_database
    client.server_info.return_value = {"version": "4.4.0"}
    return client

@pytest.fixture
def user_repository(mock_client):
    """Provide a MongoUserRepository instance with mocked MongoDB client."""
    return MongoUserRepository(client=mock_client, db_name="test_db")

def test_find_user_by_email_success(user_repository, mock_collection):
    """Test that find_user_by_email returns correct user document when email exists."""
    # Arrange
    expected_user = {"_id": "507f1f77bcf86cd799439011", "name": "John", "email": "john@example.com"}
    mock_collection.find_one.return_value = expected_user
    
    # Act
    result = user_repository.find_user_by_email("john@example.com")
    
    # Assert
    assert result == expected_user
    mock_collection.find_one.assert_called_once_with({"email": "john@example.com"})

def test_find_all_users_returns_list(user_repository, mock_collection):
    """Test that find_all_users returns list of all user documents from collection."""
    # Arrange
    expected_users = [
        {"_id": "1", "name": "John", "email": "john@example.com"},
        {"_id": "2", "name": "Jane", "email": "jane@example.com"}
    ]
    mock_collection.find.return_value = expected_users
    
    # Act
    result = user_repository.find_all_users()
    
    # Assert
    assert result == expected_users
    mock_collection.find.assert_called_once_with({})

def test_insert_user_returns_inserted_id(user_repository, mock_collection):
    """Test that insert_user successfully inserts document and returns generated object ID."""
    # Arrange
    user_doc = {"name": "John Doe", "email": "john@example.com"}
    expected_id = "507f1f77bcf86cd799439011"
    mock_collection.insert_one.return_value.inserted_id = expected_id
    
    # Act
    result = user_repository.insert_user(user_doc)
    
    # Assert
    assert result == expected_id
    mock_collection.insert_one.assert_called_once_with(user_doc)

@patch('pymongo.MongoClient')
def test_connection_failure_raises_error(mock_mongo_client):
    """Test that repository raises ConnectionFailure when unable to connect to MongoDB server."""
    # Arrange
    mock_mongo_client.side_effect = ConnectionFailure("Cannot connect to MongoDB")
    
    # Act & Assert
    with pytest.raises(ConnectionFailure, match="Cannot connect to MongoDB"):
        MongoUserRepository.from_uri("mongodb://localhost:27017")

@patch('pymongo.MongoClient')
def test_server_selection_timeout(mock_mongo_client):
    """Test that repository raises ServerSelectionTimeoutError when MongoDB server is unreachable."""
    # Arrange
    mock_client = MagicMock()
    mock_client.server_info.side_effect = ServerSelectionTimeoutError("No servers found")
    mock_mongo_client.return_value = mock_client
    
    # Act & Assert
    with pytest.raises(ServerSelectionTimeoutError):
        repo = MongoUserRepository.from_uri("mongodb://localhost:27017")
        repo.ping()
```

#### Example 7: Mocking async database connections (asyncpg)
```python
"""Test suite for async PostgreSQL operations with mocked asyncpg connections."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import asyncpg
from async_db import AsyncUserRepository

@pytest.fixture
def mock_connection():
    """Provide a mocked asyncpg connection for async database operations testing."""
    conn = AsyncMock()
    conn.fetch.return_value = []
    conn.fetchrow.return_value = None
    conn.execute.return_value = "INSERT 0 1"
    conn.__aenter__.return_value = conn
    conn.__aexit__.return_value = None
    return conn

@pytest.fixture
def mock_pool(mock_connection):
    """Provide a mocked asyncpg connection pool for async connection management testing."""
    pool = AsyncMock()
    pool.acquire.return_value.__aenter__.return_value = mock_connection
    pool.acquire.return_value.__aexit__.return_value = None
    return pool

@pytest.fixture
async def user_repository(mock_pool):
    """Provide an AsyncUserRepository instance with mocked connection pool."""
    repo = AsyncUserRepository(pool=mock_pool)
    return repo

@pytest.mark.asyncio
async def test_fetch_user_by_id_success(user_repository, mock_connection):
    """Test that fetch_user_by_id returns correct user when async query executes successfully."""
    # Arrange
    expected_user = {"id": 1, "name": "John Doe", "email": "john@example.com"}
    mock_connection.fetchrow.return_value = expected_user
    
    # Act
    result = await user_repository.fetch_user_by_id(1)
    
    # Assert
    assert result == expected_user
    mock_connection.fetchrow.assert_called_once_with(
        "SELECT id, name, email FROM users WHERE id = $1", 1
    )

@pytest.mark.asyncio
async def test_fetch_all_users_returns_list(user_repository, mock_connection):
    """Test that fetch_all_users returns list of all users from async database query."""
    # Arrange
    expected_users = [
        {"id": 1, "name": "John", "email": "john@example.com"},
        {"id": 2, "name": "Jane", "email": "jane@example.com"}
    ]
    mock_connection.fetch.return_value = expected_users
    
    # Act
    result = await user_repository.fetch_all_users()
    
    # Assert
    assert result == expected_users
    assert len(result) == 2

@pytest.mark.asyncio
async def test_insert_user_executes_query(user_repository, mock_connection):
    """Test that insert_user executes parameterized async insert query successfully."""
    # Arrange
    user_data = {"name": "John Doe", "email": "john@example.com"}
    mock_connection.execute.return_value = "INSERT 0 1"
    
    # Act
    result = await user_repository.insert_user(**user_data)
    
    # Assert
    assert result is True
    mock_connection.execute.assert_called_once()

@pytest.mark.asyncio
async def test_connection_pool_exhaustion_raises_error(mock_pool):
    """Test that repository raises error when async connection pool is exhausted."""
    # Arrange
    mock_pool.acquire.side_effect = asyncpg.TooManyConnectionsError("Pool exhausted")
    repo = AsyncUserRepository(pool=mock_pool)
    
    # Act & Assert
    with pytest.raises(asyncpg.TooManyConnectionsError, match="Pool exhausted"):
        await repo.fetch_all_users()

@pytest.mark.asyncio
@patch('asyncpg.create_pool')
async def test_create_pool_connection_failure(mock_create_pool):
    """Test that create_pool raises error when unable to establish async database connection."""
    # Arrange
    mock_create_pool.side_effect = asyncpg.PostgresConnectionError("Connection refused")
    
    # Act & Assert
    with pytest.raises(asyncpg.PostgresConnectionError, match="Connection refused"):
        await AsyncUserRepository.create_pool("postgresql://localhost/testdb")
```

## QUALITY_CHECKLIST:
Before finalizing output, verify:
- [ ] Module-level docstring is present and informative
- [ ] All test functions have clear, descriptive names
- [ ] Each test has a concise docstring explaining its purpose
- [ ] Tests use pytest idiomatically (fixtures, parametrize, raises)
- [ ] Tests are isolated and deterministic (no external dependencies without mocking)
- [ ] **ALL database connections are properly mocked**
- [ ] **Database mock fixtures are realistic and reusable**
- [ ] **Connection failure scenarios are tested**
- [ ] **Transaction handling (commit/rollback) is verified**
- [ ] **Mock interactions are verified using assert_called_* methods**
- [ ] **Connection cleanup (close, __exit__) is verified**
- [ ] Assertions are specific and meaningful
- [ ] Test count does not exceed {{{ maximum_tests_limit }}}
- [ ] Tests cover nominal cases, edge cases, and error conditions
- [ ] Database-specific edge cases covered (empty results, NULL values, connection loss)
- [ ] No redundant or trivial tests
- [ ] Code is executable and follows PEP 8
- [ ] Mocks are used appropriately for external dependencies
- [ ] Tests follow Arrange-Act-Assert pattern
- [ ] Async database operations use @pytest.mark.asyncio and AsyncMock
- [ ] Test logic is complete and validated before documentation refinement
- [ ] /document-python-projects command parameters are correctly specified for final documentation pass
- [ ] **Test file path correctly mirrors target file path with "test_" prefix on filename only**
- [ ] **Directory structure is preserved exactly as in target file**
- [ ] **Test file is co-located with target file in the same directory under tests folder.**

## MODULE PATH STRUCTURE RULES:

### ✅ CORRECT Path Transformations:
- `src/utils/database.py` → `tests/tests_utils/test_database.py`
- `app/services/user_service.py` → `tests/tests_app/services/test_user_service.py`
- `mylibrary/core/handlers/auth.py` → `tests/tests_mylibrary/core/handlers/test_auth.py`
- `backend/api/v1/endpoints/users.py` → `tests/tests_backend/api/v1/endpoints/test_users.py`
- `database_manager.py` → `tests/test_database_manager.py`

### ❌ INCORRECT Path Transformations:
- ~~`src/utils/database.py` → `tests/test_database.py`~~ (Don't create separate tests directory)
- ~~`app/services/user_service.py` → `test_app/test_services/test_user_service.py`~~ (Don't modify directory names)
- ~~`mylibrary/core/handlers/auth.py` → `mylibrary/test_core/handlers/test_auth.py`~~ (Don't add "test_" to directories)

### Key Principles:
1. **Preserve** the exact directory structure
2. **Add** "test_" prefix to the filename only
3. **Co-locate** tests with the code they test
4. **Maintain** the same module hierarchy

## USAGE:

```
/unit-tests-pytest target_file::"/path/to/file.py" dependencies::"file1.py, file2.py" max_line_length::120 maximum_tests_limit::10 min_line_length::80
```

### Example Usage:

Input:
```
/unit-tests-pytest target_file::"src/utils/user_repository.py" maximum_tests_limit::12
```
Output: 
``tests/utils/test_user_repository.py``

Input:
```
/unit-tests-pytest target_file::"app/services/database_manager.py" dependencies::"models.py, config.py" maximum_tests_limit::15 max_line_length::100
```
Output: 
``tests/app/services/test_database_manager.py``

Input:
```
/unit-tests-pytest target_file::"backend/api/handlers/async_db_handler.py" dependencies::"schemas.py" maximum_tests_limit::10
```
Output: 
``tests/backend/api/handlers/test_async_db_handler.py``

Input:
```
/unit-tests-pytest target_file::"calculator.py" maximum_tests_limit::8
```
Output: 
``tests/test_calculator.py``
