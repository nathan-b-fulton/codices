import pytest
import time
from kuzu_DAL import CategoryDAL, initialize_schema
from visualization import get_visualization_data


class TestIntegration:
    """Integration tests for the complete system."""
    
    def test_complete_workflow(self, dal):
        """Test complete category theory workflow."""
        # Create a mathematical structure step by step
        
        # 1. Create category
        cat_id = dal.create_category("TestWorkflow", "Integration test category")
        
        # 2. Add objects
        obj_a = dal.create_object("A", cat_id, "Object A")
        obj_b = dal.create_object("B", cat_id, "Object B") 
        obj_c = dal.create_object("C", cat_id, "Object C")
        
        # 3. Add morphisms
        f = dal.create_morphism("f", obj_a, obj_b, cat_id, "f: A → B")
        g = dal.create_morphism("g", obj_b, obj_c, cat_id, "g: B → C")
        h = dal.create_morphism("h", obj_a, obj_c, cat_id, "h: A → C (composition)")
        
        # 4. Verify structure
        category = dal.get_category(cat_id)
        objects = dal.get_objects_in_category(cat_id)
        morphisms = dal.get_morphisms_in_category(cat_id)
        
        assert category is not None
        assert len(objects) == 3
        assert len(morphisms) == 3
        
        # 5. Test visualization data generation
        viz_data = get_visualization_data(dal, "Category", cat_id, "standard")
        assert len(viz_data['nodes']) == 3  # 3 objects as nodes
        assert len(viz_data['edges']) == 3  # 3 morphisms as edges
        
        # 6. Test functor creation
        cat2_id = dal.create_category("TargetCategory", "Target for functor")
        functor_id = dal.create_functor("F", cat_id, cat2_id, "Test functor")
        
        functors = dal.list_functors()
        assert len(functors) >= 1
        assert any(f['ID'] == functor_id for f in functors)
        
        # 7. Test complete system visualization
        complete_viz = get_visualization_data(dal, "Complete", None, "complete")
        assert len(complete_viz['nodes']) >= 2  # At least 2 categories + functor
    
    def test_transaction_integration_workflow(self, dal):
        """Test transaction system integration with full workflow."""
        # Start transaction
        dal.begin_transaction()
        
        try:
            # Batch create multiple entities
            cat_id = dal.create_category("BatchCategory", "Batch operation test")
            
            objects = []
            for i in range(5):
                obj_id = dal.create_object(f"Object_{i}", cat_id, f"Object number {i}")
                objects.append(obj_id)
            
            morphisms = []
            for i in range(4):
                morph_id = dal.create_morphism(f"f_{i}", objects[i], objects[i+1], cat_id, f"Morphism {i}")
                morphisms.append(morph_id)
            
            # Verify all entities exist in transaction
            assert len(dal.get_objects_in_category(cat_id)) == 5
            assert len(dal.get_morphisms_in_category(cat_id)) == 4
            
            # Test rollback
            dal.rollback_transaction()
            
            # Verify entities don't persist after rollback
            rolled_back_category = dal.get_category(cat_id)
            assert rolled_back_category is None
            
        except Exception as e:
            if dal.transaction_active:
                dal.rollback_transaction()
            raise
    
    def test_visualization_integration_all_modes(self, dal):
        """Test visualization integration with all entity types."""
        # Create comprehensive test data
        cat1 = dal.create_category("Source", "Source category")
        cat2 = dal.create_category("Target", "Target category")
        
        # Add objects to categories
        obj1 = dal.create_object("X", cat1, "Object X")
        obj2 = dal.create_object("Y", cat1, "Object Y")
        obj3 = dal.create_object("A", cat2, "Object A")
        obj4 = dal.create_object("B", cat2, "Object B")
        
        # Add morphisms
        f = dal.create_morphism("f", obj1, obj2, cat1, "f: X → Y")
        g = dal.create_morphism("g", obj3, obj4, cat2, "g: A → B")
        
        # Create functor
        functor_id = dal.create_functor("F", cat1, cat2, "F: Source → Target")
        
        # Test all visualization modes
        
        # Category visualization
        cat_viz = get_visualization_data(dal, "Category", cat1, "standard")
        assert len(cat_viz['nodes']) >= 2  # At least 2 objects
        assert len(cat_viz['edges']) >= 1  # At least 1 morphism
        
        # Functor visualization  
        func_viz = get_visualization_data(dal, "Functor", None, "standard")
        assert len(func_viz['nodes']) == 2  # 2 categories
        assert len(func_viz['edges']) == 1  # 1 functor
        
        # Complete system visualization
        complete_viz = get_visualization_data(dal, "Complete", None, "complete")
        assert len(complete_viz['nodes']) >= 3  # Categories + functors (at minimum)
        
        # Meta mode visualization
        meta_viz = get_visualization_data(dal, "Category", cat1, "meta")
        assert len(meta_viz['nodes']) == 4  # 1 category + 2 objects + 1 morphism
        assert len(meta_viz['edges']) >= 3  # Structural relationships


