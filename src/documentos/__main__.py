import time

import pandas as pd
import requests
from scrap import generate_api_pages
from tqdm import tqdm

with requests.Session() as session:
    session.headers.update(
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
        }
    )
    total_data = []
    for page_data in tqdm(generate_api_pages(session), total=105):
        total_data.extend(page_data.model_dump(include={"data"})["data"])
        time.sleep(0.2)
    df = pd.DataFrame.from_records(total_data)
    df.to_csv("data/documentos.csv", index=False)
