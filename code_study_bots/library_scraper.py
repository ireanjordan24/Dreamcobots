"""
Library Scraper — discovers and catalogs coding libraries for every language globally.

Maintains an in-memory catalog of known libraries keyed by language, enriched
with metadata (purpose category, country of origin, documentation URL, known
exported symbols).  In production, ``scrape`` methods would call live package
registries (PyPI, npm, crates.io, Maven Central, etc.); here we provide a
rich stub-based simulation that drives the full ecosystem.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class LibraryRecord:
    """Metadata about a single coding library."""
    name: str
    language: str
    version: str
    purpose_category: str          # e.g. "data_science", "web_framework", "testing"
    country_of_origin: str         # ISO 3166-1 alpha-2 (e.g. "US", "DE")
    description: str
    doc_url: str
    exported_symbols: list[str] = field(default_factory=list)
    hidden_symbols: list[str] = field(default_factory=list)  # undocumented / private API
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "language": self.language,
            "version": self.version,
            "purpose_category": self.purpose_category,
            "country_of_origin": self.country_of_origin,
            "description": self.description,
            "doc_url": self.doc_url,
            "exported_symbols": self.exported_symbols,
            "hidden_symbols": self.hidden_symbols,
            "tags": self.tags,
        }


# ---------------------------------------------------------------------------
# Seed catalog (representative cross-language libraries)
# ---------------------------------------------------------------------------

_SEED_CATALOG: list[LibraryRecord] = [
    # Python — Data Science
    LibraryRecord("pandas", "python", "2.2.0", "data_science", "US",
                  "Powerful data manipulation and analysis library.",
                  "https://pandas.pydata.org/docs/",
                  exported_symbols=["DataFrame", "Series", "read_csv", "merge", "groupby",
                                    "pivot_table", "to_csv", "concat", "apply", "fillna"],
                  hidden_symbols=["_libs", "_hashtable", "_reduce", "core.internals"],
                  tags=["tabular", "etl", "analytics"]),
    LibraryRecord("numpy", "python", "1.26.0", "data_science", "US",
                  "Fundamental array computing for Python.",
                  "https://numpy.org/doc/",
                  exported_symbols=["ndarray", "zeros", "ones", "arange", "linspace",
                                    "dot", "linalg", "fft", "random", "broadcasting"],
                  hidden_symbols=["core._multiarray_umath", "_core.fromnumeric"],
                  tags=["numerical", "array", "linear-algebra"]),
    LibraryRecord("scipy", "python", "1.12.0", "data_science", "US",
                  "Fundamental algorithms for scientific computing.",
                  "https://docs.scipy.org/",
                  exported_symbols=["optimize", "integrate", "interpolate", "signal",
                                    "sparse", "stats", "linalg", "fft", "io"],
                  hidden_symbols=["_lib._testutils", "special._ufuncs"],
                  tags=["scientific", "optimization", "statistics"]),
    # Python — Machine Learning
    LibraryRecord("scikit-learn", "python", "1.4.0", "machine_learning", "FR",
                  "Simple and efficient tools for predictive data analysis.",
                  "https://scikit-learn.org/stable/",
                  exported_symbols=["LinearRegression", "RandomForestClassifier",
                                    "train_test_split", "Pipeline", "GridSearchCV",
                                    "StandardScaler", "PCA", "KMeans", "SVM", "metrics"],
                  hidden_symbols=["_base", "_utils.estimator_checks"],
                  tags=["ml", "classification", "regression", "clustering"]),
    LibraryRecord("tensorflow", "python", "2.16.0", "machine_learning", "US",
                  "End-to-end open source ML platform.",
                  "https://www.tensorflow.org/api_docs",
                  exported_symbols=["keras", "data", "train", "Module", "Variable",
                                    "GradientTape", "function", "distribute", "lite"],
                  hidden_symbols=["python.ops", "_api.v2.compat"],
                  tags=["deep-learning", "neural-networks", "gpu"]),
    LibraryRecord("pytorch", "python", "2.2.0", "machine_learning", "US",
                  "Tensors and dynamic neural networks with GPU acceleration.",
                  "https://pytorch.org/docs/",
                  exported_symbols=["Tensor", "nn", "optim", "autograd", "utils",
                                    "cuda", "DataLoader", "Module", "functional"],
                  hidden_symbols=["_C", "_dynamo", "_inductor"],
                  tags=["deep-learning", "autograd", "research"]),
    # Python — Web
    LibraryRecord("flask", "python", "3.0.0", "web_framework", "AT",
                  "Lightweight WSGI web application framework.",
                  "https://flask.palletsprojects.com/",
                  exported_symbols=["Flask", "Blueprint", "request", "Response",
                                    "jsonify", "render_template", "redirect", "url_for"],
                  hidden_symbols=["_request_ctx_stack", "signals"],
                  tags=["web", "api", "microframework"]),
    LibraryRecord("django", "python", "5.0.0", "web_framework", "US",
                  "High-level Python web framework.",
                  "https://docs.djangoproject.com/",
                  exported_symbols=["models", "views", "forms", "admin", "urls",
                                    "settings", "migrations", "signals", "middleware"],
                  hidden_symbols=["db.backends", "template.loaders"],
                  tags=["web", "orm", "batteries-included"]),
    LibraryRecord("fastapi", "python", "0.110.0", "web_framework", "CO",
                  "Modern, fast web framework for building APIs.",
                  "https://fastapi.tiangolo.com/",
                  exported_symbols=["FastAPI", "APIRouter", "Depends", "HTTPException",
                                    "Request", "Response", "BackgroundTasks", "WebSocket"],
                  hidden_symbols=["_compat", "openapi.utils"],
                  tags=["api", "async", "openapi"]),
    # Python — Automation
    LibraryRecord("requests", "python", "2.31.0", "automation", "US",
                  "Elegant and simple HTTP library for Python.",
                  "https://docs.python-requests.org/",
                  exported_symbols=["get", "post", "put", "delete", "Session",
                                    "Response", "auth", "exceptions", "adapters"],
                  hidden_symbols=["packages.urllib3", "_internal_utils"],
                  tags=["http", "rest", "scraping"]),
    LibraryRecord("beautifulsoup4", "python", "4.12.0", "automation", "US",
                  "Library for pulling data out of HTML and XML files.",
                  "https://www.crummy.com/software/BeautifulSoup/bs4/doc/",
                  exported_symbols=["BeautifulSoup", "Tag", "NavigableString",
                                    "ResultSet", "find", "find_all", "select"],
                  hidden_symbols=["formatter", "_typing"],
                  tags=["html-parsing", "web-scraping", "xml"]),
    # JavaScript — Frontend
    LibraryRecord("react", "javascript", "18.2.0", "frontend_framework", "US",
                  "A JavaScript library for building user interfaces.",
                  "https://react.dev/",
                  exported_symbols=["createElement", "Component", "useState", "useEffect",
                                    "useContext", "useRef", "useMemo", "Fragment",
                                    "Suspense", "lazy", "memo", "forwardRef"],
                  hidden_symbols=["internals", "__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED"],
                  tags=["ui", "component", "virtual-dom"]),
    LibraryRecord("vue", "javascript", "3.4.0", "frontend_framework", "CN",
                  "Progressive framework for building user interfaces.",
                  "https://vuejs.org/",
                  exported_symbols=["createApp", "defineComponent", "ref", "reactive",
                                    "computed", "watch", "onMounted", "provide", "inject"],
                  hidden_symbols=["runtime-core/src/apiSetupHelpers"],
                  tags=["ui", "progressive", "spa"]),
    LibraryRecord("lodash", "javascript", "4.17.21", "utility", "US",
                  "A modern JavaScript utility library delivering modularity.",
                  "https://lodash.com/docs/",
                  exported_symbols=["map", "filter", "reduce", "groupBy", "sortBy",
                                    "debounce", "throttle", "cloneDeep", "merge", "get"],
                  hidden_symbols=["_baseClone", "_createAssigner"],
                  tags=["utility", "functional", "collections"]),
    # JavaScript — Backend
    LibraryRecord("express", "javascript", "4.19.0", "web_framework", "US",
                  "Fast, unopinionated web framework for Node.js.",
                  "https://expressjs.com/en/api.html",
                  exported_symbols=["Router", "Request", "Response", "NextFunction",
                                    "middleware", "static", "json", "urlencoded"],
                  hidden_symbols=["_express_init", "finalhandler"],
                  tags=["nodejs", "api", "middleware"]),
    # Go
    LibraryRecord("gin", "go", "1.9.1", "web_framework", "CN",
                  "HTTP web framework written in Go.",
                  "https://gin-gonic.com/docs/",
                  exported_symbols=["Default", "Engine", "RouterGroup", "Context",
                                    "GET", "POST", "PUT", "DELETE", "Group", "Use"],
                  hidden_symbols=["internal/bytesconv", "internal/json"],
                  tags=["http", "router", "middleware"]),
    # Rust
    LibraryRecord("serde", "rust", "1.0.197", "serialization", "US",
                  "Serialization/deserialization framework for Rust.",
                  "https://serde.rs/",
                  exported_symbols=["Serialize", "Deserialize", "Serializer",
                                    "Deserializer", "ser", "de", "Error", "Value"],
                  hidden_symbols=["__private", "export"],
                  tags=["json", "serialization", "macros"]),
    # Java
    LibraryRecord("spring-boot", "java", "3.2.3", "web_framework", "US",
                  "Convention-over-configuration Spring application framework.",
                  "https://docs.spring.io/spring-boot/",
                  exported_symbols=["SpringApplication", "RestController", "Service",
                                    "Repository", "Autowired", "Component",
                                    "RequestMapping", "GetMapping", "PostMapping"],
                  hidden_symbols=["org.springframework.boot.autoconfigure.condition"],
                  tags=["enterprise", "microservices", "rest"]),
    # SQL
    LibraryRecord("sqlalchemy", "python", "2.0.28", "data_engineering", "US",
                  "The Python SQL toolkit and Object Relational Mapper.",
                  "https://docs.sqlalchemy.org/",
                  exported_symbols=["create_engine", "Session", "Column", "String",
                                    "Integer", "ForeignKey", "relationship", "select",
                                    "insert", "update", "delete", "text"],
                  hidden_symbols=["dialects.mssql.pyodbc", "pool.impl"],
                  tags=["orm", "sql", "database"]),
]

# ---------------------------------------------------------------------------
# LibraryScraper
# ---------------------------------------------------------------------------


class LibraryScraper:
    """
    Discovers and catalogs coding libraries worldwide.

    In production this class would query live registries (PyPI JSON API, npm
    registry, etc.).  The current implementation uses a seeded catalog that
    can be extended at runtime via ``register_library``.
    """

    def __init__(self) -> None:
        self._catalog: dict[str, LibraryRecord] = {}
        for lib in _SEED_CATALOG:
            self._catalog[f"{lib.language}::{lib.name}"] = lib

    # ------------------------------------------------------------------
    # Catalog access
    # ------------------------------------------------------------------

    def list_languages(self) -> list[str]:
        """Return all languages present in the catalog."""
        return sorted({rec.language for rec in self._catalog.values()})

    def list_libraries(self, language: Optional[str] = None,
                       purpose: Optional[str] = None,
                       country: Optional[str] = None) -> list[LibraryRecord]:
        """Return libraries filtered by language, purpose, and/or country."""
        results = list(self._catalog.values())
        if language:
            results = [r for r in results if r.language == language.lower()]
        if purpose:
            results = [r for r in results if r.purpose_category == purpose.lower()]
        if country:
            results = [r for r in results if r.country_of_origin.upper() == country.upper()]
        return results

    def get_library(self, language: str, name: str) -> Optional[LibraryRecord]:
        """Retrieve a specific library record."""
        return self._catalog.get(f"{language.lower()}::{name.lower()}")

    def register_library(self, record: LibraryRecord) -> None:
        """Add or update a library record in the catalog."""
        self._catalog[f"{record.language}::{record.name}"] = record

    # ------------------------------------------------------------------
    # Discovery helpers
    # ------------------------------------------------------------------

    def discover_symbols(self, language: str, name: str) -> dict:
        """
        Return all known symbols (documented + hidden) for a library.

        In production this would dynamically import the package and
        introspect its ``__all__``, private attributes, and source AST.
        """
        rec = self.get_library(language, name)
        if rec is None:
            return {"error": f"Library '{name}' not found for language '{language}'."}
        return {
            "library": name,
            "language": language,
            "documented": rec.exported_symbols,
            "hidden": rec.hidden_symbols,
            "total": len(rec.exported_symbols) + len(rec.hidden_symbols),
        }

    def scrape_by_language(self, language: str) -> list[dict]:
        """Scrape (simulate) all libraries for a given language."""
        libs = self.list_libraries(language=language)
        return [lib.to_dict() for lib in libs]

    def scrape_by_country(self, country: str) -> list[dict]:
        """Scrape (simulate) all libraries originating from a country."""
        libs = self.list_libraries(country=country)
        return [lib.to_dict() for lib in libs]

    def catalog_summary(self) -> dict:
        """Return a high-level summary of the catalog."""
        by_language: dict[str, int] = {}
        by_country: dict[str, int] = {}
        by_purpose: dict[str, int] = {}
        for rec in self._catalog.values():
            by_language[rec.language] = by_language.get(rec.language, 0) + 1
            by_country[rec.country_of_origin] = by_country.get(rec.country_of_origin, 0) + 1
            by_purpose[rec.purpose_category] = by_purpose.get(rec.purpose_category, 0) + 1
        return {
            "total_libraries": len(self._catalog),
            "by_language": by_language,
            "by_country": by_country,
            "by_purpose": by_purpose,
        }
