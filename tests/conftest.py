import os
import tempfile
import shutil
import pytest

def pytest_configure(config):
    config.addinivalue_line("markers", "integration: mark a test as an integration test.")

DESTRUCTIVE_KEYWORDS = [
    "cleanup.py", "remove", "delete", "shutil.rmtree", "os.remove", "os.rmdir", "reset", "destroy", "uninstall", "purge", "wipe"
]
DESTRUCTIVE_MARKERS = ["destructive", "purge", "reset"]
DESTRUCTIVE_FILE_PATTERNS = ["cleanup", "reset", "purge"]

@pytest.fixture(autouse=True)
def isolate_destructive(monkeypatch, request):
    destructive = False
    # Marker-based detection
    for marker in DESTRUCTIVE_MARKERS:
        if marker in getattr(request.node, 'keywords', {}):
            destructive = True
    # File-based detection
    if hasattr(request.node, 'fspath') and any(pat in str(request.node.fspath) for pat in DESTRUCTIVE_FILE_PATTERNS):
        destructive = True
    # Keyword-based detection (existing logic)
    test_name = getattr(request.node, 'name', "")
    params = getattr(getattr(request.node, 'callspec', None), 'params', {})
    if any(kw in test_name for kw in DESTRUCTIVE_KEYWORDS):
        destructive = True
    if any(any(kw in str(v) for kw in DESTRUCTIVE_KEYWORDS) for v in params.values()):
        destructive = True
    # Optionally, check source code for destructive keywords
    try:
        src = request.node.function.__code__.co_code
        if any(kw.encode() in src for kw in DESTRUCTIVE_KEYWORDS):
            destructive = True
    except Exception:
        pass
    if destructive:
        temp_venv = tempfile.mkdtemp()
        temp_config = tempfile.NamedTemporaryFile(delete=False)
        temp_db = tempfile.NamedTemporaryFile(delete=False)
        monkeypatch.setenv("SMARTAI_TEST_MODE", "1")
        monkeypatch.setenv("SMARTAI_VENV_PATH", temp_venv)
        monkeypatch.setenv("SMARTAI_DESTRUCTIVE_MODE", "1")
        monkeypatch.setenv("SMARTAI_TEMP_CONFIG", temp_config.name)
        monkeypatch.setenv("SMARTAI_TEMP_DB", temp_db.name)
        print(f"[pytest isolation] Isolated destructive test: {request.node.name}")
        yield
        shutil.rmtree(temp_venv)
        os.unlink(temp_config.name)
        os.unlink(temp_db.name)
    else:
        yield
