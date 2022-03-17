import logging
from pathlib import Path
from typing import Tuple

import torch
from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm
from transformers import pipeline

from translate_tweets import TRANSLATIONS_LOCATION
from utils.text import line_preprocessing

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(funcName)s - %(message)s ",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


RESULTS_LOCATION = Path("./results_2")
RESULTS_LOCATION.mkdir(parents=True, exist_ok=True)

device = 0 if torch.cuda.is_available() else -1
classifier = pipeline(
    "zero-shot-classification", model="facebook/bart-large-mnli", device=device
)

war_emotions = ["support",
                  "criticicism",
                  "praise",
                  "joy",
                  "euphoria",
                  "integration",
                  "devotion",
                  "sacrifice",
                  "propaganda",
                  "resistance"]
simple_emotions = [
    "anger",
    "brave",
    "fear",
    "greed",
    "help",
    "peace",
    "pride",
    "sadness",
    "stress",
    "trust",
]


# classifier(sequence_to_classify, candidate_labels)

results_to_pickle = {}


def classify_file(file_: Path) -> None:
    lang = file_.name[:2]
    topic = "".join(x for x in file_.name if x.isdigit())

    result_file = RESULTS_LOCATION / file_.name
    with file_.open() as fh, result_file.open("w+") as rfh:
        while line := fh.readline():
            line = line_preprocessing(line)
            logger.debug(f"Processing: '{line}'")
            classification_raw = classifier(line, war_emotions)

            logger.info(f"Classified sentence:\n\t{line}\n\t{classification_raw}\n\n")
            for label, score in sorted(
                zip(classification_raw["labels"], classification_raw["scores"])
            ):
                logger.info(f"\t{label}\t{score}")

            rfh.write(
                "\t".join(
                    [
                        str(score)
                        for _, score in sorted(
                            zip(
                                classification_raw["labels"],
                                classification_raw["scores"],
                            )
                        )
                    ]
                )
                + "\n"
            )


def get_lines_count(location: Path) -> int:
    result = 0
    for tweet_collection in location.glob(f"??_*.tsv"):
        result += sum(1 for line in tweet_collection.open())
    return result


def iter_tweet_collections(location: Path, progress_bar: tqdm) -> Tuple[str, Path]:
    for tweet_collection in location.glob(f"??_*.tsv"):
        progress = sum(1 for line in tweet_collection.open())
        yield tweet_collection
        progress_bar.update(progress)


if __name__ == "__main__":
    with logging_redirect_tqdm(), tqdm(
        total=get_lines_count(TRANSLATIONS_LOCATION)
    ) as progress_bar:
        for tweet_collection in iter_tweet_collections(
            TRANSLATIONS_LOCATION, progress_bar
        ):
            logger.info(f"Processing {tweet_collection.name}")
            classify_file(tweet_collection)
