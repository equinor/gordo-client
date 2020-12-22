"""Gordo client schemas."""
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class CrossValidationMetaData(BaseModel):
    scores: Dict[str, Any] = Field(default_factory=dict)
    cv_duration_sec: Optional[float] = None
    splits: Dict[str, Any] = Field(default_factory=dict)


class ModelBuildMetadata(BaseModel):
    model_offset: int = 0
    model_creation_date: Optional[str] = None
    model_builder_version: str = "1.1.0"
    cross_validation: CrossValidationMetaData = Field(default_factory=CrossValidationMetaData)
    model_training_duration_sec: Optional[float] = None
    model_meta: Dict[str, Any] = Field(default_factory=dict)


class DatasetBuildMetadata(BaseModel):
    query_duration_sec: Optional[float] = None  # How long it took to get the data
    dataset_meta: Dict[str, Any] = Field(default_factory=dict)


class BuildMetadata(BaseModel):
    model: ModelBuildMetadata = Field(default_factory=ModelBuildMetadata)
    dataset: DatasetBuildMetadata = Field(default_factory=DatasetBuildMetadata)


class Metadata(BaseModel):
    user_defined: Dict[str, Any] = Field(default_factory=dict)
    build_metadata: BuildMetadata = Field(default_factory=BuildMetadata)


class Machine(BaseModel):
    name: str
    project_name: str
    host: Optional[str]
    model: Dict[str, Any] = Field(...)
    dataset: Dict[str, Any] = Field(...)
    metadata: Metadata = Field(default_factory=Metadata)
    runtime: Dict[str, Any] = Field(default_factory=dict)
    evaluation: Optional[Dict[str, Any]] = Field(default=dict(cv_mode="full_build"))

    def __init__(self, **data):
        super().__init__(**data)
        self.host = f"gordoserver-{self.project_name}-{self.name}"
