"""Loop Detector — Detect AI agent doom loops by tracking file edit patterns.

When an agent edits the same file repeatedly for the same issue, it's likely
stuck in a doom loop. This module watches for that pattern and provides
actionable intervention messages.

Usage:
    # Record an edit event
    detector = LoopDetector.load(project_root)
    detector.record_edit("src/routes/users.py", context="adding auth middleware")
    result = detector.check("src/routes/users.py")
    detector.save()

    if result.is_loop:
        print(result.intervention_message)
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path

# Default thresholds
DEFAULT_EDIT_THRESHOLD = 3        # edits to same file
DEFAULT_TIME_WINDOW = 300         # within 5 minutes
DEFAULT_SIMILARITY_THRESHOLD = 3  # edits with similar context

STATE_FILE = ".harness/state/loop-detector.json"


@dataclass
class EditEvent:
    file: str
    timestamp: float
    context: str = ""  # brief description of what the edit was for


@dataclass
class LoopCheckResult:
    file: str
    is_loop: bool
    edit_count: int
    window_seconds: float
    intervention_message: str = ""


@dataclass
class LoopDetectorState:
    events: list[dict] = field(default_factory=list)


class LoopDetector:
    def __init__(
        self,
        project_root: Path,
        edit_threshold: int = DEFAULT_EDIT_THRESHOLD,
        time_window: int = DEFAULT_TIME_WINDOW,
    ):
        self.project_root = project_root
        self.edit_threshold = edit_threshold
        self.time_window = time_window
        self.state_file = project_root / STATE_FILE
        self.events: list[EditEvent] = []

    @classmethod
    def load(cls, project_root: Path, **kwargs) -> LoopDetector:
        """Load detector state from disk."""
        detector = cls(project_root, **kwargs)
        if detector.state_file.is_file():
            try:
                data = json.loads(detector.state_file.read_text(encoding="utf-8"))
                detector.events = [
                    EditEvent(**e) for e in data.get("events", [])
                ]
            except (json.JSONDecodeError, OSError, TypeError):
                detector.events = []
        return detector

    def save(self) -> None:
        """Persist state to disk."""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        data = {"events": [asdict(e) for e in self.events]}
        self.state_file.write_text(
            json.dumps(data, indent=2), encoding="utf-8"
        )

    def record_edit(self, file: str, context: str = "") -> None:
        """Record that a file was edited."""
        self.events.append(EditEvent(
            file=file,
            timestamp=time.time(),
            context=context,
        ))
        self._prune_old_events()

    def check(self, file: str) -> LoopCheckResult:
        """Check if a file is in a doom loop."""
        now = time.time()
        cutoff = now - self.time_window

        recent_edits = [
            e for e in self.events
            if e.file == file and e.timestamp >= cutoff
        ]

        edit_count = len(recent_edits)
        is_loop = edit_count >= self.edit_threshold

        message = ""
        if is_loop:
            message = self._build_intervention(file, recent_edits)

        return LoopCheckResult(
            file=file,
            is_loop=is_loop,
            edit_count=edit_count,
            window_seconds=self.time_window,
            intervention_message=message,
        )

    def check_all(self) -> list[LoopCheckResult]:
        """Check all recently edited files for doom loops."""
        now = time.time()
        cutoff = now - self.time_window

        # Get unique files edited in the time window
        recent_files = set(
            e.file for e in self.events if e.timestamp >= cutoff
        )

        results = []
        for file in sorted(recent_files):
            result = self.check(file)
            if result.edit_count >= 2:  # only report files with multiple edits
                results.append(result)

        return results

    def clear(self, file: str | None = None) -> None:
        """Clear edit history. If file given, clear only that file."""
        if file:
            self.events = [e for e in self.events if e.file != file]
        else:
            self.events = []

    def _prune_old_events(self) -> None:
        """Remove events older than 2x the time window."""
        cutoff = time.time() - (self.time_window * 2)
        self.events = [e for e in self.events if e.timestamp >= cutoff]

    def _build_intervention(self, file: str, recent_edits: list[EditEvent]) -> str:
        """Build an intervention message for the AI agent."""
        contexts = [e.context for e in recent_edits if e.context]
        unique_contexts = list(dict.fromkeys(contexts))  # dedupe, preserve order

        msg_parts = [
            f"LOOP ADVISORY: {file} has been edited {len(recent_edits)} times "
            f"in the last {self.time_window // 60} minutes.",
            "",
            "This may indicate a doom loop. Consider pausing to re-evaluate.",
            "If you are making progress (fixing different issues each time), you can safely ignore this.",
            "",
            "If you are stuck, try:",
            "  1. Re-read the constraint violation or error message from the start.",
            "  2. Check if you're fixing the symptom instead of the root cause.",
            "  3. Look at .harness/context/ for relevant architecture docs.",
            "  4. Consider a different approach entirely.",
        ]

        if unique_contexts:
            msg_parts.append("")
            msg_parts.append("Edit history (review to see if you're repeating yourself):")
            for i, ctx in enumerate(unique_contexts, 1):
                msg_parts.append(f"  {i}. {ctx}")

        msg_parts.extend([
            "",
            "To dismiss this advisory:",
            f"  harness loop clear --file {file}",
        ])

        return "\n".join(msg_parts)
