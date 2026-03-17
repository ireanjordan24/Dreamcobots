"""
DreamCo Autonomous Trainer — trains AI bots to learn job-specific skills,
recognize faces, identify objects, and evaluate items such as antiques,
coins, and collectibles.

Key features
------------
* Skill training per job title
* Face recognition training pipeline
* Object / item recognition pipeline
* Item valuation (antiques, coins, collectibles)
* Buddy Bot upgrade propagation — when a new skill is learned it is
  automatically pushed to *all* registered Buddy Bot instances.

GLOBAL AI SOURCES FLOW: participates via job_titles_bot.py pipeline.
"""

from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from framework import GlobalAISourcesFlow  # noqa: F401


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class TrainingSession:
    """Records a single training session."""
    session_id: str
    skill_name: str
    domain: str
    examples_used: int
    accuracy_pct: float
    status: str  # "pending" | "in_progress" | "complete" | "failed"
    notes: str = ""

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "skill_name": self.skill_name,
            "domain": self.domain,
            "examples_used": self.examples_used,
            "accuracy_pct": self.accuracy_pct,
            "status": self.status,
            "notes": self.notes,
        }


@dataclass
class ItemValuation:
    """Result of an item valuation request."""
    item_name: str
    item_type: str
    estimated_value_usd_low: float
    estimated_value_usd_high: float
    confidence_pct: float
    value_factors: List[str]
    recommended_action: str

    def to_dict(self) -> dict:
        return {
            "item_name": self.item_name,
            "item_type": self.item_type,
            "estimated_value_usd_low": self.estimated_value_usd_low,
            "estimated_value_usd_high": self.estimated_value_usd_high,
            "confidence_pct": self.confidence_pct,
            "value_factors": self.value_factors,
            "recommended_action": self.recommended_action,
        }


# ---------------------------------------------------------------------------
# Item valuation knowledge base (expanded for demo purposes)
# ---------------------------------------------------------------------------

