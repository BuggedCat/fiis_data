from datetime import datetime

import requests
from scrap import iterate_api_pages

from src.database.models import fetch_last_document_date, upsert_fnet_documento
from src.database.utils import create_db_connection, get_db_engine
from src.settings import configure_logger

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
COMMIT_THRESHOLD = 500

logging = configure_logger(name="fnet_documentos")

engine = get_db_engine()


def fetch_and_store_documents(session, db_session):
    """Fetch documents from API and store them in the database."""
    start_date = fetch_last_document_date(db_session)
    end_date = datetime.today()

    pages_generator = iterate_api_pages(session, start_date=start_date, end_date=end_date)
    for index, document in enumerate(pages_generator, 1):
        upsert_fnet_documento(db_session, document)

        if index % COMMIT_THRESHOLD == 0:
            logging.info(f"Committing after processing {index} documents.")
            db_session.commit()

    logging.info("Final commit after processing all documents.")
    db_session.commit()


if __name__ == "__main__":
    with requests.Session() as session, create_db_connection(engine) as db_session:
        session.headers.update({"User-Agent": USER_AGENT})

        try:
            fetch_and_store_documents(session, db_session)
        except Exception as e:
            logging.error(f"Error while processing documents: {e}")