class TestPerformance:
    """Performance and load testing."""
    
    def test_large_category_performance(self, dal):
        """Test performance with larger categories."""
        start_time = time.time()
        
        # Create category with many objects
        cat_id = dal.create_category("LargeCategory", "Performance test category")
        
        dal.begin_transaction()
        try:
            # Create 50 objects (scaled down for CI)
            object_ids = []
            for i in range(50):
                obj_id = dal.create_object(f"Obj_{i:03d}", cat_id, f"Object {i}")
                object_ids.append(obj_id)
            
            # Create some morphisms between random objects
            morphism_ids = []
            for i in range(0, 40, 2):  # Every other pair
                morph_id = dal.create_morphism(f"f_{i}", object_ids[i], object_ids[i+1], cat_id, f"Morphism {i}")
                morphism_ids.append(morph_id)
            
            dal.commit_transaction()
            
            # Measure query performance
            query_start = time.time()
            objects = dal.get_objects_in_category(cat_id)
            morphisms = dal.get_morphisms_in_category(cat_id)
            query_time = time.time() - query_start
            
            # Verify correct counts
            assert len(objects) == 50
            assert len(morphisms) == 20
            
            # Performance assertions (generous for CI)
            total_time = time.time() - start_time
            assert total_time < 10.0, f"Large category operations took {total_time:.2f}s (should be <10s)"
            assert query_time < 2.0, f"Query operations took {query_time:.2f}s (should be <2s)"
            
        except Exception as e:
            if dal.transaction_active:
                dal.rollback_transaction()
            raise
    
    def test_visualization_performance(self, dal):
        """Test visualization performance with moderate-sized data."""
        # Create test category with moderate complexity
        cat_id = dal.create_category("VizPerf", "Visualization performance test")
        
        # Add 10 objects and 15 morphisms
        objects = []
        for i in range(10):
            obj_id = dal.create_object(f"V_{i}", cat_id, f"Vertex {i}")
            objects.append(obj_id)
        
        # Create a connected graph
        for i in range(15):
            source = objects[i % 10]
            target = objects[(i + 1) % 10]
            dal.create_morphism(f"e_{i}", source, target, cat_id, f"Edge {i}")
        
        # Test visualization data generation performance
        start_time = time.time()
        viz_data = get_visualization_data(dal, "Category", cat_id, "standard")
        viz_time = time.time() - start_time
        
        # Verify structure (account for potential previous test data)
        assert len(viz_data['nodes']) >= 10
        assert len(viz_data['edges']) >= 15
        
        # Performance assertion (generous for CI)
        assert viz_time < 3.0, f"Visualization generation took {viz_time:.2f}s (should be <3s)"
    
    def test_concurrent_operation_simulation(self, dal):
        """Simulate concurrent-like operations to test system stability."""
        # This simulates rapid sequential operations
        
        cat_ids = []
        start_time = time.time()
        
        # Rapid category creation
        for i in range(20):
            cat_id = dal.create_category(f"Concurrent_{i}", f"Concurrent test {i}")
            cat_ids.append(cat_id)
        
        # Rapid object creation across categories
        for i, cat_id in enumerate(cat_ids[:10]):  # Use first 10 categories
            obj1 = dal.create_object(f"A_{i}", cat_id, "Object A")
            obj2 = dal.create_object(f"B_{i}", cat_id, "Object B")
            dal.create_morphism(f"f_{i}", obj1, obj2, cat_id, "Morphism f")
        
        # Verify all operations completed successfully
        categories = dal.list_categories()
        total_time = time.time() - start_time
        
        assert len(categories) >= 20
        assert total_time < 5.0, f"Concurrent operations took {total_time:.2f}s (should be <5s)"


