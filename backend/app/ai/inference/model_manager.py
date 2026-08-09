import asyncio
import os
import sys
import time
import threading
from typing import Dict, Any, List, Optional, Tuple
import psutil

from app.ai.inference.base_model import BaseAIModel, ModelStatus, BackendType
from app.ai.inference.model_registry import model_registry, ModelRegistry
from app.utils.logger import logger


class ModelManager:
    """
    Production-grade AI Model Manager responsible for:
    - Lazy loading models on demand
    - Automatic LRU unloading when model capacity / memory thresholds are reached
    - Memory footprint tracking (CPU RAM and GPU VRAM)
    - Multi-version model isolation
    - Thread-safe loading and inference synchronization
    - Automatic GPU detection and CPU fallback
    """

    def __init__(self, registry: ModelRegistry = model_registry, max_loaded_models: int = 10):
        self.registry = registry
        self.max_loaded_models = max_loaded_models
        
        self._lock = threading.RLock()
        self._async_lock = asyncio.Lock()
        
        # Storage for loaded model instances: (name, version) -> BaseAIModel
        self._loaded_models: Dict[Tuple[str, str], BaseAIModel] = {}
        # Access order for LRU tracking: list of (name, version) tuples, MRU at end
        self._access_history: List[Tuple[str, str]] = []
        
        # GPU detection & cache
        self._system_device_info = self._detect_hardware_capabilities()

    def _detect_hardware_capabilities(self) -> Dict[str, Any]:
        """
        Probe system hardware for GPU (CUDA, MPS) and ONNX execution provider capabilities.
        """
        cuda_available = False
        cuda_device_count = 0
        cuda_device_name = None
        mps_available = False
        onnx_providers = []

        # PyTorch hardware probe
        try:
            import torch
            cuda_available = torch.cuda.is_available()
            if cuda_available:
                cuda_device_count = torch.cuda.device_count()
                cuda_device_name = torch.cuda.get_device_name(0)
            if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                mps_available = True
        except ImportError:
            pass

        # ONNX Runtime probe
        try:
            import onnxruntime as ort
            onnx_providers = ort.get_available_providers()
        except ImportError:
            pass

        device = "cuda" if cuda_available else ("mps" if mps_available else "cpu")

        return {
            "preferred_device": device,
            "cuda_available": cuda_available,
            "cuda_device_count": cuda_device_count,
            "cuda_device_name": cuda_device_name,
            "mps_available": mps_available,
            "onnx_providers": onnx_providers,
            "python_version": sys.version,
            "pid": os.getpid(),
        }

    def resolve_device(self, requested_device: Optional[str] = None) -> str:
        """
        Resolve requested target device with automatic CPU fallback.
        """
        if not requested_device:
            return "cpu"
            
        req = requested_device.lower()
        if req in ("cuda", "gpu"):
            if self._system_device_info["cuda_available"]:
                return "cuda"
            elif self._system_device_info["mps_available"]:
                logger.info(f"Requested '{requested_device}' unavailable; substituting Metal MPS.")
                return "mps"
            else:
                logger.warning(f"GPU requested ('{requested_device}'), but no GPU hardware detected. Falling back to CPU.")
                return "cpu"
        elif req == "mps":
            if self._system_device_info["mps_available"]:
                return "mps"
            else:
                logger.warning("MPS requested but unavailable. Falling back to CPU.")
                return "cpu"
        
        return "cpu"

    def _touch_lru(self, key: Tuple[str, str]) -> None:
        """
        Update LRU cache order for loaded model key.
        """
        if key in self._access_history:
            self._access_history.remove(key)
        self._access_history.append(key)

    def _evict_lru_if_needed(self) -> None:
        """
        Evict least-recently-used model if loaded model capacity is exceeded.
        """
        while len(self._loaded_models) >= self.max_loaded_models and self._access_history:
            lru_key = self._access_history.pop(0)
            if lru_key in self._loaded_models:
                logger.info(f"LRU Capacity reached ({self.max_loaded_models}). Evicting model '{lru_key[0]}:{lru_key[1]}'.")
                model_to_unload = self._loaded_models.pop(lru_key)
                try:
                    model_to_unload.shutdown()
                except Exception as exc:
                    logger.error(f"Error during LRU eviction shutdown for '{lru_key[0]}': {exc}")

    def get_or_load_model(
        self,
        name: str,
        version: Optional[str] = None,
        device: Optional[str] = None,
        force_reload: bool = False,
    ) -> BaseAIModel:
        """
        Thread-safe lazy loading of model instance.
        If model is already loaded and not force_reload, return cached instance.
        Otherwise, load, warm up, and cache instance.
        """
        resolved_device = self.resolve_device(device)
        
        with self._lock:
            entry = self.registry.get_model_entry(name, version)
            actual_version = entry["version"]
            key = (name, actual_version)

            if not force_reload and key in self._loaded_models:
                model = self._loaded_models[key]
                if model.is_loaded:
                    self._touch_lru(key)
                    return model

            # Evict LRU model if capacity reached
            self._evict_lru_if_needed()

            logger.info(f"Lazy loading model '{name}:{actual_version}' on device '{resolved_device}'...")
            
            # Instantiate and load model
            model = self.registry.create_model_instance(
                name=name,
                version=actual_version,
                target_device=resolved_device,
            )
            
            try:
                model.load()
                model.warmup()
                self._loaded_models[key] = model
                self._touch_lru(key)
                logger.info(f"Successfully loaded and warmed up model '{name}:{actual_version}'.")
                return model
            except Exception as exc:
                logger.error(f"Failed to load model '{name}:{actual_version}': {str(exc)}")
                if key in self._loaded_models:
                    del self._loaded_models[key]
                raise

    async def get_or_load_model_async(
        self,
        name: str,
        version: Optional[str] = None,
        device: Optional[str] = None,
        force_reload: bool = False,
    ) -> BaseAIModel:
        """
        Asynchronous wrapper around get_or_load_model using asyncio lock.
        """
        async with self._async_lock:
            return await asyncio.to_thread(
                self.get_or_load_model,
                name=name,
                version=version,
                device=device,
                force_reload=force_reload,
            )

    def unload_model(self, name: str, version: Optional[str] = None) -> bool:
        """
        Explicitly unload a loaded model instance.
        """
        with self._lock:
            entry = self.registry.get_model_entry(name, version)
            actual_version = entry["version"]
            key = (name, actual_version)

            if key in self._loaded_models:
                model = self._loaded_models.pop(key)
                if key in self._access_history:
                    self._access_history.remove(key)
                try:
                    model.shutdown()
                    logger.info(f"Unloaded model '{name}:{actual_version}'.")
                    return True
                except Exception as exc:
                    logger.error(f"Error while shutting down model '{name}:{actual_version}': {exc}")
                    return False
            return False

    def reload_model(self, name: str, version: Optional[str] = None, device: Optional[str] = None) -> BaseAIModel:
        """
        Reload a model instance (unloads if loaded, then loads afresh).
        """
        with self._lock:
            self.unload_model(name, version)
            return self.get_or_load_model(name, version, device=device, force_reload=True)

    def unload_all(self) -> None:
        """
        Unload all active model instances and clear LRU cache.
        """
        with self._lock:
            keys = list(self._loaded_models.keys())
            for key in keys:
                model = self._loaded_models.pop(key)
                try:
                    model.shutdown()
                except Exception as exc:
                    logger.error(f"Error unloading model {key}: {exc}")
            self._access_history.clear()
            logger.info("All AI models unloaded cleanly.")

    def get_loaded_models(self) -> List[Dict[str, Any]]:
        """
        Return list of currently loaded model instances and health summaries.
        """
        with self._lock:
            result = []
            for (name, version), model in self._loaded_models.items():
                result.append(model.health())
            return result

    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Retrieve system RAM and GPU memory usage statistics.
        """
        process = psutil.Process(os.getpid())
        ram_bytes = process.memory_info().rss
        ram_mb = round(ram_bytes / (1024 * 1024), 2)
        system_ram = psutil.virtual_memory()

        gpu_stats = {}
        if self._system_device_info["cuda_available"]:
            try:
                import torch
                allocated = torch.cuda.memory_allocated(0)
                reserved = torch.cuda.memory_reserved(0)
                gpu_stats = {
                    "allocated_mb": round(allocated / (1024 * 1024), 2),
                    "reserved_mb": round(reserved / (1024 * 1024), 2),
                }
            except Exception:
                gpu_stats = {"allocated_mb": 0.0, "reserved_mb": 0.0}

        return {
            "process_ram_mb": ram_mb,
            "system_ram_percent": system_ram.percent,
            "system_ram_available_mb": round(system_ram.available / (1024 * 1024), 2),
            "gpu_memory": gpu_stats,
        }

    def get_health_status(self) -> Dict[str, Any]:
        """
        Global health diagnostics report of model manager and hardware.
        """
        loaded = self.get_loaded_models()
        return {
            "status": "healthy",
            "loaded_models_count": len(loaded),
            "max_capacity": self.max_loaded_models,
            "hardware": self._system_device_info,
            "memory": self.get_memory_stats(),
            "loaded_models": loaded,
        }


# Global singleton instance
model_manager = ModelManager()
