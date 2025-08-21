import pytest
from kuzu_DAL import CategoryDAL, initialize_schema


class TestMorphismIsolation:
    """Test that morphisms are properly isolated to their categories."""
    
    def test_morphism_category_isolation(self, dal):
        """Test that morphisms only appear in their designated categories."""
        # Create two separate categories
        cat1_id = dal.create_category("IsolationCat1", "First isolation test category")
        cat2_id = dal.create_category("IsolationCat2", "Second isolation test category")
        
        # Add objects to each category
        obj1_cat1 = dal.create_object("A1", cat1_id, "Object A in category 1")
        obj2_cat1 = dal.create_object("B1", cat1_id, "Object B in category 1")
        
        obj1_cat2 = dal.create_object("A2", cat2_id, "Object A in category 2")
        obj2_cat2 = dal.create_object("B2", cat2_id, "Object B in category 2")
        
        # Create morphisms in each category
        morph1_id = dal.create_morphism("f1", obj1_cat1, obj2_cat1, cat1_id, "Morphism in category 1")
        morph2_id = dal.create_morphism("f2", obj1_cat2, obj2_cat2, cat2_id, "Morphism in category 2")
        
        # Test morphism retrieval for each category
        morphisms_cat1 = dal.get_morphisms_in_category(cat1_id)
        morphisms_cat2 = dal.get_morphisms_in_category(cat2_id)
        
        # Verify isolation: each category should only have its own morphism
        assert len(morphisms_cat1) == 1, f"Category1 should have 1 morphism, found {len(morphisms_cat1)}"
        assert len(morphisms_cat2) == 1, f"Category2 should have 1 morphism, found {len(morphisms_cat2)}"
        
        # Verify correct morphisms in each category
        cat1_morph = morphisms_cat1[0]
        cat2_morph = morphisms_cat2[0]
        
        assert cat1_morph['name'] == 'f1', f"Category1 should contain f1, found {cat1_morph['name']}"
        assert cat1_morph['ID'] == morph1_id, f"Category1 morphism ID mismatch"
        assert cat1_morph['source_object'] == 'A1', f"f1 source should be A1, found {cat1_morph['source_object']}"
        assert cat1_morph['target_object'] == 'B1', f"f1 target should be B1, found {cat1_morph['target_object']}"
        
        assert cat2_morph['name'] == 'f2', f"Category2 should contain f2, found {cat2_morph['name']}"
        assert cat2_morph['ID'] == morph2_id, f"Category2 morphism ID mismatch"
        assert cat2_morph['source_object'] == 'A2', f"f2 source should be A2, found {cat2_morph['source_object']}"
        assert cat2_morph['target_object'] == 'B2', f"f2 target should be B2, found {cat2_morph['target_object']}"
    
    def test_multiple_morphisms_per_category(self, dal):
        """Test multiple morphisms within the same category."""
        # Create category
        cat_id = dal.create_category("MultiMorphCat", "Category with multiple morphisms")
        
        # Create objects
        obj_a = dal.create_object("A", cat_id, "Object A")
        obj_b = dal.create_object("B", cat_id, "Object B")
        obj_c = dal.create_object("C", cat_id, "Object C")
        
        # Create multiple morphisms
        f_id = dal.create_morphism("f", obj_a, obj_b, cat_id, "f: A -> B")
        g_id = dal.create_morphism("g", obj_b, obj_c, cat_id, "g: B -> C")
        h_id = dal.create_morphism("h", obj_a, obj_c, cat_id, "h: A -> C (composition)")
        
        # Retrieve morphisms
        morphisms = dal.get_morphisms_in_category(cat_id)
        
        # Should have exactly 3 morphisms
        assert len(morphisms) == 3, f"Should have 3 morphisms, found {len(morphisms)}"
        
        # Verify all morphisms are present and correct
        morphism_names = [m['name'] for m in morphisms]
        assert 'f' in morphism_names, "Morphism 'f' missing"
        assert 'g' in morphism_names, "Morphism 'g' missing"  
        assert 'h' in morphism_names, "Morphism 'h' missing"
        
        # Verify source/target relationships are correct
        f_morph = next(m for m in morphisms if m['name'] == 'f')
        assert f_morph['source_object'] == 'A' and f_morph['target_object'] == 'B'
        
        g_morph = next(m for m in morphisms if m['name'] == 'g')
        assert g_morph['source_object'] == 'B' and g_morph['target_object'] == 'C'
        
        h_morph = next(m for m in morphisms if m['name'] == 'h')
        assert h_morph['source_object'] == 'A' and h_morph['target_object'] == 'C'
    
    def test_empty_category_morphisms(self, dal):
        """Test that empty categories return no morphisms."""
        # Create category with objects but no morphisms
        cat_id = dal.create_category("EmptyCat", "Category with no morphisms")
        dal.create_object("LonelyObject", cat_id, "An object with no morphisms")
        
        # Should return empty list
        morphisms = dal.get_morphisms_in_category(cat_id)
        assert len(morphisms) == 0, f"Empty category should have 0 morphisms, found {len(morphisms)}"
    
    def test_cross_category_isolation_with_same_object_names(self, dal):
        """Test isolation when object names are the same across categories."""
        # Create two categories with identically named objects
        cat1_id = dal.create_category("SameNameCat1", "First category with same names")
        cat2_id = dal.create_category("SameNameCat2", "Second category with same names")
        
        # Create identically named objects in each category
        obj_a1 = dal.create_object("X", cat1_id, "Object X in category 1")
        obj_b1 = dal.create_object("Y", cat1_id, "Object Y in category 1")
        
        obj_a2 = dal.create_object("X", cat2_id, "Object X in category 2")  
        obj_b2 = dal.create_object("Y", cat2_id, "Object Y in category 2")
        
        # Create morphisms with same names in each category
        f1_id = dal.create_morphism("g", obj_a1, obj_b1, cat1_id, "g in category 1")
        f2_id = dal.create_morphism("g", obj_a2, obj_b2, cat2_id, "g in category 2")
        
        # Test isolation
        morphisms_cat1 = dal.get_morphisms_in_category(cat1_id)
        morphisms_cat2 = dal.get_morphisms_in_category(cat2_id)
        
        # Each should have exactly one morphism
        assert len(morphisms_cat1) == 1
        assert len(morphisms_cat2) == 1
        
        # Verify they are different morphism instances
        assert morphisms_cat1[0]['ID'] != morphisms_cat2[0]['ID']
        assert morphisms_cat1[0]['description'] == "g in category 1"
        assert morphisms_cat2[0]['description'] == "g in category 2"
    
    def test_morphism_deletion_isolation(self, dal):
        """Test that deleting morphisms doesn't affect other categories."""
        # Create two categories with morphisms
        cat1_id = dal.create_category("DeleteCat1", "First deletion test category") 
        cat2_id = dal.create_category("DeleteCat2", "Second deletion test category")
        
        # Add objects and morphisms
        obj1_c1 = dal.create_object("X1", cat1_id)
        obj2_c1 = dal.create_object("Y1", cat1_id)
        obj1_c2 = dal.create_object("X2", cat2_id)
        obj2_c2 = dal.create_object("Y2", cat2_id)
        
        morph1 = dal.create_morphism("delete_me", obj1_c1, obj2_c1, cat1_id)
        morph2 = dal.create_morphism("keep_me", obj1_c2, obj2_c2, cat2_id)
        
        # Verify both exist
        assert len(dal.get_morphisms_in_category(cat1_id)) == 1
        assert len(dal.get_morphisms_in_category(cat2_id)) == 1
        
        # Delete object from category1 (should cascade delete morphism)
        dal.delete_object(obj1_c1)
        
        # Category1 should now have no morphisms, Category2 should be unchanged
        morphisms_cat1_after = dal.get_morphisms_in_category(cat1_id)
        morphisms_cat2_after = dal.get_morphisms_in_category(cat2_id)
        
        assert len(morphisms_cat1_after) == 0, "Category1 should have no morphisms after object deletion"
        assert len(morphisms_cat2_after) == 1, "Category2 morphisms should be unaffected"
        assert morphisms_cat2_after[0]['name'] == 'keep_me', "Category2 morphism should be preserved"
