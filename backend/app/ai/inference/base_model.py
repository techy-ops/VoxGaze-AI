import time
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, Optional, List, Union
from pydantic import BaseModel, Field
from app.utils.logger import logger


class BackendType(str, Enum):
    """Supported model execution backends."""
    PYTORCH = "pytorch"
    ONNX = "onnx"
    TENSORFLOW = "tensorflow"
    OPENVINO = "openvino"
    MEDIAPIPE = "mediapipe"
    CUSTOM = "custom"


class ModelStatus(str, Enum):
    """Model operational lifecycle state."""
    UNLOADED = "unloaded"
    LOADING = "loading"
    LOADED = "loaded"
    ERROR = "error"
    UNLOADING = "unloading"


class ModelMetadata(BaseModel):
    """Metadata schema defining AI model characteristics and specifications."""
    name: str = Field(..., description="Unique name identifier for the model")
    version: str = Field(default="1.0.0", description="Semantic model version string")
    backend: BackendType = Field(default=BackendType.CUSTOM, description="Underlying model framework backend")
    description: str = Field(default="", description="Detailed description of model capabilities")
    target_device: str = Field(default="cpu", description="Target compute device (e.g., cpu, cuda, mps)")
    input_shape: Optional[List[Union[int, None]]] = Field(default=None, description="Expected input tensor dimensions")
    output_shape: Optional[List[Union[int, None]]] = Field(default=None, description="Expected output tensor dimensions")
    extra: Dict[str, Any] = Field(default_factory=dict, description="Additional model parameters or tags")


class BaseAIModel(ABC):
    """
    Abstract Base Class for all AI models in VoxGaze AI.
    Exposes a unified interface across PyTorch, ONNX, MediaPipe, TensorFlow, and custom backends.
    """

    def __init__(
        self,
        name: str,
        version: str = "1.0.0",
        backend: BackendType = BackendType.CUSTOM,
        target_device: str = "cpu",
        description: str = "",
        input_shape: Optional[List[Union[int, None]]] = None,
        output_shape: Optional[List[Union[int, None]]] = None,
        extra: Optional[Dict[str, Any]] = None,
    ):
        self._name = name
        self._version = version
        self._backend = backend
        self._target_device = target_device
        self._description = description
        self._input_shape = input_shape
        self._output_shape = output_shape
        self._extra = extra or {}
        
        self._status: ModelStatus = ModelStatus.UNLOADED
        self._load_timestamp: Optional[float] = None
        self._last_inference_timestamp: Optional[float] = None
        self._total_inferences: int = 0
        self._total_inference_time_ms: float = 0.0
        self._error_count: int = 0
        self._last_error: Optional[str] = None

    @property
    def name(self) -> str:
        return self._name

    @property
    def version(self) -> str:
        return self._version

    @property
    def backend(self) -> BackendType:
        return self._backend

    @property
    def target_device(self) -> str:
        return self._target_device

    @target_device.setter
    def target_device(self, device: str) -> None:
        self._target_device = device

    @property
    def status(self) -> ModelStatus:
        return self._status

    @property
    def is_loaded(self) -> bool:
        return self._status == ModelStatus.LOADED

    @abstractmethod
    def load(self) -> None:
        """
        Load model weights, computational graphs, or execution sessions into memory.
        """
        pass

    @abstractmethod
    def warmup(self) -> None:
        """
        Perform a dummy inference pass to initialize memory pools and eliminate cold-start latency.
        """
        pass

    @abstractmethod
    def predict(self, input_data: Any, **kwargs) -> Any:
        """
        Execute raw inference using the loaded model.
        """
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """
        Unload model, release GPU/CPU memory resources, and close active sessions.
        """
        pass

    def metadata(self) -> ModelMetadata:
        """
        Return structured metadata describing the model properties.
        """
        return ModelMetadata(
            name=self._name,
            version=self._version,
            backend=self._backend,
            description=self._description,
            target_device=self._target_device,
            input_shape=self._input_shape,
            output_shape=self._output_shape,
            extra=self._extra,
        )

    def health(self) -> Dict[str, Any]:
        """
        Return diagnostic health telemetry for this model instance.
        """
        avg_latency = (
            self._total_inference_time_ms / self._total_inferences
            if self._total_inferences > 0
            else 0.0
        )
        return {
            "name": self._name,
            "version": self._version,
            "backend": self._backend.value,
            "status": self._status.value,
            "is_loaded": self.is_loaded,
            "target_device": self._target_device,
            "load_timestamp": self._load_timestamp,
            "total_inferences": self._total_inferences,
            "avg_latency_ms": round(avg_latency, 3),
            "error_count": self._error_count,
            "last_error": self._last_error,
        }

    def record_inference_metrics(self, latency_ms: float, is_error: bool = False, error_msg: Optional[str] = None) -> None:
        """
        Record internal metrics after an inference call.
        """
        self._last_inference_timestamp = time.time()
        if is_error:
            self._error_count += 1
            self._last_error = error_msg
        else:
            self._total_inferences += 1
            self._total_inference_time_ms += latency_ms


