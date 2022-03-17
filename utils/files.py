from pathlib import Path
from typing import Tuple

from tqdm import tqdm


def get_lines_count(location: Path) -> int:
    result = 0
    for tweet_collection in location.glob(f"??_*.tsv"):
        result += sum(1 for line in tweet_collection.open())
    return result


def iter_tweet_collections(location: Path, progress_bar: tqdm) -> Tuple[str, Path]:
    for tweet_collection in sorted(location.glob(f"??_*.tsv")):
        progress = sum(1 for line in tweet_collection.open())
        yield tweet_collection
        progress_bar.update(progress)