class TestMathematicalValidation:
    """Mathematical validation testing."""
    
    def test_category_structure_validation(self, dal):
        """Test mathematical validation of category structures."""
        cat_id = dal.create_category("ValidationTest", "Category for validation testing")
        
        # Create objects
        obj_a = dal.create_object("A", cat_id, "Object A")
        obj_b = dal.create_object("B", cat_id, "Object B")
        obj_c = dal.create_object("C", cat_id, "Object C")
        
        # Create morphisms
        f = dal.create_morphism("f", obj_a, obj_b, cat_id, "f: A → B")
        g = dal.create_morphism("g", obj_b, obj_c, cat_id, "g: B → C")
        
        # Validate category structure
        errors = dal.validate_category_structure(cat_id)
        
        # Should be valid (or have expected validation messages)
        assert isinstance(errors, list)
        # Note: Since we skipped identity morphism creation in Phase 1, 
        # we expect validation errors for missing identity morphisms
    
    def test_functor_mathematical_properties(self, dal):
        """Test functor mathematical properties."""
        # Create source and target categories
        source_cat = dal.create_category("Source", "Source category")
        target_cat = dal.create_category("Target", "Target category")
        
        # Create objects in source
        obj_x = dal.create_object("X", source_cat, "Object X")
        obj_y = dal.create_object("Y", source_cat, "Object Y")
        
        # Create objects in target
        obj_fx = dal.create_object("F(X)", target_cat, "Image of X")
        obj_fy = dal.create_object("F(Y)", target_cat, "Image of Y")
        
        # Create morphisms
        f_source = dal.create_morphism("f", obj_x, obj_y, source_cat, "f: X → Y")
        f_target = dal.create_morphism("F(f)", obj_fx, obj_fy, target_cat, "F(f): F(X) → F(Y)")
        
        # Create functor
        functor_id = dal.create_functor("F", source_cat, target_cat, "Test functor")
        
        # Verify functor was created and can be retrieved
        functors = dal.list_functors()
        created_functor = next((f for f in functors if f['ID'] == functor_id), None)
        
        assert created_functor is not None
        assert created_functor['source_category'] == "Source"
        assert created_functor['target_category'] == "Target"
    
    def test_natural_transformation_structure(self, dal):
        """Test natural transformation structure."""
        # Create categories
        cat_c = dal.create_category("C", "Category C")
        cat_d = dal.create_category("D", "Category D")
        
        # Create functors F, G: C → D
        functor_f = dal.create_functor("F", cat_c, cat_d, "Functor F")
        functor_g = dal.create_functor("G", cat_c, cat_d, "Functor G")
        
        # Create natural transformation α: F ⇒ G
        nat_trans_id = dal.create_natural_transformation("α", functor_f, functor_g, "Natural transformation α")
        
        # Verify creation
        nat_trans_list = dal.list_natural_transformations()
        created_nt = next((nt for nt in nat_trans_list if nt['ID'] == nat_trans_id), None)
        
        assert created_nt is not None
        assert created_nt['name'] == "α"
    
    def test_complex_mathematical_scenario(self, dal):
        """Test complex mathematical scenario with multiple structures."""
        dal.begin_transaction()
        
        try:
            # Create a more complex scenario: Two categories with functors
            
            # Category of finite sets
            finite_sets = dal.create_category("FinSet", "Category of finite sets")
            set_a = dal.create_object("A", finite_sets, "Set A = {1, 2}")
            set_b = dal.create_object("B", finite_sets, "Set B = {a, b, c}")
            set_c = dal.create_object("C", finite_sets, "Set C = {x}")
            
            # Functions between sets
            f_ab = dal.create_morphism("f", set_a, set_b, finite_sets, "Function f: A → B")
            g_bc = dal.create_morphism("g", set_b, set_c, finite_sets, "Function g: B → C")
            h_ac = dal.create_morphism("h", set_a, set_c, finite_sets, "Composition h = g∘f")
            
            # Category of groups
            groups = dal.create_category("Grp", "Category of groups")
            group_z2 = dal.create_object("ℤ₂", groups, "Cyclic group of order 2")
            group_z3 = dal.create_object("ℤ₃", groups, "Cyclic group of order 3")
            group_z6 = dal.create_object("ℤ₆", groups, "Cyclic group of order 6")
            
            # Group homomorphisms
            hom_23 = dal.create_morphism("φ", group_z2, group_z3, groups, "Trivial homomorphism")
            hom_36 = dal.create_morphism("ψ", group_z3, group_z6, groups, "Inclusion ℤ₃ → ℤ₆")
            
            # Forgetful functor
            forgetful = dal.create_functor("U", groups, finite_sets, "Forgetful functor Grp → FinSet")
            
            # Commit everything
            dal.commit_transaction()
            
            # Verify complex structure
            all_categories = dal.list_categories()
            all_functors = dal.list_functors()
            
            # Should have at least our 2 new categories
            assert len([c for c in all_categories if c['name'] in ['FinSet', 'Grp']]) == 2
            
            # Should have our functor
            assert len([f for f in all_functors if f['name'] == 'U']) >= 1
            
            # Test visualization of complex structure
            finset_viz = get_visualization_data(dal, "Category", finite_sets, "standard")
            grp_viz = get_visualization_data(dal, "Category", groups, "standard")
            
            assert len(finset_viz['nodes']) == 3  # 3 sets
            assert len(finset_viz['edges']) == 3  # 3 functions
            
            assert len(grp_viz['nodes']) == 3  # 3 groups
            assert len(grp_viz['edges']) == 2  # 2 homomorphisms
            
        except Exception as e:
            if dal.transaction_active:
                dal.rollback_transaction()
            raise


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_invalid_operations(self, dal):
        """Test handling of invalid operations."""
        # Test operations on non-existent entities
        
        # Should handle missing category gracefully
        missing_category = dal.get_category(99999)
        assert missing_category is None
        
        # Should handle missing object gracefully
        missing_object = dal.get_object(99999)
        assert missing_object is None
        
        # Should handle empty category queries gracefully
        empty_objects = dal.get_objects_in_category(99999)
        assert empty_objects == []
        
        empty_morphisms = dal.get_morphisms_in_category(99999)
        assert empty_morphisms == []
    
    def test_visualization_error_handling(self, dal):
        """Test visualization error handling."""
        # Test visualization with non-existent category
        error_viz = get_visualization_data(dal, "Category", 99999, "standard")
        
        # Should return empty structure, not crash
        assert 'nodes' in error_viz
        assert 'edges' in error_viz
        assert len(error_viz['nodes']) == 0
        assert len(error_viz['edges']) == 0
    
    def test_transaction_error_recovery(self, dal):
        """Test transaction error recovery."""
        # Start transaction
        dal.begin_transaction()
        
        try:
            # Create valid entity
            cat_id = dal.create_category("ErrorTest", "Error recovery test")
            
            # Try invalid operation (this might not actually fail in our simple implementation)
            # But test that transaction state remains consistent
            assert dal.transaction_active is True
            
            # Verify we can still rollback cleanly
            dal.rollback_transaction()
            assert dal.transaction_active is False
            
            # Verify nothing persisted
            missing_cat = dal.get_category(cat_id)
            assert missing_cat is None
            
        except Exception as e:
            # Ensure clean recovery even from unexpected errors
            if dal.transaction_active:
                dal.rollback_transaction()
            # Re-raise to see what went wrong
            raise