class MockAIModel(BaseAIModel):
    """
    Production-grade Mock AI Model for testing, benchmarking, and CPU fallback demonstration.
    """

    def __init__(
        self,
        name: str = "mock_classifier",
        version: str = "1.0.0",
        backend: BackendType = BackendType.CUSTOM,
        target_device: str = "cpu",
        dummy_confidence: float = 0.95,
        dummy_latency_ms: float = 5.0,
    ):
        super().__init__(
            name=name,
            version=version,
            backend=backend,
            target_device=target_device,
            description="Built-in Mock AI Model for testing and fallback evaluation",
            input_shape=[1, 3, 224, 224],
            output_shape=[1, 1000],
        )
        self.dummy_confidence = dummy_confidence
        self.dummy_latency_ms = dummy_latency_ms

    def load(self) -> None:
        logger.info(f"Loading MockAIModel '{self.name}:{self.version}' on {self.target_device}...")
        self._status = ModelStatus.LOADING
        time.sleep(0.005)  # Simulate weight initialization
        self._status = ModelStatus.LOADED
        self._load_timestamp = time.time()
        logger.info(f"MockAIModel '{self.name}:{self.version}' loaded successfully.")

    def warmup(self) -> None:
        if not self.is_loaded:
            self.load()
        logger.info(f"Warming up MockAIModel '{self.name}:{self.version}'...")
        self.predict({"warmup": True})

    def predict(self, input_data: Any, **kwargs) -> Dict[str, Any]:
        if not self.is_loaded:
            raise RuntimeError(f"Cannot execute predict(): Model '{self.name}' is not loaded.")
        
        start = time.perf_counter()
        if self.dummy_latency_ms > 0:
            time.sleep(self.dummy_latency_ms / 1000.0)
            
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        self.record_inference_metrics(elapsed_ms)
        
        return {
            "label": "mock_prediction_class",
            "confidence": self.dummy_confidence,
            "raw_input_summary": str(type(input_data)),
        }

    def shutdown(self) -> None:
        logger.info(f"Shutting down MockAIModel '{self.name}:{self.version}'...")
        self._status = ModelStatus.UNLOADING
        self._status = ModelStatus.UNLOADED
        logger.info(f"MockAIModel '{self.name}:{self.version}' shut down.")


