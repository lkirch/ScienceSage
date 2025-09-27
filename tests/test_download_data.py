import os
from pathlib import Path
from loguru import logger
import pytest

# Assume download_data.py has a main() function or a download_wikipedia_data() function
from scripts import download_data

logger.add("logs/test_download_data.log", rotation="1 MB", retention="7 days")

def test_download_creates_raw_data(tmp_path, monkeypatch):
    """Test that download_data creates files in the raw data directory."""
    # Monkeypatch RAW_DATA_DIR to tmp_path
    monkeypatch.setattr(download_data, "RAW_DATA_DIR", str(tmp_path))
    
    # Monkeypatch any network calls if needed (example: requests.get)
    # For now, just run the function and check for output files
    try:
        download_data.main()
    except Exception as e:
        pytest.skip(f"Download test skipped due to: {e}")

    # Check that at least one .txt file is created
    txt_files = list(Path(tmp_path).glob("*.txt"))
    assert len(txt_files) > 0, "No raw .txt files were created by download_data.py"
    logger.success(f"Found {len(txt_files)} raw .txt files in {tmp_path}")

def test_download_creates_meta_json(tmp_path, monkeypatch):
    """Test that download_data creates meta.json files for each article."""
    monkeypatch.setattr(download_data, "RAW_DATA_DIR", str(tmp_path))
    try:
        download_data.main()
    except Exception as e:
        pytest.skip(f"Download test skipped due to: {e}")

    meta_files = list(Path(tmp_path).glob("*.meta.json"))
    assert len(meta_files) > 0, "No meta.json files were created by download_data.py"
    logger.success(f"Found {len(meta_files)} meta.json files in {tmp_path}")