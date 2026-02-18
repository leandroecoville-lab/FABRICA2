from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List

@dataclass
class Trace:
    trace_id: str

@dataclass
class OcaChange:
    path: str
    change_type: str
    notes: str = ""
    patch: str = ""

@dataclass
class OcaRisk:
    severity: str
    blast_radius: List[str] = field(default_factory=list)
    rollback_plan: str = ""

@dataclass
class OcaActors:
    author: str
    reviewer: str = ""

@dataclass
class OCA:
    oca_id: str
    pack_target: str
    type: str
    summary: str
    why: str
    changes: List[OcaChange] = field(default_factory=list)
    tests_added_or_updated: List[str] = field(default_factory=list)
    risk: OcaRisk = field(default_factory=lambda: OcaRisk(severity="low"))
    actors: OcaActors = field(default_factory=lambda: OcaActors(author="unknown"))
    trace: Trace = field(default_factory=lambda: Trace(trace_id=""))

@dataclass
class PackManifest:
    schema_version: str
    pack_id: str
    version: str
    created_at: str
    modules: List[str]
    entrypoints: List[str]
    trace: Trace
    parents: List[str] = field(default_factory=list)
    features: List[str] = field(default_factory=list)
    ops: Dict[str, Any] = field(default_factory=dict)
    tests: Dict[str, Any] = field(default_factory=dict)
