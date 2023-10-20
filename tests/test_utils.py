from datetime import date, datetime
from xml.etree import ElementTree as ET

import pytest

from src.utils import (
    clean_text,
    convert_xml_element_to_dict,
    extract_text_from_xml_tag,
    find_xml_tag,
    parse_date_string,
)


def test_find_xml_tag():
    xml_string = "<parent><child>Text</child></parent>"
    search_element = ET.fromstring(xml_string)
    found_element = find_xml_tag(search_element, "child")
    assert found_element.tag == "child"

    with pytest.raises(KeyError):
        find_xml_tag(search_element, "not_found")

    with pytest.raises(TypeError):
        find_xml_tag(None, "child")


def test_extract_text_from_xml_tag():
    xml_string = "<parent><child>Text</child></parent>"
    search_element = ET.fromstring(xml_string)
    assert extract_text_from_xml_tag(search_element, "child") == "Text"

    with pytest.raises(ValueError):
        extract_text_from_xml_tag(search_element, "not_found")


def test_convert_xml_element_to_dict():
    xml_string = (
        "<parent><child1>Text1</child1><child2>Text2</child2><child3>Text3</child3></parent>"
    )
    xml_element = ET.fromstring(xml_string)
    assert convert_xml_element_to_dict(xml_element) == {
        "child1": "Text1",
        "child2": "Text2",
        "child3": "Text3",
    }

    xml_string_empty = "<parent><child1></child1></parent>"
    xml_element_empty = ET.fromstring(xml_string_empty)
    assert convert_xml_element_to_dict(xml_element_empty) == {}


@pytest.mark.parametrize(
    "input_value, expected_output",
    [
        ("2023-10-12", datetime(2023, 10, 12)),
        ("12/10/2023", datetime(2023, 10, 12)),
        ("12/10/2023 14:30", datetime(2023, 10, 12, 14, 30)),
        (datetime(2023, 10, 12, 14, 30), datetime(2023, 10, 12, 14, 30)),
        (date(2023, 10, 12), date(2023, 10, 12)),
    ],
)
def test_parse_date_string(input_value, expected_output):
    assert parse_date_string(input_value) == expected_output


def test_parse_invalid_date_string():
    with pytest.raises(ValueError, match="Unidentified format: 2023.10.12"):
        parse_date_string("2023.10.12")


def test_clean_text():
    assert clean_text("Example: 12.345.678/0001-95") == "Example12345678000195"
