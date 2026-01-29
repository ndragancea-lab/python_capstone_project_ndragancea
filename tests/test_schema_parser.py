"""
Tests for schema_parser module
"""

import pytest
from dataforge.schema_parser import SchemaParser, parse_schema


# ================ Timestamp tests ================

@pytest.mark.parametrize("definition,expected_strategy", [
    ("timestamp:", "rand"),
    ("timestamp:rand", "rand"),  # Will ignore "rand" with warning
    ("timestamp:   ", "rand"),  # Whitespace only
])
def test_parse_timestamp_field(definition, expected_strategy):
    """Test parsing timestamp fields"""
    schema = {"created_at": definition}
    parser = SchemaParser(schema)
    parsed = parser.parse()
    
    assert parsed['created_at']['type'] == 'timestamp'
    assert parsed['created_at']['strategy'] == expected_strategy
    assert parsed['created_at']['value'] is None


# ================ String tests ================

def test_parse_str_rand():
    """Test parsing str:rand"""
    schema = {"name": "str:rand"}
    parsed = parse_schema(schema)
    
    assert parsed['name']['type'] == 'str'
    assert parsed['name']['strategy'] == 'rand'
    assert parsed['name']['value'] is None


def test_parse_str_empty():
    """Test parsing str: (empty)"""
    schema = {"description": "str:"}
    parsed = parse_schema(schema)
    
    assert parsed['description']['type'] == 'str'
    assert parsed['description']['strategy'] == 'empty'
    assert parsed['description']['value'] == ''


def test_parse_str_static():
    """Test parsing str:value (static)"""
    schema = {"status": "str:active"}
    parsed = parse_schema(schema)
    
    assert parsed['status']['type'] == 'str'
    assert parsed['status']['strategy'] == 'static'
    assert parsed['status']['value'] == 'active'


@pytest.mark.parametrize("definition,expected_list", [
    ("str:[active,inactive]", ['active', 'inactive']),
    ("str:[pending]", ['pending']),
    ("str:[one,two,three,four]", ['one', 'two', 'three', 'four']),
    ("str:[ with , spaces ]", ['with', 'spaces']),  # Strips whitespace
])
def test_parse_str_list(definition, expected_list):
    """Test parsing str:[list]"""
    schema = {"field": definition}
    parsed = parse_schema(schema)
    
    assert parsed['field']['type'] == 'str'
    assert parsed['field']['strategy'] == 'list'
    assert parsed['field']['value'] == expected_list


# ================ Integer tests ================

def test_parse_int_rand():
    """Test parsing int:rand"""
    schema = {"value": "int:rand"}
    parsed = parse_schema(schema)
    
    assert parsed['value']['type'] == 'int'
    assert parsed['value']['strategy'] == 'rand'
    assert parsed['value']['value'] is None


@pytest.mark.parametrize("definition,expected_min,expected_max", [
    ("int:rand(1,10)", 1, 10),
    ("int:rand(0,100)", 0, 100),
    ("int:rand(-10,10)", -10, 10),
    ("int:rand(-100,-50)", -100, -50),
    ("int:rand(18,65)", 18, 65),
])
def test_parse_int_range(definition, expected_min, expected_max):
    """Test parsing int:rand(min,max)"""
    schema = {"age": definition}
    parsed = parse_schema(schema)
    
    assert parsed['age']['type'] == 'int'
    assert parsed['age']['strategy'] == 'range'
    assert parsed['age']['value'] == (expected_min, expected_max)


@pytest.mark.parametrize("definition,expected_value", [
    ("int:42", 42),
    ("int:0", 0),
    ("int:-5", -5),
    ("int:999", 999),
])
def test_parse_int_static(definition, expected_value):
    """Test parsing int:value (static)"""
    schema = {"count": definition}
    parsed = parse_schema(schema)
    
    assert parsed['count']['type'] == 'int'
    assert parsed['count']['strategy'] == 'static'
    assert parsed['count']['value'] == expected_value


@pytest.mark.parametrize("definition,expected_list", [
    ("int:[1,2,3]", [1, 2, 3]),
    ("int:[10]", [10]),
    ("int:[-5,0,5,10]", [-5, 0, 5, 10]),
    ("int:[100,200,300]", [100, 200, 300]),
])
def test_parse_int_list(definition, expected_list):
    """Test parsing int:[list]"""
    schema = {"priority": definition}
    parsed = parse_schema(schema)
    
    assert parsed['priority']['type'] == 'int'
    assert parsed['priority']['strategy'] == 'list'
    assert parsed['priority']['value'] == expected_list


