import numpy as np
from typing import Dict, Any, Tuple, Optional
from app.ai.common.image_utils import crop_roi, resize_image, to_grayscale
from app.ai.eye_tracking.landmarks import landmark_extractor

# MediaPipe Mouth Landmark Indices (Outer & Inner Lips)
MOUTH_LANDMARKS = [61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291, 375, 321, 405, 314, 17, 84, 181, 91, 146]


class LipDetector:
    """
    Detects and crops mouth Region of Interest (ROI) from image frames for lip reading models.
    """

    def extract_mouth_roi(
        self,
        rgb_image: np.ndarray,
        target_resolution: Tuple[int, int] = (112, 112),
        as_grayscale: bool = True,
    ) -> Dict[str, Any]:
        """
        Detect mouth landmarks, crop ROI with margin, and normalize resolution.
        """
        h, w = rgb_image.shape[:2]
        lm_data = landmark_extractor.process_frame(rgb_image)

        if not lm_data["face_detected"] or not lm_data["raw_landmarks"]:
            # Construct centered default ROI crop if face not detected
            cx, cy = int(w / 2), int(h / 2)
            crop_w, crop_h = int(w * 0.3), int(h * 0.2)
            cropped = crop_roi(rgb_image, cx - crop_w // 2, cy - crop_h // 2, crop_w, crop_h)
            resized = resize_image(cropped, target_resolution)
            if as_grayscale:
                resized = to_grayscale(resized)
            return {
                "mouth_detected": False,
                "mouth_roi": resized,
                "resolution": f"{target_resolution[0]}x{target_resolution[1]}",
                "bbox": [cx - crop_w // 2, cy - crop_h // 2, crop_w, crop_h],
            }

        raw_landmarks = np.array(lm_data["raw_landmarks"])
        mouth_pts = raw_landmarks[MOUTH_LANDMARKS, :2]

        min_x, min_y = np.min(mouth_pts, axis=0)
        max_x, max_y = np.max(mouth_pts, axis=0)

        box_w = max_x - min_x
        box_h = max_y - min_y

        # Add 20% margin padding around mouth box
        pad_x = int(box_w * 0.25)
        pad_y = int(box_h * 0.35)

        crop_x = int(max(0, min_x - pad_x))
        crop_y = int(max(0, min_y - pad_y))
        crop_w = int(min(w - crop_x, box_w + 2 * pad_x))
        crop_h = int(min(h - crop_y, box_h + 2 * pad_y))

        cropped = crop_roi(rgb_image, crop_x, crop_y, crop_w, crop_h)
        resized = resize_image(cropped, target_resolution)

        if as_grayscale:
            resized = to_grayscale(resized)

        return {
            "mouth_detected": True,
            "mouth_roi": resized,
            "resolution": f"{target_resolution[0]}x{target_resolution[1]}",
            "bbox": [crop_x, crop_y, crop_w, crop_h],
        }


lip_detector = LipDetector()
