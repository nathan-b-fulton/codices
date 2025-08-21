import pytest
from kuzu_DAL import CategoryDAL, initialize_schema


class TestDeletionFixes:
    """Test that all deletion operations work correctly with DETACH DELETE."""
    
    def test_category_deletion_with_complex_structure(self, dal):
        """Test category deletion with objects, morphisms, and relationships."""
        # Create category with complex structure to test cascade deletion
        cat_id = dal.create_category("ComplexDeleteCat", "Category for deletion testing")
        
        # Create multiple objects
        objects = []
        for i in range(5):
            obj_id = dal.create_object(f"Obj_{i}", cat_id, f"Object {i}")
            objects.append(obj_id)
        
        # Create multiple morphisms creating a connected structure
        morphisms = []
        for i in range(4):
            morph_id = dal.create_morphism(f"f_{i}", objects[i], objects[i+1], cat_id, f"Morphism {i}")
            morphisms.append(morph_id)
        
        # Add some additional morphisms to create more complex relationships
        morph_cycle = dal.create_morphism("cycle", objects[4], objects[0], cat_id, "Cycle morphism")
        morph_diagonal = dal.create_morphism("diag", objects[0], objects[2], cat_id, "Diagonal morphism")
        
        # Verify complex structure exists
        assert len(dal.get_objects_in_category(cat_id)) == 5
        assert len(dal.get_morphisms_in_category(cat_id)) == 6
        
        # Get initial total counts
        initial_categories = len(dal.list_categories())
        
        # Delete the category (this should work with DETACH DELETE)
        success = dal.delete_category(cat_id)
        assert success is True, "Category deletion should succeed"
        
        # Verify category is completely gone
        deleted_category = dal.get_category(cat_id)
        assert deleted_category is None, "Category should be completely deleted"
        
        # Verify objects are gone
        for obj_id in objects:
            deleted_obj = dal.get_object(obj_id)
            assert deleted_obj is None, f"Object {obj_id} should be deleted"
        
        # Verify no morphisms remain
        remaining_morphisms = dal.get_morphisms_in_category(cat_id)
        assert len(remaining_morphisms) == 0, "No morphisms should remain"
        
        # Verify category count decreased
        final_categories = len(dal.list_categories())
        assert final_categories == initial_categories - 1, "Category count should decrease by 1"
    
    def test_object_deletion_cascade(self, dal):
        """Test that object deletion properly cascades to morphisms."""
        # Create category
        cat_id = dal.create_category("ObjectDeleteCat", "Category for object deletion testing")
        
        # Create objects
        obj_a = dal.create_object("A", cat_id, "Object A")
        obj_b = dal.create_object("B", cat_id, "Object B")
        obj_c = dal.create_object("C", cat_id, "Object C")
        
        # Create morphisms involving object A
        f_id = dal.create_morphism("f", obj_a, obj_b, cat_id, "f: A -> B")
        g_id = dal.create_morphism("g", obj_c, obj_a, cat_id, "g: C -> A")
        h_id = dal.create_morphism("h", obj_b, obj_c, cat_id, "h: B -> C (independent)")
        
        # Verify initial structure
        initial_morphisms = dal.get_morphisms_in_category(cat_id)
        assert len(initial_morphisms) == 3
        
        # Delete object A (should cascade delete f and g, but not h)
        success = dal.delete_object(obj_a)
        assert success is True, "Object deletion should succeed"
        
        # Verify object A is gone
        deleted_obj = dal.get_object(obj_a)
        assert deleted_obj is None, "Object A should be deleted"
        
        # Verify morphisms f and g are gone, but h remains
        remaining_morphisms = dal.get_morphisms_in_category(cat_id)
        remaining_names = [m['name'] for m in remaining_morphisms]
        
        assert 'f' not in remaining_names, "Morphism f should be deleted (had A as source)"
        assert 'g' not in remaining_names, "Morphism g should be deleted (had A as target)"
        assert 'h' in remaining_names, "Morphism h should remain (independent of A)"
        
        # Verify h is still properly connected
        h_morph = next(m for m in remaining_morphisms if m['name'] == 'h')
        assert h_morph['source_object'] == 'B'
        assert h_morph['target_object'] == 'C'
    
    def test_deletion_in_transaction(self, dal):
        """Test that deletion works properly within transactions."""
        dal.begin_transaction()
        
        try:
            # Create structure within transaction
            cat_id = dal.create_category("TransactionDeleteCat", "Category for transaction deletion")
            obj1 = dal.create_object("TempObj1", cat_id, "Temporary object 1")
            obj2 = dal.create_object("TempObj2", cat_id, "Temporary object 2")
            morph_id = dal.create_morphism("temp_f", obj1, obj2, cat_id, "Temporary morphism")
            
            # Verify structure exists in transaction
            assert len(dal.get_objects_in_category(cat_id)) == 2
            assert len(dal.get_morphisms_in_category(cat_id)) == 1
            
            # Delete category within transaction
            success = dal.delete_category(cat_id)
            assert success is True
            
            # Verify deletion within transaction
            deleted_category = dal.get_category(cat_id)
            assert deleted_category is None
            
            # Rollback transaction
            dal.rollback_transaction()
            
            # Verify nothing persisted after rollback
            final_category = dal.get_category(cat_id)
            assert final_category is None, "Nothing should persist after rollback"
            
        except Exception as e:
            if dal.transaction_active:
                dal.rollback_transaction()
            raise
    
    def test_deletion_with_functors(self, dal):
        """Test deletion behavior when categories are involved in functors."""
        # Create two categories
        source_cat = dal.create_category("SourceCat", "Source category")
        target_cat = dal.create_category("TargetCat", "Target category")
        
        # Create objects in categories
        obj_source = dal.create_object("X", source_cat, "Object in source")
        obj_target = dal.create_object("Y", target_cat, "Object in target")
        
        # Create functor between categories
        functor_id = dal.create_functor("F", source_cat, target_cat, "Test functor")
        
        # Verify functor exists
        functors = dal.list_functors()
        assert len(functors) >= 1
        
        # Delete source category
        success = dal.delete_category(source_cat)
        assert success is True
        
        # Verify source category is gone
        deleted_source = dal.get_category(source_cat)
        assert deleted_source is None
        
        # Target category should still exist
        remaining_target = dal.get_category(target_cat)
        assert remaining_target is not None
        
        # Note: Functor behavior with deleted categories depends on implementation
        # For now, we just verify the deletion succeeded
    
    def test_empty_category_deletion(self, dal):
        """Test deletion of empty categories."""
        # Create empty category
        cat_id = dal.create_category("EmptyCat", "Empty category for deletion")
        
        # Verify it exists and is empty
        category = dal.get_category(cat_id)
        assert category is not None
        assert len(dal.get_objects_in_category(cat_id)) == 0
        assert len(dal.get_morphisms_in_category(cat_id)) == 0
        
        # Delete empty category
        success = dal.delete_category(cat_id)
        assert success is True
        
        # Verify deletion
        deleted_category = dal.get_category(cat_id)
        assert deleted_category is None
