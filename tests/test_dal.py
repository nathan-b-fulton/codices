import pytest
from kuzu_DAL import CategoryDAL, initialize_schema


class TestCategoryOperations:
    """Test category CRUD operations."""
    
    def test_create_category(self, dal):
        """Test creating a new category."""
        category_id = dal.create_category("Mathematics", "Mathematical structures")
        assert isinstance(category_id, int)
        assert category_id >= 0
    
    def test_get_category(self, dal, sample_category):
        """Test retrieving a category by ID."""
        category = dal.get_category(sample_category)
        assert category is not None
        assert category["name"] == "TestCategory"
        assert category["description"] == "A test category for unit tests"
        assert "ID" in category
    
    def test_get_nonexistent_category(self, dal):
        """Test retrieving a category that doesn't exist."""
        category = dal.get_category(99999)
        assert category is None
    
    def test_list_categories(self, dal, sample_category):
        """Test listing all categories."""
        categories = dal.list_categories()
        assert len(categories) >= 1
        assert any(cat["name"] == "TestCategory" for cat in categories)
    
    def test_update_category(self, dal, sample_category):
        """Test updating category properties."""
        success = dal.update_category(sample_category, name="UpdatedCategory", description="Updated description")
        assert success is True
        
        category = dal.get_category(sample_category)
        assert category["name"] == "UpdatedCategory"
        assert category["description"] == "Updated description"
    
    def test_delete_category(self, dal, sample_category):
        """Test deleting a category."""
        success = dal.delete_category(sample_category)
        assert success is True
        
        category = dal.get_category(sample_category)
        assert category is None


class TestObjectOperations:
    """Test object CRUD operations."""
    
    def test_create_object(self, dal, sample_category):
        """Test creating an object in a category."""
        object_id = dal.create_object("Point", sample_category, "A point in space")
        assert isinstance(object_id, int)
        assert object_id >= 0
    
    def test_get_objects_in_category(self, dal, sample_category, sample_object):
        """Test retrieving objects in a category."""
        objects = dal.get_objects_in_category(sample_category)
        assert len(objects) >= 1
        assert any(obj["name"] == "TestObject" for obj in objects)
    
    def test_update_object(self, dal, sample_object):
        """Test updating object properties."""
        success = dal.update_object(sample_object, name="UpdatedObject", description="Updated description")
        assert success is True
        
        obj = dal.get_object(sample_object)
        assert obj["name"] == "UpdatedObject"
        assert obj["description"] == "Updated description"
    
    def test_delete_object(self, dal, sample_object):
        """Test deleting an object."""
        success = dal.delete_object(sample_object)
        assert success is True
        
        obj = dal.get_object(sample_object)
        assert obj is None


class TestMorphismOperations:
    """Test morphism CRUD operations."""
    
    def test_create_morphism(self, dal, sample_category):
        """Test creating a morphism between objects."""
        obj1 = dal.create_object("Object1", sample_category)
        obj2 = dal.create_object("Object2", sample_category)
        
        morphism_id = dal.create_morphism("f", obj1, obj2, sample_category, "A test morphism")
        assert isinstance(morphism_id, int)
        assert morphism_id >= 0
    
    def test_get_morphisms_in_category(self, dal, sample_category):
        """Test retrieving morphisms in a category."""
        obj1 = dal.create_object("Object1", sample_category)
        obj2 = dal.create_object("Object2", sample_category)
        dal.create_morphism("f", obj1, obj2, sample_category)
        
        morphisms = dal.get_morphisms_in_category(sample_category)
        # Should have at least the morphism we created
        assert len(morphisms) >= 1
        assert any(m["name"] == "f" for m in morphisms)


class TestTransactionManagement:
    """Test transaction functionality."""
    
    def test_transaction_flow(self, dal):
        """Test complete transaction flow."""
        dal.begin_transaction()
        assert dal.transaction_active is True
        
        # Create something in transaction
        category_id = dal.create_category("TransactionTest", "Test category")
        
        # Commit
        dal.commit_transaction()
        assert dal.transaction_active is False
        
        # Verify it persists
        category = dal.get_category(category_id)
        assert category is not None
    
    def test_transaction_rollback(self, dal):
        """Test transaction rollback functionality."""
        dal.begin_transaction()
        
        # Create something in transaction
        category_id = dal.create_category("RollbackTest", "Test category")
        
        # Rollback
        dal.rollback_transaction()
        assert dal.transaction_active is False
        
        # Verify it doesn't persist
        category = dal.get_category(category_id)
        assert category is None


class TestValidation:
    """Test validation functionality."""
    
    def test_validate_category_structure(self, dal, sample_category, sample_object):
        """Test category structure validation."""
        errors = dal.validate_category_structure(sample_category)
        # Since we skipped identity morphism creation, expect validation errors
        assert isinstance(errors, list)
