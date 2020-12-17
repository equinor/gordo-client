"""Gordo client schemas."""
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

machine = {
    "name": "test-model",
    "dataset": {
        "target_tag_list": ["TRC1", "TRC2"],
        "data_provider": {"min_size": 100, "max_size": 300, "type": "RandomDataProvider"},
        "resolution": "10T",
        "row_filter": "",
        "known_filter_periods": [],
        "aggregation_methods": "mean",
        "row_filter_buffer_size": 0,
        "asset": None,
        "default_asset": None,
        "n_samples_threshold": 0,
        "low_threshold": -1000,
        "high_threshold": 50000,
        "interpolation_method": "linear_interpolation",
        "interpolation_limit": "8H",
        "filter_periods": {},
        "tag_normalizer": "default",
        "train_start_date": "2015-01-01T00:00:00+00:00",
        "train_end_date": "2015-06-01T00:00:00+00:00",
        "tag_list": ["TRC1", "TRC2"],
        "type": "RandomDataset",
    },
    "model": {"sklearn.decomposition.PCA": {"svd_solver": "auto"}},
    "metadata": {
        "user_defined": {},
        "build_metadata": {
            "model": {
                "model_offset": 0,
                "model_creation_date": None,
                "model_builder_version": "1.1.0",
                "cross_validation": {"scores": {}, "cv_duration_sec": None, "splits": {}},
                "model_training_duration_sec": None,
                "model_meta": {},
            },
            "dataset": {"query_duration_sec": None, "dataset_meta": {}},
        },
    },
    "runtime": {"reporters": []},
    "project_name": "project-name",
    "evaluation": {"cv_mode": "full_build"},
}


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
    metadata: Optional[Metadata] = Field(default_factory=Metadata)
    runtime: Dict[str, Any] = None
    evaluation: Optional[Dict[str, Any]] = None

    def __init__(self, **data):
        super().__init__(**data)
        self.host = f"gordoserver-{self.project_name}-{self.name}"
