import asyncio
import time
from typing import Any, List, Optional, Callable
from concurrent.futures import ThreadPoolExecutor

from app.ai.inference.prediction import Prediction
from app.ai.inference.model_manager import model_manager, ModelManager
from app.utils.logger import logger


class InferenceEngine:
    """
    Asynchronous Inference Pipeline Engine for VoxGaze AI.

    Handles:
    - Input tensor routing
    - Non-blocking model execution via thread pool
    - Latency breakdown measurement
    - Confidence extraction
    - Batch prediction support
    """

    def __init__(
        self,
        manager: ModelManager = model_manager,
        max_workers: int = 4,
    ):
        self.manager = manager
        self.thread_pool = ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix="AIInferenceWorker",
        )

    def _extract_confidence(self, raw_prediction: Any) -> float:
        """
        Extract numeric confidence score from model prediction output.
        """
        if isinstance(raw_prediction, dict):
            if (
                "confidence" in raw_prediction
                and isinstance(raw_prediction["confidence"], (int, float))
            ):
                return float(raw_prediction["confidence"])

            if (
                "score" in raw_prediction
                and isinstance(raw_prediction["score"], (int, float))
            ):
                return float(raw_prediction["score"])

        elif isinstance(raw_prediction, (float, int)):
            return float(raw_prediction)

        elif hasattr(raw_prediction, "confidence"):
            return float(getattr(raw_prediction, "confidence"))

        return 1.0

    async def infer(
        self,
        model_name: str,
        input_data: Any,
        version: Optional[str] = None,
        device: Optional[str] = None,
        preprocess_fn: Optional[Callable[[Any], Any]] = None,
        postprocess_fn: Optional[Callable[[Any], Any]] = None,
        **kwargs,
    ) -> Prediction:
        """
        Execute asynchronous single-item inference pipeline.

        Steps:
        1. Run preprocess_fn if provided and measure preprocessing time.
        2. Get/load model instance via ModelManager.
        3. Offload raw predict() call to thread pool.
        4. Measure inference execution time.
        5. Run postprocess_fn if provided.
        6. Return a structured Prediction object.
        """
        pipeline_start = time.perf_counter()

        # 1. Preprocessing
        pre_start = time.perf_counter()

        if preprocess_fn:
            if asyncio.iscoroutinefunction(preprocess_fn):
                processed_input = await preprocess_fn(input_data)
            else:
                processed_input = preprocess_fn(input_data)
        else:
            processed_input = input_data

        preprocess_time_ms = (time.perf_counter() - pre_start) * 1000.0

        # 2. Model Retrieval (Lazy loading)
        model = await self.manager.get_or_load_model_async(
            name=model_name,
            version=version,
            device=device,
        )

        # 3. Inference offloaded to ThreadPoolExecutor
        inf_start = time.perf_counter()
        loop = asyncio.get_running_loop()

        try:
            raw_output = await loop.run_in_executor(
                self.thread_pool,
                lambda: model.predict(processed_input, **kwargs),
            )

            inference_time_ms = (
                time.perf_counter() - inf_start
            ) * 1000.0

        except Exception as exc:
            inference_time_ms = (
                time.perf_counter() - inf_start
            ) * 1000.0

            logger.error(
                f"Inference execution failed on model "
                f"'{model_name}': {str(exc)}"
            )
            raise

        # 4. Postprocessing
        post_start = time.perf_counter()

        if postprocess_fn:
            if asyncio.iscoroutinefunction(postprocess_fn):
                final_output = await postprocess_fn(raw_output)
            else:
                final_output = postprocess_fn(raw_output)
        else:
            final_output = raw_output

        postprocess_time_ms = (
            time.perf_counter() - post_start
        ) * 1000.0

        # 5. Total metrics computation & payload construction
        total_time_ms = (
            time.perf_counter() - pipeline_start
        ) * 1000.0

        confidence = self._extract_confidence(final_output)

        prediction_obj = Prediction(
            model_name=model.name,
            model_version=model.version,
            confidence=confidence,
            processing_time_ms=round(total_time_ms, 3),
            prediction=final_output,
            metadata={
                "backend": model.backend.value,
                "target_device": model.target_device,
            },
            preprocessing_time_ms=round(preprocess_time_ms, 3),
            inference_time_ms=round(inference_time_ms, 3),
            postprocessing_time_ms=round(postprocess_time_ms, 3),
        )

        logger.debug(
            f"Prediction completed for '{model_name}:{model.version}' "
            f"[Total: {prediction_obj.processing_time_ms}ms, "
            f"Inf: {prediction_obj.inference_time_ms}ms]"
        )

        return prediction_obj

    async def infer_batch(
        self,
        model_name: str,
        batch_inputs: List[Any],
        version: Optional[str] = None,
        device: Optional[str] = None,
        preprocess_fn: Optional[Callable[[Any], Any]] = None,
        postprocess_fn: Optional[Callable[[Any], Any]] = None,
        **kwargs,
    ) -> List[Prediction]:
        """
        Execute concurrent batch inference for a list of inputs.

        Raises:
            ValueError: If batch_inputs is empty.
        """
        if not batch_inputs:
            raise ValueError(
                "batch_inputs must contain at least one input."
            )

        tasks = [
            self.infer(
                model_name=model_name,
                input_data=item,
                version=version,
                device=device,
                preprocess_fn=preprocess_fn,
                postprocess_fn=postprocess_fn,
                **kwargs,
            )
            for item in batch_inputs
        ]

        return await asyncio.gather(*tasks)

    def shutdown(self) -> None:
        """
        Shutdown worker thread pool.
        """
        self.thread_pool.shutdown(wait=False)


# Global singleton instance
inference_engine = InferenceEngine()
