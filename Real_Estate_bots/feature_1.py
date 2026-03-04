"""
Feature 1: Real estate bot for property listings.
Functionality: Aggregates property listings from various sources.
Use Cases: Home buyers looking for listings.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from industry.real_estate import Property, RealEstateAI
import uuid


class PropertyListingBot(RealEstateAI):
    """Aggregates and presents property listings for home buyers."""

    def add_sample_listings(self) -> None:
        """Populate the bot with a representative set of sample listings."""
        samples = [
            Property(str(uuid.uuid4()), "123 Oak St", "Austin", "TX", "78701", "sale", 450000, 3, 2.0, 1800),
            Property(str(uuid.uuid4()), "456 Pine Ave", "Austin", "TX", "78702", "sale", 320000, 2, 1.0, 1100),
            Property(str(uuid.uuid4()), "789 Elm Rd", "Dallas", "TX", "75201", "rent", 2200, 2, 2.0, 950),
        ]
        for p in samples:
            self.add_property(p)

    def summary(self) -> str:
        """Return a human-readable summary of current listings."""
        all_props = list(self._properties.values())
        lines = [f"{'ADDRESS':<25} {'CITY':<12} {'TYPE':<6} {'PRICE':>10}"]
        lines.append("-" * 58)
        for p in all_props:
            price_str = f"${p.price:,.0f}"
            lines.append(f"{p.address:<25} {p.city:<12} {p.listing_type:<6} {price_str:>10}")
        return "\n".join(lines)


if __name__ == "__main__":
    bot = PropertyListingBot()
    bot.start()
    bot.add_sample_listings()
    print(bot.summary())
    print("\nFor sale in Austin:")
    results = bot.search_properties(city="Austin", listing_type="sale")
    for p in results:
        print(f"  {p.address} – ${p.price:,.0f}")
    bot.stop()