_ITEM_VALUATION_KB: Dict[str, Dict[str, Any]] = {
    # Coins
    "penny": {
        "type": "coin",
        "low": 0.01, "high": 200.0, "confidence": 72,
        "factors": ["year of minting", "mint mark", "condition/grade", "composition (copper vs. zinc)", "rare errors"],
        "action": "Check the year and mint mark. A 1909-S VDB Lincoln cent can be worth $700+; most modern pennies are face value.",
    },
    "quarter": {
        "type": "coin",
        "low": 0.25, "high": 500.0, "confidence": 70,
        "factors": ["year", "mint mark", "condition", "silver content (pre-1965)", "key dates"],
        "action": "Pre-1965 quarters contain 90% silver and are worth $4+ for melt. Key dates like the 1932-D can be worth thousands.",
    },
    "silver dollar": {
        "type": "coin",
        "low": 20.0, "high": 5000.0, "confidence": 68,
        "factors": ["year", "mint mark", "grade", "silver content", "rare varieties"],
        "action": "Morgan and Peace dollars are popular collectibles. Have it graded by PCGS or NGC to maximize value.",
    },
    "gold coin": {
        "type": "coin",
        "low": 500.0, "high": 50000.0, "confidence": 75,
        "factors": ["gold purity", "weight", "year", "condition", "rarity"],
        "action": "Verify gold content and have authenticated by a reputable numismatist or grading service.",
    },
    # Antiques
    "antique furniture": {
        "type": "antique",
        "low": 100.0, "high": 50000.0, "confidence": 60,
        "factors": ["age (100+ years)", "maker / provenance", "wood type", "condition", "style period"],
        "action": "Look for maker marks on the underside. Original hardware and finish increases value significantly.",
    },
    "antique clock": {
        "type": "antique",
        "low": 50.0, "high": 10000.0, "confidence": 62,
        "factors": ["maker", "movement type", "age", "condition", "originality"],
        "action": "Research the maker's mark. Clocks by Seth Thomas or Howard Miller carry premium value.",
    },
    "antique jewelry": {
        "type": "antique",
        "low": 50.0, "high": 100000.0, "confidence": 65,
        "factors": ["metal type", "gemstones", "maker/designer", "era", "condition"],
        "action": "Have gemstones independently appraised. Hallmarks can identify the maker and metal purity.",
    },
    "vintage painting": {
        "type": "art",
        "low": 50.0, "high": 500000.0, "confidence": 50,
        "factors": ["artist", "provenance", "condition", "subject matter", "size"],
        "action": "Check for artist signature and any gallery labels on the back. Art appraisers can provide a certified valuation.",
    },
    "vintage watch": {
        "type": "collectible",
        "low": 100.0, "high": 200000.0, "confidence": 68,
        "factors": ["brand (Rolex, Patek, Omega)", "model reference", "year", "condition", "originality"],
        "action": "Rolex, Patek Philippe, and vintage Omega watches can command premium prices. Avoid polishing the case.",
    },
    "sports card": {
        "type": "collectible",
        "low": 0.10, "high": 10000000.0, "confidence": 55,
        "factors": ["player", "year", "set", "rookie card", "grade (PSA/Beckett)", "population"],
        "action": "Submit valuable cards to PSA or Beckett for grading. A PSA 10 rookie card of a Hall of Famer can be worth thousands.",
    },
    "comic book": {
        "type": "collectible",
        "low": 1.0, "high": 500000.0, "confidence": 58,
        "factors": ["issue number", "first appearance", "condition/grade", "publisher", "era"],
        "action": "Action Comics #1 and Amazing Fantasy #15 are the most valuable. Have key issues graded by CGC.",
    },
    "vinyl record": {
        "type": "collectible",
        "low": 1.0, "high": 10000.0, "confidence": 60,
        "factors": ["artist", "label pressing", "year", "condition (grading)", "original vs. reissue"],
        "action": "Original pressings on desirable labels (Blue Note, Sun Records) are most valuable. Check Discogs for pricing.",
    },
    "stamp": {
        "type": "collectible",
        "low": 0.01, "high": 5000000.0, "confidence": 55,
        "factors": ["country of origin", "year", "printing errors", "condition", "centering"],
        "action": "The British Guiana 1¢ Magenta is the world's most valuable stamp. Have rare stamps certified by APS or PSE.",
    },
    "antique toy": {
        "type": "collectible",
        "low": 5.0, "high": 50000.0, "confidence": 58,
        "factors": ["brand", "year", "condition", "original packaging", "rarity"],
        "action": "Original packaging and mint condition dramatically increase value. Hot Wheels and GI Joe rarities are highly sought.",
    },
    "vintage camera": {
        "type": "collectible",
        "low": 20.0, "high": 5000.0, "confidence": 65,
        "factors": ["brand (Leica, Hasselblad)", "model", "condition", "working order", "accessories"],
        "action": "Leica cameras hold value best. Ensure the shutter and light seals are in good condition.",
    },
}


# ---------------------------------------------------------------------------
# Autonomous Trainer
# ---------------------------------------------------------------------------

