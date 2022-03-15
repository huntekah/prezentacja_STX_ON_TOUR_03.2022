import os
import requests
from credentials import BEARER_TOKEN
from topics import topics
from tqdm import tqdm
from pathlib import Path
import logging

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(funcName)s - %(message)s ",
    datefmt="%H:%M:%S",
    level=logging.INFO,
)
TWEETS_LOCATION = Path("./tweets")


def process_query(query: str, query_id: int, lang: str) -> None:
    response = single_request(query, lang)
    save_response_to_file(response, query_id, lang)


def single_request(query: str, lang: str) -> requests.Response:
    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}",
    }

    params = (
        ("query", f"{query} lang:{lang}"),
        ("max_results", "100"),
        ("expansions", "geo.place_id"),
        ("tweet.fields", "created_at,text,geo,lang"),
        ("user.fields", "location"),
    )

    logging.info(f"Send request about topic '{topic}' in language {lang}")
    return requests.get(
        "https://api.twitter.com/2/tweets/search/recent", headers=headers, params=params
    )


def save_response_to_file(
    response: requests.Response, topic_id: int, lang: str
) -> None:
    result_file = TWEETS_LOCATION / f"{lang}_{topic_id}.tsv"
    if response.status_code != 200:
        logging.info(response.status_code)
    with result_file.open("w") as f:
        try:
            for data_item in response.json()["data"]:
                f.write(data_item["text"].replace("\n", " ") + "\n")
        except:
            logging.warning(f"Couldnt save response for {lang}_{topic_id}")


if __name__ == "__main__":
    with tqdm(
        total=sum([len(lang_topics) for lang_topics in topics.items()])
    ) as progress_bar:
        for lang in topics:
            for id_, topic in enumerate(topics[lang]):
                process_query(topic, id_, lang)
                progress_bar.update()
