# DataForge Project Index

Quick navigation guide for the DataForge project.

## 📚 Documentation (Start Here)

| Document | Description | When to Read |
|----------|-------------|--------------|
| [README.md](README.md) | **Main documentation** - Usage guide, examples, FAQ | Start here for usage |
| [FINAL_REPORT.md](FINAL_REPORT.md) | **Project completion report** - Statistics, achievements | Review after completion |
| [PROJECT_REQUIREMENTS_AND_ARCHITECTURE.md](PROJECT_REQUIREMENTS_AND_ARCHITECTURE.md) | Complete requirements and architecture | Understanding design decisions |
| [examples/README.md](examples/README.md) | Example schemas documentation | Learning schema patterns |

---

## 🎯 Quick Access by Task

### I want to USE the utility
→ Start with [README.md](README.md)
- See "Quick Start" section
- Review "Usage" section
- Check "Examples" section

### I want to see EXAMPLE SCHEMAS
→ Go to [examples/](examples/) folder
1. [user_activity_schema.json](examples/user_activity_schema.json)
2. [ecommerce_orders_schema.json](examples/ecommerce_orders_schema.json)
3. [iot_sensors_schema.json](examples/iot_sensors_schema.json)
4. [web_logs_schema.json](examples/web_logs_schema.json)
5. [financial_transactions_schema.json](examples/financial_transactions_schema.json)
6. [social_media_schema.json](examples/social_media_schema.json)

### I want to UNDERSTAND the code
→ Start with [PROJECT_REQUIREMENTS_AND_ARCHITECTURE.md](PROJECT_REQUIREMENTS_AND_ARCHITECTURE.md)
- See "Module Architecture" section
- Review "Data Flow" section
- Check module responsibilities

### I want to see TEST COVERAGE
→ Check [FINAL_REPORT.md](FINAL_REPORT.md)
- See "Testing Summary" section
- 295 tests across 9 test modules

### I want to TROUBLESHOOT
→ See [README.md](README.md) FAQ section
- Common questions
- Troubleshooting guide
- Error solutions

---

## 📦 Source Code Structure

### Core Modules (dataforge/)

| Module | Purpose | Key Functions |
|--------|---------|---------------|
| [cli.py](dataforge/cli.py) | Command-line interface | `create_parser()`, `parse_arguments()` |
| [config.py](dataforge/config.py) | Configuration management | `load_default_config()`, `merge_config_with_args()` |
| [validator.py](dataforge/validator.py) | Input validation | `validate_path()`, `validate_all_parameters()` |
| [schema_parser.py](dataforge/schema_parser.py) | Schema parsing | `parse_schema()`, `extract_strategy()` |
| [data_generator.py](dataforge/data_generator.py) | Data generation | `create_generator()`, `generate_*()` functions |
| [file_manager.py](dataforge/file_manager.py) | File operations | `create_multiple_files()`, `generate_prefix()` |
| [multiprocessor.py](dataforge/multiprocessor.py) | Parallel processing | `generate_files_parallel()` |
| [logger.py](dataforge/logger.py) | Logging setup | `setup_logger()` |
| [utils.py](dataforge/utils.py) | Utilities | Helper functions |

### Test Modules (tests/)

| Test Module | Tests | Coverage |
|-------------|-------|----------|
| [test_cli.py](tests/test_cli.py) | 40+ | CLI argument parsing |
| [test_config.py](tests/test_config.py) | 25+ | Configuration loading |
| [test_validator.py](tests/test_validator.py) | 45+ | Input validation |
| [test_schema_parser.py](tests/test_schema_parser.py) | 60+ | Schema parsing |
| [test_data_generator.py](tests/test_data_generator.py) | 50+ | Data generation |
| [test_file_manager.py](tests/test_file_manager.py) | 30+ | File operations |
| [test_multiprocessor.py](tests/test_multiprocessor.py) | 15+ | Multiprocessing |
| [test_integration.py](tests/test_integration.py) | 20+ | End-to-end tests |
| [test_special.py](tests/test_special.py) | 8 | Performance & edge cases |

