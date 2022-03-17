import logging
from pathlib import Path

import torch
from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm
from transformers import pipeline

from translate_tweets import TRANSLATIONS_LOCATION
from utils.files import get_lines_count, iter_tweet_collections
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


war_emotions = [
    "criticicism",
    "devotion",
    "euphoria",
    "integration",
    "joy",
    "praise",
    "propaganda",
    "resistance",
    "sacrifice",
    "support",
]

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


results_to_pickle = {}


class NLP_Classifier:
    def __init__(self) -> None:
        self.classifier = pipeline(
            "zero-shot-classification", model="facebook/bart-large-mnli", device=device
        )

    def __call__(self, file_: Path, *args, **kwargs) -> None:
        # lang = file_.name[:2]
        # topic = "".join(x for x in file_.name if x.isdigit())

        result_file = RESULTS_LOCATION / file_.name
        with file_.open() as fh, result_file.open("w+") as rfh:
            while line := fh.readline():
                line = line_preprocessing(line)
                logger.debug(f"Processing: '{line}'")
                classification_raw = self.classifier(line, war_emotions)

                logger.info(
                    f"Classified sentence:\n\t{line}\n\t{classification_raw}\n\n"
                )
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


if __name__ == "__main__":
    tweet_classifier = NLP_Classifier()
    with logging_redirect_tqdm(), tqdm(
        total=get_lines_count(TRANSLATIONS_LOCATION)
    ) as progress_bar:
        for tweet_collection in iter_tweet_collections(
            TRANSLATIONS_LOCATION, progress_bar
        ):
            logger.info(f"Processing {tweet_collection.name}")
            tweet_classifier(tweet_collection)
