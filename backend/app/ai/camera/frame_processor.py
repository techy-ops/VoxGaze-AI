import numpy as np
from typing import Tuple, Dict, Any, Optional
from app.ai.common.image_utils import bytes_to_numpy, to_rgb, resize_image, crop_roi, encode_image_bytes
from app.utils.logger import logger

SUPPORTED_IMAGE_FORMATS = {"jpeg", "jpg", "png", "webp", "bmp"}
SUPPORTED_VIDEO_FORMATS = {"mp4", "webm", "avi", "mov"}


class FrameProcessor:
    """
    Production-grade frame processor for validating, resizing, normalizing,
    and transforming incoming camera frames and video streams.
    """

    def validate_image_payload(self, image_bytes: bytes, filename: Optional[str] = None) -> bool:
        """
        Validate incoming image file bytes and format extension.
        """
        if not image_bytes or len(image_bytes) == 0:
            raise ValueError("Empty image payload received.")

        if filename:
            ext = filename.split(".")[-1].lower() if "." in filename else ""
            if ext and ext not in SUPPORTED_IMAGE_FORMATS and ext not in SUPPORTED_VIDEO_FORMATS:
                logger.warning(f"Unsupported payload format extension: {ext}")

        return True

    def process_frame(
        self,
        image_bytes: bytes,
        target_size: Optional[Tuple[int, int]] = (640, 480),
        normalize: bool = False,
    ) -> Dict[str, Any]:
        """
        Full pipeline: Decode bytes -> Validate -> Convert RGB -> Resize -> Optional Normalize.
        Returns dictionary containing BGR array, RGB array, metadata, and normalized float array.
        """
        self.validate_image_payload(image_bytes)
        bgr_arr = bytes_to_numpy(image_bytes)
        orig_h, orig_w = bgr_arr.shape[:2]

        if target_size and (orig_w != target_size[0] or orig_h != target_size[1]):
            resized_bgr = resize_image(bgr_arr, target_size)
        else:
            resized_bgr = bgr_arr

        rgb_arr = to_rgb(resized_bgr)
        h, w = resized_bgr.shape[:2]

        normalized_arr = None
        if normalize:
            normalized_arr = rgb_arr.astype(np.float32) / 255.0

        return {
            "bgr_image": resized_bgr,
            "rgb_image": rgb_arr,
            "normalized_image": normalized_arr,
            "original_size": (orig_w, orig_h),
            "processed_size": (w, h),
            "channels": 3 if len(resized_bgr.shape) == 3 else 1,
        }

    def crop_region_of_interest(self, image_arr: np.ndarray, bbox: Tuple[int, int, int, int]) -> np.ndarray:
        """
        Crop bounding box Region of Interest (x, y, width, height) from image array.
        """
        x, y, w, h = bbox
        return crop_roi(image_arr, x, y, w, h)


frame_processor = FrameProcessor()
