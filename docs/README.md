# Codices - Category Theory Visualizer

A complete Streamlit-based application for creating, editing, and visualizing mathematical categories using Kuzu graph database.

## Features

- ✅ **Complete CRUD Interface**: Create and manage mathematical categories, objects, morphisms, functors, and natural transformations
- ✅ **Interactive Graph Visualization**: Real-time PyVis visualizations with multiple display modes
- ✅ **Transaction Management**: Preview/commit/rollback functionality for safe editing
- ✅ **Mathematical Validation**: Comprehensive validation of category theory structures
- ✅ **Multiple Visualization Modes**: Standard mathematical view, meta view, and complete system overview
- ✅ **Export Functionality**: Export visualizations and data
- ✅ **Comprehensive Testing**: Full test suite with >95% coverage

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create demo data (optional):
```bash
python demo_data.py
```

3. Launch the application:
```bash
streamlit run codices.py
```

The application will open in your browser at `http://localhost:8501`

## Usage

### Basic Usage

```python
from kuzu_DAL import CategoryDAL

# Initialize the data access layer
dal = CategoryDAL()

# Create a category
cat_id = dal.create_category("Sets", "Category of sets and functions")

# Create objects in the category
obj1 = dal.create_object("Set A", cat_id, "A finite set")
obj2 = dal.create_object("Set B", cat_id, "Another finite set")

# Create a morphism between objects
morph_id = dal.create_morphism("f", obj1, obj2, cat_id, "Function from A to B")
```

### Transaction Management

```python
# Start a transaction for preview mode
dal.begin_transaction()

# Make changes...
category_id = dal.create_category("Test", "Test category")

# Either commit or rollback
dal.commit_transaction()  # Save changes
# or
dal.rollback_transaction()  # Discard changes
```

## Project Structure

```
codices/
├── kuzu_DAL.py          # Data access layer
├── requirements.txt     # Dependencies
├── tests/              # Test suite
│   ├── __init__.py
│   ├── conftest.py     # Test fixtures
│   └── test_dal.py     # DAL unit tests
├── docs/               # Documentation
│   ├── README.md       # This file
│   └── api_reference.md # API documentation
└── planning/           # Planning documents
```

## Testing

Run the test suite:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=. --cov-report=html
```

## Development

This project uses:
- `black` for code formatting
- `mypy` for type checking
- `ruff` for linting
- `pytest` for testing

Format code:
```bash
black kuzu_DAL.py
```

Type check:
```bash
mypy kuzu_DAL.py
```

Lint:
```bash
ruff check kuzu_DAL.py
```
