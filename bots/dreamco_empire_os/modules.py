"""
DreamCo Empire OS — Additional Modules

Implements the remaining Empire OS buttons as lightweight modules:
  - Divisions        — organise empire into specialised categories
  - AI Models Hub    — manage and switch pre-trained AI models
  - AI Ecosystem     — visualise relationships between AI agents
  - Crypto Tracker   — crypto asset and signal tracking
  - Payments Hub     — payment flow management
  - Biz Launch       — guided new-business launcher
  - Code Lab         — automation code sandbox
  - Loans & Deals    — financing and deal consolidation
  - Debug Intel      — bot error and bottleneck hub
  - Pricing Engine   — pricing optimisation
  - Connections      — API and integration registry
  - Time Capsule     — data archival and historical insights
  - Autonomy Control — empire-wide bot autonomy management
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
from framework import GlobalAISourcesFlow  # noqa: F401


# ==========================================================================
# Divisions
# ==========================================================================

class Divisions:
    """Organise empire bots and operations into named divisions."""

    def __init__(self) -> None:
        self._divisions: dict[str, dict] = {}

    def create_division(self, name: str, purpose: str, bot_names: Optional[list] = None) -> dict:
        self._divisions[name] = {
            "name": name,
            "purpose": purpose,
            "bots": bot_names or [],
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        return self._divisions[name]

    def add_bot(self, division_name: str, bot_name: str) -> dict:
        div = self._get(division_name)
        if bot_name not in div["bots"]:
            div["bots"].append(bot_name)
        return {"division": division_name, "bot_added": bot_name}

    def list_divisions(self) -> list:
        return list(self._divisions.values())

    def get_division(self, name: str) -> dict:
        return self._get(name)

    def _get(self, name: str) -> dict:
        if name not in self._divisions:
            raise KeyError(f"Division '{name}' not found.")
        return self._divisions[name]


# ==========================================================================
# AI Models Hub
# ==========================================================================

class ModelStatus(Enum):
    AVAILABLE = "available"
    DEPRECATED = "deprecated"
    BETA = "beta"


@dataclass
class AIModel:
    model_id: str
    name: str
    provider: str
    task: str
    version: str
    status: ModelStatus = ModelStatus.AVAILABLE
    active: bool = False
    registered_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class AIModelsHub:
    """Library and manager for AI models with version control and activation."""

    def __init__(self) -> None:
        self._models: dict[str, AIModel] = {}

    def register_model(
        self,
        model_id: str,
        name: str,
        provider: str,
        task: str,
        version: str = "1.0",
    ) -> dict:
        model = AIModel(model_id=model_id, name=name, provider=provider, task=task, version=version)
        self._models[model_id] = model
        return _model_to_dict(model)

    def activate_model(self, model_id: str) -> dict:
        model = self._get_model(model_id)
        model.active = True
        return {"model_id": model_id, "active": True}

    def deactivate_model(self, model_id: str) -> dict:
        model = self._get_model(model_id)
        model.active = False
        return {"model_id": model_id, "active": False}

    def list_models(self, active_only: bool = False) -> list:
        models = list(self._models.values())
        if active_only:
            models = [m for m in models if m.active]
        return [_model_to_dict(m) for m in models]

    def get_model(self, model_id: str) -> dict:
        return _model_to_dict(self._get_model(model_id))

    def _get_model(self, model_id: str) -> AIModel:
        if model_id not in self._models:
            raise KeyError(f"Model '{model_id}' not found.")
        return self._models[model_id]


def _model_to_dict(m: AIModel) -> dict:
    return {
        "model_id": m.model_id,
        "name": m.name,
        "provider": m.provider,
        "task": m.task,
        "version": m.version,
        "status": m.status.value,
        "active": m.active,
        "registered_at": m.registered_at,
    }


# ==========================================================================
# AI Ecosystem
# ==========================================================================

class OntologyState(Enum):
    DRAFT = "draft"
    STAGED = "staged"
    APPROVED = "approved"
    DEPRECATED = "deprecated"


@dataclass
class OntologyProposal:
    proposal_id: str
    layer: str
    action: str
    target_id: str
    payload: dict[str, Any]
    proposed_by: str
    state: OntologyState = OntologyState.DRAFT
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    staged_at: Optional[str] = None
    approved_at: Optional[str] = None
    rejected_reason: Optional[str] = None
    validation_errors: list[str] = field(default_factory=list)


class AIEcosystem:
    """
    Governed ontology-driven AI ecosystem.

    Layers:
      1. Core ontology (immutable)
      2. Domain ontologies
      3. Bot ontologies
      4. Runtime graph (dynamic, no direct core mutation)
    """

    CORE_ONTOLOGY_CONCEPTS: tuple[str, ...] = (
        "agent",
        "capability",
        "workflow",
        "memory",
        "tool",
        "division",
        "revenuestream",
        "goal",
        "permission",
        "event",
    )

    DEFAULT_SYNONYMS: dict[str, str] = {
        "leadgeneratorbot": "lead_generation_bot",
        "prospecthunter": "lead_generation_bot",
        "customeracquisitionai": "lead_generation_bot",
        "realtorbot": "real_estate_bot",
    }

    def __init__(self) -> None:
        # Layer 1 — immutable core ontology
        self._core_ontology: dict[str, Any] = {
            "concepts": list(self.CORE_ONTOLOGY_CONCEPTS),
            "version": "1.0.0",
            "state": OntologyState.APPROVED.value,
            "immutable": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        # Layer 2/3 ontologies
        self._domain_ontologies: dict[str, dict[str, Any]] = {}
        self._bot_ontologies: dict[str, dict[str, Any]] = {}

        # Layer 4 runtime knowledge graph
        self._nodes: dict[str, dict] = {}
        self._edges: list = []

        # Canonical taxonomy and capabilities
        self._canonical_terms: dict[str, str] = dict(self.DEFAULT_SYNONYMS)
        self._capabilities: dict[str, dict[str, Any]] = {}
        self._agent_capabilities: dict[str, set[str]] = {}

        # Governance pipeline
        self._proposals: dict[str, OntologyProposal] = {}
        self._proposal_counter = 0
        self._ontology_versions: dict[str, list[dict[str, Any]]] = {
            "domain": [],
            "bot": [],
        }
        self._pinned_versions: dict[str, str] = {}

        # Guardrails
        self._guardrails: dict[str, Any] = {
            "kill_switch": False,
            "rate_limit_per_minute": 120,
            "workflow_budget_limit": 1_000.0,
            "manual_override_required": False,
        }
        self._execution_usage: dict[str, dict[str, Any]] = {}
        self._agent_permissions: dict[str, set[str]] = {}

        # Memory separation
        self._memory: dict[str, Any] = {
            "runtime": {},
            "semantic": {},
            "procedural": {},
            "economic": [],
        }

        # Observability and auditability
        self._event_log: list[dict[str, Any]] = []
        self._audit_log: list[dict[str, Any]] = []
        self._alerts: list[dict[str, Any]] = []

    @staticmethod
    def _slug(value: str) -> str:
        return "".join(ch for ch in value.lower() if ch.isalnum())

    def canonicalize_term(self, term: str) -> str:
        key = self._slug(term)
        return self._canonical_terms.get(key, term.strip().lower().replace(" ", "_"))

    def register_synonym(self, alias: str, canonical: str) -> dict:
        canonical_term = self.canonicalize_term(canonical)
        self._canonical_terms[self._slug(alias)] = canonical_term
        self._audit("synonym_registered", {"alias": alias, "canonical": canonical_term})
        return {"alias": alias, "canonical": canonical_term}

    def get_core_ontology(self) -> dict:
        return dict(self._core_ontology)

    def create_domain_ontology(
        self,
        domain_id: str,
        name: str,
        capabilities: Optional[list[str]] = None,
        version: str = "1.0.0",
        state: OntologyState = OntologyState.DRAFT,
    ) -> dict:
        entry = {
            "domain_id": domain_id,
            "name": self.canonicalize_term(name),
            "capabilities": sorted({self.canonicalize_term(c) for c in (capabilities or [])}),
            "version": version,
            "state": state.value,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self._domain_ontologies[domain_id] = entry
        self._record_version("domain", domain_id, entry)
        self._audit("domain_ontology_created", {"domain_id": domain_id, "version": version})
        return entry

    def create_bot_ontology(
        self,
        bot_id: str,
        name: str,
        domains: list[str],
        capabilities: Optional[list[str]] = None,
        version: str = "1.0.0",
        state: OntologyState = OntologyState.DRAFT,
    ) -> dict:
        for domain_id in domains:
            if domain_id not in self._domain_ontologies:
                raise KeyError(f"Domain ontology '{domain_id}' not found.")
        entry = {
            "bot_id": bot_id,
            "name": self.canonicalize_term(name),
            "domains": domains,
            "capabilities": sorted({self.canonicalize_term(c) for c in (capabilities or [])}),
            "version": version,
            "state": state.value,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self._bot_ontologies[bot_id] = entry
        self._record_version("bot", bot_id, entry)
        self._audit("bot_ontology_created", {"bot_id": bot_id, "version": version})
        return entry

    def list_domain_ontologies(self) -> list[dict]:
        return list(self._domain_ontologies.values())

    def list_bot_ontologies(self) -> list[dict]:
        return list(self._bot_ontologies.values())

    def propose_ontology_change(
        self,
        layer: str,
        action: str,
        target_id: str,
        payload: dict[str, Any],
        proposed_by: str = "runtime",
    ) -> dict:
        if layer == "core":
            raise PermissionError("Runtime cannot mutate core ontology directly.")
        if layer not in ("domain", "bot"):
            raise ValueError("Layer must be one of: domain, bot.")
        self._proposal_counter += 1
        proposal_id = f"proposal_{self._proposal_counter:06d}"
        proposal = OntologyProposal(
            proposal_id=proposal_id,
            layer=layer,
            action=action,
            target_id=target_id,
            payload=payload,
            proposed_by=proposed_by,
        )
        self._proposals[proposal_id] = proposal
        self._audit("ontology_change_proposed", {"proposal_id": proposal_id, "layer": layer, "action": action})
        return self._proposal_to_dict(proposal)

    def validate_proposal(self, proposal_id: str) -> dict:
        proposal = self._get_proposal(proposal_id)
        errors: list[str] = []
        if proposal.layer == "domain" and proposal.action == "upsert":
            if "name" not in proposal.payload:
                errors.append("Domain upsert requires 'name'.")
        if proposal.layer == "bot" and proposal.action == "upsert":
            domains = proposal.payload.get("domains", [])
            missing = [d for d in domains if d not in self._domain_ontologies]
            if missing:
                errors.append(f"Unknown domains: {missing}")
        proposal.validation_errors = errors
        self._audit("ontology_proposal_validated", {"proposal_id": proposal_id, "valid": len(errors) == 0})
        return {
            "proposal_id": proposal_id,
            "valid": len(errors) == 0,
            "errors": errors,
        }

    def stage_proposal(self, proposal_id: str, reviewer: str = "governance") -> dict:
        proposal = self._get_proposal(proposal_id)
        validation = self.validate_proposal(proposal_id)
        if not validation["valid"]:
            raise ValueError(f"Proposal '{proposal_id}' failed validation: {validation['errors']}")
        proposal.state = OntologyState.STAGED
        proposal.staged_at = datetime.now(timezone.utc).isoformat()
        self._audit("ontology_proposal_staged", {"proposal_id": proposal_id, "reviewer": reviewer})
        return self._proposal_to_dict(proposal)

    def approve_proposal(self, proposal_id: str, approver: str = "governance") -> dict:
        proposal = self._get_proposal(proposal_id)
        if proposal.state != OntologyState.STAGED:
            raise ValueError("Proposal must be staged before approval.")
        if proposal.layer == "domain":
            entry = self.create_domain_ontology(
                domain_id=proposal.target_id,
                name=proposal.payload["name"],
                capabilities=proposal.payload.get("capabilities", []),
                version=proposal.payload.get("version", "1.0.0"),
                state=OntologyState.APPROVED,
            )
            self._pinned_versions[f"domain:{proposal.target_id}"] = entry["version"]
        elif proposal.layer == "bot":
            entry = self.create_bot_ontology(
                bot_id=proposal.target_id,
                name=proposal.payload["name"],
                domains=proposal.payload.get("domains", []),
                capabilities=proposal.payload.get("capabilities", []),
                version=proposal.payload.get("version", "1.0.0"),
                state=OntologyState.APPROVED,
            )
            self._pinned_versions[f"bot:{proposal.target_id}"] = entry["version"]
        else:
            raise ValueError(f"Unsupported proposal layer '{proposal.layer}'.")
        proposal.state = OntologyState.APPROVED
        proposal.approved_at = datetime.now(timezone.utc).isoformat()
        self._audit("ontology_proposal_approved", {"proposal_id": proposal_id, "approver": approver})
        return self._proposal_to_dict(proposal)

    def reject_proposal(self, proposal_id: str, reason: str) -> dict:
        proposal = self._get_proposal(proposal_id)
        proposal.rejected_reason = reason
        proposal.state = OntologyState.DEPRECATED
        self._audit("ontology_proposal_rejected", {"proposal_id": proposal_id, "reason": reason})
        return self._proposal_to_dict(proposal)

    def rollback_ontology(self, layer: str, target_id: str, version: str) -> dict:
        if layer not in ("domain", "bot"):
            raise ValueError("Layer must be one of: domain, bot.")
        history = self._ontology_versions[layer]
        candidates = [
            item for item in history
            if item["target_id"] == target_id and item["snapshot"].get("version") == version
        ]
        if not candidates:
            raise KeyError(f"No {layer} ontology version '{version}' for '{target_id}'.")
        latest = candidates[-1]["snapshot"]
        if layer == "domain":
            self._domain_ontologies[target_id] = dict(latest)
        else:
            self._bot_ontologies[target_id] = dict(latest)
        self._pinned_versions[f"{layer}:{target_id}"] = version
        self._audit("ontology_rolled_back", {"layer": layer, "target_id": target_id, "version": version})
        return {"layer": layer, "target_id": target_id, "version": version, "rolled_back": True}

    def register_capability(
        self,
        capability_id: str,
        name: str,
        domain: str,
        version: str = "1.0.0",
        state: OntologyState = OntologyState.APPROVED,
    ) -> dict:
        entry = {
            "capability_id": capability_id,
            "name": self.canonicalize_term(name),
            "domain": domain,
            "version": version,
            "state": state.value,
            "registered_at": datetime.now(timezone.utc).isoformat(),
        }
        self._capabilities[capability_id] = entry
        self._audit("capability_registered", {"capability_id": capability_id, "domain": domain})
        return entry

    def assign_capability(self, agent_id: str, capability_id: str) -> dict:
        if agent_id not in self._nodes:
            raise KeyError(f"Agent '{agent_id}' not found.")
        if capability_id not in self._capabilities:
            raise KeyError(f"Capability '{capability_id}' not found.")
        self._agent_capabilities.setdefault(agent_id, set()).add(capability_id)
        self._audit("capability_assigned", {"agent_id": agent_id, "capability_id": capability_id})
        return {"agent_id": agent_id, "capability_id": capability_id, "assigned": True}

    def set_agent_permissions(self, agent_id: str, permissions: list[str]) -> dict:
        if agent_id not in self._nodes:
            raise KeyError(f"Agent '{agent_id}' not found.")
        self._agent_permissions[agent_id] = set(permissions)
        self._audit("agent_permissions_set", {"agent_id": agent_id, "permissions": permissions})
        return {"agent_id": agent_id, "permissions": sorted(self._agent_permissions[agent_id])}

    def configure_guardrails(
        self,
        *,
        kill_switch: Optional[bool] = None,
        rate_limit_per_minute: Optional[int] = None,
        workflow_budget_limit: Optional[float] = None,
        manual_override_required: Optional[bool] = None,
    ) -> dict:
        if kill_switch is not None:
            self._guardrails["kill_switch"] = kill_switch
        if rate_limit_per_minute is not None:
            self._guardrails["rate_limit_per_minute"] = max(1, int(rate_limit_per_minute))
        if workflow_budget_limit is not None:
            self._guardrails["workflow_budget_limit"] = max(0.0, float(workflow_budget_limit))
        if manual_override_required is not None:
            self._guardrails["manual_override_required"] = manual_override_required
        self._audit("guardrails_configured", dict(self._guardrails))
        return dict(self._guardrails)

    def emergency_stop(self, reason: str) -> dict:
        self._guardrails["kill_switch"] = True
        alert = {"kind": "kill_switch", "reason": reason, "timestamp": datetime.now(timezone.utc).isoformat()}
        self._alerts.append(alert)
        self._audit("kill_switch_enabled", {"reason": reason})
        return {"kill_switch": True, "reason": reason}

    def clear_emergency_stop(self) -> dict:
        self._guardrails["kill_switch"] = False
        self._audit("kill_switch_disabled", {})
        return {"kill_switch": False}

    def authorize_execution(
        self,
        agent_id: str,
        operation: str,
        estimated_cost_usd: float = 0.0,
        required_permissions: Optional[list[str]] = None,
        override: bool = False,
    ) -> dict:
        if agent_id not in self._nodes:
            raise KeyError(f"Agent '{agent_id}' not found.")
        if self._guardrails["kill_switch"] and not override:
            return {"allowed": False, "reason": "kill_switch_enabled"}
        if self._guardrails["manual_override_required"] and not override:
            return {"allowed": False, "reason": "manual_override_required"}
        granted = self._agent_permissions.get(agent_id, set())
        required = set(required_permissions or [])
        if not required.issubset(granted):
            return {"allowed": False, "reason": "missing_permissions", "missing": sorted(required - granted)}
        usage = self._execution_usage.setdefault(agent_id, {"count": 0, "cost_usd": 0.0})
        if usage["count"] >= self._guardrails["rate_limit_per_minute"] and not override:
            return {"allowed": False, "reason": "rate_limit_exceeded"}
        if usage["cost_usd"] + estimated_cost_usd > self._guardrails["workflow_budget_limit"] and not override:
            return {"allowed": False, "reason": "workflow_budget_exceeded"}
        usage["count"] += 1
        usage["cost_usd"] = round(usage["cost_usd"] + estimated_cost_usd, 4)
        self._trace("execution_authorized", {
            "agent_id": agent_id,
            "operation": operation,
            "estimated_cost_usd": estimated_cost_usd,
        })
        return {"allowed": True, "agent_id": agent_id, "operation": operation}

    def record_memory(self, memory_type: str, key: str, value: Any) -> dict:
        if memory_type not in self._memory:
            raise ValueError("memory_type must be one of: runtime, semantic, procedural, economic")
        if memory_type == "economic":
            if not isinstance(value, dict):
                raise TypeError("Economic memory entries must be dict objects.")
            self._memory["economic"].append({"key": key, "value": value, "timestamp": datetime.now(timezone.utc).isoformat()})
        else:
            self._memory[memory_type][key] = value
        self._trace("memory_recorded", {"memory_type": memory_type, "key": key})
        self._audit("memory_recorded", {"memory_type": memory_type, "key": key})
        return {"memory_type": memory_type, "key": key, "recorded": True}

    def get_memory_snapshot(self) -> dict:
        return {
            "runtime": dict(self._memory["runtime"]),
            "semantic": dict(self._memory["semantic"]),
            "procedural": dict(self._memory["procedural"]),
            "economic": list(self._memory["economic"]),
        }

    def add_agent(self, agent_id: str, name: str, agent_type: str) -> dict:
        canonical_name = self.canonicalize_term(name)
        node = {
            "agent_id": agent_id,
            "name": canonical_name,
            "type": self.canonicalize_term(agent_type),
            "added_at": datetime.now(timezone.utc).isoformat(),
        }
        self._nodes[agent_id] = node
        self._agent_capabilities.setdefault(agent_id, set())
        self._agent_permissions.setdefault(agent_id, set())
        self._trace("agent_added", {"agent_id": agent_id, "name": canonical_name})
        return node

    def add_relationship(self, from_id: str, to_id: str, relationship: str, semantic_type: str = "runtime") -> dict:
        if from_id not in self._nodes or to_id not in self._nodes:
            raise KeyError("Both from_id and to_id must exist as agents before creating a relationship.")
        edge = {
            "from": from_id,
            "to": to_id,
            "relationship": self.canonicalize_term(relationship),
            "semantic_type": self.canonicalize_term(semantic_type),
            "added_at": datetime.now(timezone.utc).isoformat(),
        }
        self._edges.append(edge)
        self._trace("relationship_added", {"from": from_id, "to": to_id, "relationship": edge["relationship"]})
        return edge

    def get_graph(self) -> dict:
        return {
            "nodes": list(self._nodes.values()),
            "edges": self._edges,
            "total_agents": len(self._nodes),
            "total_relationships": len(self._edges),
            "governance": {
                "core_ontology_version": self._core_ontology["version"],
                "open_proposals": sum(1 for p in self._proposals.values() if p.state == OntologyState.DRAFT),
                "staged_proposals": sum(1 for p in self._proposals.values() if p.state == OntologyState.STAGED),
                "approved_proposals": sum(1 for p in self._proposals.values() if p.state == OntologyState.APPROVED),
            },
            "guardrails": dict(self._guardrails),
            "memory_counts": {
                "runtime": len(self._memory["runtime"]),
                "semantic": len(self._memory["semantic"]),
                "procedural": len(self._memory["procedural"]),
                "economic": len(self._memory["economic"]),
            },
        }

    def get_governance_summary(self) -> dict:
        return {
            "core_ontology": self.get_core_ontology(),
            "domain_ontologies": len(self._domain_ontologies),
            "bot_ontologies": len(self._bot_ontologies),
            "capabilities": len(self._capabilities),
            "proposals": {
                "draft": sum(1 for p in self._proposals.values() if p.state == OntologyState.DRAFT),
                "staged": sum(1 for p in self._proposals.values() if p.state == OntologyState.STAGED),
                "approved": sum(1 for p in self._proposals.values() if p.state == OntologyState.APPROVED),
                "deprecated": sum(1 for p in self._proposals.values() if p.state == OntologyState.DEPRECATED),
            },
            "pinned_versions": dict(self._pinned_versions),
            "alerts": list(self._alerts),
        }

    def get_event_trace(self, limit: int = 200) -> list[dict]:
        return self._event_log[-max(1, limit):]

    def get_audit_log(self, limit: int = 200) -> list[dict]:
        return self._audit_log[-max(1, limit):]

    def _proposal_to_dict(self, proposal: OntologyProposal) -> dict:
        return {
            "proposal_id": proposal.proposal_id,
            "layer": proposal.layer,
            "action": proposal.action,
            "target_id": proposal.target_id,
            "payload": proposal.payload,
            "proposed_by": proposal.proposed_by,
            "state": proposal.state.value,
            "created_at": proposal.created_at,
            "staged_at": proposal.staged_at,
            "approved_at": proposal.approved_at,
            "rejected_reason": proposal.rejected_reason,
            "validation_errors": list(proposal.validation_errors),
        }

    def _get_proposal(self, proposal_id: str) -> OntologyProposal:
        if proposal_id not in self._proposals:
            raise KeyError(f"Proposal '{proposal_id}' not found.")
        return self._proposals[proposal_id]

    def _record_version(self, layer: str, target_id: str, snapshot: dict[str, Any]) -> None:
        self._ontology_versions[layer].append({
            "target_id": target_id,
            "snapshot": dict(snapshot),
            "recorded_at": datetime.now(timezone.utc).isoformat(),
        })

    def _trace(self, event: str, payload: dict[str, Any]) -> None:
        self._event_log.append({
            "event": event,
            "payload": payload,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    def _audit(self, action: str, details: dict[str, Any]) -> None:
        self._audit_log.append({
            "action": action,
            "details": details,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })


# ==========================================================================
# Crypto Tracker
# ==========================================================================

@dataclass
class CryptoAsset:
    symbol: str
    name: str
    amount: float = 0.0
    purchase_price_usd: float = 0.0
    current_price_usd: float = 0.0

    @property
    def value_usd(self) -> float:
        return round(self.amount * self.current_price_usd, 2)

    @property
    def pnl_usd(self) -> float:
        return round(self.amount * (self.current_price_usd - self.purchase_price_usd), 2)


class CryptoTracker:
    """Track crypto holdings, signals, and market alerts."""

    def __init__(self) -> None:
        self._assets: dict[str, CryptoAsset] = {}
        self._signals: list = []

    def add_asset(self, symbol: str, name: str, amount: float, purchase_price_usd: float) -> dict:
        asset = CryptoAsset(symbol=symbol, name=name, amount=amount,
                            purchase_price_usd=purchase_price_usd,
                            current_price_usd=purchase_price_usd)
        self._assets[symbol] = asset
        return {"symbol": symbol, "name": name, "amount": amount}

    def update_price(self, symbol: str, current_price_usd: float) -> dict:
        if symbol not in self._assets:
            raise KeyError(f"Asset '{symbol}' not found.")
        self._assets[symbol].current_price_usd = current_price_usd
        asset = self._assets[symbol]
        return {"symbol": symbol, "current_price_usd": current_price_usd,
                "pnl_usd": asset.pnl_usd, "value_usd": asset.value_usd}

    def record_signal(self, symbol: str, signal: str, confidence_pct: float) -> dict:
        entry = {"symbol": symbol, "signal": signal, "confidence_pct": confidence_pct,
                 "timestamp": datetime.now(timezone.utc).isoformat()}
        self._signals.append(entry)
        return entry

    def get_portfolio(self) -> dict:
        total_value = sum(a.value_usd for a in self._assets.values())
        total_pnl = sum(a.pnl_usd for a in self._assets.values())
        return {
            "assets": [
                {"symbol": a.symbol, "name": a.name, "amount": a.amount,
                 "purchase_price_usd": a.purchase_price_usd,
                 "current_price_usd": a.current_price_usd,
                 "value_usd": a.value_usd, "pnl_usd": a.pnl_usd}
                for a in self._assets.values()
            ],
            "total_portfolio_value_usd": round(total_value, 2),
            "total_pnl_usd": round(total_pnl, 2),
            "signals": self._signals[-10:],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# ==========================================================================
# Payments Hub
# ==========================================================================

class PaymentStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


@dataclass
class Payment:
    payment_id: str
    from_party: str
    to_party: str
    amount_usd: float
    currency: str = "USD"
    status: PaymentStatus = PaymentStatus.PENDING
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class PaymentsHub:
    """Manage payment flows, automated billing, and revenue intake."""

    def __init__(self) -> None:
        self._payments: list[Payment] = []
        self._counter: int = 0

    def create_payment(self, from_party: str, to_party: str, amount_usd: float, currency: str = "USD") -> dict:
        self._counter += 1
        payment = Payment(
            payment_id=f"pay_{self._counter:06d}",
            from_party=from_party,
            to_party=to_party,
            amount_usd=round(amount_usd, 2),
            currency=currency,
        )
        self._payments.append(payment)
        return _payment_to_dict(payment)

    def complete_payment(self, payment_id: str) -> dict:
        payment = self._get_payment(payment_id)
        payment.status = PaymentStatus.COMPLETED
        return _payment_to_dict(payment)

    def fail_payment(self, payment_id: str) -> dict:
        payment = self._get_payment(payment_id)
        payment.status = PaymentStatus.FAILED
        return _payment_to_dict(payment)

    def get_summary(self) -> dict:
        completed = [p for p in self._payments if p.status == PaymentStatus.COMPLETED]
        return {
            "total_payments": len(self._payments),
            "completed": len(completed),
            "failed": sum(1 for p in self._payments if p.status == PaymentStatus.FAILED),
            "pending": sum(1 for p in self._payments if p.status == PaymentStatus.PENDING),
            "total_volume_usd": round(sum(p.amount_usd for p in completed), 2),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def list_payments(self) -> list:
        return [_payment_to_dict(p) for p in self._payments]

    def _get_payment(self, payment_id: str) -> Payment:
        for p in self._payments:
            if p.payment_id == payment_id:
                return p
        raise KeyError(f"Payment '{payment_id}' not found.")


def _payment_to_dict(p: Payment) -> dict:
    return {
        "payment_id": p.payment_id,
        "from_party": p.from_party,
        "to_party": p.to_party,
        "amount_usd": p.amount_usd,
        "currency": p.currency,
        "status": p.status.value,
        "created_at": p.created_at,
    }


# ==========================================================================
# Biz Launch
# ==========================================================================

class BizLaunch:
    """Guided launcher for new side businesses powered by DreamCo bots."""

    LAUNCH_TEMPLATES = {
        "saas": {
            "name": "SaaS Product",
            "steps": ["Validate idea", "Build MVP", "Set up payments", "Launch marketing bot", "Acquire first 10 customers"],
            "estimated_revenue_month_1_usd": 500.0,
        },
        "ecommerce": {
            "name": "E-Commerce Store",
            "steps": ["Pick niche", "Source products", "Set up store", "Automate fulfillment", "Run ads bot"],
            "estimated_revenue_month_1_usd": 800.0,
        },
        "ai_service": {
            "name": "AI Service Agency",
            "steps": ["Define service offer", "Build sample bot", "Create portfolio", "Find first client", "Automate delivery"],
            "estimated_revenue_month_1_usd": 1500.0,
        },
        "content": {
            "name": "Content Empire",
            "steps": ["Choose platform", "Content strategy", "Build AI writer bot", "Monetise via ads/sponsorships", "Scale"],
            "estimated_revenue_month_1_usd": 300.0,
        },
    }

    def __init__(self) -> None:
        self._launches: list = []

    def launch_business(self, business_type: str, name: str) -> dict:
        template = self.LAUNCH_TEMPLATES.get(business_type)
        if not template:
            raise ValueError(f"Unknown business type '{business_type}'. Options: {list(self.LAUNCH_TEMPLATES)}")
        launch = {
            "business_name": name,
            "type": business_type,
            "template": template["name"],
            "steps": template["steps"],
            "estimated_revenue_month_1_usd": template["estimated_revenue_month_1_usd"],
            "launched_at": datetime.now(timezone.utc).isoformat(),
            "status": "in_progress",
        }
        self._launches.append(launch)
        return launch

    def get_templates(self) -> list:
        return [
            {"type": k, "name": v["name"], "estimated_revenue_month_1_usd": v["estimated_revenue_month_1_usd"]}
            for k, v in self.LAUNCH_TEMPLATES.items()
        ]

    def list_launches(self) -> list:
        return list(self._launches)


# ==========================================================================
# Code Lab
# ==========================================================================

class CodeLab:
    """Sandbox for creating and testing automation scripts and bot prototypes."""

    def __init__(self) -> None:
        self._scripts: dict[str, dict] = {}
        self._run_log: list = []

    def save_script(self, script_id: str, name: str, language: str, code: str) -> dict:
        script = {
            "script_id": script_id,
            "name": name,
            "language": language,
            "code": code,
            "saved_at": datetime.now(timezone.utc).isoformat(),
            "run_count": 0,
        }
        self._scripts[script_id] = script
        return script

    def run_script(self, script_id: str) -> dict:
        if script_id not in self._scripts:
            raise KeyError(f"Script '{script_id}' not found.")
        script = self._scripts[script_id]
        script["run_count"] += 1
        result = {
            "script_id": script_id,
            "name": script["name"],
            "language": script["language"],
            "status": "executed",
            "ran_at": datetime.now(timezone.utc).isoformat(),
        }
        self._run_log.append(result)
        return result

    def list_scripts(self) -> list:
        return list(self._scripts.values())

    def get_run_log(self) -> list:
        return list(self._run_log)


# ==========================================================================
# Loans & Deals
# ==========================================================================

class LoansDeals:
    """Centralise financing tools and deal tracking."""

    def __init__(self) -> None:
        self._loans: list = []
        self._deals: list = []

    def add_loan(self, name: str, principal_usd: float, interest_rate_pct: float, term_months: int) -> dict:
        monthly_rate = interest_rate_pct / 100 / 12
        if monthly_rate > 0:
            monthly_payment = round(
                principal_usd * monthly_rate / (1 - (1 + monthly_rate) ** (-term_months)), 2
            )
        else:
            monthly_payment = round(principal_usd / term_months, 2)
        loan = {
            "name": name,
            "principal_usd": principal_usd,
            "interest_rate_pct": interest_rate_pct,
            "term_months": term_months,
            "monthly_payment_usd": monthly_payment,
            "total_repayment_usd": round(monthly_payment * term_months, 2),
            "added_at": datetime.now(timezone.utc).isoformat(),
        }
        self._loans.append(loan)
        return loan

    def add_deal(self, name: str, value_usd: float, partner: str, notes: str = "") -> dict:
        deal = {
            "name": name,
            "value_usd": value_usd,
            "partner": partner,
            "notes": notes,
            "added_at": datetime.now(timezone.utc).isoformat(),
        }
        self._deals.append(deal)
        return deal

    def get_summary(self) -> dict:
        total_loan = sum(l["principal_usd"] for l in self._loans)
        total_deal = sum(d["value_usd"] for d in self._deals)
        return {
            "total_loans": len(self._loans),
            "total_loan_principal_usd": round(total_loan, 2),
            "total_deals": len(self._deals),
            "total_deal_value_usd": round(total_deal, 2),
            "loans": self._loans,
            "deals": self._deals,
        }


# ==========================================================================
# Debug Intel
# ==========================================================================

class DebugLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class DebugIntel:
    """Bot debugging and troubleshooting hub."""

    def __init__(self) -> None:
        self._logs: list = []

    def log(self, bot_name: str, message: str, level: DebugLevel = DebugLevel.INFO) -> dict:
        entry = {
            "bot_name": bot_name,
            "message": message,
            "level": level.value,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._logs.append(entry)
        return entry

    def get_errors(self, bot_name: Optional[str] = None) -> list:
        errors = [l for l in self._logs if l["level"] in ("error", "critical")]
        if bot_name:
            errors = [l for l in errors if l["bot_name"] == bot_name]
        return errors

    def get_logs(self, level: Optional[DebugLevel] = None, limit: int = 50) -> list:
        logs = self._logs
        if level:
            logs = [l for l in logs if l["level"] == level.value]
        return logs[-limit:]

    def get_summary(self) -> dict:
        return {
            "total_logs": len(self._logs),
            "errors": sum(1 for l in self._logs if l["level"] == "error"),
            "warnings": sum(1 for l in self._logs if l["level"] == "warning"),
            "criticals": sum(1 for l in self._logs if l["level"] == "critical"),
        }


# ==========================================================================
# Pricing Engine
# ==========================================================================

class PricingEngine:
    """Set, test, and optimise pricing for bots and services."""

    def __init__(self) -> None:
        self._prices: dict[str, dict] = {}
        self._ab_tests: list = []

    def set_price(self, product_id: str, name: str, price_usd: float, tier: str = "standard") -> dict:
        entry = {"product_id": product_id, "name": name, "price_usd": round(price_usd, 2),
                 "tier": tier, "updated_at": datetime.now(timezone.utc).isoformat()}
        self._prices[product_id] = entry
        return entry

    def ab_test(self, product_id: str, price_a_usd: float, price_b_usd: float) -> dict:
        test = {
            "product_id": product_id,
            "price_a_usd": round(price_a_usd, 2),
            "price_b_usd": round(price_b_usd, 2),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self._ab_tests.append(test)
        return test

    def list_prices(self) -> list:
        return list(self._prices.values())


# ==========================================================================
# Connections
# ==========================================================================

class Connections:
    """Registry for API keys, third-party integrations, and bot-to-bot links."""

    def __init__(self) -> None:
        self._integrations: dict[str, dict] = {}

    def add_integration(self, integration_id: str, name: str, endpoint: str,
                        integration_type: str = "api") -> dict:
        entry = {
            "integration_id": integration_id,
            "name": name,
            "endpoint": endpoint,
            "type": integration_type,
            "status": "active",
            "added_at": datetime.now(timezone.utc).isoformat(),
        }
        self._integrations[integration_id] = entry
        return entry

    def disable_integration(self, integration_id: str) -> dict:
        if integration_id not in self._integrations:
            raise KeyError(f"Integration '{integration_id}' not found.")
        self._integrations[integration_id]["status"] = "disabled"
        return {"integration_id": integration_id, "status": "disabled"}

    def list_integrations(self, active_only: bool = False) -> list:
        intgs = list(self._integrations.values())
        if active_only:
            intgs = [i for i in intgs if i["status"] == "active"]
        return intgs


# ==========================================================================
# Time Capsule
# ==========================================================================

class TimeCapsule:
    """Archive of bot data, logs, and historical snapshots."""

    def __init__(self) -> None:
        self._archive: list = []

    def archive(self, label: str, data: dict) -> dict:
        entry = {
            "label": label,
            "data": data,
            "archived_at": datetime.now(timezone.utc).isoformat(),
        }
        self._archive.append(entry)
        return {"label": label, "archived_at": entry["archived_at"]}

    def retrieve(self, label: str) -> list:
        return [e for e in self._archive if e["label"] == label]

    def list_archives(self) -> list:
        return [{"label": e["label"], "archived_at": e["archived_at"]} for e in self._archive]


# ==========================================================================
# Autonomy Control
# ==========================================================================

class AutonomyMode(Enum):
    MANUAL = "manual"
    SEMI_AUTO = "semi_auto"
    FULL_AUTO = "full_auto"


class AutonomyControl:
    """Empire-wide bot autonomy management."""

    def __init__(self) -> None:
        self._bot_autonomy: dict[str, AutonomyMode] = {}
        self._global_mode: AutonomyMode = AutonomyMode.MANUAL

    def set_global_mode(self, mode: AutonomyMode) -> dict:
        self._global_mode = mode
        return {"global_autonomy_mode": mode.value}

    def set_bot_mode(self, bot_name: str, mode: AutonomyMode) -> dict:
        self._bot_autonomy[bot_name] = mode
        return {"bot": bot_name, "autonomy_mode": mode.value}

    def get_bot_mode(self, bot_name: str) -> str:
        return self._bot_autonomy.get(bot_name, self._global_mode).value

    def get_status(self) -> dict:
        return {
            "global_mode": self._global_mode.value,
            "bot_overrides": {k: v.value for k, v in self._bot_autonomy.items()},
            "total_bots_configured": len(self._bot_autonomy),
        }
