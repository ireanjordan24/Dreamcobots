"""Ingestion sub-package: scrapers and dataset normalisation."""

from .dataset_normalizer import DatasetNormalizer
from .github_scraper import GitHubScraper
from .kaggle_scraper import KaggleScraper
from .paper_scraper import PaperScraper

__all__ = ["PaperScraper", "GitHubScraper", "KaggleScraper", "DatasetNormalizer"]
