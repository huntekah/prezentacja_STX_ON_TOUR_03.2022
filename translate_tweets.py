from transformers import pipeline
from pathlib import Path
from typing import Tuple, Dict, Optional
from get_tweets import TWEETS_LOCATION
from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm
import logging

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(funcName)s - %(message)s ",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

TRANSLATIONS_LOCATION = Path("./translations")
model_checkpoints = {
    "ru_en": "Helsinki-NLP/opus-mt-ru-en",
    "pl_en": "Helsinki-NLP/opus-mt-pl-en",
    "uk_en": "Helsinki-NLP/opus-mt-uk-en",
}

translators: Dict[str, pipeline] = {}


def translate_file(lang: str, file_: Path, progress_bar: Optional[tqdm] = None) -> None:
    translator = get_translator(lang)
    result_file = TRANSLATIONS_LOCATION / file_.name
    with file_.open() as fh, result_file.open("w") as rfh:
        while line := fh.readline():
            translation_raw = translator(line)
            try:
                translation = translation_raw[0]["translation_text"]
            except:
                continue
            if progress_bar:
                progress_bar.update()

            logger.info(
                f"Translated sentence:\n\t{line.strip()}\n\t{translation.strip()}\n\n"
            )
            rfh.write(translation.strip() + "\n")


def get_translator(lang: str) -> pipeline:
    key = f"{lang}_en"
    if translator := translators.get(key):
        return translator
    else:
        translators[key] = pipeline("translation", model=model_checkpoints[key])
        return translators[key]


def get_lines_count(location: Path) -> int:
    result = 0
    for lang in ("ru", "pl", "uk"):
        for tweet_collection in TWEETS_LOCATION.glob(f"{lang}_*.tsv"):
            result += sum(1 for line in tweet_collection.open())
    return result


def iter_tweet_collections(location: Path) -> Tuple[str, Path]:
    for lang in ("ru", "pl", "uk"):
        for tweet_collection in TWEETS_LOCATION.glob(f"{lang}_*.tsv"):
            yield lang, tweet_collection


if __name__ == "__main__":
    with logging_redirect_tqdm(), tqdm(
        total=get_lines_count(TWEETS_LOCATION)
    ) as progress_bar:
        for lang, tweet_collection in iter_tweet_collections(TWEETS_LOCATION):
            logger.info(f"Processing {tweet_collection.name}")
            translate_file(lang, tweet_collection, progress_bar)
