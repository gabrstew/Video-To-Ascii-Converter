import os
import random

from pathlib import Path

import requests
from dotenv import load_dotenv


load_dotenv()

API_KEY = os.getenv("PIXABAY_API_KEY")

API_URL = "https://pixabay.com/api/videos/"

CACHE_DIRECTORY = Path("cache")

CACHE_DIRECTORY.mkdir(
    exist_ok=True
)


def search_videos(
    query="",
    page=1,
    per_page=20,
    order="popular"
):

    if not API_KEY:
        raise RuntimeError(
            "PIXABAY_API_KEY was not found."
        )

    parameters = {
        "key": API_KEY,
        "safesearch": "true",
        "page": page,
        "per_page": per_page,
        "order": order
    }

    # An empty query means:
    # search Pixabay videos generally.
    if query:
        parameters["q"] = query

    response = requests.get(
        API_URL,
        params=parameters,
        timeout=15
    )

    response.raise_for_status()

    return response.json()


def choose_random_video(data):

    videos = data["hits"]

    if not videos:
        raise RuntimeError(
            "No videos were found."
        )

    return random.choice(videos)


def download_video(video):

    video_id = video["id"]

    video_url = (
        video["videos"]["tiny"]["url"]
    )

    destination = (
        CACHE_DIRECTORY
        / f"pixabay_{video_id}.mp4"
    )

    if destination.exists():
        return destination

    response = requests.get(
        video_url,
        stream=True,
        timeout=60
    )

    response.raise_for_status()

    with destination.open("wb") as file:

        for chunk in response.iter_content(
            chunk_size=8192
        ):

            file.write(chunk)

    return destination


def get_random_video_pool(
    count=20,
    query=""
):

    if count < 1:
        raise ValueError(
            "count must be at least 1"
        )

    # First request:
    # discover how many results are accessible

    first_page = search_videos(
        query=query,
        page=1,
        per_page=20
    )

    total_hits = first_page["totalHits"]

    if total_hits == 0:
        raise RuntimeError(
            "Pixabay returned no videos."
        )

    # Pixabay normally exposes at most 500
    # results for one query.
    accessible_results = min(
        total_hits,
        500
    )

    # We'll use 20 results per page.
    per_page = 20

    total_pages = (
        accessible_results
        + per_page
        - 1
    ) // per_page

    selected = {}

    # Include the first page we already downloaded
    # rather than wasting that API request.
    pages_cache = {
        1: first_page["hits"]
    }

    # Randomly sample pages until we have enough
    # unique video IDs.

    while (
        len(selected) < count
        and len(selected) < accessible_results
    ):

        random_page = random.randint(
            1,
            total_pages
        )

        if random_page not in pages_cache:

            # Randomly use popular/latest as another
            # small source of variation.
            order = random.choice(
                ["popular", "latest"]
            )

            data = search_videos(
                query=query,
                page=random_page,
                per_page=per_page,
                order=order
            )

            pages_cache[random_page] = (
                data["hits"]
            )

        page_videos = pages_cache[
            random_page
        ]

        if not page_videos:
            continue

        video = random.choice(
            page_videos
        )

        # Dictionary keyed by ID automatically
        # prevents duplicates.
        selected[video["id"]] = video

    videos = list(
        selected.values()
    )

    random.shuffle(videos)

    return videos