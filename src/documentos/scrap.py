import math
from datetime import date, datetime
from typing import Generator, Optional

import requests

from src.settings import configure_logger
from src.utils import parse_date_string
from src.validators import APIResponse, FnetDocumento

API_ENDPOINT = "https://fnet.bmfbovespa.com.br/fnet/publico/pesquisarGerenciadorDocumentosDados"
DEFAULT_PAGE_SIZE = 200
FUND_TYPE = 1
DOC_CATEGORY_ID = 14

DateTimeStr = datetime | date
APIQueryParams = dict[str, str | int]

logger = configure_logger("fnet_documentos_api")


def construct_api_query(
    start_date: Optional[DateTimeStr] = None,
    end_date: Optional[DateTimeStr] = None,
    page_number: int = 0,
) -> APIQueryParams:
    """Construct the query parameters for the API request.

    Args:
        start_date (Optional[DateTimeStr]): Start date for the data fetch.
        end_date (Optional[DateTimeStr]): End date for the data fetch.
        page_number (int): Page number for pagination.

    Returns:
        APIQueryParams: A dictionary containing the query parameters for the API request.
    """
    query_params = {
        "d": 0,
        "s": page_number * DEFAULT_PAGE_SIZE,
        "l": DEFAULT_PAGE_SIZE,
        "tipoFundo": FUND_TYPE,
        "idCategoriaDocumento": DOC_CATEGORY_ID,
        "o[0][dataEntrega]": "asc",
    }
    try:
        if start_date:
            query_params["dataInicial"] = parse_date_string(start_date).strftime("%d/%m/%Y")
        if end_date:
            query_params["dataFinal"] = parse_date_string(end_date).strftime("%d/%m/%Y")
    except Exception as e:
        logger.error(f"Error processing date parameters: {e}")

    return query_params


def retrieve_api_data(
    session: requests.Session,
    query_params: APIQueryParams,
) -> dict | None:
    """Fetch data from the API using the provided session and query parameters.

    Args:
        session (requests.Session): The session to use for the API request.
        query_params (APIQueryParams): The query parameters for the API request.

    Returns:
        dict | None: The API response data or None if there was an error.
    """
    try:
        response = session.get(API_ENDPOINT, params=query_params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Failed to fetch data from URL {API_ENDPOINT}. Error: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error during API request: {e}")
        return None


def log_data_fetch_period(start_date: Optional[DateTimeStr], end_date: Optional[DateTimeStr]):
    """Log the date range for data fetching."""
    if start_date and end_date:
        logger.info(
            "Initiating data fetch for the date range: %s to %s.",
            start_date.strftime("%Y-%m-%d %H:%M:%S"),
            end_date.strftime("%Y-%m-%d %H:%M:%S"),
        )
    else:
        logger.info("Initiating data fetch from the beginning of records.")


def fetch_page_data(
    session: requests.Session,
    start_date: Optional[DateTimeStr],
    end_date: Optional[DateTimeStr],
    page_number: int,
) -> dict | None:
    """Fetch data for a specific page."""
    query_params = construct_api_query(start_date, end_date, page_number)
    return retrieve_api_data(session, query_params)


def calculate_total_pages(
    total_records: int,
    page_size: int,
) -> int:
    """Calculate the total number of pages based on total records and page size.

    Args:
        total_records (int): Total number of records from the API.
        page_size (int): Number of items on each page.

    Returns:
        int: Total number of pages.
    """
    try:
        return math.ceil(total_records / page_size)
    except Exception as e:
        logger.error(f"Error calculating total pages: {e}")
        return 0


def iterate_api_pages(
    session: requests.Session,
    start_date: Optional[DateTimeStr] = None,
    end_date: Optional[DateTimeStr] = None,
    items_per_page: int = DEFAULT_PAGE_SIZE,
) -> Generator[FnetDocumento, None, None]:
    """Generator to iterate over API pages and yield documents."""
    log_data_fetch_period(start_date, end_date)

    current_page = 0
    page_data = fetch_page_data(session, start_date, end_date, current_page)

    if not page_data or "recordsTotal" not in page_data:
        logger.error("Invalid or missing data in API response.")
        return

    total_pages = calculate_total_pages(page_data["recordsTotal"], items_per_page)
    logger.info(
        f"Fetching a total of {page_data['recordsTotal']} records across {total_pages} pages."
    )

    try:
        while current_page < total_pages:
            yield from APIResponse.model_validate(page_data).documents
            current_page += 1
            logger.info(f"Processing page {current_page} of {total_pages}")
            page_data = fetch_page_data(session, start_date, end_date, current_page)
    except Exception as e:
        logger.error(f"Error iterating over API pages: {e}")
