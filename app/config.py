from __future__ import annotations

import os
from dataclasses import dataclass
from dotenv import load_dotenv


load_dotenv(override=True)


def _get_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None or value == "":
        return default
    try:
        return float(value)
    except ValueError as exc:
        raise ValueError(f"Environment variable {name} must be a float, got: {value}") from exc


@dataclass(frozen=True)
class ModelConfig:
    model: str
    temperature: float


@dataclass(frozen=True)
class Settings:
    planner: ModelConfig
    writer: ModelConfig
    judge: ModelConfig
    editor: ModelConfig


settings = Settings(
    planner=ModelConfig(
        model=os.getenv("PLANNER_MODEL", "gpt-4o"),
        temperature=_get_float("PLANNER_TEMPERATURE", 0.0),
    ),
    writer=ModelConfig(
        model=os.getenv("WRITER_MODEL", "gpt-4o"),
        temperature=_get_float("WRITER_TEMPERATURE", 0.7),
    ),
    judge=ModelConfig(
        model=os.getenv("JUDGE_MODEL", "gpt-4o-mini"),
        temperature=_get_float("JUDGE_TEMPERATURE", 0.0),
    ),
    editor=ModelConfig(
        model=os.getenv("EDITOR_MODEL", "gpt-4o"),
        temperature=_get_float("EDITOR_TEMPERATURE", 0.4),
    ),
)