---

## 🚀 Common Tasks

### Run the utility
```bash
# Basic usage
python -m dataforge . --files_count=10 \
  --data_schema='{"id":"int:rand","name":"str:rand"}'

# Console output
python -m dataforge . --files_count=0 --data_lines=5 \
  --data_schema='{"id":"int:rand"}'

# Use example schema
python -m dataforge ./output --files_count=50 \
  --data_schema=./examples/ecommerce_orders_schema.json
```

### Run tests
```bash
# All tests
pytest

# Specific module
pytest tests/test_schema_parser.py

# With coverage
pytest --cov=dataforge --cov-report=html

# Verbose
pytest -v
```

### Get help
```bash
python -m dataforge --help
```

---

## 📊 Project Statistics

- **Development Stages:** 11/11 completed ✅
- **Python Modules:** 11
- **Test Modules:** 11
- **Total Tests:** 295 (all passing) ✅
- **Lines of Code:** ~3,262
- **Example Schemas:** 6
- **Documentation Files:** 7

---

## ✅ Requirements Checklist

### Functional Requirements
- ✅ FR-1: Generate JSON data according to schema
- ✅ FR-2: Support timestamp, str, and int types
- ✅ FR-3: Multiple generation strategies
- ✅ FR-4: File and console output modes
- ✅ FR-5: Configurable file naming
- ✅ FR-6: Multiprocessing support
- ✅ FR-7: Configuration file support
- ✅ FR-8: Clear existing files option

### Non-Functional Requirements
- ✅ NFR-1: Fast generation with multiprocessing
- ✅ NFR-2: Comprehensive error handling
- ✅ NFR-3: Detailed logging
- ✅ NFR-4: User-friendly CLI
- ✅ NFR-5: Cross-platform compatibility
- ✅ NFR-6: Comprehensive testing
- ✅ NFR-7: Clear documentation
- ✅ NFR-8: JSON Lines output format

---

## 🎓 Learning Resources

### New to the project?
1. Read [README.md](README.md) - Overview and quick start
2. Try examples from [examples/](examples/)
3. Review [PROJECT_REQUIREMENTS_AND_ARCHITECTURE.md](PROJECT_REQUIREMENTS_AND_ARCHITECTURE.md)

### Want to understand the implementation?
1. Check [PROJECT_REQUIREMENTS_AND_ARCHITECTURE.md](PROJECT_REQUIREMENTS_AND_ARCHITECTURE.md) - See architecture and design
2. Check module docstrings in [dataforge/](dataforge/)
3. Study test cases in [tests/](tests/)

### Want to verify completeness?
1. Check [FINAL_REPORT.md](FINAL_REPORT.md) - Complete statistics
2. Review [PROJECT_REQUIREMENTS_AND_ARCHITECTURE.md](PROJECT_REQUIREMENTS_AND_ARCHITECTURE.md) - All requirements
3. Run `pytest -v` to see all tests

---

## 🔍 File Locations

### Configuration
- [default.ini](default.ini) - Default configuration values

### Dependencies
- [requirements.txt](requirements.txt) - Python dependencies

### Entry Points
- [dataforge/__main__.py](dataforge/__main__.py) - Module entry point
- [dataforge/__init__.py](dataforge/__init__.py) - Package initialization

---

## 📞 Support

For issues and questions:
1. Check [README.md FAQ](README.md#-faq--troubleshooting)
2. Review [examples/](examples/) for usage patterns
3. Check test files for expected behavior
4. Review [PROJECT_REQUIREMENTS_AND_ARCHITECTURE.md](PROJECT_REQUIREMENTS_AND_ARCHITECTURE.md) for design details

---

## 🎯 Project Status

**Status:** ✅ COMPLETED  
**Date:** January 29, 2026  
**Version:** 1.0  
**Tests:** 295/295 passing ✅  
**Documentation:** Complete ✅  
**Production Ready:** Yes ✅

---

*Quick tip: Use Ctrl+F (Cmd+F on Mac) to search this index for specific topics!*

