import numpy as np
from PIL import Image

from pyzbar.pyzbar import decode

from warnings import filterwarnings

filterwarnings(action="ignore")


def qr_code_scanner(frame):
    """
    Scan a video frame and return Product ID.

    Expected QR format:
        101-ABC123

    Returned value:
        101
    """

    if frame is None:
        return None

    try:
        # ----------------------------------------------------
        # Make sure the frame is a valid numpy array
        # ----------------------------------------------------
        image = np.asarray(frame)

        if image.size == 0:
            return None

        # ----------------------------------------------------
        # 1. Try original frame
        # ----------------------------------------------------
        decoded_objs = decode(image)

        if decoded_objs:

            for obj in decoded_objs:

                try:
                    scanned_text = obj.data.decode(
                        "utf-8"
                    ).strip()
                except Exception:
                    continue

                p_id = scanned_text.split(
                    "-"
                )[0].strip()

                if p_id:
                    return p_id

        # ----------------------------------------------------
        # 2. Try grayscale image
        # ----------------------------------------------------
        if image.ndim == 3:

            gray = np.mean(
                image,
                axis=2
            ).astype(np.uint8)

            decoded_objs = decode(gray)

            if decoded_objs:

                for obj in decoded_objs:

                    try:
                        scanned_text = obj.data.decode(
                            "utf-8"
                        ).strip()
                    except Exception:
                        continue

                    p_id = scanned_text.split(
                        "-"
                    )[0].strip()

                    if p_id:
                        return p_id

        # ----------------------------------------------------
        # 3. Resize image for small QR codes
        # ----------------------------------------------------
        if image.ndim == 3:

            pil_image = Image.fromarray(
                image
            )

            width, height = pil_image.size

            # Make the image 2x larger
            enlarged = pil_image.resize(
                (
                    width * 2,
                    height * 2
                )
            )

            enlarged_array = np.asarray(
                enlarged
            )

            decoded_objs = decode(
                enlarged_array
            )

            if decoded_objs:

                for obj in decoded_objs:

                    try:
                        scanned_text = obj.data.decode(
                            "utf-8"
                        ).strip()
                    except Exception:
                        continue

                    p_id = scanned_text.split(
                        "-"
                    )[0].strip()

                    if p_id:
                        return p_id

        # ----------------------------------------------------
        # Nothing detected
        # ----------------------------------------------------
        return None

    except Exception as e:

        print(
            "QR scanner error:",
            e
        )

        return None
