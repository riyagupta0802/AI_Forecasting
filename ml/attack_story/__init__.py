"""HEX HIVE Phase 8 — Attack Story Module Package.

Provides event normalization, multi-factor correlation, chronological timeline assembly,
and automated incident narrative generation grounded in real CICIDS2017 network flow telemetry.
"""

from ml.attack_story.events import NetworkSecurityEvent, load_normalized_events
from ml.attack_story.correlation import EventCorrelator, CorrelatedAttackCluster
from ml.attack_story.timeline import ChronologicalTimelineBuilder
from ml.attack_story.story import AttackStoryEngine, attack_story_engine

__all__ = [
    "NetworkSecurityEvent",
    "load_normalized_events",
    "EventCorrelator",
    "CorrelatedAttackCluster",
    "ChronologicalTimelineBuilder",
    "AttackStoryEngine",
    "attack_story_engine",
]

