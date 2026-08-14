import streamlit as st
import cv2
import numpy as np
from camera_input_live import camera_input_live


def qr_code_scanner():

    st.write("### 📷 Scan Product QR Code")
    st.info("Allow camera permission and show the QR code to the camera.")

    # Browser-based live camera
    image = camera_input_live()

    if image is None:
        return None

    try:

        # Get image bytes
        image_bytes = image.getvalue()

        # Convert bytes to NumPy array
        image_array = np.frombuffer(
            image_bytes,
            np.uint8
        )

        # Convert to OpenCV image
        frame = cv2.imdecode(
            image_array,
            cv2.IMREAD_COLOR
        )

        if frame is None:
            return None

        # QR detector
        detector = cv2.QRCodeDetector()

        # Detect and decode QR
        data, points, _ = detector.detectAndDecode(frame)

        if data:

            scanned_value = data.strip()

            st.success(
                f"✅ QR Code Detected: {scanned_value}"
            )

            return scanned_value

        st.warning(
            "🔍 QR code not detected. "
            "Please keep the QR code inside the camera view."
        )

        return None

    except Exception as e:

        st.error(
            f"QR scanning error: {e}"
        )

        return None
