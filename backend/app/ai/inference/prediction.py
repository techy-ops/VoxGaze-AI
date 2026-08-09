import time
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class Prediction(BaseModel):
    """
    Standardized AI Prediction response object.
    Enforces a consistent payload structure across all inference pipelines and models.
    """
    model_name: str = Field(..., description="Name of the model that executed the prediction")
    model_version: str = Field(default="1.0.0", description="Version of the model executed")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Overall prediction confidence score (0.0 - 1.0)")
    processing_time_ms: float = Field(..., description="Total processing time in milliseconds")
    prediction: Any = Field(..., description="Model prediction output payload (labels, tensors, arrays, or dicts)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Execution metadata, device info, and tags")
    
    # Timing breakdown (in milliseconds)
    preprocessing_time_ms: float = Field(default=0.0, description="Time spent in data preprocessing")
    inference_time_ms: float = Field(default=0.0, description="Time spent in raw model execution")
    postprocessing_time_ms: float = Field(default=0.0, description="Time spent in output postprocessing")
    timestamp: float = Field(default_factory=time.time, description="Unix timestamp of prediction generation")

    model_config = {
        "protected_namespaces": (),
        "arbitrary_types_allowed": True,
    }

