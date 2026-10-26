
import cv2
import numpy as np


class Camera:
    def __init__(self, index=0, width=640, height=480, mirror=True):
        self.index = index
        self.width = width
        self.height = height
        self.mirror = mirror
        self.cap = None

    def open(self):
        self.cap = cv2.VideoCapture(self.index, cv2.CAP_DSHOW)

        if not self.cap.isOpened():
            self.cap.release()
            self.cap = cv2.VideoCapture(self.index)

        if not self.cap.isOpened():
            raise RuntimeError(
                "Kamera tidak dapat dibuka. "
                "Periksa koneksi webcam."
            )

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

        return self

    def read(self):
        if self.cap is None:
            return False, None

        success, frame = self.cap.read()

        if not success:
            return False, None

        if self.mirror:
            frame = cv2.flip(frame, 1)

        return True, frame

    def release(self):
        if self.cap is not None:
            self.cap.release()
            self.cap = None


class HandTracker:
    def __init__(
        self,
        min_area=1500,
        hue_tolerance=10,
        saturation_tolerance=60,
        value_tolerance=65
    ):
        self.min_area = min_area
        self.hue_tolerance = hue_tolerance
        self.saturation_tolerance = saturation_tolerance
        self.value_tolerance = value_tolerance

        self.target_color = None
        self.center = None
        self.bounding_box = None
        self.mask = None

    def calibrate(self, frame, x, y, radius=5):
        height, width = frame.shape[:2]

        if not (0 <= x < width and 0 <= y < height):
            return False

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        x1 = max(0, x - radius)
        x2 = min(width, x + radius + 1)
        y1 = max(0, y - radius)
        y2 = min(height, y + radius + 1)

        patch = hsv[y1:y2, x1:x2]

        if patch.size == 0:
            return False

        self.target_color = np.median(
            patch.reshape(-1, 3),
            axis=0
        ).astype(np.uint8)

        self.center = None
        self.bounding_box = None

        return True

    def reset_calibration(self):
        self.target_color = None
        self.center = None
        self.bounding_box = None
        self.mask = None

    def process(self, frame, draw=True):
        output = frame.copy()

        if self.target_color is None:
            if draw:
                cv2.putText(
                    output,
                    "Klik warna target untuk kalibrasi",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.65,
                    (0, 255, 255),
                    2
                )

            self.center = None
            self.bounding_box = None
            self.mask = np.zeros(
                frame.shape[:2],
                dtype=np.uint8
            )

            return output

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        target_h, target_s, target_v = map(
            int, self.target_color
        )

        # Hue OpenCV memiliki rentang 0 sampai 179.
        lower_h = max(0, target_h - self.hue_tolerance)
        upper_h = min(179, target_h + self.hue_tolerance)

        lower_s = max(
            0, target_s - self.saturation_tolerance
        )
        upper_s = min(
            255, target_s + self.saturation_tolerance
        )

        lower_v = max(0, target_v - self.value_tolerance)
        upper_v = min(255, target_v + self.value_tolerance)

        lower = np.array(
            [lower_h, lower_s, lower_v],
            dtype=np.uint8
        )
        upper = np.array(
            [upper_h, upper_s, upper_v],
            dtype=np.uint8
        )

        self.mask = cv2.inRange(hsv, lower, upper)

        kernel = np.ones((5, 5), np.uint8)

        self.mask = cv2.morphologyEx(
            self.mask,
            cv2.MORPH_OPEN,
            kernel
        )

        self.mask = cv2.morphologyEx(
            self.mask,
            cv2.MORPH_CLOSE,
            kernel
        )

        contours, _ = cv2.findContours(
            self.mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        candidates = []

        for contour in contours:
            area = cv2.contourArea(contour)

            if area < self.min_area:
                continue

            x, y, w, h = cv2.boundingRect(contour)

            candidates.append({
                "area": area,
                "box": (x, y, w, h),
                "center": (x + w // 2, y + h // 2)
            })

        selected = None

        if candidates:
            if self.center is None:
                selected = max(
                    candidates,
                    key=lambda item: item["area"]
                )
            else:
                previous_x, previous_y = self.center

                nearby = [
                    item for item in candidates
                    if (
                        (
                            item["center"][0] - previous_x
                        ) ** 2
                        +
                        (
                            item["center"][1] - previous_y
                        ) ** 2
                    ) ** 0.5 < 180
                ]

                if nearby:
                    selected = max(
                        nearby,
                        key=lambda item: item["area"]
                    )

        if selected is not None:
            raw_x, raw_y = selected["center"]

            if self.center is None:
                smooth_x, smooth_y = raw_x, raw_y
            else:
                old_x, old_y = self.center

                smooth_x = int(0.7 * old_x + 0.3 * raw_x)
                smooth_y = int(0.7 * old_y + 0.3 * raw_y)

            self.center = (smooth_x, smooth_y)
            self.bounding_box = selected["box"]

            if draw:
                x, y, w, h = self.bounding_box

                cv2.rectangle(
                    output,
                    (x, y),
                    (x + w, y + h),
                    (0, 255, 0),
                    2
                )

                cv2.circle(
                    output,
                    self.center,
                    7,
                    (0, 0, 255),
                    -1
                )

                cv2.putText(
                    output,
                    "Target terdeteksi",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2
                )
        else:
            self.center = None
            self.bounding_box = None

            if draw:
                cv2.putText(
                    output,
                    "Target tidak terdeteksi",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 0, 255),
                    2
                )

        return output

    def has_hand(self):
        return self.center is not None

    def get_position(self):
        return self.center

    def get_mask(self):
        return self.mask

    def close(self):
        pass