class PyTorchModelWrapper(BaseAIModel):
    """
    Wrapper adapter for PyTorch (torch.nn.Module or ScriptModule) models.
    """

    def __init__(
        self,
        name: str,
        version: str = "1.0.0",
        model_instance: Optional[Any] = None,
        weights_path: Optional[str] = None,
        target_device: str = "cpu",
        **kwargs,
    ):
        super().__init__(
            name=name,
            version=version,
            backend=BackendType.PYTORCH,
            target_device=target_device,
            **kwargs,
        )
        self.model_instance = model_instance
        self.weights_path = weights_path

    def load(self) -> None:
        logger.info(f"Loading PyTorch model '{self.name}' on target device '{self.target_device}'...")
        self._status = ModelStatus.LOADING
        try:
            import torch
            if self.weights_path and not self.model_instance:
                self.model_instance = torch.jit.load(self.weights_path, map_location=self.target_device)
            if self.model_instance and hasattr(self.model_instance, "to"):
                self.model_instance.to(self.target_device)
                if hasattr(self.model_instance, "eval"):
                    self.model_instance.eval()
            self._status = ModelStatus.LOADED
            self._load_timestamp = time.time()
            logger.info(f"PyTorch model '{self.name}' loaded successfully.")
        except Exception as exc:
            self._status = ModelStatus.ERROR
            self._last_error = str(exc)
            logger.error(f"Failed to load PyTorch model '{self.name}': {exc}")
            raise

    def warmup(self) -> None:
        if not self.is_loaded:
            self.load()
        try:
            import torch
            dummy_shape = self._input_shape or [1, 3, 224, 224]
            clean_shape = [s if (s is not None and s > 0) else 1 for s in dummy_shape]
            dummy_tensor = torch.zeros(*clean_shape, device=self.target_device)
            with torch.no_grad():
                self.predict(dummy_tensor)
            logger.info(f"PyTorch model '{self.name}' warmup complete.")
        except Exception as exc:
            logger.warning(f"PyTorch warmup skipped/failed for '{self.name}': {exc}")

    def predict(self, input_data: Any, **kwargs) -> Any:
        if not self.is_loaded or self.model_instance is None:
            raise RuntimeError(f"PyTorch model '{self.name}' is not loaded.")
        start = time.perf_counter()
        try:
            import torch
            if isinstance(input_data, torch.Tensor):
                tensor_input = input_data.to(self.target_device)
            else:
                tensor_input = torch.as_tensor(input_data, device=self.target_device)
                
            with torch.no_grad():
                out = self.model_instance(tensor_input)
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            self.record_inference_metrics(elapsed_ms)
            return out
        except Exception as exc:
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            self.record_inference_metrics(elapsed_ms, is_error=True, error_msg=str(exc))
            raise

    def shutdown(self) -> None:
        logger.info(f"Shutting down PyTorch model '{self.name}'...")
        self._status = ModelStatus.UNLOADING
        self.model_instance = None
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except Exception:
            pass
        self._status = ModelStatus.UNLOADED