# ================ Complex schema tests ================

def test_parse_complex_schema():
    """Test parsing a complex schema with multiple field types"""
    schema = {
        "id": "int:rand",
        "timestamp": "timestamp:",
        "name": "str:rand",
        "age": "int:rand(18,65)",
        "status": "str:[active,inactive,pending]",
        "priority": "int:[1,2,3,4,5]",
        "email": "str:test@example.com",
        "count": "int:100"
    }
    
    parsed = parse_schema(schema)
    
    # Check all fields are parsed
    assert len(parsed) == 8
    
    # id: int:rand
    assert parsed['id']['type'] == 'int'
    assert parsed['id']['strategy'] == 'rand'
    
    # timestamp: timestamp:
    assert parsed['timestamp']['type'] == 'timestamp'
    assert parsed['timestamp']['strategy'] == 'rand'
    
    # name: str:rand
    assert parsed['name']['type'] == 'str'
    assert parsed['name']['strategy'] == 'rand'
    
    # age: int:rand(18,65)
    assert parsed['age']['type'] == 'int'
    assert parsed['age']['strategy'] == 'range'
    assert parsed['age']['value'] == (18, 65)
    
    # status: str:[active,inactive,pending]
    assert parsed['status']['type'] == 'str'
    assert parsed['status']['strategy'] == 'list'
    assert parsed['status']['value'] == ['active', 'inactive', 'pending']
    
    # priority: int:[1,2,3,4,5]
    assert parsed['priority']['type'] == 'int'
    assert parsed['priority']['strategy'] == 'list'
    assert parsed['priority']['value'] == [1, 2, 3, 4, 5]
    
    # email: str:test@example.com
    assert parsed['email']['type'] == 'str'
    assert parsed['email']['strategy'] == 'static'
    assert parsed['email']['value'] == 'test@example.com'
    
    # count: int:100
    assert parsed['count']['type'] == 'int'
    assert parsed['count']['strategy'] == 'static'
    assert parsed['count']['value'] == 100


# ================ Error handling tests ================

def test_parse_invalid_type():
    """Test that invalid type raises error"""
    schema = {"field": "invalid_type:value"}
    parser = SchemaParser(schema)
    
    with pytest.raises(SystemExit) as exc_info:
        parser.parse()
    assert exc_info.value.code == 1


def test_parse_missing_colon():
    """Test that missing colon raises error"""
    schema = {"field": "str_rand"}
    parser = SchemaParser(schema)
    
    with pytest.raises(SystemExit) as exc_info:
        parser.parse()
    assert exc_info.value.code == 1


def test_parse_empty_schema():
    """Test that empty schema raises error"""
    schema = {}
    parser = SchemaParser(schema)
    
    with pytest.raises(SystemExit) as exc_info:
        parser.parse()
    assert exc_info.value.code == 1


def test_parse_non_dict_schema():
    """Test that non-dict schema raises error"""
    parser = SchemaParser("not a dict")
    
    with pytest.raises(SystemExit) as exc_info:
        parser.parse()
    assert exc_info.value.code == 1


def test_parse_non_string_definition():
    """Test that non-string field definition raises error"""
    schema = {"field": 123}
    parser = SchemaParser(schema)
    
    with pytest.raises(SystemExit) as exc_info:
        parser.parse()
    assert exc_info.value.code == 1


def test_parse_int_empty_value():
    """Test that int with empty value raises error"""
    schema = {"count": "int:"}
    parser = SchemaParser(schema)
    
    with pytest.raises(SystemExit) as exc_info:
        parser.parse()
    assert exc_info.value.code == 1


def test_parse_int_invalid_static_value():
    """Test that int with invalid static value raises error"""
    schema = {"count": "int:not_a_number"}
    parser = SchemaParser(schema)
    
    with pytest.raises(SystemExit) as exc_info:
        parser.parse()
    assert exc_info.value.code == 1


def test_parse_int_list_with_non_integers():
    """Test that int list with non-integers raises error"""
    schema = {"priority": "int:[1,two,3]"}
    parser = SchemaParser(schema)
    
    with pytest.raises(SystemExit) as exc_info:
        parser.parse()
    assert exc_info.value.code == 1


def test_parse_int_range_invalid_order():
    """Test that int range with min >= max raises error"""
    schema = {"age": "int:rand(65,18)"}  # min > max
    parser = SchemaParser(schema)
    
    with pytest.raises(SystemExit) as exc_info:
        parser.parse()
    assert exc_info.value.code == 1


