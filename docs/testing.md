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