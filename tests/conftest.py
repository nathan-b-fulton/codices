import pytest
import tempfile
import shutil
from pathlib import Path
import sys
import os
import uuid

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kuzu_DAL import CategoryDAL, initialize_schema


@pytest.fixture(scope="function")
def temp_db_path():
    """Create a unique temporary database for each test."""
    # Use UUID to ensure unique database paths
    temp_dir = tempfile.mkdtemp(prefix=f"codices_test_{uuid.uuid4().hex[:8]}_")
    db_path = Path(temp_dir) / "test_kuzu_db"
    
    yield str(db_path)
    
    # Cleanup - force remove even if files are locked
    try:
        if db_path.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)
    except Exception:
        pass  # Ignore cleanup errors in tests


@pytest.fixture(scope="function")
def dal(temp_db_path):
    """Create a CategoryDAL instance with initialized schema."""
    # Clear any Streamlit cache that might interfere
    try:
        import streamlit as st
        if hasattr(st, 'cache_data'):
            st.cache_data.clear()
    except Exception:
        pass  # Ignore if streamlit not available or cache doesn't exist
    
    # Initialize with fresh schema
    initialize_schema(temp_db_path)
    dal_instance = CategoryDAL(temp_db_path)
    
    # Verify clean state
    categories = dal_instance.list_categories()
    assert len(categories) == 0, f"Database not clean: found {len(categories)} existing categories"
    
    yield dal_instance
    
    # Ensure complete cleanup
    try:
        if dal_instance.transaction_active:
            dal_instance.rollback_transaction()
        # Close database connections
        del dal_instance
    except Exception:
        pass  # Ignore cleanup errors


@pytest.fixture(autouse=True)
def clear_streamlit_cache():
    """Clear Streamlit cache before each test."""
    try:
        import streamlit as st
        # Clear all caches
        if hasattr(st, 'cache_data'):
            st.cache_data.clear()
        if hasattr(st, 'cache_resource'):
            st.cache_resource.clear()
    except Exception:
        pass


@pytest.fixture
def sample_category(dal):
    """Create a sample category for testing with unique name."""
    # Use unique names to avoid conflicts even if databases somehow overlap
    unique_suffix = uuid.uuid4().hex[:6]
    return dal.create_category(f"TestCategory_{unique_suffix}", "A test category for unit tests")


@pytest.fixture
def sample_object(dal, sample_category):
    """Create a sample object in the test category."""
    unique_suffix = uuid.uuid4().hex[:6]
    return dal.create_object(f"TestObject_{unique_suffix}", sample_category, "A test object")
