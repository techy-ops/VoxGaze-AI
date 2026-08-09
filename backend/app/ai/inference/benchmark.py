import time
import math
import statistics
import asyncio
from typing import Any, Dict, Optional, List

from app.ai.inference.base_model import BaseAIModel
from app.ai.inference.inference_engine import inference_engine, InferenceEngine
from app.ai.inference.model_manager import model_manager, ModelManager
from app.utils.logger import logger


class ModelBenchmark:
    """
    Performance Benchmarking Utility for VoxGaze AI models.
    Evaluates model latency percentiles (p50, p95, p99), throughput (FPS/QPS),
    and memory footprint delta over repeated inference iterations.
    """

    def __init__(self, engine: InferenceEngine = inference_engine, manager: ModelManager = model_manager):
        self.engine = engine
        self.manager = manager

    async def run_benchmark(
        self,
        model_name: str,
        sample_input: Any,
        version: Optional[str] = None,
        device: Optional[str] = None,
        iterations: int = 50,
        warmup_iterations: int = 5,
    ) -> Dict[str, Any]:
        """
        Execute benchmark run for a model and compute detailed performance telemetry.
        """
        logger.info(f"Starting performance benchmark for model '{model_name}' ({iterations} iterations)...")
        
        # Initial memory measurement
        mem_before = self.manager.get_memory_stats()
        
        # 1. Warmup passes
        for _ in range(warmup_iterations):
            await self.engine.infer(model_name, sample_input, version=version, device=device)

        # 2. Measured iterations
        latencies_ms: List[float] = []
        inference_times_ms: List[float] = []
        
        start_total = time.perf_counter()
        for _ in range(iterations):
            prediction = await self.engine.infer(model_name, sample_input, version=version, device=device)
            latencies_ms.append(prediction.processing_time_ms)
            inference_times_ms.append(prediction.inference_time_ms)
        elapsed_total_sec = time.perf_counter() - start_total

        # Memory measurement post-benchmark
        mem_after = self.manager.get_memory_stats()

        # Compute statistics
        sorted_latencies = sorted(latencies_ms)
        mean_latency = statistics.mean(sorted_latencies)
        median_latency = statistics.median(sorted_latencies)
        min_latency = min(sorted_latencies)
        max_latency = max(sorted_latencies)

        # Percentile calculations
        p95_idx = max(0, math.ceil(0.95 * len(sorted_latencies)) - 1)
        p99_idx = max(0, math.ceil(0.99 * len(sorted_latencies)) - 1)
        p95_latency = sorted_latencies[p95_idx]
        p99_latency = sorted_latencies[p99_idx]

        throughput_qps = iterations / elapsed_total_sec if elapsed_total_sec > 0 else 0.0

        benchmark_report = {
            "model_name": model_name,
            "version": version or "default",
            "device": device or "cpu",
            "iterations": iterations,
            "warmup_iterations": warmup_iterations,
            "total_duration_sec": round(elapsed_total_sec, 3),
            "throughput_qps": round(throughput_qps, 2),
            "latency_ms": {
                "mean": round(mean_latency, 3),
                "median": round(median_latency, 3),
                "min": round(min_latency, 3),
                "max": round(max_latency, 3),
                "p95": round(p95_latency, 3),
                "p99": round(p99_latency, 3),
            },
            "raw_inference_time_ms": {
                "mean": round(statistics.mean(inference_times_ms), 3),
                "min": round(min(inference_times_ms), 3),
                "max": round(max(inference_times_ms), 3),
            },
            "memory": {
                "before_ram_mb": mem_before["process_ram_mb"],
                "after_ram_mb": mem_after["process_ram_mb"],
                "delta_ram_mb": round(mem_after["process_ram_mb"] - mem_before["process_ram_mb"], 2),
            },
        }

        logger.info(
            f"Benchmark complete for '{model_name}': {round(throughput_qps, 1)} QPS, "
            f"mean latency: {round(mean_latency, 2)}ms, p95: {round(p95_latency, 2)}ms"
        )
        return benchmark_report


# Global singleton instance
benchmark_runner = ModelBenchmark()
