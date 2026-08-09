import io
import numpy as np
from PIL import Image
from typing import Tuple, Optional
from app.utils.logger import logger

try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    cv2 = None


def bytes_to_numpy(image_bytes: bytes) -> np.ndarray:
    """
    Decode raw byte string (JPEG, PNG, etc.) into numpy BGR array.
    """
    if not image_bytes:
        raise ValueError("Provided image_bytes payload is empty.")

    try:
        if OPENCV_AVAILABLE:
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None:
                raise ValueError("Corrupted or unsupported image file payload.")
            return img
        else:
            pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            # Convert RGB PIL image to BGR numpy array
            rgb_arr = np.array(pil_image)
            bgr_arr = rgb_arr[:, :, ::-1].copy()
            return bgr_arr
    except Exception as exc:
        logger.error(f"Image decoding failed: {str(exc)}")
        raise ValueError(f"Failed to decode image: {str(exc)}")


def to_rgb(image_bgr: np.ndarray) -> np.ndarray:
    """
    Convert BGR numpy image array to RGB format.
    """
    if OPENCV_AVAILABLE and len(image_bgr.shape) == 3 and image_bgr.shape[2] == 3:
        return cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    elif len(image_bgr.shape) == 3 and image_bgr.shape[2] == 3:
        return image_bgr[:, :, ::-1]
    return image_bgr


def to_bgr(image_rgb: np.ndarray) -> np.ndarray:
    """
    Convert RGB numpy image array to BGR format.
    """
    if OPENCV_AVAILABLE and len(image_rgb.shape) == 3 and image_rgb.shape[2] == 3:
        return cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
    elif len(image_rgb.shape) == 3 and image_rgb.shape[2] == 3:
        return image_rgb[:, :, ::-1]
    return image_rgb


def to_grayscale(image: np.ndarray) -> np.ndarray:
    """
    Convert RGB/BGR image to single channel grayscale.
    """
    if len(image.shape) == 2:
        return image
    if OPENCV_AVAILABLE:
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        return np.dot(image[..., :3], [0.2989, 0.5870, 0.1140]).astype(np.uint8)


def resize_image(image: np.ndarray, target_size: Tuple[int, int]) -> np.ndarray:
    """
    Resize image array to target (width, height).
    """
    width, height = target_size
    if OPENCV_AVAILABLE:
        return cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)
    else:
        pil_img = Image.fromarray(to_rgb(image))
        resized = pil_img.resize((width, height), Image.Resampling.LANCZOS)
        return to_bgr(np.array(resized))


def crop_roi(image: np.ndarray, x: int, y: int, width: int, height: int) -> np.ndarray:
    """
    Crop bounding box Region of Interest (ROI) from image numpy array safely.
    """
    h, w = image.shape[:2]
    x1 = max(0, min(x, w - 1))
    y1 = max(0, min(y, h - 1))
    x2 = max(x1 + 1, min(x + width, w))
    y2 = max(y1 + 1, min(y + height, h))
    return image[y1:y2, x1:x2]


def encode_image_bytes(image_bgr: np.ndarray, format_ext: str = ".jpg") -> bytes:
    """
    Encode numpy image array into JPEG/PNG bytes payload.
    """
    if OPENCV_AVAILABLE:
        success, buffer = cv2.imencode(format_ext, image_bgr)
        if success:
            return buffer.tobytes()

    pil_img = Image.fromarray(to_rgb(image_bgr))
    buf = io.BytesIO()
    fmt = "JPEG" if format_ext.lower() in [".jpg", ".jpeg"] else "PNG"
    pil_img.save(buf, format=fmt)
    return buf.getvalue()
