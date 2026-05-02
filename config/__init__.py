"""DreamCo config package.

Makes the ``config/`` directory a proper Python package so that
``from config.settings import settings`` works regardless of what
other ``config.py`` files may be present in bot sub-directories on
``sys.path``.
"""
