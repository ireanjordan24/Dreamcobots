import importlib.util
import json
from pathlib import Path

import requests


def _load_module():
    repo_root = Path(__file__).resolve().parents[1]
    module_path = repo_root / "scripts" / "integration_lookup.py"
    spec = importlib.util.spec_from_file_location("integration_lookup_script", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_fetch_integration_opportunities_handles_request_errors(monkeypatch):
    module = _load_module()
    monkeypatch.setattr(module, "API_KEY", "configured-key")

    def _raise_request_error(*args, **kwargs):
        raise requests.RequestException("network down")

    monkeypatch.setattr(module.requests, "get", _raise_request_error)
    assert module.fetch_integration_opportunities("test query") == {}


def test_save_integration_results_creates_output_file(tmp_path, monkeypatch):
    module = _load_module()
    output_file = tmp_path / "data" / "integration_lookup.json"
    monkeypatch.setattr(module, "OUTPUT_PATH", output_file)

    module.save_integration_results("query-a", {"result": 1})
    assert output_file.exists()
    data = json.loads(output_file.read_text(encoding="utf-8"))
    assert data["query-a"] == {"result": 1}
