import pytest
import tempfile
from pathlib import Path

from kuzu_DAL import CategoryDAL, initialize_schema
from visualization import get_visualization_data, create_pyvis_network


class TestVisualization:
    """Test visualization functionality."""
    
    @pytest.fixture
    def setup_test_data(self, dal):
        """Create test data for visualization."""
        # Create a category with objects and morphisms
        cat_id = dal.create_category("TestVizCategory", "Category for visualization testing")
        obj1 = dal.create_object("A", cat_id, "Object A")
        obj2 = dal.create_object("B", cat_id, "Object B")
        obj3 = dal.create_object("C", cat_id, "Object C")
        
        # Create some morphisms
        morph1 = dal.create_morphism("f", obj1, obj2, cat_id, "Morphism f: A -> B")
        morph2 = dal.create_morphism("g", obj2, obj3, cat_id, "Morphism g: B -> C")
        morph3 = dal.create_morphism("h", obj1, obj3, cat_id, "Morphism h: A -> C")
        
        return {
            'category_id': cat_id,
            'objects': [obj1, obj2, obj3],
            'morphisms': [morph1, morph2, morph3]
        }
    
    def test_category_visualization_data(self, dal, setup_test_data):
        """Test getting visualization data for a category."""
        test_data = setup_test_data
        
        viz_data = get_visualization_data(dal, "Category", test_data['category_id'], "standard")
        
        assert 'nodes' in viz_data
        assert 'edges' in viz_data
        assert 'metadata' in viz_data
        
        # Should have 3 object nodes
        assert len(viz_data['nodes']) == 3
        
        # Should have 3 morphism edges
        assert len(viz_data['edges']) == 3
        
        # Check metadata
        metadata = viz_data['metadata']
        assert metadata['object_count'] == 3
        assert metadata['morphism_count'] == 3
        assert metadata['mode'] == 'standard'
    
    def test_category_meta_mode_visualization(self, dal, setup_test_data):
        """Test meta mode visualization showing all entities as nodes."""
        test_data = setup_test_data
        
        viz_data = get_visualization_data(dal, "Category", test_data['category_id'], "meta")
        
        # Should have 1 category + 3 objects + 3 morphisms = 7 nodes
        assert len(viz_data['nodes']) == 7
        
        # Should have structural edges
        assert len(viz_data['edges']) > 3
    
    def test_functor_visualization_data(self, dal):
        """Test getting visualization data for functors."""
        # Create two categories
        cat1 = dal.create_category("Source", "Source category")
        cat2 = dal.create_category("Target", "Target category")
        
        # Create a functor
        functor_id = dal.create_functor("F", cat1, cat2, "Test functor")
        
        viz_data = get_visualization_data(dal, "Functor", None, "standard")
        
        assert 'nodes' in viz_data
        assert 'edges' in viz_data
        
        # Should have 2 category nodes
        assert len(viz_data['nodes']) == 2
        
        # Should have 1 functor edge
        assert len(viz_data['edges']) == 1
    
    def test_pyvis_network_creation(self, dal, setup_test_data):
        """Test creating PyVis network from visualization data."""
        test_data = setup_test_data
        
        viz_data = get_visualization_data(dal, "Category", test_data['category_id'], "standard")
        
        config = {
            'height': '400px',
            'width': '100%',
            'directed': True
        }
        
        net = create_pyvis_network(viz_data['nodes'], viz_data['edges'], config)
        
        # Check that network was created
        assert net is not None
        assert hasattr(net, 'nodes')
        assert hasattr(net, 'edges')
        
        # Check node and edge counts
        assert len(net.nodes) == len(viz_data['nodes'])
        assert len(net.edges) == len(viz_data['edges'])
    
    def test_empty_visualization_data(self, dal):
        """Test visualization with no data."""
        viz_data = get_visualization_data(dal, "Category", 99999, "standard")
        
        # Should handle missing category gracefully
        assert 'nodes' in viz_data
        assert 'edges' in viz_data
        assert len(viz_data['nodes']) == 0
        assert len(viz_data['edges']) == 0
    
    def test_layout_configurations(self, dal, setup_test_data):
        """Test different layout configurations."""
        test_data = setup_test_data
        viz_data = get_visualization_data(dal, "Category", test_data['category_id'], "standard")
        
        layouts = ['force_directed', 'hierarchical', 'circular', 'manual']
        
        for layout in layouts:
            config = {
                'height': '400px',
                'width': '100%',
                'directed': True,
                'layout': layout,
                'show_labels': True,
                'physics_strength': 0.3
            }
            
            net = create_pyvis_network(viz_data['nodes'], viz_data['edges'], config)
            
            # Verify network was created
            assert net is not None
            assert len(net.nodes) == len(viz_data['nodes'])
            assert len(net.edges) == len(viz_data['edges'])
    
    def test_physics_strength_adjustment(self, dal, setup_test_data):
        """Test physics strength adjustment for force-directed layout."""
        test_data = setup_test_data
        viz_data = get_visualization_data(dal, "Category", test_data['category_id'], "standard")
        
        # Test different physics strengths
        strengths = [0.1, 0.5, 1.0, 2.0]
        
        for strength in strengths:
            config = {
                'layout': 'force_directed',
                'physics_strength': strength
            }
            
            net = create_pyvis_network(viz_data['nodes'], viz_data['edges'], config)
            
            # Should create successfully with any strength value
            assert net is not None
    
    def test_edge_label_toggle(self, dal, setup_test_data):
        """Test edge label show/hide functionality."""
        test_data = setup_test_data
        viz_data = get_visualization_data(dal, "Category", test_data['category_id'], "standard")
        
        # Test with labels enabled
        config_with_labels = {
            'layout': 'force_directed',
            'show_labels': True
        }
        net_with_labels = create_pyvis_network(viz_data['nodes'], viz_data['edges'], config_with_labels)
        
        # Test with labels disabled
        config_without_labels = {
            'layout': 'force_directed', 
            'show_labels': False
        }
        net_without_labels = create_pyvis_network(viz_data['nodes'], viz_data['edges'], config_without_labels)
        
        # Both should create successfully
        assert net_with_labels is not None
        assert net_without_labels is not None
    
    def test_basic_network_creation(self, dal, setup_test_data):
        """Test basic network creation functionality."""
        test_data = setup_test_data
        viz_data = get_visualization_data(dal, "Category", test_data['category_id'], "standard")
        
        # Test network creation
        config = {
            'layout': 'force_directed'
        }
        net = create_pyvis_network(viz_data['nodes'], viz_data['edges'], config)
        
        # Network should create successfully
        assert net is not None
        assert len(net.nodes) > 0
        assert len(net.edges) >= 0
