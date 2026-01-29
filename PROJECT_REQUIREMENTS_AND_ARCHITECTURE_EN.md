# Capstone Project: Test Data Generation Utility
## Requirements, Architecture and Implementation Plan

---

## 1. PROJECT DESCRIPTION

**Utility Name:** DataForge

**Purpose:** Console utility for generating test JSON data based on user-defined data schema. Used for testing data pipelines, data transformation validation.

**Output Format:** JSON (JSON Lines - https://jsonlines.org/)

---

## 2. FUNCTIONAL REQUIREMENTS (FR)

### FR-1: Data Schema Parsing
- **FR-1.1:** Utility must accept data schema in JSON format
- **FR-1.2:** Schema can be provided in two ways:
  - As a string in command line
  - As a path to JSON file with schema
- **FR-1.3:** Schema must support the following data types:
  - `timestamp` - current Unix timestamp
  - `str` - string values
  - `int` - integer values
- **FR-1.4:** Each type supports the following generation strategies:
  - `rand` - random generation
  - `[value1, value2, ...]` - random choice from list
  - `rand(from, to)` - random number in range (int only)
  - `specific_value` - static value
  - `empty_value` - empty value (None for int, "" for str)

### FR-2: Data Generation
- **FR-2.1:** Generate random UUID for `str:rand` type using `uuid.uuid4()`
- **FR-2.2:** Generate random integers for `int:rand` in range [0, 10000]
- **FR-2.3:** Generate random values from list using `random.choice()`
- **FR-2.4:** Generate random numbers in specified range for `int:rand(from, to)`
- **FR-2.5:** Generate current Unix timestamp for `timestamp:` type
- **FR-2.6:** Use static values where specified
- **FR-2.7:** Each data line must contain all keys from schema

### FR-3: File Operations
- **FR-3.1:** Generate specified number of JSON files
- **FR-3.2:** Each file must contain specified number of data lines
- **FR-3.3:** Support file name prefixes:
  - `count` - sequential number (file_name_1.json, file_name_2.json, ...)
  - `random` - random number
  - `uuid` - unique UUID
- **FR-3.4:** Save files to specified path (relative or absolute)
- **FR-3.5:** Output format - JSON Lines (each line is separate JSON object)
- **FR-3.6:** If `files_count=0`, output data to console (stdout)

### FR-4: File Management
- **FR-4.1:** `clear_path` option to delete existing files with matching name before generation
- **FR-4.2:** Check existence and validity of save path

### FR-5: Multiprocessing
- **FR-5.1:** Support parallel file generation using multiprocessing
- **FR-5.2:** Evenly distribute file count between processes
- **FR-5.3:** Automatically limit number of processes to `os.cpu_count()`

### FR-6: Configuration
- **FR-6.1:** All parameters must have default values
- **FR-6.2:** Default values stored in `default.ini` file
- **FR-6.3:** Values read using `configparser`
- **FR-6.4:** Parameter names in `default.ini` identical to command line parameters

### FR-7: Command Line Interface
- **FR-7.1:** Use `argparse` for argument parsing
- **FR-7.2:** All parameters can be passed via command line
- **FR-7.3:** `--help` command must show:
  - Utility name
  - Description of each parameter
  - Default values
  - Usage examples

### FR-8: Logging
- **FR-8.1:** All important actions logged to console
- **FR-8.2:** Use `logging` module
- **FR-8.3:** Logging levels:
  - `INFO` - start/completion of generation, progress
  - `WARNING` - warnings (e.g., ignoring values for timestamp)
  - `ERROR` - errors before exit
- **FR-8.4:** Optional: duplicate logs to file

---

## 3. NON-FUNCTIONAL REQUIREMENTS (NFR)

### NFR-1: Error Handling
- **NFR-1.1:** All errors must be handled gracefully without traceback
- **NFR-1.2:** Use `sys.exit(1)` instead of `raise` for critical errors
- **NFR-1.3:** Each error must be logged with `logging.error()`
- **NFR-1.4:** Validate all input parameters

### NFR-2: Code Quality
- **NFR-2.1:** Code must be divided into functions/classes/logical blocks
- **NFR-2.2:** Avoid monolithic code
- **NFR-2.3:** Follow clean code principles
- **NFR-2.4:** Clear variable and function names

### NFR-3: Testing
- **NFR-3.1:** Use `pytest` for unit tests
- **NFR-3.2:** Coverage of all main functionalities
- **NFR-3.3:** Use parameterized tests
- **NFR-3.4:** Use fixtures for file-based tests

### NFR-4: Performance
- **NFR-4.1:** Efficient generation of large data volumes
- **NFR-4.2:** Parallel processing when using multiprocessing
- **NFR-4.3:** Optimal memory usage

### NFR-5: Compatibility
- **NFR-5.1:** Python 3.6+
- **NFR-5.2:** Use only Python standard library
- **NFR-5.3:** Cross-platform (Windows, Linux, macOS)

---

## 4. TECHNICAL REQUIREMENTS

### Required Python Modules:
1. `argparse` - command line argument parsing
2. `json` - JSON format handling
3. `os` / `shutil` - file system operations
4. `time` - timestamp generation
5. `random` - random data generation
6. `configparser` - configuration reading
7. `logging` - logging
8. `uuid` - UUID generation
9. `pytest` - testing
10. `multiprocessing` - parallel processing
11. `sys` - system operations and exit

### Utility Input Parameters:

| Parameter | Type | Description | Validation |
|----------|-----|----------|-----------|
| `path_to_save_files` | str (positional) | Path to save files | Check existence, must be directory |
| `--files_count` | int | Number of files to generate | >= 0 (0 = output to console) |
| `--file_name` | str | Base file name | Valid file name |
| `--file_prefix` | choice | File name prefix | ['count', 'random', 'uuid'] |
| `--data_schema` | str | JSON schema or path to file | Valid JSON |
| `--data_lines` | int | Number of lines in each file | > 0 |
| `--clear_path` | flag | Clear existing files | store_true |
| `--multiprocessing` | int | Number of processes | >= 1, <= os.cpu_count() |

---

## 5. SYSTEM ARCHITECTURE

### 5.1. Overall Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    CLI Interface                         │
│                   (argparse)                             │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│               Configuration Manager                      │
│            (ConfigParser + Defaults)                     │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                 Validator Module                         │
│          (Validate all input parameters)                 │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Schema Parser Module                        │
│         (Parse and validate data schema)                 │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│            Data Generator Module                         │
│     (Generate data based on parsed schema)               │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│           File Manager Module                            │
│  (Handle file creation, naming, and cleanup)             │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│         Multiprocessing Coordinator                      │
│      (Distribute work across processes)                  │
└─────────────────────────────────────────────────────────┘
```

### 5.2. Module Structure

#### Module 1: CLI Interface (`cli.py`)
**Responsibilities:**
- Define command line interface
- Parse arguments using argparse
- Display help messages
- Program entry point

**Functions:**
- `create_parser()` - create ArgumentParser
- `parse_arguments()` - parse arguments
- `main()` - main function

#### Module 2: Configuration Manager (`config.py`)
**Responsibilities:**
- Read default.ini
- Provide default values
- Merge values from config and CLI

**Functions:**
- `load_default_config()` - load default.ini
- `get_config_value()` - get parameter value
- `create_default_config()` - create default.ini if missing

#### Module 3: Validator (`validator.py`)
**Responsibilities:**
- Validate all input parameters
- Check paths, value ranges
- Validate data schema

**Functions:**
- `validate_path()` - check path_to_save_files
- `validate_files_count()` - check files_count
- `validate_multiprocessing()` - check and correct multiprocessing
- `validate_schema()` - basic schema check
- `validate_all_parameters()` - validate all parameters

#### Module 4: Schema Parser (`schema_parser.py`)
**Responsibilities:**
- Parse JSON schema
- Parse type:value notation
- Prepare generators for each field

**Classes/Functions:**
- `SchemaParser` class
  - `parse()` - main parsing method
  - `parse_field()` - parse individual field
  - `parse_type_and_value()` - parse type:value
  - `validate_field_type()` - check type
  - `get_field_generators()` - get generators

#### Module 5: Data Generator (`data_generator.py`)
**Responsibilities:**
- Generate data according to schema
- Implement different generation strategies
- Generate single line/multiple lines

**Classes/Functions:**
- `DataGenerator` class
  - `generate_line()` - generate single line
  - `generate_lines()` - generate multiple lines
- Generation functions for each type:
  - `generate_timestamp()` - current timestamp
  - `generate_str_rand()` - random UUID
  - `generate_int_rand()` - random number
  - `generate_from_list()` - choose from list
  - `generate_int_range()` - number in range
  - `generate_static_value()` - static value

#### Module 6: File Manager (`file_manager.py`)
**Responsibilities:**
- Create and name files
- Write data to files (JSON Lines format)
- Clear directory
- Console output

**Functions:**
- `generate_file_name()` - generate file name with prefix
- `write_jsonlines()` - write data in JSON Lines format
- `clear_directory()` - delete files with matching name
- `write_to_console()` - output data to stdout
- `create_single_file()` - create single file

#### Module 7: Multiprocessing Coordinator (`multiprocessor.py`)
**Responsibilities:**
- Coordinate parallel generation
- Distribute work between processes
- Collect results

**Functions:**
- `distribute_work()` - distribute file count
- `generate_files_parallel()` - parallel generation
- `worker_function()` - worker process function

#### Module 8: Logger Setup (`logger.py`)
**Responsibilities:**
- Configure logging
- Format messages

**Functions:**
- `setup_logger()` - configure logger
- `log_start()` - log start of work
- `log_completion()` - log completion

#### Module 9: Utils (`utils.py`)
**Responsibilities:**
- Helper functions
- Common utilities

**Functions:**
- `is_json_file()` - check if string is path to file
- `load_json_from_file()` - load JSON from file
- `safe_exit()` - safe exit with logging

---

## 6. PROJECT STRUCTURE

```
python_capstone_project_ndragancea/
│
├── dataforge/                      # Main utility package
│   ├── __init__.py
│   ├── __main__.py                 # Entry point (python -m dataforge)
│   ├── cli.py                      # CLI interface
│   ├── config.py                   # Configuration handling
│   ├── validator.py                # Parameter validation
│   ├── schema_parser.py            # Data schema parsing
│   ├── data_generator.py           # Data generation
│   ├── file_manager.py             # File management
│   ├── multiprocessor.py           # Multiprocessing
│   ├── logger.py                   # Logging setup
│   └── utils.py                    # Helper functions
│
├── tests/                          # Tests
│   ├── __init__.py
│   ├── conftest.py                 # Fixtures for pytest
│   ├── test_schema_parser.py      # Schema parser tests
│   ├── test_data_generator.py     # Data generator tests
│   ├── test_validator.py          # Validator tests
│   ├── test_file_manager.py       # File manager tests
│   ├── test_multiprocessing.py    # Multiprocessing tests
│   ├── test_integration.py        # Integration tests
│   └── fixtures/                  # Test data
│       ├── test_schema_1.json
│       ├── test_schema_2.json
│       └── ...
│
├── default.ini                     # Default configuration
├── requirements.txt                # Dependencies (for pytest)
├── README.md                       # Project documentation
├── setup.py                        # Setup script for installation
└── .gitignore                      # Git ignore file
```

---

## 7. DETAILED IMPLEMENTATION PLAN

### STAGE 1: Project Setup (1-2 hours)
**Tasks:**
1. Create project structure (folders and files)
2. Create `default.ini` with default parameters
3. Create `requirements.txt`
4. Create basic `README.md`
5. Setup `.gitignore`
6. Initialize Git repository

**Result:** Ready project structure

---

### STAGE 2: Basic Modules Implementation (3-4 hours)

#### 2.1. Logger Setup (`logger.py`)
```python
# Functions:
- setup_logger() - basic setup
- Message formatting
```

#### 2.2. Configuration Manager (`config.py`)
```python
# Functions:
- load_default_config() - read default.ini
- create_default_config() - create default.ini if missing
```

#### 2.3. Utils (`utils.py`)
```python
# Functions:
- is_json_file() - determine if string or file path
- load_json_from_file() - load JSON
- safe_exit() - correct exit with error
```

**Testing:**
- Write basic tests for each module

**Result:** Working helper modules

---

### STAGE 3: CLI Interface (2-3 hours)

#### 3.1. Implementation of `cli.py`
```python
# Create ArgumentParser with:
- Positional argument path_to_save_files
- Optional arguments (--files_count, --file_name, etc.)
- Setup help messages
- Define choices for file_prefix
- Setup store_true for clear_path
```

#### 3.2. Create entry point
```python
# __main__.py
# main() function
```

**Testing:**
- Check argument parsing
- Check help message

**Result:** Working CLI interface

---

### STAGE 4: Validator Module (2-3 hours)

#### 4.1. Implementation of `validator.py`
```python
# Validation functions:
- validate_path() - check existence and type of path
- validate_files_count() - files_count >= 0
- validate_multiprocessing() - correct to os.cpu_count()
- validate_data_lines() - data_lines > 0
- validate_schema() - basic JSON check
- validate_all_parameters() - comprehensive validation
```

**Testing:**
- Parameterized tests for each validation function
- Edge case tests
- Error tests

**Result:** Complete input data validation

---

### STAGE 5: Schema Parser (4-5 hours)

#### 5.1. Implementation of `schema_parser.py`
```python
# SchemaParser class:
- parse() - main method
- parse_field() - parse one field
- _split_type_value() - split by ":"
- _validate_type() - check type (timestamp/str/int)
- _parse_str_value() - parse values for str
- _parse_int_value() - parse values for int
- _parse_timestamp_value() - parse for timestamp (with warning)
- _parse_list() - parse list of values
- _parse_range() - parse rand(from, to)

# Returns structure:
{
  'field_name': {
    'type': 'str'|'int'|'timestamp',
    'strategy': 'rand'|'list'|'range'|'static'|'empty',
    'value': None | list | (from, to) | static_value
  }
}
```

**Testing:**
- Parameterized tests for different types and strategies
- Tests for incorrect schemas
- Edge case tests

**Result:** Complete data schema parser

---

### STAGE 6: Data Generator (3-4 hours)

#### 6.1. Implementation of `data_generator.py`
```python
# DataGenerator class:
- __init__(parsed_schema) - initialization with parsed schema
- generate_line() - generate single data line
- generate_lines(count) - generate multiple lines
- _generate_field_value() - generate value for one field

# Helper functions:
- generate_timestamp() -> float
- generate_str_rand() -> str (UUID)
- generate_int_rand() -> int
- generate_from_list(values) -> any
- generate_int_range(from, to) -> int
- generate_static(value) -> value
- generate_empty(type) -> None | ""
```

**Testing:**
- Parameterized tests for different data types
- Tests for different schemas
- Output format check

**Result:** Working data generator

---

### STAGE 7: File Manager (3-4 hours)

#### 7.1. Implementation of `file_manager.py`
```python
# Functions:
- generate_file_name(base_name, prefix_type, index) -> str
- write_jsonlines(filepath, data_lines) -> None
- write_to_console(data_lines) -> None
- clear_directory(path, file_pattern) -> None
- create_single_file(params) -> str (filepath)
  # params: path, file_name, prefix, index, data
```

**Testing:**
- Test file name generation with different prefixes
- Test file writing (using temporary files)
- Test directory cleanup (clear_path)
- Test using fixtures

**Result:** Complete file management

---

### STAGE 8: Multiprocessing Coordinator (3-4 hours)

#### 8.1. Implementation of `multiprocessor.py`
```python
# Functions:
- distribute_work(total_files, num_processes) -> list[int]
  # Returns list with file count for each process
- worker_function(args) -> list[str]
  # Function for worker process
  # args: (process_id, files_to_create, common_params)
- generate_files_parallel(params) -> list[str]
  # Main function for parallel generation
```

**Testing:**
- Test work distribution
- Test file creation with multiprocessing > 1
- Check number of created files
- Check data correctness

**Result:** Working parallel generation

---

### STAGE 9: Integration and Main Module (2-3 hours)

#### 9.1. Final integration in `cli.py`
```python
# main() function:
1. Parse arguments
2. Load configuration
3. Validate parameters
4. Parse schema
5. Choose mode (console or files)
6. Choose mode (single-process or multi-process)
7. Generate data
8. Log results
```

**Testing:**
- Integration tests
- End-to-end tests with different parameters

**Result:** Fully working utility

---

### STAGE 10: Additional Tests (2-3 hours)

#### 10.1. Writing all required tests
1. ✅ Parameterized test for different data types
2. ✅ Parameterized test for different schemas
3. ✅ Test with temporary files and fixtures for loading schema from file
4. ✅ Test for clear_path
5. ✅ Test for saving files to disk
6. ✅ Test for checking file count with multiprocessing > 1
7. ✅ Custom additional test

**Result:** Complete test coverage

---

### STAGE 11: Documentation and Final Check (1-2 hours)

#### 11.1. Complete documentation
- Update README.md with usage examples
- Add docstrings to all functions and classes
- Create sample data schemas

#### 11.2. Final check
- Run all tests
- Check all requirements
- Check error handling
- Test on different OS (if possible)

**Result:** Ready for submission project

---

## 8. USAGE EXAMPLES

### Example 1: Generate to current directory
```bash
python -m dataforge . --files_count=3 --file_name=test_data --file_prefix=count \
  --data_schema='{"date":"timestamp:", "name":"str:rand", "age":"int:rand(18,65)"}'
```

**Result:**
- test_data_1.json
- test_data_2.json
- test_data_3.json

### Example 2: Load schema from file
```bash
python -m dataforge ./output --files_count=5 --data_schema=./schemas/user_schema.json
```

### Example 3: Output to console
```bash
python -m dataforge . --files_count=0 --data_lines=10 \
  --data_schema='{"id":"int:rand", "status":"str:[\"active\",\"inactive\"]"}'
```

### Example 4: With multiprocessing
```bash
python -m dataforge ./data --files_count=100 --multiprocessing=4 \
  --file_prefix=uuid --clear_path
```

---

## 9. default.ini STRUCTURE

```ini
[DEFAULT]
files_count = 10
file_name = generated_data
file_prefix = count
data_lines = 1000
multiprocessing = 1

[SCHEMA]
# Default schema example
default_schema = {"id": "int:rand", "timestamp": "timestamp:", "value": "str:rand"}
```

---

## 10. ACCEPTANCE CRITERIA

### ✅ Functionality
- [ ] All features implemented and working
- [ ] All command line parameters work correctly
- [ ] Data generation matches schema
- [ ] Multiprocessing works correctly
- [ ] File prefixes work (count, random, uuid)
- [ ] clear_path correctly deletes files
- [ ] Console output works (files_count=0)

### ✅ Error Handling
- [ ] All possible errors handled
- [ ] No unhandled traceback
- [ ] sys.exit(1) used instead of raise
- [ ] All errors logged with logging.error()
- [ ] Correct validation of all input parameters

### ✅ Code Quality
- [ ] Code divided into functions/classes/modules
- [ ] No monolithic code
- [ ] Clear variable and function names
- [ ] Docstrings for all public functions

### ✅ Testing
- [ ] All unit tests written
- [ ] Parameterized tests for data types
- [ ] Parameterized tests for schemas
- [ ] Tests with fixtures and temporary files
- [ ] Test for clear_path
- [ ] Test for multiprocessing
- [ ] All tests pass successfully

### ✅ Documentation
- [ ] README.md with instructions
- [ ] Usage examples
- [ ] Help messages are informative
- [ ] default.ini created and filled

---

## 11. TEST SCENARIOS

### Test 1: Different data types (parameterized)
```python
@pytest.mark.parametrize("data_type,strategy,expected_type", [
    ("str", "rand", str),
    ("int", "rand", int),
    ("timestamp", "", float),
    ("str", "['val1','val2']", str),
    ("int", "rand(1,100)", int),
])
def test_data_types(data_type, strategy, expected_type):
    # Test generation of different types
```

### Test 2: Different schemas (parameterized)
```python
@pytest.mark.parametrize("schema", [
    {"name": "str:rand"},
    {"age": "int:rand(1,90)"},
    {"date": "timestamp:", "name": "str:rand"},
    {"status": "str:['active','inactive','pending']"},
])
def test_schemas(schema):
    # Test different schemas
```

### Test 3: Load schema from file (with fixtures)
```python
@pytest.fixture
def temp_schema_file(tmp_path):
    schema = {"test": "str:rand"}
    file_path = tmp_path / "schema.json"
    with open(file_path, 'w') as f:
        json.dump(schema, f)
    return file_path

def test_schema_from_file(temp_schema_file):
    # Test loading from file
```

### Test 4: clear_path
```python
def test_clear_path(tmp_path):
    # Create files
    # Run with clear_path
    # Check that old files are deleted
```

### Test 5: Save to disk
```python
def test_save_to_disk(tmp_path):
    # Generate files
    # Check existence
    # Check content (JSON Lines)
```

### Test 6: Multiprocessing
```python
def test_multiprocessing(tmp_path):
    # Generate with multiprocessing=4
    # Check file count
    # Check all files are valid
```

### Test 7: Custom test
```python
def test_custom():
    # For example, performance test
    # or test for very large data
    # or test for edge cases
```

---

## 12. POTENTIAL ISSUES AND SOLUTIONS

### Issue 1: File name conflicts with multiprocessing
**Solution:** Use unique prefixes or counters for each process

### Issue 2: Special characters handling in schema
**Solution:** Escaping or using raw strings

### Issue 3: Performance with large volumes
**Solution:** Generate and write data in chunks, buffering

### Issue 4: Cross-platform path handling
**Solution:** Use os.path or pathlib

### Issue 5: Interrupt handling (Ctrl+C)
**Solution:** Signal handlers for graceful shutdown

---

## 13. EXTENSIONS (OPTIONAL)

If time permits, can add:

1. **Additional data types:**
   - float
   - bool
   - date (formatted dates)

2. **Additional output formats:**
   - CSV
   - XML
   - Parquet

3. **Progress bar:** Show generation progress

4. **Validation of generated data:** Check schema compliance

5. **Statistics:** Output statistics about generated data

6. **Schema templates:** Preset schemas for typical scenarios

---

## 14. TIMELINE ESTIMATE

**Total time: 25-35 hours**

- Stage 1: Setup - 1-2 hours
- Stage 2: Basic modules - 3-4 hours
- Stage 3: CLI - 2-3 hours
- Stage 4: Validator - 2-3 hours
- Stage 5: Schema Parser - 4-5 hours
- Stage 6: Data Generator - 3-4 hours
- Stage 7: File Manager - 3-4 hours
- Stage 8: Multiprocessing - 3-4 hours
- Stage 9: Integration - 2-3 hours
- Stage 10: Tests - 2-3 hours
- Stage 11: Documentation - 1-2 hours

---

## 15. VERIFICATION CHECKLIST

### Before starting coding:
- [ ] All required Python modules studied
- [ ] All requirements understood
- [ ] Project structure created

### During development:
- [ ] Each module tested separately
- [ ] Logging added where needed
- [ ] Error handling implemented
- [ ] Code is readable and structured

### Before submission:
- [ ] All tests pass
- [ ] All requirements met
- [ ] Documentation complete
- [ ] Examples work
- [ ] No unhandled exceptions
- [ ] Help messages are informative
- [ ] default.ini created
- [ ] README.md up to date

---

## 16. DATA SCHEMA SPECIFICATION

### Schema Format
```json
{
  "field_name": "type:generation_instruction"
}
```

### Supported Types
- `timestamp` - Unix timestamp (float)
- `str` - String value
- `int` - Integer value

### Generation Instructions

#### For `timestamp:`
- Any value after `:` is ignored (with warning)
- Always generates current Unix timestamp using `time.time()`
- Example: `"date": "timestamp:"`

#### For `str:`
- `rand` - generates random UUID using `str(uuid.uuid4())`
  - Example: `"name": "str:rand"`
- `['value1', 'value2', ...]` - random choice from list using `random.choice()`
  - Example: `"type": "str:['client', 'partner', 'government']"`
- `specific_value` - static string value
  - Example: `"category": "str:user"`
- Empty - empty string `""`
  - Example: `"optional": "str:"`

#### For `int:`
- `rand` - generates random integer in range [0, 10000] using `random.randint(0, 10000)`
  - Example: `"id": "int:rand"`
- `rand(from, to)` - generates random integer in specified range using `random.randint(from, to)`
  - Example: `"age": "int:rand(18, 90)"`
- `[value1, value2, ...]` - random choice from list using `random.choice()`
  - Example: `"status_code": "int:[200, 404, 500]"`
- `specific_value` - static integer value (must be valid integer)
  - Example: `"version": "int:1"`
- Empty - None value
  - Example: `"optional_number": "int:"`

### Error Cases
1. Invalid type (not timestamp/str/int) - ERROR, exit
2. `rand(from, to)` with non-int type - ERROR, exit
3. Static value doesn't match type (e.g., `"int:hello"`) - ERROR, exit
4. Invalid JSON format - ERROR, exit
5. Malformed list syntax - ERROR, exit
6. Malformed range syntax - ERROR, exit

### Schema Examples

#### Example 1: User Data
```json
{
  "user_id": "str:rand",
  "username": "str:rand",
  "email": "str:rand",
  "age": "int:rand(18, 80)",
  "status": "str:['active', 'inactive', 'suspended']",
  "created_at": "timestamp:",
  "subscription_level": "int:[1, 2, 3]"
}
```

#### Example 2: Transaction Data
```json
{
  "transaction_id": "str:rand",
  "amount": "int:rand(1, 10000)",
  "currency": "str:USD",
  "type": "str:['purchase', 'refund', 'transfer']",
  "timestamp": "timestamp:",
  "status": "str:completed"
}
```

#### Example 3: Log Entry
```json
{
  "log_id": "str:rand",
  "level": "str:['INFO', 'WARNING', 'ERROR', 'DEBUG']",
  "timestamp": "timestamp:",
  "message": "str:rand",
  "source": "str:application",
  "line_number": "int:rand(1, 1000)"
}
```

---

## 17. EXPECTED OUTPUT FORMAT

### JSON Lines Format
Each file should contain one JSON object per line (newline-delimited JSON):

```json
{"date": 1534717897.967033, "name": "f82a44ac-daa7-4b8f-8569-83898fb9b312", "type": "partner", "age": 45}
{"date": 1534717898.442959, "name": "660ddea3-cbe4-47cf-918f-bafec6e87951", "type": "government", "age": 12}
{"date": 1534717896.136228, "name": "0c8ccb4b-2b5c-4a50-ad46-b0e08f7f8448", "type": "client", "age": 61}
```

**Important:** 
- Each line is a valid JSON object
- No commas between lines
- No enclosing array brackets
- Format complies with https://jsonlines.org/

---

## 18. ERROR MESSAGES GUIDE

All error messages should be clear and actionable:

### Path Errors
```
ERROR: Path '/invalid/path' does not exist
ERROR: Path '/some/file.txt' exists but is not a directory
```

### Parameter Errors
```
ERROR: files_count must be >= 0, got: -5
ERROR: data_lines must be > 0, got: 0
ERROR: multiprocessing must be >= 1, got: 0
ERROR: Invalid file_prefix 'invalid', must be one of: count, random, uuid
```

### Schema Errors
```
ERROR: Invalid data schema: not a valid JSON
ERROR: Invalid type 'float' in field 'price'. Supported types: timestamp, str, int
ERROR: rand(from, to) can only be used with int type, not str
ERROR: Invalid static value 'abc' for int type in field 'age'
ERROR: Failed to parse list in field 'status': invalid syntax
```

### File Errors
```
ERROR: Failed to create file '/path/file.json': Permission denied
ERROR: Failed to write to file '/path/file.json': Disk full
ERROR: Failed to load schema from file '/path/schema.json': File not found
```

---

## 19. LOGGING OUTPUT GUIDE

### INFO Level Messages
```
INFO: Starting DataForge utility
INFO: Configuration loaded from default.ini
INFO: Validating parameters...
INFO: Parameters validated successfully
INFO: Parsing data schema...
INFO: Schema parsed: 5 fields defined
INFO: Generating 100 files with 1000 lines each...
INFO: Using 4 processes for parallel generation
INFO: Process 1 starting: 25 files to generate
INFO: Process 1 completed: 25 files generated
INFO: All processes completed
INFO: Successfully generated 100 files in /path/to/output
INFO: Total lines generated: 100000
INFO: Generation completed in 12.34 seconds
```

### WARNING Level Messages
```
WARNING: timestamp type does not support values, ignoring 'somevalue' in field 'date'
WARNING: multiprocessing value 16 exceeds CPU count (8), setting to 8
WARNING: File 'data.json' already exists and will be overwritten
```

### ERROR Level Messages
```
ERROR: Invalid schema: missing required field
ERROR: Cannot create directory: permission denied
ERROR: Validation failed: files_count must be non-negative
```

---

## 20. COMMAND LINE HELP OUTPUT

Example of expected `--help` output:

```
usage: dataforge [-h] [--files_count FILES_COUNT] [--file_name FILE_NAME]
                 [--file_prefix {count,random,uuid}] [--data_schema DATA_SCHEMA]
                 [--data_lines DATA_LINES] [--clear_path]
                 [--multiprocessing MULTIPROCESSING]
                 path_to_save_files

DataForge - Test Data Generation Utility
Generate test JSON data based on custom data schemas for testing data pipelines.

positional arguments:
  path_to_save_files    Path where files will be saved (relative or absolute).
                        Use '.' for current directory.

optional arguments:
  -h, --help            show this help message and exit
  --files_count FILES_COUNT
                        Number of files to generate. Use 0 to output to console.
                        (default: 10)
  --file_name FILE_NAME
                        Base name for generated files (default: generated_data)
  --file_prefix {count,random,uuid}
                        Prefix strategy for file names when generating multiple files.
                        count: sequential numbers, random: random numbers, uuid: unique identifiers
                        (default: count)
  --data_schema DATA_SCHEMA
                        JSON schema string or path to JSON file containing schema.
                        Example: '{"name":"str:rand","age":"int:rand(1,90)"}'
                        (default: {"id":"int:rand","timestamp":"timestamp:","value":"str:rand"})
  --data_lines DATA_LINES
                        Number of data lines to generate in each file (default: 1000)
  --clear_path          Delete existing files with matching name before generation
  --multiprocessing MULTIPROCESSING
                        Number of parallel processes to use for file generation.
                        (default: 1, max: cpu_count)

Examples:
  Generate 3 files in current directory:
    dataforge . --files_count=3 --file_name=data --file_prefix=count

  Load schema from file:
    dataforge ./output --data_schema=./schema.json

  Output to console:
    dataforge . --files_count=0 --data_lines=10

  Parallel generation:
    dataforge ./output --files_count=100 --multiprocessing=4
```

---

**End of Document**

