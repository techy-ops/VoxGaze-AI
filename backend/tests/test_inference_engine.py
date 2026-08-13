import anyio
import pytest

from app.ai.inference.base_model import MockAIModel
from app.ai.inference.model_registry import ModelRegistry
from app.ai.inference.model_manager import ModelManager
from app.ai.inference.inference_engine import InferenceEngine
from app.ai.inference.benchmark import ModelBenchmark
from app.ai.inference.prediction import Prediction


def test_inference_pipeline_execution():
    async def run():
        registry = ModelRegistry()
        registry.register(
            model_cls_or_factory=lambda name, version, **kwargs: MockAIModel(
                name=name,
                version=version,
                dummy_confidence=0.94,
                **kwargs,
            ),
            name="pipeline_test_model",
            version="1.0.0",
        )
        manager = ModelManager(registry=registry)
        engine = InferenceEngine(manager=manager)

        def preprocess(data):
            return {"preprocessed": True, "raw": data}

        def postprocess(raw_out):
            raw_out["postprocessed"] = True
            return raw_out

        prediction = await engine.infer(
            model_name="pipeline_test_model",
            input_data={"input_val": 42},
            preprocess_fn=preprocess,
            postprocess_fn=postprocess,
        )

        assert isinstance(prediction, Prediction)
        assert prediction.model_name == "pipeline_test_model"
        assert prediction.confidence == 0.94
        assert prediction.processing_time_ms > 0
        assert prediction.preprocessing_time_ms >= 0
        assert prediction.inference_time_ms >= 0
        assert prediction.postprocessing_time_ms >= 0
        assert prediction.prediction["postprocessed"] is True

    anyio.run(run)


def test_batch_inference_execution():
    async def run():
        registry = ModelRegistry()
        registry.register(
            model_cls_or_factory=lambda name, version, **kwargs: MockAIModel(
                name=name,
                version=version,
                **kwargs,
            ),
            name="batch_test_model",
            version="1.0.0",
        )
        manager = ModelManager(registry=registry)
        engine = InferenceEngine(manager=manager)

        inputs = [{"id": 1}, {"id": 2}, {"id": 3}]
        predictions = await engine.infer_batch(
            model_name="batch_test_model",
            batch_inputs=inputs,
        )

        assert len(predictions) == 3

        for pred in predictions:
            assert isinstance(pred, Prediction)
            assert pred.model_name == "batch_test_model"

    anyio.run(run)


def test_batch_inference_rejects_empty_input():
    async def run():
        registry = ModelRegistry()
        registry.register(
            model_cls_or_factory=lambda name, version, **kwargs: MockAIModel(
                name=name,
                version=version,
                **kwargs,
            ),
            name="empty_batch_test_model",
            version="1.0.0",
        )
        manager = ModelManager(registry=registry)
        engine = InferenceEngine(manager=manager)

        with pytest.raises(
            ValueError,
            match="batch_inputs must contain at least one input\\.",
        ):
            await engine.infer_batch(
                model_name="empty_batch_test_model",
                batch_inputs=[],
            )

        engine.shutdown()

    anyio.run(run)


def test_model_benchmark_utility():
    async def run():
        registry = ModelRegistry()
        registry.register(
            model_cls_or_factory=lambda name, version, **kwargs: MockAIModel(
                name=name,
                version=version,
                dummy_latency_ms=1.0,
                **kwargs,
            ),
            name="benchmark_test_model",
            version="1.0.0",
        )
        manager = ModelManager(registry=registry)
        engine = InferenceEngine(manager=manager)
        benchmark = ModelBenchmark(engine=engine, manager=manager)

        report = await benchmark.run_benchmark(
            model_name="benchmark_test_model",
            sample_input={"test": 123},
            iterations=10,
            warmup_iterations=2,
        )

        assert report["model_name"] == "benchmark_test_model"
        assert report["iterations"] == 10
        assert report["throughput_qps"] > 0
        assert "latency_ms" in report
        assert report["latency_ms"]["mean"] > 0

    anyio.run(run)