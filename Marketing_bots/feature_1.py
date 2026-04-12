# Feature 1: Marketing bot for social media posting.
# Functionality: Automates posting updates to social media channels.
# Use Cases: Businesses maintaining an active online presence.
#
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
# See framework/global_ai_sources_flow.py for the full pipeline specification.
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from framework import GlobalAISourcesFlow


class SocialMediaPoster:
    def __init__(self):
        self.flow = GlobalAISourcesFlow(bot_name="SocialMediaPoster")
        self._posts = []

    def create_post(self, platform, content, scheduled_time=None):
        post = {"id": f"post_{len(self._posts)+1}", "platform": platform, "content": content, "scheduled_time": scheduled_time, "status": "draft"}
        self._posts.append(post)
        return post

    def publish_post(self, post_id):
        for p in self._posts:
            if p["id"] == post_id:
                p["status"] = "published"
                return True
        return False

    def get_posts(self, platform=None):
        if platform:
            return [p for p in self._posts if p["platform"] == platform]
        return list(self._posts)

    def run(self):
        return self.flow.run_pipeline(raw_data={"bot": "SocialMediaPoster", "posts": len(self._posts)}, learning_method="supervised")
