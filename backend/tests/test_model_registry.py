import pytest
from app.ai.inference.base_model import BaseAIModel, BackendType, MockAIModel
from app.ai.inference.model_registry import ModelRegistry


def test_registry_registration_and_listing():
    registry = ModelRegistry()
    initial_count = len(registry.list_models())

    # Register custom model
    registry.register(
        model_cls_or_factory=lambda name, version, **kwargs: MockAIModel(name=name, version=version, **kwargs),
        name="custom_test_model",
        version="2.0.0",
        backend=BackendType.PYTORCH,
        description="Custom Test Model",
    )

    assert registry.has_model("custom_test_model", "2.0.0") is True
    assert registry.has_model("custom_test_model") is True
    assert len(registry.list_models()) == initial_count + 1

    entry = registry.get_model_entry("custom_test_model", "2.0.0")
    assert entry["name"] == "custom_test_model"
    assert entry["version"] == "2.0.0"
    assert entry["backend"] == BackendType.PYTORCH


def test_registry_instantiation():
    registry = ModelRegistry()
    registry.register(
        model_cls_or_factory=lambda name, version, **kwargs: MockAIModel(name=name, version=version, dummy_confidence=0.99, **kwargs),
        name="instantiation_test",
        version="1.0.0",
        backend=BackendType.CUSTOM,
    )

    model_inst = registry.create_model_instance("instantiation_test", "1.0.0", target_device="cpu")
    assert isinstance(model_inst, BaseAIModel)
    assert model_inst.name == "instantiation_test"
    assert model_inst.version == "1.0.0"


def test_registry_unregistration():
    registry = ModelRegistry()
    registry.register(
        model_cls_or_factory=lambda name, version, **kwargs: MockAIModel(name=name, version=version, **kwargs),
        name="temp_model",
        version="1.0.0",
    )

    assert registry.has_model("temp_model") is True
    unregistered = registry.unregister("temp_model", "1.0.0")
    assert unregistered is True
    assert registry.has_model("temp_model") is False


def test_registry_unregistered_model_raises_key_error():
    registry = ModelRegistry()
    with pytest.raises(KeyError):
        registry.get_model_entry("non_existent_model_xyz")
