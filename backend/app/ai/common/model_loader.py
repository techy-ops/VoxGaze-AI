import threading
from typing import Dict, Any, Optional
from app.utils.logger import logger

# Import mediapipe safely with fallback handling
try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    mp = None


class ModelLoader:
    """
    Singleton AI Model Loader supporting thread-safe lazy loading for MediaPipe,
    PyTorch, ONNX, and custom ML models.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(ModelLoader, cls).__new__(cls)
                    cls._instance._models: Dict[str, Any] = {}
                    cls._instance._face_mesh = None
                    cls._instance._hands = None
                    cls._instance._face_detection = None
        return cls._instance

    def get_face_mesh(self, max_num_faces: int = 1, min_detection_confidence: float = 0.5, min_tracking_confidence: float = 0.5):
        """
        Get or initialize MediaPipe FaceMesh model.
        """
        if not MEDIAPIPE_AVAILABLE:
            logger.warning("MediaPipe is not installed. FaceMesh lazy load operating in fallback mode.")
            return None

        if self._face_mesh is None:
            with self._lock:
                if self._face_mesh is None:
                    try:
                        logger.info("Initializing MediaPipe FaceMesh model...")
                        mp_face_mesh = mp.solutions.face_mesh
                        self._face_mesh = mp_face_mesh.FaceMesh(
                            max_num_faces=max_num_faces,
                            refine_landmarks=True,
                            min_detection_confidence=min_detection_confidence,
                            min_tracking_confidence=min_tracking_confidence,
                        )
                        logger.info("MediaPipe FaceMesh model loaded successfully.")
                    except Exception as exc:
                        logger.error(f"Failed to load MediaPipe FaceMesh: {str(exc)}")
                        self._face_mesh = None
        return self._face_mesh

    def get_hands(self, max_num_hands: int = 2, min_detection_confidence: float = 0.5, min_tracking_confidence: float = 0.5):
        """
        Get or initialize MediaPipe Hands model.
        """
        if not MEDIAPIPE_AVAILABLE:
            logger.warning("MediaPipe is not installed. Hands lazy load operating in fallback mode.")
            return None

        if self._hands is None:
            with self._lock:
                if self._hands is None:
                    try:
                        logger.info("Initializing MediaPipe Hands model...")
                        mp_hands = mp.solutions.hands
                        self._hands = mp_hands.Hands(
                            max_num_hands=max_num_hands,
                            min_detection_confidence=min_detection_confidence,
                            min_tracking_confidence=min_tracking_confidence,
                        )
                        logger.info("MediaPipe Hands model loaded successfully.")
                    except Exception as exc:
                        logger.error(f"Failed to load MediaPipe Hands: {str(exc)}")
                        self._hands = None
        return self._hands

    def get_face_detection(self, min_detection_confidence: float = 0.5):
        """
        Get or initialize MediaPipe FaceDetection model.
        """
        if not MEDIAPIPE_AVAILABLE:
            logger.warning("MediaPipe is not installed. FaceDetection lazy load operating in fallback mode.")
            return None

        if self._face_detection is None:
            with self._lock:
                if self._face_detection is None:
                    try:
                        logger.info("Initializing MediaPipe FaceDetection model...")
                        mp_face_detection = mp.solutions.face_detection
                        self._face_detection = mp_face_detection.FaceDetection(
                            min_detection_confidence=min_detection_confidence
                        )
                        logger.info("MediaPipe FaceDetection loaded successfully.")
                    except Exception as exc:
                        logger.error(f"Failed to load MediaPipe FaceDetection: {str(exc)}")
                        self._face_detection = None
        return self._face_detection

    def load_onnx_model(self, model_name: str, model_path: str) -> Optional[Any]:
        """
        Lazy load an ONNX model session.
        """
        if model_name in self._models:
            return self._models[model_name]

        with self._lock:
            if model_name not in self._models:
                try:
                    import onnxruntime as ort
                    logger.info(f"Loading ONNX model '{model_name}' from path: {model_path}")
                    session = ort.InferenceSession(model_path)
                    self._models[model_name] = session
                    return session
                except Exception as exc:
                    logger.error(f"Failed to load ONNX model '{model_name}': {str(exc)}")
                    return None
        return self._models.get(model_name)

    def load_pytorch_model(self, model_name: str, model_path: str) -> Optional[Any]:
        """
        Lazy load a PyTorch model.
        """
        if model_name in self._models:
            return self._models[model_name]

        with self._lock:
            if model_name not in self._models:
                try:
                    import torch
                    logger.info(f"Loading PyTorch model '{model_name}' from path: {model_path}")
                    model = torch.load(model_path, map_location=torch.device("cpu"))
                    model.eval()
                    self._models[model_name] = model
                    return model
                except Exception as exc:
                    logger.error(f"Failed to load PyTorch model '{model_name}': {str(exc)}")
                    return None
        return self._models.get(model_name)

    def get_model(self, model_name: str) -> Optional[Any]:
        """
        Get registered model by name.
        """
        return self._models.get(model_name)


model_loader = ModelLoader()
