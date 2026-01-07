# Web Automation Tool

Desktop application for automating repetitive browser tasks without requiring development skills.

## Setup

### Prerequisites
- Python 3.11+
- Poetry (for dependency management)

### Installation

1. **Install Poetry** (if not already installed):
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. **Clone and setup project**:
   ```bash
   cd "c:\Users\emacryz\Python Projects\WebAutomationTool\WebAutomationTool"
   poetry install
   ```

3. **Run the application**:
   ```bash
   poetry run python src/main.py
   ```

   Or activate the virtual environment:
   ```bash
   poetry shell
   python src/main.py
   ```

## Development

### Install development dependencies:
```bash
poetry install --with dev
```

### Run tests:
```bash
poetry run pytest
```

### Code formatting:
```bash
poetry run black src/
poetry run flake8 src/
```

## Project Structure

```
src/
├── main.py              # Application entry point
├── ui/                  # User interface components
│   ├── main_window.py
│   ├── task_execution_page.py
│   ├── task_manager_page.py
│   └── subscription_page.py
├── core/                # Core automation logic
├── models/              # Data models
└── utils/               # Utility functions
```