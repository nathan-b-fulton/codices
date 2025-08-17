# Codices - Category Theory Visualizer

A Streamlit-based application for creating, editing, and visualizing mathematical categories using Kuzu graph database.

## Features

- Create and manage mathematical categories, objects, morphisms, functors, and natural transformations
- Interactive graph visualization using PyVis
- Transaction-based editing with preview/commit/rollback functionality
- Comprehensive validation of category theory structures

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Initialize the database schema:
```python
from kuzu_DAL import initialize_schema
initialize_schema()
```

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
