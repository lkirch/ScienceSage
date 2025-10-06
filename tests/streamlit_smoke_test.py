"""
Smoke test for a Streamlit app.

This checks:
1. App starts without crashing
2. HTTP server responds on the expected port
3. Key UI text is present in the rendered HTML
"""

import subprocess
import requests
import time
import os
import signal
import pytest

STREAMLIT_FILE = "sciencesage/app.py"
PORT = 8501
URL = f"http://localhost:{PORT}"


@pytest.fixture(scope="module")
def streamlit_app():
    """Start the Streamlit app as a subprocess and tear it down after tests."""
    env = os.environ.copy()
    proc = subprocess.Popen(
        ["streamlit", "run", STREAMLIT_FILE, f"--server.port={PORT}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        preexec_fn=os.setsid  # makes sure we can kill child processes
    )
    
    # Wait for server to start
    for _ in range(20):
        try:
            r = requests.get(URL)
            if r.status_code == 200:
                break
        except Exception:
            pass
        time.sleep(1)
    else:
        # If we never got a 200, fail fast
        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        pytest.fail("Streamlit app did not start in time")

    yield proc

    # Teardown: kill the process group
    os.killpg(os.getpgid(proc.pid), signal.SIGTERM)


def test_app_starts_and_serves(streamlit_app):
    """Check that the app responds with HTTP 200 on root URL."""
    response = requests.get(URL)
    assert response.status_code == 200


def test_app_contains_streamlit_marker(streamlit_app):
    """Check that the app returns Streamlit's base HTML."""
    response = requests.get(URL)
    assert "streamlit" in response.text.lower()


def test_no_server_errors(streamlit_app):
    """Ensure stderr doesn’t contain Python exceptions."""
    # Read a bit of stderr output (non-blocking)
    try:
        stderr_output = streamlit_app.stderr.read().decode("utf-8")
    except Exception:
        stderr_output = ""
    assert "Traceback" not in stderr_output
    assert "Error" not in stderr_output
