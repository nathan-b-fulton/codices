import pytest
import tempfile
import shutil
from pathlib import Path
import sys
import os

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kuzu_DAL import CategoryDAL, initialize_schema


@pytest.fixture
def temp_db_path():
    """Create a temporary database for testing."""
    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / "test_kuzu_db"
    yield str(db_path)
    # Cleanup
    if db_path.exists():
        shutil.rmtree(temp_dir)


@pytest.fixture
def dal(temp_db_path):
    """Create a CategoryDAL instance with initialized schema."""
    initialize_schema(temp_db_path)
    return CategoryDAL(temp_db_path)


@pytest.fixture
def sample_category(dal):
    """Create a sample category for testing."""
    return dal.create_category("TestCategory", "A test category for unit tests")


@pytest.fixture
def sample_object(dal, sample_category):
    """Create a sample object in the test category."""
    return dal.create_object("TestObject", sample_category, "A test object")
