import pytest
from app.ai.inference.base_model import BackendType, MockAIModel, ModelStatus
from app.ai.inference.model_registry import ModelRegistry
from app.ai.inference.model_manager import ModelManager


def test_model_manager_lazy_loading_and_unloading():
    registry = ModelRegistry()
    registry.register(
        model_cls_or_factory=lambda name, version, **kwargs: MockAIModel(name=name, version=version, **kwargs),
        name="manager_test_model",
        version="1.0.0",
    )
    manager = ModelManager(registry=registry, max_loaded_models=5)

    assert len(manager.get_loaded_models()) == 0

    # Lazy load
    model = manager.get_or_load_model("manager_test_model", "1.0.0")
    assert model.is_loaded is True
    assert model.status == ModelStatus.LOADED
    assert len(manager.get_loaded_models()) == 1

    # Repeat call returns cached loaded model instance
    model_cached = manager.get_or_load_model("manager_test_model", "1.0.0")
    assert model_cached is model

    # Unload
    unloaded = manager.unload_model("manager_test_model", "1.0.0")
    assert unloaded is True
    assert len(manager.get_loaded_models()) == 0


def test_model_manager_lru_eviction():
    registry = ModelRegistry()
    # Register 3 models with max capacity = 2
    for i in range(1, 4):
        registry.register(
            model_cls_or_factory=lambda name, version, **kwargs: MockAIModel(name=name, version=version, **kwargs),
            name=f"lru_model_{i}",
            version="1.0.0",
        )

    manager = ModelManager(registry=registry, max_loaded_models=2)

    m1 = manager.get_or_load_model("lru_model_1")
    m2 = manager.get_or_load_model("lru_model_2")
    assert len(manager.get_loaded_models()) == 2

    # Loading 3rd model triggers LRU eviction of lru_model_1
    m3 = manager.get_or_load_model("lru_model_3")
    assert len(manager.get_loaded_models()) == 2
    
    loaded_names = [m["name"] for m in manager.get_loaded_models()]
    assert "lru_model_1" not in loaded_names
    assert "lru_model_2" in loaded_names
    assert "lru_model_3" in loaded_names


def test_model_manager_cpu_fallback():
    manager = ModelManager()
    # Request CUDA device when CUDA is not present
    device = manager.resolve_device("cuda")
    if not manager._system_device_info["cuda_available"]:
        assert device in ("cpu", "mps")
    else:
        assert device == "cuda"


def test_model_manager_health_telemetry():
    registry = ModelRegistry()
    registry.register(
        model_cls_or_factory=lambda name, version, **kwargs: MockAIModel(name=name, version=version, **kwargs),
        name="telemetry_model",
        version="1.0.0",
    )
    manager = ModelManager(registry=registry)
    manager.get_or_load_model("telemetry_model")

    health = manager.get_health_status()
    assert health["status"] == "healthy"
    assert health["loaded_models_count"] == 1
    assert "memory" in health
    assert "hardware" in health
