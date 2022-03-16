import logging
from pathlib import Path

import requests
from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm

from credentials import BEARER_TOKEN
from topics import topics

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(funcName)s - %(message)s ",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

TWEETS_LOCATION = Path("./tweets")
TWEETS_PER_TOPIC = 10


def process_query(query: str, query_id: int, lang: str) -> None:
    response: requests.Response = single_request(query, lang)
    save_response_to_file(response, query_id, lang)


def single_request(query: str, lang: str) -> requests.Response:
    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}",
    }

    params = (
        ("query", f"{query} lang:{lang} -is:retweet"),
        ("max_results", f"{TWEETS_PER_TOPIC}"),
        ("expansions", "geo.place_id"),
        ("tweet.fields", "created_at,text,geo,lang"),
        ("user.fields", "location"),
    )

    logger.info(f"Send request about topic '{topic}' in language {lang}")
    return requests.get(
        "https://api.twitter.com/2/tweets/search/recent", headers=headers, params=params
    )


def save_response_to_file(
    response: requests.Response, topic_id: int, lang: str
) -> None:
    result_file: Path = TWEETS_LOCATION / f"{lang}_{topic_id}.tsv"
    if response.status_code != 200:
        logger.info(response.status_code)
    with result_file.open("a") as f:
        try:
            for data_item in response.json()["data"]:
                f.write(data_item["text"].replace("\n", " ") + "\n")
        except:
            logger.warning(f"Couldnt save response for {lang}_{topic_id}")


if __name__ == "__main__":
    with logging_redirect_tqdm(), tqdm(
        total=sum([len(lang_topics) for lang_topics in topics.values()])
    ) as progress_bar:
        for lang in topics:
            for id_, topic in enumerate(topics[lang]):
                process_query(topic, id_, lang)
                progress_bar.update()
