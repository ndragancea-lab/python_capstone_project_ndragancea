# DataForge - Test Data Generation Utility

<p align="center">
  <strong>Console utility for generating test JSON data based on custom data schemas</strong>
</p>

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
  - [Command Line Arguments](#command-line-arguments)
  - [Data Schema Format](#data-schema-format)
  - [Examples](#examples)
- [Configuration](#configuration)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Development](#development)
- [Requirements](#requirements)

---

## 🎯 Overview

**DataForge** is a powerful console utility designed to generate test data for data pipelines. It allows you to define custom data schemas and generates JSON data according to those schemas, supporting various data types and generation strategies.

**Key Use Cases:**
- Testing data pipeline transformations
- Validating data processing logic
- Generating mock data for development
- Performance testing with large datasets

---

## ✨ Features

- ✅ **Flexible Schema Definition** - Define data structure using JSON schema notation
- ✅ **Multiple Data Types** - Support for `timestamp`, `str`, and `int` types
- ✅ **Generation Strategies** - Random, list-based, range-based, static, and empty values
- ✅ **File Management** - Generate multiple files with configurable naming (count, random, uuid)
- ✅ **Console Output** - Output data directly to console for quick testing
- ✅ **Multiprocessing** - Parallel file generation for better performance
- ✅ **Configuration** - Default values stored in `default.ini`
- ✅ **Comprehensive Logging** - Track all operations with detailed logging
- ✅ **Error Handling** - Graceful error handling with informative messages
- ✅ **JSON Lines Format** - Industry-standard output format

---

## 🚀 Installation

### Prerequisites
- Python 3.6 or higher
- Git

### Steps

1. **Clone the repository:**
```bash
git clone https://github.com/ndragancea-lab/python_capstone_project_ndragancea.git
cd python_capstone_project_ndragancea
```

2. **Create virtual environment:**
```bash
python3 -m venv venv
```

3. **Activate virtual environment:**
```bash
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

4. **Install dependencies:**
```bash
pip install -r requirements.txt
```

5. **Verify installation:**
```bash
python -m dataforge --help
```

**Note:** Always activate the virtual environment before running the utility.

---

## ⚡ Quick Start

**First, activate the virtual environment:**
```bash
cd python_capstone_project_ndragancea
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows
```

### Option 1: Using the convenience script (macOS/Linux only)
```bash
# Make script executable (first time only)
chmod +x run_dataforge.sh

# Generate files with random user data
./run_dataforge.sh . --files_count=3 --file_name=users \
  --data_schema='{"id":"int:rand","name":"str:rand","age":"int:rand(18,80)"}'

# Output to console
./run_dataforge.sh . --files_count=0 --data_lines=10 \
  --data_schema='{"timestamp":"timestamp:","value":"int:rand"}'
```

### Option 2: Direct Python execution (all platforms)
```bash
# Generate 3 files with random user data
python -m dataforge . --files_count=3 --file_name=users \
  --data_schema='{"id":"int:rand","name":"str:rand","age":"int:rand(18,80)"}'

# Output 10 lines to console
python -m dataforge . --files_count=0 --data_lines=10 \
  --data_schema='{"timestamp":"timestamp:","value":"int:rand"}'
```

**Without virtual environment activation:**
```bash
# Use python3 instead of python
python3 -m dataforge . --files_count=0 --data_lines=10 \
  --data_schema='{"timestamp":"timestamp:","value":"int:rand"}'
```

---

## 📖 Usage

**Note:** Make sure the virtual environment is activated:
```bash
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows
```

### Command Line Arguments

```bash
# With venv activated:
python -m dataforge <path_to_save_files> [OPTIONS]

# Or use the convenience script (macOS/Linux):
./run_dataforge.sh <path_to_save_files> [OPTIONS]

# Or without venv activation:
python3 -m dataforge <path_to_save_files> [OPTIONS]
```

#### Positional Arguments:
- `path_to_save_files` - Directory where files will be saved (use `.` for current directory)

#### Optional Arguments:

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--files_count` | int | 10 | Number of files to generate (0 = console output) |
| `--file_name` | str | generated_data | Base name for files |
| `--file_prefix` | choice | count | Prefix type: `count`, `random`, or `uuid` |
| `--data_schema` | str | (from config) | JSON schema string or path to schema file |
| `--data_lines` | int | 1000 | Number of lines per file |
| `--clear_path` | flag | False | Delete matching files before generation |
| `--multiprocessing` | int | 1 | Number of parallel processes |

### Data Schema Format

Schema uses the notation: `"field_name": "type:generation_instruction"`

#### Supported Types:
- `timestamp` - Current Unix timestamp
- `str` - String values
- `int` - Integer values

#### Generation Instructions:

| Type | Instruction | Example | Description |
|------|------------|---------|-------------|
| `str` | `rand` | `"name": "str:rand"` | Random UUID |
| `str` | `['val1','val2']` | `"type": "str:['client','partner']"` | Random choice from list |
| `str` | `value` | `"category": "str:user"` | Static value |
| `str` | (empty) | `"optional": "str:"` | Empty string |
| `int` | `rand` | `"id": "int:rand"` | Random int [0, 10000] |
| `int` | `rand(from,to)` | `"age": "int:rand(18,65)"` | Random int in range |
| `int` | `['1','2','3']` | `"code": "int:[200,404,500]"` | Random choice from list |
| `int` | `value` | `"version": "int:1"` | Static value |
| `int` | (empty) | `"optional": "int:"` | None |
| `timestamp` | (any) | `"date": "timestamp:"` | Current timestamp |

### Examples

#### Example 1: Simple user data
```bash
python -m dataforge . --files_count=5 --file_name=users --file_prefix=count \
  --data_schema='{"user_id":"str:rand","username":"str:rand","age":"int:rand(18,80)","status":"str:[\"active\",\"inactive\"]","created_at":"timestamp:"}'
```

Output files:
- `users_1.json`
- `users_2.json`
- `users_3.json`
- `users_4.json`
- `users_5.json`

Each file contains lines like:
```json
{"user_id": "f82a44ac-daa7-4b8f-8569-83898fb9b312", "username": "660ddea3-cbe4-47cf-918f-bafec6e87951", "age": 45, "status": "active", "created_at": 1534717897.967033}
{"user_id": "0c8ccb4b-2b5c-4a50-ad46-b0e08f7f8448", "username": "a1b2c3d4-e5f6-7890-abcd-ef1234567890", "age": 32, "status": "inactive", "created_at": 1534717898.442959}
```

#### Example 2: Load schema from file
Create `schema.json`:
```json
{
  "transaction_id": "str:rand",
  "amount": "int:rand(1,10000)",
  "currency": "str:USD",
  "type": "str:['purchase','refund','transfer']",
  "timestamp": "timestamp:"
}
```

Run:
```bash
python -m dataforge ./output --files_count=10 --data_schema=./schema.json
```

#### Example 3: Console output
```bash
python -m dataforge . --files_count=0 --data_lines=5 \
  --data_schema='{"id":"int:rand","value":"str:rand"}'
```

#### Example 4: Parallel generation with cleanup
```bash
python -m dataforge ./data --files_count=100 --multiprocessing=4 \
  --file_prefix=uuid --clear_path
```

#### Example 5: E-commerce orders dataset
```bash
python -m dataforge ./orders --files_count=20 --file_name=order \
  --data_schema='{"order_id":"str:rand","customer_id":"int:rand(1000,9999)","product":"str:[\"laptop\",\"phone\",\"tablet\",\"monitor\"]","quantity":"int:rand(1,5)","price":"int:rand(100,2000)","status":"str:[\"pending\",\"shipped\",\"delivered\"]","created":"timestamp:"}'
```

#### Example 6: IoT sensor data
```bash
python -m dataforge ./sensors --files_count=50 --data_lines=5000 \
  --file_name=sensor_data --multiprocessing=4 \
  --data_schema='{"sensor_id":"str:rand","temperature":"int:rand(-10,40)","humidity":"int:rand(20,80)","pressure":"int:rand(980,1020)","timestamp":"timestamp:"}'
```

#### Example 7: Web server logs simulation
```bash
python -m dataforge ./logs --files_count=10 --data_lines=10000 \
  --file_prefix=random --file_name=access_log \
  --data_schema='{"ip":"str:rand","method":"str:[\"GET\",\"POST\",\"PUT\",\"DELETE\"]","path":"str:[\"/api/users\",\"/api/products\",\"/api/orders\"]","status_code":"int:[200,201,400,404,500]","response_time":"int:rand(10,5000)","timestamp":"timestamp:"}'
```

##### Example 8: Financial transactions
Create `financial_schema.json`:
```json
{
  "transaction_id": "str:rand",
  "account_from": "int:rand(10000,99999)",
  "account_to": "int:rand(10000,99999)",
  "amount": "int:rand(1,100000)",
  "currency": "str:[\"USD\",\"EUR\",\"GBP\"]",
  "type": "str:[\"transfer\",\"payment\",\"withdrawal\",\"deposit\"]",
  "status": "str:[\"completed\",\"pending\",\"failed\"]",
  "timestamp": "timestamp:"
}
```

Run:
```bash
python -m dataforge ./transactions --files_count=100 \
  --file_name=transaction --file_prefix=uuid \
  --data_schema=./financial_schema.json --multiprocessing=8
```

### 📚 More Examples

See the [examples/](examples/) directory for ready-to-use schema files:
- **User Activity Tracking** - Website/app user behavior
- **E-commerce Orders** - Online store transactions
- **IoT Sensor Data** - Industrial sensor readings
- **Web Server Logs** - HTTP request logs
- **Financial Transactions** - Banking data
- **Social Media Posts** - Post analytics

Each example includes:
- Pre-configured JSON schema
- Usage instructions
- Field descriptions
- Performance recommendations

---

## 🎨 Advanced Usage

### Performance Optimization

For large datasets, use multiprocessing:
```bash
# Generate 1000 files with 10,000 lines each using 8 cores
python -m dataforge ./bigdata --files_count=1000 --data_lines=10000 \
  --multiprocessing=8 --file_prefix=uuid
```

### Schema Validation

DataForge validates schemas before generation:
```bash
# This will produce an error - invalid strategy
python -m dataforge . --data_schema='{"id":"int:invalid"}'
```

### Console Mode for Quick Testing

Use `--files_count=0` for immediate output:
```bash
# Test your schema before generating files
python -m dataforge . --files_count=0 --data_lines=3 \
  --data_schema='{"test":"str:rand"}'
```

### Clean Regeneration

Use `--clear_path` to remove old files before generation:
```bash
# Remove all files matching "data_*.json" pattern before generating new ones
python -m dataforge ./output --file_name=data --clear_path
```

---

## ⚙️ Configuration

Default values are stored in `default.ini`:

```ini
[DEFAULT]
files_count = 10
file_name = generated_data
file_prefix = count
data_lines = 1000
multiprocessing = 1

[SCHEMA]
default_schema = {"id": "int:rand", "timestamp": "timestamp:", "value": "str:rand"}
```

---

## 🧪 Testing

### Running Tests

**First, activate virtual environment:**
```bash
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows
```

Run all tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=dataforge --cov-report=html
```

Run specific test file:
```bash
pytest tests/test_schema_parser.py
```

Run verbose mode:
```bash
pytest -v
```

**Deactivate virtual environment when done:**
```bash
deactivate
```

### Test Coverage

The project has **295 comprehensive tests** covering:

| Module | Test Count | Coverage Areas |
|--------|------------|----------------|
| `test_cli.py` | 40+ tests | Argument parsing, help text, validation |
| `test_config.py` | 25+ tests | Config loading, defaults, file handling |
| `test_validator.py` | 45+ tests | Input validation, error cases |
| `test_schema_parser.py` | 60+ tests | Schema parsing, all data types |
| `test_data_generator.py` | 50+ tests | Data generation, all strategies |
| `test_file_manager.py` | 30+ tests | File operations, prefixes |
| `test_multiprocessor.py` | 15+ tests | Parallel processing |
| `test_integration.py` | 20+ tests | End-to-end workflows |
| `test_special.py` | 8 tests | Performance, stress, edge cases |

### Special Tests

The `test_special.py` module includes advanced tests:
- **Performance Benchmark**: Compares single vs. parallel processing
- **Data Consistency**: Verifies data across multiple runs
- **Complex Schemas**: Tests all types and strategies together
- **Stress Testing**: Large files (1000+ lines)
- **Edge Cases**: Minimal and maximal configurations
- **Uniqueness Verification**: Random and UUID prefix uniqueness
- **Distribution Analysis**: Statistical randomness validation

---

## 📁 Project Structure

```
python_capstone_project_ndragancea/
├── dataforge/                  # Main application package
│   ├── __init__.py            # Package initialization
│   ├── __main__.py            # Entry point for module execution
│   ├── cli.py                 # Command line interface
│   ├── config.py              # Configuration management
│   ├── validator.py           # Input validation
│   ├── schema_parser.py       # Data schema parsing
│   ├── data_generator.py      # Data generation logic
│   ├── file_manager.py        # File operations
│   ├── multiprocessor.py      # Parallel processing
│   ├── logger.py              # Logging setup
│   └── utils.py               # Utility functions
├── tests/                     # Test suite (295 tests)
│   ├── __init__.py
│   ├── conftest.py           # Pytest fixtures
│   ├── test_cli.py           # CLI tests
│   ├── test_config.py        # Configuration tests
│   ├── test_validator.py     # Validation tests
│   ├── test_schema_parser.py # Schema parsing tests
│   ├── test_data_generator.py # Data generation tests
│   ├── test_file_manager.py  # File operations tests
│   ├── test_multiprocessor.py # Multiprocessing tests
│   ├── test_integration.py   # Integration tests
│   ├── test_special.py       # Special & performance tests
│   └── fixtures/             # Test data files
├── examples/                  # Ready-to-use schema examples
│   ├── README.md             # Examples documentation
│   ├── user_activity_schema.json
│   ├── ecommerce_orders_schema.json
│   ├── iot_sensors_schema.json
│   ├── web_logs_schema.json
│   ├── financial_transactions_schema.json
│   └── social_media_schema.json
├── venv/                      # Virtual environment (not in git)
├── default.ini                # Default configuration
├── requirements.txt           # Python dependencies
├── run_dataforge.sh           # Convenience script for running (macOS/Linux)
├── README.md                  # This file
└── .gitignore                # Git ignore rules
```

---

## 🛠️ Development

### Setting Up Development Environment

1. **Clone and setup:**
```bash
git clone https://github.com/ndragancea-lab/python_capstone_project_ndragancea.git
cd python_capstone_project_ndragancea
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

2. **Run tests:**
```bash
pytest -v
```

3. **Make changes and test:**
```bash
# Edit code...
pytest tests/
python -m dataforge . --files_count=0 --data_lines=3 --data_schema='{"id":"int:rand"}'
```

4. **Deactivate when done:**
```bash
deactivate
```

### Module Responsibilities

1. **cli.py** - Command line interface and argument parsing
2. **config.py** - Load and manage default configuration
3. **validator.py** - Validate all input parameters
4. **schema_parser.py** - Parse and validate data schemas
5. **data_generator.py** - Generate data based on schema
6. **file_manager.py** - Handle file creation and writing
7. **multiprocessor.py** - Coordinate parallel file generation
8. **logger.py** - Configure application logging
9. **utils.py** - Helper functions and utilities

### Convenience Script

The `run_dataforge.sh` script automatically activates the virtual environment:

```bash
#!/bin/bash
# Automatically activates venv and runs dataforge
source venv/bin/activate
python -m dataforge "$@"
```

Usage:
```bash
./run_dataforge.sh . --files_count=10 --data_schema='{"id":"int:rand"}'
```

---

## 📦 Requirements

All dependencies are from Python standard library except testing:

**Standard Library:**
- argparse
- json
- os, shutil
- time
- random
- configparser
- logging
- uuid
- multiprocessing
- sys

**Testing:**
- pytest >= 7.0.0
- pytest-cov >= 3.0.0

---

## ❓ FAQ & Troubleshooting

### Common Questions

**Q: How do I generate large datasets efficiently?**  
A: Use the `--multiprocessing` parameter with the number of CPU cores available:
```bash
python -m dataforge ./data --files_count=1000 --multiprocessing=8
```

**Q: Can I use the same schema across multiple runs?**  
A: Yes! Save your schema to a JSON file and reference it:
```bash
python -m dataforge ./output --data_schema=./my_schema.json
```

**Q: How do I generate unique IDs?**  
A: Use `"str:rand"` for UUID-based unique identifiers:
```bash
--data_schema='{"id":"str:rand"}'
```

**Q: What's the difference between file prefix types?**
- `count` - Sequential numbers (data_1.json, data_2.json, ...)
- `random` - 8-character random strings (data_a3f9b2c1.json, ...)
- `uuid` - Full UUID v4 (data_f47ac10b-58cc-4372-a567-0e02b2c3d479.json, ...)

**Q: How do I test my schema before generating thousands of files?**  
A: Use console mode with `--files_count=0`:
```bash
python -m dataforge . --files_count=0 --data_lines=5 --data_schema='YOUR_SCHEMA'
```

### Troubleshooting

**Problem: "Invalid schema format" error**  
Solution: Ensure your schema is valid JSON. Use single quotes for the outer string and double quotes inside:
```bash
--data_schema='{"field":"type:instruction"}'
```

**Problem: Files not being generated**  
Solution: Check that:
1. The output directory exists
2. You have write permissions
3. `--files_count` is greater than 0

**Problem: Slow generation performance**  
Solution: Enable multiprocessing for large datasets:
```bash
--multiprocessing=4  # Use 4 CPU cores
```

**Problem: Memory issues with large files**  
Solution: DataForge writes line-by-line, but if issues persist:
1. Reduce `--data_lines` per file
2. Increase `--files_count` to spread data across more files
3. Enable `--multiprocessing` to distribute memory load

**Problem: Import errors**  
Solution: Ensure you're running from the project root:
```bash
cd /path/to/python_capstone_project_ndragancea
python -m dataforge . --help
```

**Problem: Configuration not loading**  
Solution: Ensure `default.ini` exists in the project root. If missing, run:
```bash
python -m dataforge . --help  # This creates default.ini if missing
```

---

## 📊 Performance Metrics

Based on testing (MacBook Pro, M1, 8 cores):

| Configuration | Files | Lines/File | Time (single) | Time (8 cores) | Speedup |
|--------------|-------|------------|---------------|----------------|---------|
| Small | 10 | 100 | 0.5s | 0.2s | 2.5x |
| Medium | 100 | 1,000 | 5.2s | 1.4s | 3.7x |
| Large | 1,000 | 10,000 | 52s | 14s | 3.7x |

**Note:** Actual performance depends on:
- CPU cores available
- Disk I/O speed
- Schema complexity
- Operating system

---

## 📄 License

This project is part of the Python Capstone Project.

---

## 🤝 Contributing

This is a capstone project. Please refer to project requirements for contribution guidelines.

---

## 📞 Support

For issues and questions, please refer to the project documentation or contact the project maintainer.

---

**Built with ❤️ for testing data pipelines**

