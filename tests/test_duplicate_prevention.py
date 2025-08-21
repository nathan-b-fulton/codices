import pytest
from kuzu_DAL import CategoryDAL, initialize_schema


class TestDuplicatePrevention:
    """Test duplicate entity prevention."""
    
    def test_duplicate_category_prevention(self, dal):
        """Test that duplicate category names are prevented."""
        # Create initial category
        cat_id1 = dal.create_category("UniqueCategory", "First category")
        
        # Try to create duplicate - should fail
        with pytest.raises(ValueError, match="already exists"):
            dal.create_category("UniqueCategory", "Second category with same name")
        
        # Verify only one category exists
        categories = dal.list_categories()
        unique_categories = [cat for cat in categories if cat['name'] == "UniqueCategory"]
        assert len(unique_categories) == 1
        assert unique_categories[0]['ID'] == cat_id1
    
    def test_duplicate_object_prevention_within_category(self, dal):
        """Test that duplicate object names within a category are prevented."""
        # Create category
        cat_id = dal.create_category("TestCat", "Test category")
        
        # Create initial object
        obj_id1 = dal.create_object("UniqueObject", cat_id, "First object")
        
        # Try to create duplicate in same category - should fail
        with pytest.raises(ValueError, match="already exists"):
            dal.create_object("UniqueObject", cat_id, "Second object with same name")
        
        # Verify only one object exists
        objects = dal.get_objects_in_category(cat_id)
        unique_objects = [obj for obj in objects if obj['name'] == "UniqueObject"]
        assert len(unique_objects) == 1
        assert unique_objects[0]['ID'] == obj_id1
    
    def test_duplicate_object_allowed_across_categories(self, dal):
        """Test that objects with same name are allowed in different categories."""
        # Create two categories
        cat_id1 = dal.create_category("Category1", "First category")
        cat_id2 = dal.create_category("Category2", "Second category")
        
        # Create objects with same name in different categories - should succeed
        obj_id1 = dal.create_object("SameName", cat_id1, "Object in category 1")
        obj_id2 = dal.create_object("SameName", cat_id2, "Object in category 2")
        
        # Verify both objects exist
        objects1 = dal.get_objects_in_category(cat_id1)
        objects2 = dal.get_objects_in_category(cat_id2)
        
        assert len(objects1) == 1
        assert len(objects2) == 1
        assert objects1[0]['name'] == "SameName"
        assert objects2[0]['name'] == "SameName"
        assert objects1[0]['ID'] != objects2[0]['ID']
    
    def test_duplicate_morphism_prevention_within_category(self, dal):
        """Test that duplicate morphism names within a category are prevented."""
        # Create category and objects
        cat_id = dal.create_category("TestCat", "Test category")
        obj1 = dal.create_object("A", cat_id, "Object A")
        obj2 = dal.create_object("B", cat_id, "Object B")
        obj3 = dal.create_object("C", cat_id, "Object C")
        
        # Create initial morphism
        morph_id1 = dal.create_morphism("f", obj1, obj2, cat_id, "First morphism")
        
        # Try to create duplicate in same category - should fail
        with pytest.raises(ValueError, match="already exists"):
            dal.create_morphism("f", obj1, obj3, cat_id, "Second morphism with same name")
        
        # Verify only one morphism with that name exists
        morphisms = dal.get_morphisms_in_category(cat_id)
        unique_morphisms = [morph for morph in morphisms if morph['name'] == "f"]
        assert len(unique_morphisms) == 1
        assert unique_morphisms[0]['ID'] == morph_id1
    
    def test_update_to_existing_name_prevention(self, dal):
        """Test that updating to an existing name is prevented."""
        # Create two categories
        cat_id1 = dal.create_category("FirstCategory", "First category")
        cat_id2 = dal.create_category("SecondCategory", "Second category")
        
        # Try to update first category to have same name as second - should fail
        with pytest.raises(ValueError, match="already exists"):
            dal.update_category(cat_id1, name="SecondCategory")
        
        # Verify names haven't changed
        cat1 = dal.get_category(cat_id1)
        cat2 = dal.get_category(cat_id2)
        
        assert cat1['name'] == "FirstCategory"
        assert cat2['name'] == "SecondCategory"
    
    def test_transaction_duplicate_prevention(self, dal):
        """Test duplicate prevention works within transactions."""
        dal.begin_transaction()
        
        try:
            # Create category in transaction
            cat_id = dal.create_category("TransactionCat", "Category in transaction")
            
            # Try to create duplicate in same transaction - should fail
            with pytest.raises(ValueError, match="already exists"):
                dal.create_category("TransactionCat", "Duplicate in transaction")
            
            # Rollback to clean state
            dal.rollback_transaction()
            
            # Verify nothing persisted
            categories = dal.list_categories()
            transaction_cats = [cat for cat in categories if cat['name'] == "TransactionCat"]
            assert len(transaction_cats) == 0
            
        except Exception as e:
            if dal.transaction_active:
                dal.rollback_transaction()
            raise
    
    def test_case_sensitive_names(self, dal):
        """Test that names are case-sensitive."""
        # Create category
        cat_id1 = dal.create_category("MyCategory", "Lowercase version")
        
        # Create category with different case - should succeed
        cat_id2 = dal.create_category("MYCATEGORY", "Uppercase version")
        cat_id3 = dal.create_category("myCategory", "Mixed case version")
        
        # Verify all exist
        categories = dal.list_categories()
        names = [cat['name'] for cat in categories]
        
        assert "MyCategory" in names
        assert "MYCATEGORY" in names  
        assert "myCategory" in names
        assert len(set(names)) >= 3  # At least our 3 unique names
