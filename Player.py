import cv2
import sys
import time

from colorama import just_fix_windows_console
from renderer import frame_to_ascii


# Makes ANSI terminal commands work properly
# in the Windows console / VS Code terminal.
just_fix_windows_console()


def write_terminal(text):
    """
    Writes text directly to the terminal and
    immediately flushes the output buffer.
    """
    sys.stdout.write(text)
    sys.stdout.flush()


def enter_video_screen():
    """
    Switches to the terminal's alternate screen.

    This is useful for programs such as video players
    because the frames do not fill normal terminal
    scrollback.
    """

    # Enter alternate screen buffer
    write_terminal("\033[?1049h")

    # Hide cursor
    write_terminal("\033[?25l")

    # Clear screen and move to upper-left
    write_terminal("\033[2J\033[H")


def leave_video_screen():
    """
    Restores the user's normal terminal.
    """

    # Show cursor again
    write_terminal("\033[?25h")

    # Leave alternate screen
    write_terminal("\033[?1049l")


def clear_frame():
    """
    Completely clears the current video screen.
    """

    write_terminal("\033[2J\033[H")


def draw_frame(ascii_frame):
    """
    Replaces the current ASCII image with the new one.
    """

    # Home position
    write_terminal("\033[H")

    # Draw frame
    write_terminal(ascii_frame)

    # Erase anything remaining from the previous frame
    write_terminal("\033[J")


def play_video(video_path, duration=20):
    """
    Plays a video as ASCII for exactly `duration`
    real-world seconds.

    If the video is shorter than the requested duration,
    it loops until the duration expires.
    """

    video = cv2.VideoCapture(str(video_path))

    if not video.isOpened():
        raise RuntimeError(
            f"Could not open video: {video_path}"
        )

    fps = video.get(cv2.CAP_PROP_FPS)

    if fps <= 0:
        fps = 24

    frame_duration = 1 / fps

    playback_start = time.perf_counter()

    try:

        # Remove anything left over from the previous video
        clear_frame()

        while True:

            # Check the 20-second video slot

            total_elapsed = (
                time.perf_counter()
                - playback_start
            )

            if total_elapsed >= duration:
                break

            frame_start = time.perf_counter()

            # Read next video frame

            success, frame = video.read()

            # Video ended naturally.
            # Rewind instead of ending playback.
            if not success:

                video.set(
                    cv2.CAP_PROP_POS_FRAMES,
                    0
                )

                continue

            # Video frame -> ASCII

            ascii_frame = frame_to_ascii(frame)

            # Replace previous frame

            draw_frame(ascii_frame)

            # Maintain correct timing

            processing_time = (
                time.perf_counter()
                - frame_start
            )

            sleep_time = (
                frame_duration
                - processing_time
            )

            if sleep_time > 0:
                time.sleep(sleep_time)

    finally:

        video.release()

        # Completely remove the previous video before
        # another one is displayed.
        clear_frame()