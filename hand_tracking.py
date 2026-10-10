import cv2
 
class Camera:
 
    def __init__(self, index=0, width=640, height=480, mirror=True):
        self.index = index
        self.width = width
        self.height = height
        self.mirror = mirror
        self.cap = None
 
    def open(self):
        self.cap = cv2.VideoCapture(self.index, cv2.CAP_DSHOW) if hasattr(cv2, "CAP_DSHOW") else cv2.VideoCapture(self.index)
        if not self.cap.isOpened():
            self.cap.release()
            self.cap = None
            raise RuntimeError(
                f"Webcam dengan index {self.index} tidak bisa dibuka. "
                "Pastikan webcam terhubung dan tidak dipakai aplikasi lain."
            )
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        return self
 
    def read(self):
        if self.cap is None:
            return False, None
        ok, frame = self.cap.read()
        if not ok:
            return False, None
        if self.mirror:
            frame = cv2.flip(frame, 1)
        return True, frame
 
    def release(self):
        if self.cap is not None:
            self.cap.release()
            self.cap = None
 
    def __enter__(self):
        return self.open()
 
    def __exit__(self, exc_type, exc, tb):
        self.release()
 
 
class HandTracker:
    WRIST = 0
    THUMB_TIP = 4
    INDEX_TIP = 8
    MIDDLE_TIP = 12
    RING_TIP = 16
    PINKY_TIP = 20
 
    def __init__(self, max_hands=1, detection_conf=0.7, tracking_conf=0.6):
        try:
            import mediapipe as mp
        except ImportError as e:
            raise ImportError(
                "MediaPipe belum terpasang. Jalankan: pip install mediapipe"
            ) from e
 
        self._mp_hands = mp.solutions.hands
        self._mp_draw = mp.solutions.drawing_utils
        self._hands = self._mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_hands,
            min_detection_confidence=detection_conf,
            min_tracking_confidence=tracking_conf,
        )
        self.results = None
 
    def process(self, frame, draw=True):
        
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        self.results = self._hands.process(rgb)
 
        if draw and self.results.multi_hand_landmarks:
            for hand in self.results.multi_hand_landmarks:
                self._mp_draw.draw_landmarks(frame, hand, self._mp_hands.HAND_CONNECTIONS)
        return frame
 
    def has_hand(self):
        return bool(self.results and self.results.multi_hand_landmarks)
 
    def get_landmarks(self, frame_shape, hand_index=0):
        if not self.has_hand() or hand_index >= len(self.results.multi_hand_landmarks):
            return []
        h, w = frame_shape[:2]
        hand = self.results.multi_hand_landmarks[hand_index]
        return [(i, int(lm.x * w), int(lm.y * h)) for i, lm in enumerate(hand.landmark)]
 
    
def fingers_up(self, landmarks):
    if len(landmarks) < 21:
        return [0, 0, 0, 0]

    pts = {i: (x, y) for i, x, y in landmarks}

    fingers = []

    for tip in (8, 12, 16, 20):
        pip = tip - 2
        fingers.append(
            1 if pts[tip][1] < pts[pip][1] else 0
        )

    return fingers


def is_open_hand(self, landmarks):
    fingers = self.fingers_up(landmarks)
    return sum(fingers) == 4


def is_fist(self, landmarks):
    fingers = self.fingers_up(landmarks)
    return sum(fingers) == 0
    
def close(self):
    self._hands.close()
 