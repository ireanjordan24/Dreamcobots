"""
Pillar 5 — Communities of Practice.

Fosters collaborative channels and ideation spaces that accelerate AI
adoption scaling through shared learning, peer recognition, and
structured knowledge exchange.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
import uuid


# ---------------------------------------------------------------------------
# Domain models
# ---------------------------------------------------------------------------

@dataclass
class Community:
    """A Community of Practice channel."""

    community_id: str
    name: str
    description: str
    channel_type: str    # "slack" | "discord" | "github_discussion" | "forum" | "workshop_series"
    focus_area: str      # e.g. "revenue_bots", "ai_governance", "scaling", "onboarding"
    member_ids: list[str] = field(default_factory=list)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict:
        return {
            "community_id": self.community_id,
            "name": self.name,
            "description": self.description,
            "channel_type": self.channel_type,
            "focus_area": self.focus_area,
            "member_count": len(self.member_ids),
            "created_at": self.created_at,
        }


@dataclass
class IdeationPost:
    """A collaborative idea or knowledge contribution in a community."""

    post_id: str
    community_id: str
    author_id: str
    title: str
    body: str
    tags: list[str] = field(default_factory=list)
    upvotes: int = 0
    posted_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict:
        return {
            "post_id": self.post_id,
            "community_id": self.community_id,
            "author_id": self.author_id,
            "title": self.title,
            "body": self.body,
            "tags": list(self.tags),
            "upvotes": self.upvotes,
            "posted_at": self.posted_at,
        }


# ---------------------------------------------------------------------------
# Valid values
# ---------------------------------------------------------------------------

VALID_CHANNEL_TYPES = {
    "slack", "discord", "github_discussion", "forum", "workshop_series"
}


# ---------------------------------------------------------------------------
# Communities of Practice engine
# ---------------------------------------------------------------------------

class CommunityOfPractice:
    """
    Manages AI Communities of Practice for collaborative knowledge exchange.

    Provides community creation, membership management, ideation posts, and
    contribution analytics.
    """

    def __init__(self) -> None:
        self._communities: dict[str, Community] = {}
        self._posts: list[IdeationPost] = []

    # ------------------------------------------------------------------
    # Community management
    # ------------------------------------------------------------------

    def create_community(
        self,
        name: str,
        description: str,
        channel_type: str,
        focus_area: str,
    ) -> Community:
        """Create a new Community of Practice channel."""
        if channel_type not in VALID_CHANNEL_TYPES:
            raise ValueError(
                f"Invalid channel_type '{channel_type}'. "
                f"Valid: {sorted(VALID_CHANNEL_TYPES)}"
            )
        community_id = f"cop-{uuid.uuid4().hex[:8]}"
        community = Community(
            community_id=community_id,
            name=name,
            description=description,
            channel_type=channel_type,
            focus_area=focus_area,
        )
        self._communities[community_id] = community
        return community

    def get_community(self, community_id: str) -> Community:
        """Return a community by ID."""
        if community_id not in self._communities:
            raise KeyError(f"Community '{community_id}' not found.")
        return self._communities[community_id]

    def list_communities(
        self, focus_area: Optional[str] = None
    ) -> list[dict]:
        """Return all communities, optionally filtered by focus area."""
        communities = self._communities.values()
        if focus_area is not None:
            communities = [c for c in communities if c.focus_area == focus_area]
        return [c.to_dict() for c in communities]

    # ------------------------------------------------------------------
    # Membership
    # ------------------------------------------------------------------

    def join_community(self, community_id: str, user_id: str) -> None:
        """Add a user to a community."""
        community = self.get_community(community_id)
        if user_id not in community.member_ids:
            community.member_ids.append(user_id)

    def leave_community(self, community_id: str, user_id: str) -> None:
        """Remove a user from a community."""
        community = self.get_community(community_id)
        if user_id in community.member_ids:
            community.member_ids.remove(user_id)

    def get_members(self, community_id: str) -> list[str]:
        """Return the list of member IDs for a community."""
        return list(self.get_community(community_id).member_ids)

    # ------------------------------------------------------------------
    # Ideation posts
    # ------------------------------------------------------------------

    def post_idea(
        self,
        community_id: str,
        author_id: str,
        title: str,
        body: str,
        tags: Optional[list[str]] = None,
    ) -> IdeationPost:
        """Submit a new ideation post to a community."""
        self.get_community(community_id)  # validate community exists
        post = IdeationPost(
            post_id=f"post-{uuid.uuid4().hex[:8]}",
            community_id=community_id,
            author_id=author_id,
            title=title,
            body=body,
            tags=tags or [],
        )
        self._posts.append(post)
        return post

    def upvote_post(self, post_id: str) -> None:
        """Upvote an ideation post."""
        for post in self._posts:
            if post.post_id == post_id:
                post.upvotes += 1
                return
        raise KeyError(f"Post '{post_id}' not found.")

    def list_posts(
        self,
        community_id: Optional[str] = None,
        top_n: Optional[int] = None,
    ) -> list[dict]:
        """
        Return posts, optionally filtered by community and ranked by upvotes.
        """
        posts = self._posts
        if community_id is not None:
            posts = [p for p in posts if p.community_id == community_id]
        posts = sorted(posts, key=lambda p: p.upvotes, reverse=True)
        if top_n is not None:
            posts = posts[:top_n]
        return [p.to_dict() for p in posts]

    # ------------------------------------------------------------------
    # Programme analytics
    # ------------------------------------------------------------------

    def collaboration_report(self) -> dict:
        """Return a summary of community collaboration activity."""
        total_members = sum(
            len(c.member_ids) for c in self._communities.values()
        )
        top_post = max(self._posts, key=lambda p: p.upvotes) if self._posts else None
        return {
            "total_communities": len(self._communities),
            "total_members": total_members,
            "total_posts": len(self._posts),
            "top_post_upvotes": top_post.upvotes if top_post else 0,
            "top_post_title": top_post.title if top_post else None,
        }
