from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ClipRenderPlan:
    payload: dict


@dataclass(frozen=True)
class ProjectRenderPlan:
    clips: list[dict]
