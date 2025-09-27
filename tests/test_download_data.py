import os
import json
import pytest
from unittest.mock import patch, MagicMock

from scripts.download_data import (
    save_file,
    save_json,
    get_image_urls,
    filter_categories,
    download_wikipedia_raw,
    download_category_articles,
)

# --- save_file ---
def test_save_file(tmp_path):
    file_path = tmp_path / "subdir" / "test.txt"
    save_file(str(file_path), "hello world")
    assert file_path.read_text(encoding="utf-8") == "hello world"

# --- save_json ---
def test_save_json(tmp_path):
    file_path = tmp_path / "subdir" / "test.json"
    data = {"a": 1, "b": 2}
    save_json(str(file_path), data)
    loaded = json.loads(file_path.read_text(encoding="utf-8"))
    assert loaded == data

# --- get_image_urls ---
@patch("requests.get")
def test_get_image_urls_basic(mock_get):
    # First call: returns images
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.side_effect = [
        {
            "query": {
                "pages": {
                    "1": {
                        "images": [
                            {"title": "File:img1.jpg"},
                            {"title": "File:img2.png"},
                            {"title": "File:img3.gif"},  # should be ignored
                        ]
                    }
                }
            }
        },
        {
            "query": {
                "pages": {
                    "2": {
                        "imageinfo": [{"url": "http://img1.jpg"}]
                    },
                    "3": {
                        "imageinfo": [{"url": "http://img2.png"}]
                    }
                }
            }
        }
    ]
    from sciencesage.config import WIKI_URL, WIKI_USER_AGENT
    urls = get_image_urls("TestPage", WIKI_USER_AGENT, max_images=2)
    assert urls == ["http://img1.jpg", "http://img2.png"]

@patch("requests.get")
def test_get_image_urls_status_not_200(mock_get):
    mock_get.return_value.status_code = 404
    from sciencesage.config import WIKI_USER_AGENT
    urls = get_image_urls("TestPage", WIKI_USER_AGENT)
    assert urls == []

# --- filter_categories ---
def test_filter_categories_basic():
    cats = [
        "Category:Articles with short description",
        "Category:Physics",
        "Category:Wikipedia pages",
        "Category:Commons",
        "Category:Science",
    ]
    filtered = filter_categories(cats)
    assert "Category:Physics" in filtered
    assert "Category:Science" in filtered
    assert "Category:Articles with short description" not in filtered
    assert "Category:Wikipedia pages" not in filtered
    assert "Category:Commons" not in filtered

# --- download_wikipedia_raw ---
@patch("wikipediaapi.Wikipedia")
@patch("requests.get")
@patch("scripts.download_data.save_file")
@patch("scripts.download_data.save_json")
def test_download_wikipedia_raw_success(mock_save_json, mock_save_file, mock_requests_get, mock_wikipedia):
    # Setup mock Wikipedia page
    mock_page = MagicMock()
    mock_page.exists.return_value = True
    mock_page.text = "Some text"
    mock_page.title = "TestTitle"
    mock_page.fullurl = "http://testurl"
    mock_page.summary = "Summary"
    mock_page.categories = {"Category:Physics": None, "Category:Wikipedia": None}
    mock_wikipedia.return_value.page.return_value = mock_page

    # Mock requests.get for HTML
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = "<html>content</html>"
    mock_requests_get.return_value = mock_resp

    from sciencesage.config import RAW_DATA_DIR, WIKI_USER_AGENT
    download_wikipedia_raw("TestTitle", WIKI_USER_AGENT)

    # Check save_file called for text and html
    assert mock_save_file.call_count >= 2
    # Check save_json called for meta
    assert mock_save_json.call_count == 1

@patch("wikipediaapi.Wikipedia")
def test_download_wikipedia_raw_page_not_exists(mock_wikipedia):
    mock_page = MagicMock()
    mock_page.exists.return_value = False
    mock_wikipedia.return_value.page.return_value = mock_page
    from sciencesage.config import WIKI_USER_AGENT
    # Should not raise
    download_wikipedia_raw("NonExistent", WIKI_USER_AGENT)

# --- download_category_articles ---
@patch("wikipediaapi.Wikipedia")
@patch("scripts.download_data.download_wikipedia_raw")
def test_download_category_articles_success(mock_download_raw, mock_wikipedia):
    mock_cat_page = MagicMock()
    mock_cat_page.exists.return_value = True
    # Simulate two articles
    mock_cat_page.categorymembers = {
        "Article1": MagicMock(ns=0),
        "Article2": MagicMock(ns=0),
        "Category:Subcat": MagicMock(ns=14),
    }
    mock_wikipedia.return_value.page.return_value = mock_cat_page
    from sciencesage.config import WIKI_USER_AGENT
    count = download_category_articles("Physics", WIKI_USER_AGENT)
    assert count == 2
    assert mock_download_raw.call_count == 2

@patch("wikipediaapi.Wikipedia")
def test_download_category_articles_cat_not_exists(mock_wikipedia):
    mock_cat_page = MagicMock()
    mock_cat_page.exists.return_value = False
    mock_wikipedia.return_value.page.return_value = mock_cat_page
    from sciencesage.config import WIKI_USER_AGENT
    count = download_category_articles("NonExistentCat", WIKI_USER_AGENT)
    assert count == 0