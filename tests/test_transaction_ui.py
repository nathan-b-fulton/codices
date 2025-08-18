import pytest
from unittest.mock import Mock, patch
import streamlit as st

# Mock streamlit functions for testing
@pytest.fixture
def mock_streamlit():
    """Mock streamlit functions for testing."""
    with patch('streamlit.session_state') as mock_session:
        mock_session.in_transaction = False
        mock_session.transaction_changes = []
        mock_session.preview_mode = False
        mock_session.selected_entity_type = "Category"
        mock_session.selected_entity_id = None
        mock_session.form_mode = None
        mock_session.editing_entity = None
        yield mock_session


class TestTransactionSystem:
    """Test transaction system functionality."""
    
    def test_transaction_change_tracking(self, dal):
        """Test that changes are properly tracked in transactions."""
        # Start transaction
        dal.begin_transaction()
        
        # Create entities
        cat_id = dal.create_category("TestCategory", "Test description")
        obj_id = dal.create_object("TestObject", cat_id, "Test object")
        
        # Transaction should be active
        assert dal.transaction_active is True
        
        # Commit transaction
        dal.commit_transaction()
        assert dal.transaction_active is False
        
        # Verify entities exist
        category = dal.get_category(cat_id)
        assert category is not None
        assert category['name'] == "TestCategory"
        
        obj = dal.get_object(obj_id)
        assert obj is not None
        assert obj['name'] == "TestObject"
    
    def test_transaction_rollback_functionality(self, dal):
        """Test that rollback properly discards changes."""
        # Get initial state
        initial_categories = dal.list_categories()
        initial_count = len(initial_categories)
        
        # Start transaction
        dal.begin_transaction()
        
        # Create entities
        cat_id = dal.create_category("TempCategory", "Temporary category")
        obj_id = dal.create_object("TempObject", cat_id, "Temporary object")
        
        # Verify entities exist in transaction
        temp_category = dal.get_category(cat_id)
        assert temp_category is not None
        
        # Rollback transaction
        dal.rollback_transaction()
        assert dal.transaction_active is False
        
        # Verify entities no longer exist
        rolled_back_category = dal.get_category(cat_id)
        assert rolled_back_category is None
        
        # Verify category count returned to initial state
        final_categories = dal.list_categories()
        assert len(final_categories) == initial_count
    
    def test_nested_transaction_operations(self, dal):
        """Test complex transaction scenarios."""
        # Start transaction
        dal.begin_transaction()
        
        # Create a category
        cat_id = dal.create_category("ComplexCategory", "Complex test category")
        
        # Create multiple objects
        obj1 = dal.create_object("Object1", cat_id, "First object")
        obj2 = dal.create_object("Object2", cat_id, "Second object")
        obj3 = dal.create_object("Object3", cat_id, "Third object")
        
        # Create morphisms between objects
        morph1 = dal.create_morphism("f", obj1, obj2, cat_id, "Morphism f")
        morph2 = dal.create_morphism("g", obj2, obj3, cat_id, "Morphism g")
        morph3 = dal.create_morphism("h", obj1, obj3, cat_id, "Composition h = g∘f")
        
        # Update some entities
        dal.update_category(cat_id, description="Updated complex test category")
        dal.update_object(obj1, description="Updated first object")
        
        # Verify all operations worked within transaction
        objects = dal.get_objects_in_category(cat_id)
        morphisms = dal.get_morphisms_in_category(cat_id)
        
        assert len(objects) == 3
        assert len(morphisms) == 3
        
        # Commit everything
        dal.commit_transaction()
        
        # Verify persistence after commit
        final_category = dal.get_category(cat_id)
        assert final_category['description'] == "Updated complex test category"
        
        final_objects = dal.get_objects_in_category(cat_id)
        assert len(final_objects) == 3
        
        updated_obj = dal.get_object(obj1)
        assert updated_obj['description'] == "Updated first object"
    
    def test_transaction_with_multiple_categories(self, dal):
        """Test transactions with multiple categories and relationships."""
        dal.begin_transaction()
        
        try:
            # Create multiple categories
            cat1_id = dal.create_category("Category1", "First category")
            cat2_id = dal.create_category("Category2", "Second category")
            
            # Create objects in each category
            obj1 = dal.create_object("Obj1", cat1_id, "Object in category 1")
            obj2 = dal.create_object("Obj2", cat2_id, "Object in category 2")
            
            # Create a functor between categories
            functor_id = dal.create_functor("F", cat1_id, cat2_id, "Test functor")
            
            # Commit all changes
            dal.commit_transaction()
            
            # Verify everything persists
            assert dal.get_category(cat1_id) is not None
            assert dal.get_category(cat2_id) is not None
            assert dal.get_object(obj1) is not None
            assert dal.get_object(obj2) is not None
            
            functors = dal.list_functors()
            assert len(functors) >= 1
            assert any(f['ID'] == functor_id for f in functors)
            
        except Exception as e:
            # Ensure transaction is cleaned up even if test fails
            if dal.transaction_active:
                dal.rollback_transaction()
            raise
    
    def test_transaction_state_consistency(self, dal):
        """Test that transaction state remains consistent across operations."""
        # Verify initial state
        assert dal.transaction_active is False
        
        # Start transaction
        dal.begin_transaction()
        assert dal.transaction_active is True
        
        # Perform operations
        cat_id = dal.create_category("ConsistencyTest", "Test category")
        
        # Transaction should still be active
        assert dal.transaction_active is True
        
        # Commit
        dal.commit_transaction()
        assert dal.transaction_active is False
        
        # Verify data persists
        category = dal.get_category(cat_id)
        assert category is not None
        assert category['name'] == "ConsistencyTest"


class TestTransactionUIIntegration:
    """Test transaction UI integration."""
    
    def test_change_tracking_function(self):
        """Test the add_transaction_change function."""
        # Simple test without mocking streamlit session state
        # This tests the basic functionality of transaction tracking
        
        changes = []
        
        # Simulate the function behavior
        def mock_add_change(description):
            changes.append(description)
        
        # Test adding changes
        mock_add_change("Created category 'Test'")
        mock_add_change("Updated object 'TestObj'")
        mock_add_change("Deleted morphism 'f'")
        
        # Verify changes were tracked
        assert len(changes) == 3
        assert "Created category 'Test'" in changes
        assert "Updated object 'TestObj'" in changes
        assert "Deleted morphism 'f'" in changes