def test_parse_int_range_equal_values():
    """Test that int range with min == max raises error"""
    schema = {"value": "int:rand(50,50)"}  # min == max
    parser = SchemaParser(schema)
    
    with pytest.raises(SystemExit) as exc_info:
        parser.parse()
    assert exc_info.value.code == 1


def test_parse_empty_list():
    """Test that empty list raises error"""
    schema = {"field": "str:[]"}
    parser = SchemaParser(schema)
    
    with pytest.raises(SystemExit) as exc_info:
        parser.parse()
    assert exc_info.value.code == 1


def test_parse_list_with_only_spaces():
    """Test that list with only spaces raises error"""
    schema = {"field": "str:[  ,  ,  ]"}
    parser = SchemaParser(schema)
    
    with pytest.raises(SystemExit) as exc_info:
        parser.parse()
    assert exc_info.value.code == 1


# ================ Edge cases tests ================

def test_parse_str_with_special_characters():
    """Test parsing static string with special characters"""
    schema = {"message": "str:Hello, World! @#$%"}
    parsed = parse_schema(schema)
    
    assert parsed['message']['type'] == 'str'
    assert parsed['message']['strategy'] == 'static'
    assert parsed['message']['value'] == 'Hello, World! @#$%'


def test_parse_str_with_colon():
    """Test parsing static string with colon (takes only first colon)"""
    schema = {"url": "str:http://example.com"}
    parsed = parse_schema(schema)
    
    assert parsed['url']['type'] == 'str'
    assert parsed['url']['strategy'] == 'static'
    assert parsed['url']['value'] == 'http://example.com'


def test_parse_int_large_range():
    """Test parsing int with large range"""
    schema = {"value": "int:rand(0,1000000)"}
    parsed = parse_schema(schema)
    
    assert parsed['value']['type'] == 'int'
    assert parsed['value']['strategy'] == 'range'
    assert parsed['value']['value'] == (0, 1000000)


def test_parse_multiple_fields_with_errors():
    """Test that error in one field stops parsing"""
    schema = {
        "valid_field": "str:rand",
        "invalid_field": "invalid_type:value"
    }
    parser = SchemaParser(schema)
    
    # Should fail on invalid field
    with pytest.raises(SystemExit):
        parser.parse()


# ================ SchemaParser class methods tests ================

def test_split_type_value():
    """Test _split_type_value method"""
    parser = SchemaParser({})
    
    # Normal case
    data_type, value = parser._split_type_value("field", "str:rand")
    assert data_type == "str"
    assert value == "rand"
    
    # Empty value
    data_type, value = parser._split_type_value("field", "timestamp:")
    assert data_type == "timestamp"
    assert value == ""
    
    # Multiple colons
    data_type, value = parser._split_type_value("field", "str:http://example.com")
    assert data_type == "str"
    assert value == "http://example.com"


def test_validate_type_valid():
    """Test _validate_type with valid types"""
    parser = SchemaParser({})
    
    # Should not raise
    parser._validate_type("field", "timestamp")
    parser._validate_type("field", "str")
    parser._validate_type("field", "int")


def test_validate_type_invalid():
    """Test _validate_type with invalid type"""
    parser = SchemaParser({})
    
    with pytest.raises(SystemExit) as exc_info:
        parser._validate_type("field", "invalid")
    assert exc_info.value.code == 1


def test_parse_list_method():
    """Test _parse_list method"""
    parser = SchemaParser({})
    
    # Normal list
    values = parser._parse_list("field", "[one,two,three]")
    assert values == ['one', 'two', 'three']
    
    # With spaces
    values = parser._parse_list("field", "[ one , two , three ]")
    assert values == ['one', 'two', 'three']
    
    # Single value
    values = parser._parse_list("field", "[single]")
    assert values == ['single']


# ================ Integration tests ================

def test_parse_schema_function():
    """Test parse_schema convenience function"""
    schema = {
        "id": "int:rand",
        "name": "str:rand",
        "timestamp": "timestamp:"
    }
    
    parsed = parse_schema(schema)
    
    assert len(parsed) == 3
    assert 'id' in parsed
    assert 'name' in parsed
    assert 'timestamp' in parsed


def test_schema_parser_reusable():
    """Test that SchemaParser can be reused"""
    schema1 = {"field1": "str:rand"}
    parser = SchemaParser(schema1)
    parsed1 = parser.parse()
    
    # Create new parser for new schema
    schema2 = {"field2": "int:rand"}
    parser2 = SchemaParser(schema2)
    parsed2 = parser2.parse()
    
    assert 'field1' in parsed1
    assert 'field2' in parsed2
    assert 'field1' not in parsed2
    assert 'field2' not in parsed1

