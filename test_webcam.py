
import sys
import time
import cv2

from hand_tracking import Camera, HandTracker


def main():
    use_hand = "--hand" in sys.argv

    cam = Camera(index=1, width=640, height=480)
    tracker = None

    try:
        cam.open()
        print("Webcam berhasil dibuka.")
        print("Tekan 'q' atau ESC untuk keluar.")

        if use_hand:
            tracker = HandTracker(max_hands=1)
            print("Deteksi tangan aktif.")
        else:
            print("Mode webcam saja.")
            print("Gunakan: python test_webcam.py --hand")

        prev_time = time.time()

        while True:
            ok, frame = cam.read()

            if not ok:
                print("Gagal membaca frame dari webcam.")
                break

            status = "Mode webcam saja"

            if tracker is not None:
                frame = tracker.process(frame)

                if tracker.has_hand():
                    landmarks = tracker.get_landmarks(frame.shape)
                    fingers = tracker.fingers_up(landmarks)


                    extended_fingers = sum(fingers[1:])

                    if extended_fingers >= 4:
                        status = "TANGAN TERBUKA"
                    elif extended_fingers == 0:
                        status = "TANGAN MENGEPAL"
                    else:
                        status = f"GESTURE LAIN: {fingers}"

                    cv2.putText(
                        frame,
                        f"Jari: {fingers}",
                        (10, 100),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (255, 255, 0),
                        2
                    )
                else:
                    status = "Tangan tidak terdeteksi"

            now = time.time()
            fps = 1.0 / max(now - prev_time, 1e-6)
            prev_time = now

            cv2.putText(
                frame,
                status,
                (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 255),
                2
            )

            cv2.putText(
                frame,
                f"FPS: {fps:.1f}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )

            cv2.imshow("Tes Webcam dan Gesture", frame)

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q") or key == 27:
                break

    except KeyboardInterrupt:
        print("\nProgram dihentikan oleh pengguna.")

    except Exception as e:
        print(f"Terjadi error: {e}")

    finally:
        if tracker is not None:
            tracker.close()

        cam.release()
        cv2.destroyAllWindows()
        print("Kamera ditutup.")


if __name__ == "__main__":
    main()
