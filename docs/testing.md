## 🧪 Running Tests

Unit and integration tests are located in the `tests/` directory and use [pytest](https://docs.pytest.org/).

### Run all tests
```bash
pytest
```

### Run tests with verbose output
```bash
pytest -v
```

### Run a specific test file
```bash
pytest tests/test_pipeline.py
```

> **Tip:**  
> Make sure your virtual environment is activated and all dependencies are installed before running tests.

Some integration tests require a running Qdrant instance and a valid OpenAI API key.  
You can skip these by default, or set the required environment variables to enable

## Running the Tests

You can run all tests using:

```sh
make tests
```

This will execute the full test suite in the recommended order.

## Test Script Overview

| Test Script Name                       | General Description                                      | Script/Module Tested                        | Functions/Features Tested                          | Special Requirements                |
|----------------------------------------|----------------------------------------------------------|---------------------------------------------|----------------------------------------------------|-------------------------------------|
| test_preprocess.py                     | Tests text chunking and preprocessing                    | scripts/preprocess.py                       | chunk_text_by_paragraphs, filter_categories, etc.  | None                                |
| test_download_data.py                  | Tests Wikipedia data and image downloading               | scripts/download_data.py                    | Data download, image retrieval, file saving        | Internet connection                 |
| test_create_ground_truth_dataset.py    | Tests creation of ground truth datasets                  | scripts/create_ground_truth_dataset.py      | Dataset creation logic, file output                | None                                |
| test_validate_ground_truth_dataset.py  | Tests validation of ground truth datasets                | scripts/validate_ground_truth_dataset.py    | validate_dataset, error reporting                  | None                                |
| test_embed.py                          | Tests embedding generation and storage                   | scripts/embed.py                            | Embedding creation, Qdrant integration             | Qdrant server running               |
| test_retrieval_system.py               | Tests retrieval and answer generation                    | sciencesage/retrieval_system.py             | retrieve_context, generate_answer, etc.            | Qdrant server running               |
| test_feedback_manager.py               | Tests feedback saving and retrieval                      | sciencesage/feedback_manager.py             | save_feedback, load_feedback, error handling       | None                                |
| test_summarize_metrics.py              | Tests metrics summarization and CSV output               | scripts/summarize_metrics.py                | summarize_metrics, CSV writing                     | None                                |
| streamlit_smoke_test.py                | Smoke test for Streamlit UI startup                      | sciencesage/app.py                          | App launch, UI rendering                           | Streamlit server must be running    |

**Manual UI Testing:**  
A manual UI testing checklist is also available.  
See [sciencesage_ui_manual_testing_checklist.md](sciencesage_ui_manual_testing_checklist.md) for details.