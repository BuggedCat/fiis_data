import re
from datetime import date, datetime
from xml.etree import ElementTree as ET
from xml.etree.cElementTree import Element


def find_xml_tag(search_element: Element | None, target_tag: str) -> Element:
    """
    Find a specific XML tag within an XML element.

    Args:
        search_element (Element | None): The XML element to search within.
        target_tag (str): The tag name to search for.

    Returns:
        Element: The found XML element.

    Raises:
        TypeError: If search_element is None.
        KeyError: If target_tag is not found.

    Examples:
        >>> xml_string = "<parent><child>Text</child></parent>"
        >>> search_element = ET.fromstring(xml_string)
        >>> find_xml_tag(search_element, 'child').tag
        'child'

        >>> find_xml_tag(None, 'child')
        TypeError: Element can't be None

        >>> find_xml_tag(search_element, 'not_found')
        KeyError: Tag not found in element: not_found
    """
    if not search_element:
        raise TypeError("Element can't be None")

    found_element = search_element.find(target_tag)

    if not isinstance(found_element, Element):
        raise KeyError(f"Tag not found in element: {target_tag}")

    return found_element


def extract_text_from_xml_tag(search_element: Element, target_tag: str) -> str:
    """
    Extract the text content from a specified tag within an XML element.

    Args:
        search_element (Element): The XML element in which to search for the target tag.
        target_tag (str): The tag name to search for within the XML element.

    Returns:
        str: The text content of the found XML tag.

    Raises:
        ValueError: If there is no text content for the target tag.
    """
    text_content = search_element.findtext(target_tag)

    if not text_content:
        raise ValueError(f"No text for tag: {target_tag}")

    return text_content


def convert_xml_element_to_dict(xml_element: ET.Element) -> dict[str, str]:
    """
    Convert an XML element to a dictionary.

    Args:
        xml_element (ET.Element): An XML element to be converted.

    Returns:
        dict: Mapping of tag names to text content. Empty if no text or child elements.

    Examples:
        >>> xml_string = "<parent><child1>Text1</child1><child2>Text2</child2></parent>"
        >>> xml_element = ET.fromstring(xml_string)
        >>> convert_xml_element_to_dict(xml_element)
        {'child1': 'Text1', 'child2': 'Text2'}

        >>> xml_string_empty = "<parent><child1></child1></parent>"
        >>> xml_element_empty = ET.fromstring(xml_string_empty)
        >>> convert_xml_element_to_dict(xml_element_empty)
        {}
    """
    tag_text_mapping = {}
    for elem in xml_element.iter():
        if len(elem) == 0:
            text_content = elem.text.strip() if elem.text else None
            if text_content:
                tag_text_mapping[elem.tag] = text_content

    return tag_text_mapping


def parse_date_string(date_string: str | date) -> datetime | date:
    """
    Parse a date string into a datetime object.

    Args:
        date_string (str | date): A date string to be parsed.

    Returns:
        datetime: A datetime object representing the parsed date.

    Raises:
        ValueError: If the date string cannot be parsed with any of the specified formats.

    Examples:
        >>> parse_date_string("2023-10-12")
        datetime.datetime(2023, 10, 12, 0, 0)
        >>> parse_date_string("12/10/2023")
        ValueError: Unidentified format: 12/10/2023
    """
    if isinstance(date_string, (date, datetime)):
        return date_string

    possible_formats = [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%d/%m/%Y %H:%M",
    ]
    for date_format in possible_formats:
        try:
            return datetime.strptime(date_string, date_format)
        except ValueError:
            pass
    raise ValueError(
        f"Unidentified format: {date_string}",
    )


def clean_text(text: str) -> str:
    """
    Remove non-alphanumeric characters from a text string.

    Args:
        text (str): The input string that may contain non-alphanumeric characters.

    Returns:
        str: A cleaned string with all non-alphanumeric characters removed.

    Example:
    >>> clean_text("Example: 12.345.678/0001-95")
    'Example12345678000195'
    """
    return re.sub(r"\W+", "", text)