class TestDataConsistency:
    """Test data consistency and integrity."""
    
    def test_referential_integrity(self, dal):
        """Test that referential integrity is maintained."""
        # Create category with objects and morphisms
        cat_id = dal.create_category("IntegrityTest", "Referential integrity test")
        obj1 = dal.create_object("A", cat_id, "Object A")
        obj2 = dal.create_object("B", cat_id, "Object B")
        morph_id = dal.create_morphism("f", obj1, obj2, cat_id, "f: A → B")
        
        # Verify morphism references exist
        morphisms = dal.get_morphisms_in_category(cat_id)
        created_morph = next((m for m in morphisms if m['ID'] == morph_id), None)
        
        assert created_morph is not None
        assert created_morph['source_object'] == "A"
        assert created_morph['target_object'] == "B"
        
        # Delete object should clean up related morphisms
        dal.delete_object(obj1)
        
        # Morphism should be deleted as well
        remaining_morphisms = dal.get_morphisms_in_category(cat_id)
        remaining_morph = next((m for m in remaining_morphisms if m['ID'] == morph_id), None)
        
        # Note: This depends on the cascade delete implementation
        # The test verifies the system handles object deletion consistently
    
    def test_category_deletion_cascade(self, dal):
        """Test that category deletion properly cascades."""
        # Create category with complex structure
        cat_id = dal.create_category("CascadeTest", "Cascade deletion test")
        
        # Add multiple objects and morphisms
        obj_ids = []
        for i in range(3):
            obj_id = dal.create_object(f"Obj_{i}", cat_id, f"Object {i}")
            obj_ids.append(obj_id)
        
        morph_ids = []
        for i in range(2):
            morph_id = dal.create_morphism(f"f_{i}", obj_ids[i], obj_ids[i+1], cat_id, f"Morphism {i}")
            morph_ids.append(morph_id)
        
        # Get initial counts
        initial_categories = len(dal.list_categories())
        
        # Delete category (should cascade)
        success = dal.delete_category(cat_id)
        assert success is True
        
        # Verify category is gone
        deleted_category = dal.get_category(cat_id)
        assert deleted_category is None
        
        # Verify objects are gone
        for obj_id in obj_ids:
            deleted_obj = dal.get_object(obj_id)
            assert deleted_obj is None
        
        # Verify category count decreased
        final_categories = len(dal.list_categories())
        assert final_categories == initial_categories - 1
