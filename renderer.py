import cv2

ASCII_CHARS = "@%#*+=-:. "


def frame_to_ascii(frame, width=100):

    gray = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2GRAY
    )

    original_height, original_width = gray.shape

    aspect_ratio = original_height / original_width

    new_height = int(
        width * aspect_ratio * 0.5
    )

    resized = cv2.resize(
        gray,
        (width, new_height)
    )

    ascii_rows = []

    for row in resized:

        ascii_row = ""

        for pixel in row:

            index = int(
                pixel / 256 * len(ASCII_CHARS)
            )

            ascii_row += ASCII_CHARS[index]

        ascii_rows.append(ascii_row)

    return "\n".join(ascii_rows)