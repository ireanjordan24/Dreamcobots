"""
bots/dataforge/licensing/license_generator.py

LicenseGenerator – generates license text for DataForge datasets.
"""

import logging
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)

_CURRENT_YEAR = datetime.now(timezone.utc).year

_CC_VARIANTS: dict[str, dict[str, str]] = {
    "CC-BY-4.0": {
        "full_name": "Creative Commons Attribution 4.0 International",
        "url": "https://creativecommons.org/licenses/by/4.0/",
        "permissions": "copy, redistribute, adapt for any purpose, including commercially",
        "conditions": "give appropriate credit, link to license, indicate changes",
    },
    "CC-BY-SA-4.0": {
        "full_name": "Creative Commons Attribution-ShareAlike 4.0 International",
        "url": "https://creativecommons.org/licenses/by-sa/4.0/",
        "permissions": "copy, redistribute, adapt",
        "conditions": "give credit, share-alike under same license",
    },
    "CC-BY-NC-4.0": {
        "full_name": "Creative Commons Attribution-NonCommercial 4.0 International",
        "url": "https://creativecommons.org/licenses/by-nc/4.0/",
        "permissions": "copy, redistribute, adapt for non-commercial purposes",
        "conditions": "give credit, no commercial use",
    },
    "CC0-1.0": {
        "full_name": "Creative Commons Zero v1.0 Universal (Public Domain)",
        "url": "https://creativecommons.org/publicdomain/zero/1.0/",
        "permissions": "copy, distribute, use, modify, without restriction",
        "conditions": "none",
    },
}


class LicenseGenerator:
    """
    Generates license text and metadata for DataForge datasets.

    Supports Creative Commons variants, MIT, commercial, and custom
    data licenses.
    """

    def __init__(self, author: str = "DreamCobots DataForge") -> None:
        """
        Initialise the generator.

        Args:
            author: Default author/organization name embedded in licenses.
        """
        self.author = author
        logger.info("LicenseGenerator initialised (author='%s')", author)

    # ------------------------------------------------------------------
    # Creative Commons
    # ------------------------------------------------------------------

    def generate_cc_license(self, license_type: str = "CC-BY-4.0") -> str:
        """
        Generate a Creative Commons license notice.

        Args:
            license_type: One of ``"CC-BY-4.0"``, ``"CC-BY-SA-4.0"``,
                          ``"CC-BY-NC-4.0"``, or ``"CC0-1.0"``.
                          Defaults to ``"CC-BY-4.0"`` for unknown types.

        Returns:
            A formatted license notice string.
        """
        variant = _CC_VARIANTS.get(license_type.upper(), _CC_VARIANTS["CC-BY-4.0"])
        text = (
            f"Dataset License: {variant['full_name']}\n"
            f"Copyright (c) {_CURRENT_YEAR} {self.author}\n\n"
            f"You are free to:\n"
            f"  {variant['permissions']}\n\n"
            f"Under the following conditions:\n"
            f"  {variant['conditions']}\n\n"
            f"Full license text: {variant['url']}\n"
        )
        logger.debug("Generated CC license: %s", license_type)
        return text

    # ------------------------------------------------------------------
    # MIT
    # ------------------------------------------------------------------

    def generate_mit_license(self) -> str:
        """
        Generate an MIT License notice for datasets or accompanying code.

        Returns:
            The MIT License text as a string.
        """
        text = (
            f"MIT License\n\n"
            f"Copyright (c) {_CURRENT_YEAR} {self.author}\n\n"
            "Permission is hereby granted, free of charge, to any person obtaining a copy\n"
            "of this dataset and associated documentation files (the \"Dataset\"), to deal\n"
            "in the Dataset without restriction, including without limitation the rights\n"
            "to use, copy, modify, merge, publish, distribute, sublicense, and/or sell\n"
            "copies of the Dataset, and to permit persons to whom the Dataset is\n"
            "furnished to do so, subject to the following conditions:\n\n"
            "The above copyright notice and this permission notice shall be included in all\n"
            "copies or substantial portions of the Dataset.\n\n"
            'THE DATASET IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR\n'
            "IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,\n"
            "FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE\n"
            "AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER\n"
            "LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,\n"
            "OUT OF OR IN CONNECTION WITH THE DATASET OR THE USE OR OTHER DEALINGS IN THE\n"
            "DATASET.\n"
        )
        logger.debug("Generated MIT license")
        return text

    # ------------------------------------------------------------------
    # Commercial
    # ------------------------------------------------------------------

    def generate_commercial_license(self, terms: dict[str, Any] | None = None) -> str:
        """
        Generate a commercial dataset license.

        Args:
            terms: Optional dict overriding default commercial terms.  Recognised
                   keys: ``price_usd``, ``sublicensing_allowed``, ``expiry_years``,
                   ``permitted_uses``.

        Returns:
            A formatted commercial license notice string.
        """
        t = {
            "price_usd": 0.0,
            "sublicensing_allowed": False,
            "expiry_years": 1,
            "permitted_uses": ["research", "development", "commercial AI training"],
            **(terms or {}),
        }
        permitted_str = ", ".join(t["permitted_uses"])
        sublicense_str = "is" if t["sublicensing_allowed"] else "is NOT"
        text = (
            f"Commercial Dataset License\n\n"
            f"Copyright (c) {_CURRENT_YEAR} {self.author}\n\n"
            f"License Fee: ${t['price_usd']:.2f} USD\n"
            f"License Term: {t['expiry_years']} year(s) from date of purchase\n"
            f"Permitted Uses: {permitted_str}\n"
            f"Sublicensing {sublicense_str} permitted\n\n"
            "This license grants the licensee a non-exclusive right to access and\n"
            "use the dataset solely for the permitted uses listed above.\n"
            "Redistribution in original or modified form is prohibited without\n"
            "explicit written consent from the licensor.\n\n"
            f"Licensor: {self.author}\n"
            f"Effective Date: {datetime.now(timezone.utc).date()}\n"
        )
        logger.debug("Generated commercial license (price=$%.2f)", t["price_usd"])
        return text

    # ------------------------------------------------------------------
    # Custom data license
    # ------------------------------------------------------------------

    def generate_data_license(self, restrictions: list[str] | None = None) -> str:
        """
        Generate a custom data license with explicit restrictions.

        Args:
            restrictions: List of restriction strings to embed in the license.
                          Defaults to a conservative set if not provided.

        Returns:
            A formatted data license string.
        """
        default_restrictions = [
            "No redistribution without written consent",
            "No use in training discriminatory AI systems",
            "Attribution to DreamCobots DataForge required in all publications",
            "Must comply with applicable data protection regulations (GDPR, CCPA, HIPAA)",
        ]
        r = restrictions if restrictions else default_restrictions
        restriction_block = "\n".join(f"  - {item}" for item in r)

        text = (
            f"DataForge Data License\n\n"
            f"Copyright (c) {_CURRENT_YEAR} {self.author}\n\n"
            "This dataset is made available subject to the following terms and restrictions:\n\n"
            f"{restriction_block}\n\n"
            "Use of this dataset constitutes acceptance of these terms.\n"
            "For licensing inquiries contact: legal@dreamcobots.ai\n"
        )
        logger.debug("Generated custom data license with %d restrictions", len(r))
        return text