class ONNXModelWrapper(BaseAIModel):
    """
    Wrapper adapter for ONNX Runtime (onnxruntime.InferenceSession) models.
    """

    def __init__(
        self,
        name: str,
        version: str = "1.0.0",
        model_path: Optional[str] = None,
        session_instance: Optional[Any] = None,
        target_device: str = "cpu",
        **kwargs,
    ):
        super().__init__(
            name=name,
            version=version,
            backend=BackendType.ONNX,
            target_device=target_device,
            **kwargs,
        )
        self.model_path = model_path
        self.session_instance = session_instance

    def load(self) -> None:
        logger.info(f"Loading ONNX model '{self.name}' on device '{self.target_device}'...")
        self._status = ModelStatus.LOADING
        try:
            import onnxruntime as ort
            providers = ["CPUExecutionProvider"]
            if self.target_device.lower() in ("cuda", "gpu") and "CUDAExecutionProvider" in ort.get_available_providers():
                providers.insert(0, "CUDAExecutionProvider")
            
            if self.model_path and not self.session_instance:
                self.session_instance = ort.InferenceSession(self.model_path, providers=providers)
            self._status = ModelStatus.LOADED
            self._load_timestamp = time.time()
            logger.info(f"ONNX model '{self.name}' loaded successfully with providers {providers}.")
        except Exception as exc:
            self._status = ModelStatus.ERROR
            self._last_error = str(exc)
            logger.error(f"Failed to load ONNX model '{self.name}': {exc}")
            raise

    def warmup(self) -> None:
        if not self.is_loaded:
            self.load()
        if self.session_instance:
            try:
                import numpy as np
                input_meta = self.session_instance.get_inputs()[0]
                shape = [s if isinstance(s, int) and s > 0 else 1 for s in input_meta.shape]
                dummy_input = np.zeros(shape, dtype=np.float32)
                self.predict({input_meta.name: dummy_input})
                logger.info(f"ONNX model '{self.name}' warmup complete.")
            except Exception as exc:
                logger.warning(f"ONNX warmup failed for '{self.name}': {exc}")

    def predict(self, input_data: Any, **kwargs) -> Any:
        if not self.is_loaded or self.session_instance is None:
            raise RuntimeError(f"ONNX model '{self.name}' is not loaded.")
        start = time.perf_counter()
        try:
            import numpy as np
            if isinstance(input_data, dict):
                feed_dict = input_data
            else:
                input_meta = self.session_instance.get_inputs()[0]
                arr = np.asarray(input_data, dtype=np.float32)
                feed_dict = {input_meta.name: arr}
                
            outputs = self.session_instance.run(None, feed_dict)
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            self.record_inference_metrics(elapsed_ms)
            return outputs
        except Exception as exc:
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            self.record_inference_metrics(elapsed_ms, is_error=True, error_msg=str(exc))
            raise

    def shutdown(self) -> None:
        logger.info(f"Shutting down ONNX model '{self.name}'...")
        self._status = ModelStatus.UNLOADING
        self.session_instance = None
        self._status = ModelStatus.UNLOADED


class MediaPipeModelWrapper(BaseAIModel):
    """
    Wrapper adapter for MediaPipe solutions / tasks.
    """

    def __init__(
        self,
        name: str,
        version: str = "1.0.0",
        solution_factory: Optional[Any] = None,
        **kwargs,
    ):
        super().__init__(
            name=name,
            version=version,
            backend=BackendType.MEDIAPIPE,
            target_device="cpu",
            **kwargs,
        )
        self.solution_factory = solution_factory
        self.solution_instance = None

    def load(self) -> None:
        logger.info(f"Loading MediaPipe model '{self.name}'...")
        self._status = ModelStatus.LOADING
        try:
            if callable(self.solution_factory):
                self.solution_instance = self.solution_factory()
            self._status = ModelStatus.LOADED
            self._load_timestamp = time.time()
            logger.info(f"MediaPipe model '{self.name}' loaded.")
        except Exception as exc:
            self._status = ModelStatus.ERROR
            self._last_error = str(exc)
            logger.error(f"Failed to load MediaPipe model '{self.name}': {exc}")
            raise

    def warmup(self) -> None:
        if not self.is_loaded:
            self.load()
        try:
            import numpy as np
            dummy_frame = np.zeros((224, 224, 3), dtype=np.uint8)
            self.predict(dummy_frame)
        except Exception:
            pass

    def predict(self, input_data: Any, **kwargs) -> Any:
        if not self.is_loaded:
            raise RuntimeError(f"MediaPipe model '{self.name}' is not loaded.")
        start = time.perf_counter()
        try:
            if hasattr(self.solution_instance, "process"):
                res = self.solution_instance.process(input_data)
            elif callable(self.solution_instance):
                res = self.solution_instance(input_data, **kwargs)
            else:
                res = {"status": "success", "processed": True}
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            self.record_inference_metrics(elapsed_ms)
            return res
        except Exception as exc:
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            self.record_inference_metrics(elapsed_ms, is_error=True, error_msg=str(exc))
            raise

    def shutdown(self) -> None:
        logger.info(f"Shutting down MediaPipe model '{self.name}'...")
        self._status = ModelStatus.UNLOADING
        if hasattr(self.solution_instance, "close"):
            try:
                self.solution_instance.close()
            except Exception:
                pass
        self.solution_instance = None
        self._status = ModelStatus.UNLOADED