class AutonomousTrainer:
    """
    Trains AI bots with job-specific skills and enables face/object recognition
    and item valuation capabilities.

    Buddy Bot upgrade propagation: when a skill is trained, all registered
    Buddy Bot instances are notified and upgraded automatically.
    """

    def __init__(self) -> None:
        self._sessions: List[TrainingSession] = []
        self._trained_skills: Dict[str, List[str]] = {}  # bot_name -> [skills]
        self._registered_buddy_bots: List[str] = []
        self._session_counter: int = 0
        self._valuation_kb = dict(_ITEM_VALUATION_KB)

    # -----------------------------------------------------------------------
    # Buddy Bot registry
    # -----------------------------------------------------------------------

    def register_buddy_bot(self, bot_id: str) -> None:
        """Register a Buddy Bot instance to receive automatic upgrades."""
        if bot_id not in self._registered_buddy_bots:
            self._registered_buddy_bots.append(bot_id)

    def list_buddy_bots(self) -> List[str]:
        """Return all registered Buddy Bot IDs."""
        return list(self._registered_buddy_bots)

    def _propagate_skill_to_all_buddy_bots(self, skill_name: str) -> List[str]:
        """Push a newly trained skill to all registered Buddy Bots."""
        upgraded = []
        for bot_id in self._registered_buddy_bots:
            skills = self._trained_skills.setdefault(bot_id, [])
            if skill_name not in skills:
                skills.append(skill_name)
                upgraded.append(bot_id)
        return upgraded

    # -----------------------------------------------------------------------
    # Job skill training
    # -----------------------------------------------------------------------

    def train_job_skill(
        self,
        bot_name: str,
        skill_name: str,
        domain: str,
        examples: int = 100,
    ) -> TrainingSession:
        """
        Train a bot to perform a specific job skill.

        Parameters
        ----------
        bot_name : str
            Identifier of the bot being trained.
        skill_name : str
            Name of the skill (e.g. "customer service", "invoice processing").
        domain : str
            Industry domain (e.g. "Healthcare", "Finance").
        examples : int
            Number of training examples to simulate.

        Returns
        -------
        TrainingSession
        """
        self._session_counter += 1
        session_id = f"train_{self._session_counter:05d}"

        # Simulate accuracy based on example count
        accuracy = min(95.0, 55.0 + (examples / 100.0) * 20.0)

        session = TrainingSession(
            session_id=session_id,
            skill_name=skill_name,
            domain=domain,
            examples_used=examples,
            accuracy_pct=round(accuracy, 1),
            status="complete",
            notes=f"Bot '{bot_name}' trained on '{skill_name}' in '{domain}' domain.",
        )
        self._sessions.append(session)

        # Register skill on this bot
        skills = self._trained_skills.setdefault(bot_name, [])
        if skill_name not in skills:
            skills.append(skill_name)

        # Propagate to all registered Buddy Bots
        self._propagate_skill_to_all_buddy_bots(skill_name)

        return session

    def get_bot_skills(self, bot_name: str) -> List[str]:
        """Return all skills a given bot has been trained on."""
        return list(self._trained_skills.get(bot_name, []))

    def list_sessions(self) -> List[TrainingSession]:
        """Return all training sessions recorded."""
        return list(self._sessions)

    # -----------------------------------------------------------------------
    # Face recognition training
    # -----------------------------------------------------------------------

    def train_face_recognition(self, bot_name: str, num_faces: int = 50) -> TrainingSession:
        """
        Train a bot to recognize human faces.

        Parameters
        ----------
        bot_name : str
            Identifier of the bot being trained.
        num_faces : int
            Number of face samples to train on.
        """
        return self.train_job_skill(
            bot_name=bot_name,
            skill_name="face_recognition",
            domain="Computer Vision",
            examples=num_faces,
        )

    # -----------------------------------------------------------------------
    # Object recognition training
    # -----------------------------------------------------------------------

    def train_object_recognition(
        self,
        bot_name: str,
        object_classes: List[str],
        examples_per_class: int = 100,
    ) -> TrainingSession:
        """
        Train a bot to identify specific object classes.

        Parameters
        ----------
        bot_name : str
            Identifier of the bot being trained.
        object_classes : List[str]
            List of object categories to recognise (e.g. ["coin", "antique"]).
        examples_per_class : int
            Training examples per class.
        """
        total_examples = len(object_classes) * examples_per_class
        skill_name = f"object_recognition:{'|'.join(object_classes)}"
        return self.train_job_skill(
            bot_name=bot_name,
            skill_name=skill_name,
            domain="Computer Vision",
            examples=total_examples,
        )

    # -----------------------------------------------------------------------
    # Item valuation
    # -----------------------------------------------------------------------

    def valuate_item(self, item_name: str) -> ItemValuation:
        """
        Estimate the value of an item such as a penny, antique, or collectible.

        Parameters
        ----------
        item_name : str
            Name of the item to evaluate (e.g. "penny", "antique clock").

        Returns
        -------
        ItemValuation
        """
        key = item_name.lower().strip()
        # Try exact match first, then partial match
        record = self._valuation_kb.get(key)
        if record is None:
            for kb_key, kb_val in self._valuation_kb.items():
                if kb_key in key or key in kb_key:
                    record = kb_val
                    break

        if record is None:
            # Generic fallback for unknown items
            return ItemValuation(
                item_name=item_name,
                item_type="unknown",
                estimated_value_usd_low=1.0,
                estimated_value_usd_high=10000.0,
                confidence_pct=30.0,
                value_factors=["rarity", "condition", "age", "provenance", "demand"],
                recommended_action=(
                    "Item not found in the DreamCo valuation database. "
                    "Consider consulting a professional appraiser for an accurate valuation."
                ),
            )

        return ItemValuation(
            item_name=item_name,
            item_type=record["type"],
            estimated_value_usd_low=record["low"],
            estimated_value_usd_high=record["high"],
            confidence_pct=float(record["confidence"]),
            value_factors=list(record["factors"]),
            recommended_action=record["action"],
        )

    def list_valuatable_items(self) -> List[str]:
        """Return all item names in the valuation knowledge base."""
        return sorted(self._valuation_kb.keys())
