import random

from concurrent.futures import (
    ThreadPoolExecutor
)

from online_source import (
    get_random_video_pool,
    download_video
)

from Player import (
    play_video,
    enter_video_screen,
    leave_video_screen
)


VIDEO_DURATION = 20

# Empty string means general Pixabay video search.
SEARCH_QUERY = ""

# Number of unique videos selected each cycle.
POOL_SIZE = 20

# Number of videos to download simultaneously.
PREFETCH_COUNT = 3


def prepare_video(video):
    """
    Downloads one video and returns both
    its local path and metadata.
    """

    path = download_video(video)

    return path, video


def run_video_cycle():
    """
    Creates a fresh randomized pool of videos
    and plays every one once.
    """
    videos = get_random_video_pool(
        count=POOL_SIZE,
        query=SEARCH_QUERY
    )

    random.shuffle(videos)

    # Thread pool handles background downloading

    with ThreadPoolExecutor(
        max_workers=PREFETCH_COUNT
    ) as executor:

        pending = []

        video_iterator = iter(videos)

        # Initially queue several downloads

        for _ in range(PREFETCH_COUNT):

            try:
                video = next(video_iterator)

            except StopIteration:
                break

            future = executor.submit(
                prepare_video,
                video
            )

            pending.append(future)

        # Play videos while downloads continue

        while pending:

            # First queued video should already
            # be downloading in the background.
            current_future = pending.pop(0)

            try:

                path, information = (
                    current_future.result()
                )

            except Exception:
                # Failed download.
                # Skip it instead of stopping
                # the entire player.
                continue

            # Start another download BEFORE
            # playing this video.

            try:

                next_video = next(
                    video_iterator
                )

                future = executor.submit(
                    prepare_video,
                    next_video
                )

                pending.append(
                    future
                )

            except StopIteration:
                pass

            # Play current video for 20 seconds

            play_video(
                path,
                duration=VIDEO_DURATION
            )


def main():

    # Enter a dedicated video display area.
    #
    # This is what should solve the terminal
    # stacking problem.
    enter_video_screen()

    try:

        while True:

            # Every cycle creates a new random
            # set of 20 videos.
            run_video_cycle()

    except KeyboardInterrupt:
        pass

    finally:

        # Always restore the user's normal
        # terminal, even after Ctrl+C.
        leave_video_screen()

        print(
            "ASCII video player stopped."
        )


if __name__ == "__main__":
    main()