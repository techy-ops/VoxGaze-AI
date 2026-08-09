import numpy as np
from typing import Tuple
from app.ai.camera.frame_processor import frame_processor


def prepare_input_tensor(image_rgb: np.ndarray, target_size: Tuple[int, int] = (224, 224)) -> np.ndarray:
    """
    Prepare standard NCHW normalized PyTorch / ONNX input tensor array from RGB image array.
    """
    processed = frame_processor.process_frame(
        image_bytes=image_rgb.tobytes() if isinstance(image_rgb, np.ndarray) else image_rgb,
        target_size=target_size,
        normalize=True,
    )
    norm_arr = processed["normalized_image"]
    if norm_arr is None:
        norm_arr = image_rgb.astype(np.float32) / 255.0

    # HWC -> CHW -> NCHW
    chw_arr = np.transpose(norm_arr, (2, 0, 1))
    nchw_tensor = np.expand_dims(chw_arr, axis=0)
    return nchw_tensor
