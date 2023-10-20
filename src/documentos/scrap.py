import logging
import math
from datetime import date, datetime
from typing import Generator

import requests

from src.models import APIResponse
from src.utils import parse_date_string

BASE_URL = "https://fnet.bmfbovespa.com.br/fnet/publico/pesquisarGerenciadorDocumentosDados"
DEFAULT_LIMIT = 200
TIPO_FUNDO = 1
ID_CATEGORIA_DOCUMENTO = 14

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - [%(funcName)s] - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)

StrDatetime = str | datetime | date
UrlParams = dict[str, str | int]


def get_query_params(
    start_date: StrDatetime | None,
    end_date: StrDatetime | None,
    page: int = 0,
) -> UrlParams:
    params = {
        "d": 0,
        "s": page * DEFAULT_LIMIT,
        "l": DEFAULT_LIMIT,
        "tipoFundo": TIPO_FUNDO,
        "idCategoriaDocumento": ID_CATEGORIA_DOCUMENTO,
        "o[0][dataEntrega]": "desc",
    }

    if start_date:
        params["dataInicial"] = parse_date_string(start_date).strftime("%d/%m/%Y")
    if end_date:
        params["dataFinal"] = parse_date_string(end_date).strftime("%d/%m/%Y")

    return params


def fetch_data_from_api(
    session: requests.Session,
    params: UrlParams,
) -> dict | None:
    try:
        response = session.get(BASE_URL, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Failed to fetch data. Error: {e}")
        return None


def generate_api_pages(
    session: requests.Session,
    start_date: StrDatetime | None = None,
    end_date: StrDatetime | None = None,
    items_per_page: int = DEFAULT_LIMIT,
) -> Generator[APIResponse, None, None]:
    page_number = 0
    data = fetch_data_from_api(session, get_query_params(start_date, end_date, page_number))

    if not data:
        return

    total_num_pages = total_pages(data["recordsTotal"], items_per_page)
    while page_number < total_num_pages:
        yield APIResponse.model_validate(data)
        page_number += 1
        data = fetch_data_from_api(session, get_query_params(start_date, end_date, page_number))


def total_pages(
    total_records: int,
    items_per_page: int,
) -> int:
    """
    Calculates the total number of pages based on the API response.

    Args:
        data (dict): The API response data.
        items_per_page (int): The number of items per page.

    Returns:
        int: The total number of pages.
    """
    return math.ceil(total_records / items_per_page)
