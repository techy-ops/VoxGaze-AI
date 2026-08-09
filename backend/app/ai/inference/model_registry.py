import threading
from typing import Dict, Any, List, Optional, Type, Callable, Tuple
from app.ai.inference.base_model import BaseAIModel, BackendType, MockAIModel
from app.utils.logger import logger


class ModelRegistry:
    """
    Thread-safe registry for managing AI model definitions, factory functions, and versions.
    Supports PyTorch, ONNX Runtime, TensorFlow, OpenVINO, and MediaPipe backends.
    """

    def __init__(self):
        self._lock = threading.RLock()
        # Storage schema: key is (model_name, model_version) -> tuple(model_cls_or_factory, default_backend, metadata_dict)
        self._registry: Dict[Tuple[str, str], Dict[str, Any]] = {}
        # Alias for default model version: model_name -> default_version
        self._default_versions: Dict[str, str] = {}
        
        # Pre-register standard built-in models
        self._register_default_models()

    def _register_default_models(self) -> None:
        """
        Pre-registers built-in mock and pipeline model definitions.
        """
        self.register(
            model_cls_or_factory=lambda name, version, **kwargs: MockAIModel(name=name, version=version, **kwargs),
            name="mock_classifier",
            version="1.0.0",
            backend=BackendType.CUSTOM,
            description="Default Mock Classifier for testing and baseline benchmarking",
        )
        self.register(
            model_cls_or_factory=lambda name, version, **kwargs: MockAIModel(name=name, version=version, dummy_confidence=0.98, **kwargs),
            name="eye_gaze_estimator",
            version="1.0.0",
            backend=BackendType.PYTORCH,
            description="PyTorch Eye Gaze Direction & Point-of-Regard Estimator",
        )
        self.register(
            model_cls_or_factory=lambda name, version, **kwargs: MockAIModel(name=name, version=version, dummy_confidence=0.96, **kwargs),
            name="lip_reading_net",
            version="1.0.0",
            backend=BackendType.ONNX,
            description="ONNX Lip Reading Word & Sequence Decoder",
        )
        self.register(
            model_cls_or_factory=lambda name, version, **kwargs: MockAIModel(name=name, version=version, dummy_confidence=0.97, **kwargs),
            name="sign_language_yolo",
            version="1.0.0",
            backend=BackendType.PYTORCH,
            description="Sign Language Gesture and Hand Pose Classifier",
        )

    def register(
        self,
        model_cls_or_factory: Callable[..., BaseAIModel],
        name: str,
        version: str = "1.0.0",
        backend: BackendType = BackendType.CUSTOM,
        description: str = "",
        input_shape: Optional[List[Any]] = None,
        output_shape: Optional[List[Any]] = None,
        extra: Optional[Dict[str, Any]] = None,
        is_default: bool = True,
    ) -> None:
        """
        Register a model factory or class in the global registry.
        """
        with self._lock:
            key = (name, version)
            entry = {
                "factory": model_cls_or_factory,
                "name": name,
                "version": version,
                "backend": backend,
                "description": description,
                "input_shape": input_shape,
                "output_shape": output_shape,
                "extra": extra or {},
            }
            self._registry[key] = entry
            
            if is_default or name not in self._default_versions:
                self._default_versions[name] = version

            logger.info(f"Registered model '{name}:{version}' [Backend: {backend.value}] in ModelRegistry.")

    def get_model_entry(self, name: str, version: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieve model registry entry dictionary.
        """
        with self._lock:
            resolved_version = version or self._default_versions.get(name)
            if not resolved_version:
                raise KeyError(f"Model '{name}' is not registered in ModelRegistry.")

            key = (name, resolved_version)
            if key not in self._registry:
                raise KeyError(f"Model '{name}:{resolved_version}' is not registered in ModelRegistry.")

            return self._registry[key]

    def create_model_instance(
        self,
        name: str,
        version: Optional[str] = None,
        target_device: str = "cpu",
        **kwargs,
    ) -> BaseAIModel:
        """
        Instantiate a new BaseAIModel object from registered factory.
        """
        entry = self.get_model_entry(name, version)
        factory = entry["factory"]
        res = factory(
            name=entry["name"],
            version=entry["version"],
            target_device=target_device,
            **kwargs,
        )
        if not isinstance(res, BaseAIModel):
            raise TypeError(f"Factory for '{name}' did not return an instance of BaseAIModel.")
        return res

    def unregister(self, name: str, version: Optional[str] = None) -> bool:
        """
        Unregister a model definition.
        """
        with self._lock:
            resolved_version = version or self._default_versions.get(name)
            if not resolved_version:
                return False

            key = (name, resolved_version)
            if key in self._registry:
                del self._registry[key]
                if self._default_versions.get(name) == resolved_version:
                    remaining_versions = [v for (n, v) in self._registry.keys() if n == name]
                    if remaining_versions:
                        self._default_versions[name] = remaining_versions[0]
                    else:
                        del self._default_versions[name]
                logger.info(f"Unregistered model '{name}:{resolved_version}' from ModelRegistry.")
                return True
            return False

    def list_models(self) -> List[Dict[str, Any]]:
        """
        Return metadata for all registered models.
        """
        with self._lock:
            models_list = []
            for (name, version), entry in self._registry.items():
                is_default = self._default_versions.get(name) == version
                models_list.append({
                    "name": name,
                    "version": version,
                    "backend": entry["backend"].value if isinstance(entry["backend"], BackendType) else str(entry["backend"]),
                    "description": entry["description"],
                    "input_shape": entry["input_shape"],
                    "output_shape": entry["output_shape"],
                    "is_default_version": is_default,
                    "extra": entry["extra"],
                })
            return models_list

    def has_model(self, name: str, version: Optional[str] = None) -> bool:
        """
        Check if model is registered.
        """
        with self._lock:
            resolved_version = version or self._default_versions.get(name)
            if not resolved_version:
                return False
            return (name, resolved_version) in self._registry


# Global singleton instance
model_registry = ModelRegistry()
