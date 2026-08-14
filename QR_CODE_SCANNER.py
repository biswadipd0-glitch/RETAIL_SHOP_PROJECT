import cv2


def qr_code_scanner():
    """
    Opens a separate OpenCV camera window.
    Scans one QR code and returns its decoded value.
    """

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        raise Exception("Cannot open camera.")

    detector = cv2.QRCodeDetector()

    scanned_value = None

    print("Camera started. Show the QR code to the camera.")
    print("Press Q to cancel scanning.")

    while True:
        ret, frame = camera.read()

        if not ret:
            continue

        # Try to detect and decode QR
        data, points, _ = detector.detectAndDecode(frame)

        # Draw rectangle around detected QR
        if points is not None:
            points = points.astype(int)

            for i in range(len(points[0])):
                pt1 = tuple(points[0][i])
                pt2 = tuple(points[0][(i + 1) % len(points[0])])

                cv2.line(
                    frame,
                    pt1,
                    pt2,
                    (0, 255, 0),
                    3
                )

        # Display instruction
        cv2.putText(
            frame,
            "Show QR Code | Press Q to Cancel",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )

        # If QR detected
        if data:
            scanned_value = data.strip()

            cv2.putText(
                frame,
                f"Scanned: {scanned_value}",
                (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )

            cv2.imshow("QR Scanner", frame)

            # Give user a moment to see successful scan
            cv2.waitKey(800)

            break

        cv2.imshow("QR Scanner", frame)

        # Press Q to cancel
        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break

    camera.release()
    cv2.destroyAllWindows()

    # Make absolutely sure window closes
    for _ in range(5):
        cv2.waitKey(1)

    return scanned_value
