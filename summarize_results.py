import logging
import operator
from pathlib import Path
from typing import Dict

from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm

from classify_tweets import RESULTS_LOCATION, simple_emotions, war_emotions
from topics import id_to_topic
from utils.files import get_lines_count, iter_tweet_collections

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(funcName)s - %(message)s ",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

ANALYZED_EMOTIONS = sorted(war_emotions)


def analize_results(file_: Path) -> None:
    lang = file_.name[:2]
    topic_id = int("".join(x for x in file_.name if x.isdigit()))
    topic = id_to_topic("pl", topic_id)

    # logger.info(f"Processing topic '{topic}' from '{lang}'")

    file_scores = []
    with file_.open() as fh:
        for line in fh.readlines():
            # logger.info([score for score in line.split()])
            line_scores = [float(score) for score in line.split()]
            file_scores.append(line_scores)
            # for label, score in zip(ANALYZED_EMOTIONS, scores):
            #     logger.info(f"{100 * score:.4f}\t{label}")

    opinions_number = len(file_scores)
    average_scores: Dict[str, float] = {}
    for i, label in enumerate(ANALYZED_EMOTIONS):
        average_scores[label] = 100 * (
            sum([line_score[i] for line_score in file_scores]) / opinions_number
        )

    strongest_label = max(average_scores.items(), key=operator.itemgetter(1))
    # print(f"Country '{lang}' about topic '{topic}' feels {strongest_label[1]}% '{strongest_label[0]}'")
    print(f"'{topic}' feels {strongest_label[1]:.1f}% '{strongest_label[0]}'")


if __name__ == "__main__":
    with logging_redirect_tqdm(), tqdm(
        total=get_lines_count(RESULTS_LOCATION)
    ) as progress_bar:
        for tweet_collection in iter_tweet_collections(RESULTS_LOCATION, progress_bar):
            # logger.info(f"Analyzing {tweet_collection.name}")
            analize_results(tweet_collection)
