
import cv2
from hand_tracking import Camera, HandTracker


def main():
    camera = Camera(
        index=0,
        width=640,
        height=480,
        mirror=True
    )

    tracker = HandTracker()
    window_name = "Fruity Catch - Kalibrasi Warna"

    mouse_data = {"frame": None}

    def on_mouse(event, x, y, flags, param):
        if event != cv2.EVENT_LBUTTONDOWN:
            return

        frame = param["frame"]

        if frame is None:
            print("Frame kamera belum tersedia. Coba klik lagi.")
            return

        success = tracker.calibrate(frame, x, y)

        if success:
            color = tracker.target_color
            print(
                "Kalibrasi berhasil! "
                f"HSV = ({int(color[0])}, "
                f"{int(color[1])}, {int(color[2])})"
            )
        else:
            print("Kalibrasi gagal. Coba klik bagian target lagi.")

    try:
        camera.open()

        cv2.namedWindow(window_name)
        cv2.setMouseCallback(
            window_name,
            on_mouse,
            mouse_data
        )

        print("=" * 45)
        print("FRUITY CATCH - TES DETEKSI WARNA")
        print("=" * 45)
        print("1. Klik bagian tengah sarung tangan.")
        print("2. Gerakkan tangan untuk menguji deteksi.")
        print("3. Tekan C untuk menghapus kalibrasi.")
        print("4. Klik target lagi untuk kalibrasi ulang.")
        print("5. Tekan Q atau ESC untuk keluar.")
        print("=" * 45)

        while True:
            success, frame = camera.read()

            if not success:
                print("Gagal membaca frame webcam.")
                break

            mouse_data["frame"] = frame.copy()

            result = tracker.process(frame, draw=True)

            if tracker.target_color is None:
                cv2.putText(
                    result,
                    "Klik warna target untuk kalibrasi",
                    (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    (0, 255, 255),
                    2
                )
            else:
                cv2.putText(
                    result,
                    "Klik target untuk kalibrasi ulang",
                    (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 255),
                    1
                )

            cv2.imshow(window_name, result)

            mask = tracker.get_mask()

            if mask is not None:
                cv2.imshow("Mask Deteksi", mask)

            key = cv2.waitKey(1) & 0xFF

            if key == ord("c"):
                tracker.reset_calibration()
                print(
                    "Kalibrasi dihapus. "
                    "Klik warna target untuk kalibrasi ulang."
                )

            elif key == ord("q") or key == 27:
                break

    except RuntimeError as error:
        print(f"Error kamera: {error}")

    finally:
        camera.release()
        tracker.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
