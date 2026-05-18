"""
Deployment Engine — one-click website deployment to major cloud platforms.

Supports AWS (S3 + CloudFront), Vercel, Netlify, GitHub Pages, local servers,
and Docker containers. Competes with Hostinger, GoDaddy, and Shopify hosting.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional

from framework import GlobalAISourcesFlow  # noqa: F401


class DeployTarget(Enum):
    """Supported deployment targets."""

    AWS = "aws"
    VERCEL = "vercel"
    NETLIFY = "netlify"
    GITHUB_PAGES = "github_pages"
    CLOUDFLARE = "cloudflare"
    DOCKER = "docker"
    LOCAL = "local"


DEPLOY_TARGETS: List[str] = [dt.value for dt in DeployTarget]

_TARGET_URLS: dict = {
    DeployTarget.AWS: "https://{id}.s3-website.us-east-1.amazonaws.com",
    DeployTarget.VERCEL: "https://{id}.vercel.app",
    DeployTarget.NETLIFY: "https://{id}.netlify.app",
    DeployTarget.GITHUB_PAGES: "https://{id}.github.io",
    DeployTarget.CLOUDFLARE: "https://{id}.pages.dev",
    DeployTarget.DOCKER: "http://localhost:8080/{id}",
    DeployTarget.LOCAL: "http://localhost:3000",
}

_ESTIMATED_SECONDS: dict = {
    DeployTarget.AWS: 60,
    DeployTarget.VERCEL: 25,
    DeployTarget.NETLIFY: 30,
    DeployTarget.GITHUB_PAGES: 45,
    DeployTarget.CLOUDFLARE: 20,
    DeployTarget.DOCKER: 15,
    DeployTarget.LOCAL: 5,
}

_TARGET_FEATURES: dict = {
    DeployTarget.AWS: [
        "Global CDN (CloudFront)", "Custom domain", "SSL/TLS",
        "S3 static hosting", "Auto-scaling",
    ],
    DeployTarget.VERCEL: [
        "Edge network", "Custom domain", "SSL/TLS",
        "Preview deployments", "Serverless functions",
    ],
    DeployTarget.NETLIFY: [
        "Global CDN", "Custom domain", "SSL/TLS",
        "Form handling", "Netlify Functions", "Split testing",
    ],
    DeployTarget.GITHUB_PAGES: [
        "Free hosting", "Custom domain", "SSL/TLS", "GitHub Actions CI/CD",
    ],
    DeployTarget.CLOUDFLARE: [
        "Cloudflare edge", "Custom domain", "SSL/TLS",
        "Workers integration", "DDoS protection",
    ],
    DeployTarget.DOCKER: [
        "Container deployment", "Port mapping", "Volume support",
        "docker-compose ready",
    ],
    DeployTarget.LOCAL: [
        "Zero-config local server", "Hot-reload", "Debug mode",
    ],
}


class DeploymentEngineError(Exception):
    """Raised for invalid deployment operations."""


class DeploymentEngine:
    """One-click website deployment engine for DreamCo Website Builder.

    Usage::

        engine = DeploymentEngine()
        dep = engine.deploy("site_001", "my-site", "vercel")
        live = engine.simulate_live(dep["deployment_id"])
    """

    def __init__(self) -> None:
        self._deployments: dict = {}  # deployment_id -> record

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def deploy(
        self,
        site_id: str,
        site_name: str,
        target: str,
        custom_domain: Optional[str] = None,
        config: Optional[dict] = None,
    ) -> dict:
        """Initiate a deployment of *site_id* to *target*.

        Parameters
        ----------
        site_id:       Identifier of the website being deployed.
        site_name:     Human-readable site name (used in URL slug).
        target:        One of ``DEPLOY_TARGETS``.
        custom_domain: Optional custom domain to map.
        config:        Target-specific overrides.

        Returns
        -------
        dict  Deployment record with ``status = "DEPLOYING"``.
        """
        if target not in DEPLOY_TARGETS:
            raise DeploymentEngineError(
                f"Unknown deploy target '{target}'. Valid: {DEPLOY_TARGETS}"
            )

        dt_enum = DeployTarget(target)
        deployment_id = f"dep_{uuid.uuid4().hex[:12]}"
        slug = site_name.lower().replace(" ", "-")[:20]
        url_template = _TARGET_URLS[dt_enum]
        endpoint = url_template.format(id=slug)

        record = {
            "deployment_id": deployment_id,
            "site_id": site_id,
            "site_name": site_name,
            "target": target,
            "status": "DEPLOYING",
            "endpoint_url": endpoint,
            "custom_domain": custom_domain,
            "features": list(_TARGET_FEATURES.get(dt_enum, [])),
            "estimated_seconds": _ESTIMATED_SECONDS.get(dt_enum, 60),
            "config": dict(config) if config else {},
            "created_at": datetime.now(tz=timezone.utc).isoformat(),
            "live_at": None,
            "ssl_enabled": target != DeployTarget.LOCAL.value,
        }
        self._deployments[deployment_id] = record
        return {k: v for k, v in record.items() if k != "config"}

    def simulate_live(self, deployment_id: str) -> dict:
        """Simulate the deployment going LIVE (for testing/demos).

        Returns
        -------
        dict  ``{deployment_id, status, endpoint_url, live_at}``
        """
        record = self._get_deployment(deployment_id)
        record["status"] = "LIVE"
        record["live_at"] = datetime.now(tz=timezone.utc).isoformat()
        return {
            "deployment_id": deployment_id,
            "status": "LIVE",
            "endpoint_url": record["endpoint_url"],
            "live_at": record["live_at"],
        }

    def get_deployment(self, deployment_id: str) -> dict:
        """Return full deployment details.

        Returns
        -------
        dict
        """
        record = self._get_deployment(deployment_id)
        return {k: v for k, v in record.items() if k != "config"}

    def list_deployments(self, site_id: str) -> List[dict]:
        """Return all deployments for *site_id*.

        Returns
        -------
        list[dict]
        """
        return [
            {k: v for k, v in rec.items() if k != "config"}
            for rec in self._deployments.values()
            if rec["site_id"] == site_id
        ]

    def rollback(self, deployment_id: str) -> dict:
        """Roll back a LIVE deployment to ROLLED_BACK status.

        Returns
        -------
        dict
        """
        record = self._get_deployment(deployment_id)
        if record["status"] not in ("LIVE", "DEPLOYING"):
            raise DeploymentEngineError(
                f"Cannot roll back deployment with status '{record['status']}'."
            )
        record["status"] = "ROLLED_BACK"
        return {
            "deployment_id": deployment_id,
            "status": "ROLLED_BACK",
            "endpoint_url": record["endpoint_url"],
        }

    def get_targets_info(self) -> List[dict]:
        """Return information about all available deployment targets.

        Returns
        -------
        list[dict]
        """
        return [
            {
                "target": dt.value,
                "estimated_seconds": _ESTIMATED_SECONDS[dt],
                "features": _TARGET_FEATURES.get(dt, []),
            }
            for dt in DeployTarget
        ]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_deployment(self, deployment_id: str) -> dict:
        if deployment_id not in self._deployments:
            raise DeploymentEngineError(
                f"Deployment '{deployment_id}' not found."
            )
        return self._deployments[deployment_id]
