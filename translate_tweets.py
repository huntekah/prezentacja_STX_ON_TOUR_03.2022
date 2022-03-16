from transformers import pipeline
from pathlib import Path
from typing import Tuple
from get_tweets import TWEETS_LOCATION

model_checkpoints = {
    "ru_en": "Helsinki-NLP/opus-mt-ru-en",
    "pl_en": "Helsinki-NLP/opus-mt-pl-en",
    "uk_en": "Helsinki-NLP/opus-mt-uk-en",
}


def iter_tweet_collections(location: Path) -> Tuple[str, Path]:
    for lang in ("ru", "pl", "uk"):
        for tweet_collection in TWEETS_LOCATION.glob(f"{lang}_*.tsv"):
            yield lang, tweet_collection


def translate_file(lang: str, file_: Path) -> None:
    with file_.open() as fh:
        while line := fh.readline():
            print(file_.name, line)


if __name__ == "__main__":
    for lang, tweet_collection in iter_tweet_collections(TWEETS_LOCATION):
        translate_file(lang, tweet_collection)
        # print(tweets_topic_collection)
        # print(type(tweets_topic_collection))
        # print(dir(tweets_topic_collection))
        # exit()
