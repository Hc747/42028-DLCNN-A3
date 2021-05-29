from typing import Tuple
from cv2 import FONT_HERSHEY_SIMPLEX

IMAGE_SIZE: int = 224
IMAGE_CHANNELS: int = 3
IMAGE_SHAPE: Tuple[int, int, int] = (IMAGE_SIZE, IMAGE_SIZE, IMAGE_CHANNELS)

COLOUR_RED: Tuple[int, int, int] = (255, 0, 0)
COLOUR_GREEN: Tuple[int, int, int] = (0, 255, 0)
COLOUR_BLUE: Tuple[int, int, int] = (0, 0, 255)
COLOUR_WHITE: Tuple[int, int, int] = (255, 255, 255)
COLOUR_BLACK: Tuple[int, int, int] = (0, 0, 0)

FONT_SCALE: float = 0.4
FONT_FACE: int = FONT_HERSHEY_SIMPLEX
TEXT_OFFSET: int = 10

RANDOM_STATE: int = 694_201_337
VALIDATION_SPLIT: float = 0.2

MASK_DETECTOR_ANDREW: str = 'andrew'
MASK_DETECTOR_ASHISH: str = 'ashish'
MASK_DETECTOR_CABANI: str = 'cabani'
ALL_MASK_DETECTORS = [MASK_DETECTOR_ANDREW, MASK_DETECTOR_ASHISH, MASK_DETECTOR_CABANI]

FACE_DETECTOR_CNN: str = 'cnn'
FACE_DETECTOR_SVM: str = 'svm'
FACE_DETECTOR_MEDIA_PIPE: str = 'mediapipe'
ALL_FACE_DETECTORS = [FACE_DETECTOR_CNN, FACE_DETECTOR_SVM, FACE_DETECTOR_MEDIA_PIPE]

MIN_SCALE: float = 0.1
MAX_SCALE: float = 10.0
