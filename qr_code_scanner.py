from pyzbar.pyzbar import decode

from warnings import filterwarnings

filterwarnings(action="ignore")


def qr_code_scanner(frame):

    try:

        decoded_objs = decode(frame)

    except Exception as e:

        print(
            "Error decoding QR code:",
            e
        )

        return None

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

    return None