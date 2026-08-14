import streamlit as st
import cv2
import numpy as np
from camera_input_live import camera_input_live


def qr_code_scanner():

    # --------------------------------------------------------
    # SESSION STATE
    # --------------------------------------------------------

    if "qr_found" not in st.session_state:
        st.session_state.qr_found = False

    if "qr_value" not in st.session_state:
        st.session_state.qr_value = None


    # --------------------------------------------------------
    # IF QR ALREADY FOUND
    # --------------------------------------------------------

    if st.session_state.qr_found:

        return st.session_state.qr_value


    # --------------------------------------------------------
    # CAMERA
    # --------------------------------------------------------

    st.write("### 📷 Scan Product QR Code")

    st.info(
        "Allow camera permission and place the "
        "product QR code inside the camera."
    )


    image = camera_input_live(
        debounce=200,
        show_controls=True
    )


    # --------------------------------------------------------
    # CAMERA IS STARTING
    # --------------------------------------------------------

    if image is None:

        st.info(
            "📷 Starting camera... "
            "Please allow camera access in your browser."
        )

        return None


    # --------------------------------------------------------
    # CONVERT IMAGE TO OPENCV
    # --------------------------------------------------------

    try:

        image_bytes = image.getvalue()

        image_array = np.frombuffer(
            image_bytes,
            np.uint8
        )

        frame = cv2.imdecode(
            image_array,
            cv2.IMREAD_COLOR
        )


        if frame is None:

            st.warning(
                "Unable to read camera image."
            )

            return None


        # ----------------------------------------------------
        # QR CODE DETECTOR
        # ----------------------------------------------------

        detector = cv2.QRCodeDetector()


        data, points, _ = detector.detectAndDecode(
            frame
        )


        # ----------------------------------------------------
        # QR DETECTED
        # ----------------------------------------------------

        if data:

            data = data.strip()


            st.session_state.qr_found = True

            st.session_state.qr_value = data


            st.success(
                f"✅ QR Code Detected: {data}"
            )


            return data


        # ----------------------------------------------------
        # QR NOT DETECTED YET
        # ----------------------------------------------------

        st.info(
            "🔍 Looking for QR code..."
        )

        return None


    except Exception as e:

        st.error(
            f"QR scanner error: {e}"
        )

        return None
