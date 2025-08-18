import streamlit as st
from pyvis.network import Network
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

from kuzu_DAL import CategoryDAL

logger = logging.getLogger(__name__)

# Node styling configuration
NODE_STYLES = {
    'Category': {'color': '#ff6b6b', 'shape': 'box', 'size': 25},
    'Object': {'color': '#4ecdc4', 'shape': 'circle', 'size': 20},
    'Morphism': {'color': '#45b7d1', 'shape': 'triangle', 'size': 15},
    'Functor': {'color': '#96ceb4', 'shape': 'diamond', 'size': 22},
    'Natural_Transformation': {'color': '#feca57', 'shape': 'star', 'size': 18}
}

# Edge styling configuration
EDGE_STYLES = {
    'morphism': {'color': '#34495e', 'width': 2, 'arrows': 'to'},
    'functor': {'color': '#9b59b6', 'width': 3, 'arrows': 'to'},
    'natural_transformation': {'color': '#e67e22', 'width': 2, 'arrows': 'to'},
    'structural': {'color': '#bdc3c7', 'width': 1, 'dashes': True}
}


@st.cache_data
def get_visualization_data(_dal: CategoryDAL, entity_type: str, entity_id: Optional[int] = None, mode: str = 'standard') -> Dict[str, Any]:
    """
    Query database and return data structure for visualization.
    
    Args:
        dal: Data access layer instance
        entity_type: Type of entity to visualize
        entity_id: Specific entity ID (None for all)
        mode: Visualization mode ('standard', 'complete', 'meta')
        
    Returns:
        Dictionary with nodes, edges, and metadata
    """
    try:
        if entity_type == "Category" and entity_id is not None:
            return get_category_visualization_data(_dal, entity_id, mode)
        elif entity_type == "Functor":
            return get_functor_visualization_data(_dal, mode)
        elif entity_type == "Natural Transformation":
            return get_natural_transformation_visualization_data(_dal, mode)
        else:
            return get_complete_graph_data(_dal, mode)
            
    except Exception as e:
        logger.error(f"Failed to get visualization data: {e}")
        return {"nodes": [], "edges": [], "metadata": {"error": str(e)}}


def get_category_visualization_data(dal: CategoryDAL, category_id: int, mode: str) -> Dict[str, Any]:
    """Get visualization data for a specific category."""
    try:
        category = dal.get_category(category_id)
        if not category:
            return {"nodes": [], "edges": [], "metadata": {"error": "Category not found"}}
        
        objects = dal.get_objects_in_category(category_id)
        morphisms = dal.get_morphisms_in_category(category_id)
        
        nodes = []
        edges = []
        
        # Add category as central node if in meta mode
        if mode == 'meta':
            nodes.append({
                'id': f"cat_{category_id}",
                'label': category['name'],
                'title': f"Category: {category['name']}\n{category['description']}",
                'color': NODE_STYLES['Category']['color'],
                'shape': NODE_STYLES['Category']['shape'],
                'size': NODE_STYLES['Category']['size']
            })
        
        # Add objects as nodes
        for obj in objects:
            nodes.append({
                'id': f"obj_{obj['ID']}",
                'label': obj['name'],
                'title': f"Object: {obj['name']}\n{obj['description']}",
                'color': NODE_STYLES['Object']['color'],
                'shape': NODE_STYLES['Object']['shape'],
                'size': NODE_STYLES['Object']['size']
            })
            
            # Add structural edge from category to object in meta mode
            if mode == 'meta':
                edges.append({
                    'from': f"cat_{category_id}",
                    'to': f"obj_{obj['ID']}",
                    'color': EDGE_STYLES['structural']['color'],
                    'width': EDGE_STYLES['structural']['width'],
                    'dashes': EDGE_STYLES['structural'].get('dashes', False),
                    'title': 'contains'
                })
        
        # Add morphisms as edges (standard mode) or nodes (meta mode)
        for morph in morphisms:
            if mode == 'meta':
                # Add morphism as node
                nodes.append({
                    'id': f"morph_{morph['ID']}",
                    'label': morph['name'],
                    'title': f"Morphism: {morph['name']}\n{morph['description']}\nIdentity: {morph['is_identity']}",
                    'color': NODE_STYLES['Morphism']['color'],
                    'shape': NODE_STYLES['Morphism']['shape'],
                    'size': NODE_STYLES['Morphism']['size']
                })
                
                # Add edges from morphism to source/target objects
                if morph['source_object']:
                    source_obj_id = next((obj['ID'] for obj in objects if obj['name'] == morph['source_object']), None)
                    if source_obj_id is not None:
                        edges.append({
                            'from': f"morph_{morph['ID']}",
                            'to': f"obj_{source_obj_id}",
                            'color': EDGE_STYLES['structural']['color'],
                            'width': EDGE_STYLES['structural']['width'],
                            'title': 'source'
                        })
                
                if morph['target_object']:
                    target_obj_id = next((obj['ID'] for obj in objects if obj['name'] == morph['target_object']), None)
                    if target_obj_id is not None:
                        edges.append({
                            'from': f"morph_{morph['ID']}",
                            'to': f"obj_{target_obj_id}",
                            'color': EDGE_STYLES['structural']['color'],
                            'width': EDGE_STYLES['structural']['width'],
                            'title': 'target'
                        })
            else:
                # Add morphism as edge between objects (standard mode)
                if morph['source_object'] and morph['target_object']:
                    source_obj_id = next((obj['ID'] for obj in objects if obj['name'] == morph['source_object']), None)
                    target_obj_id = next((obj['ID'] for obj in objects if obj['name'] == morph['target_object']), None)
                    
                    if source_obj_id is not None and target_obj_id is not None:
                        edge_style = EDGE_STYLES['morphism'].copy()
                        if morph['is_identity']:
                            edge_style['color'] = '#2c3e50'
                            edge_style['width'] = 1
                        
                        edges.append({
                            'from': f"obj_{source_obj_id}",
                            'to': f"obj_{target_obj_id}",
                            'label': morph['name'],
                            'title': f"Morphism: {morph['name']}\n{morph['description']}",
                            'color': edge_style['color'],
                            'width': edge_style['width'],
                            'arrows': edge_style['arrows']
                        })
        
        metadata = {
            'category_name': category['name'],
            'object_count': len(objects),
            'morphism_count': len(morphisms),
            'mode': mode
        }
        
        return {"nodes": nodes, "edges": edges, "metadata": metadata}
        
    except Exception as e:
        logger.error(f"Failed to get category visualization data: {e}")
        return {"nodes": [], "edges": [], "metadata": {"error": str(e)}}


def get_functor_visualization_data(dal: CategoryDAL, mode: str) -> Dict[str, Any]:
    """Get visualization data for functors."""
    try:
        categories = dal.list_categories()
        functors = dal.list_functors()
        
        nodes = []
        edges = []
        
        # Add categories as nodes
        for cat in categories:
            nodes.append({
                'id': f"cat_{cat['ID']}",
                'label': cat['name'],
                'title': f"Category: {cat['name']}\n{cat['description']}",
                'color': NODE_STYLES['Category']['color'],
                'shape': NODE_STYLES['Category']['shape'],
                'size': NODE_STYLES['Category']['size']
            })
        
        # Add functors as edges between categories
        for functor in functors:
            if functor['source_category'] and functor['target_category']:
                source_cat_id = next((cat['ID'] for cat in categories if cat['name'] == functor['source_category']), None)
                target_cat_id = next((cat['ID'] for cat in categories if cat['name'] == functor['target_category']), None)
                
                if source_cat_id is not None and target_cat_id is not None:
                    edges.append({
                        'from': f"cat_{source_cat_id}",
                        'to': f"cat_{target_cat_id}",
                        'label': functor['name'],
                        'title': f"Functor: {functor['name']}\n{functor['description']}",
                        'color': EDGE_STYLES['functor']['color'],
                        'width': EDGE_STYLES['functor']['width'],
                        'arrows': EDGE_STYLES['functor']['arrows']
                    })
        
        metadata = {
            'category_count': len(categories),
            'functor_count': len(functors),
            'mode': mode
        }
        
        return {"nodes": nodes, "edges": edges, "metadata": metadata}
        
    except Exception as e:
        logger.error(f"Failed to get functor visualization data: {e}")
        return {"nodes": [], "edges": [], "metadata": {"error": str(e)}}


def get_natural_transformation_visualization_data(dal: CategoryDAL, mode: str) -> Dict[str, Any]:
    """Get visualization data for natural transformations."""
    try:
        functors = dal.list_functors()
        nat_trans = dal.list_natural_transformations()
        
        nodes = []
        edges = []
        
        # Add functors as nodes
        for functor in functors:
            nodes.append({
                'id': f"func_{functor['ID']}",
                'label': functor['name'],
                'title': f"Functor: {functor['name']}\n{functor['description']}\n{functor['source_category']} → {functor['target_category']}",
                'color': NODE_STYLES['Functor']['color'],
                'shape': NODE_STYLES['Functor']['shape'],
                'size': NODE_STYLES['Functor']['size']
            })
        
        # Add natural transformations as edges between functors
        for nt in nat_trans:
            # For now, create placeholder edges
            # In a full implementation, we'd query for the actual functor relationships
            edges.append({
                'from': f"func_0",  # Placeholder
                'to': f"func_1",    # Placeholder  
                'label': nt['name'],
                'title': f"Natural Transformation: {nt['name']}\n{nt['description']}",
                'color': EDGE_STYLES['natural_transformation']['color'],
                'width': EDGE_STYLES['natural_transformation']['width'],
                'arrows': EDGE_STYLES['natural_transformation']['arrows']
            })
        
        metadata = {
            'functor_count': len(functors),
            'natural_transformation_count': len(nat_trans),
            'mode': mode
        }
        
        return {"nodes": nodes, "edges": edges, "metadata": metadata}
        
    except Exception as e:
        logger.error(f"Failed to get natural transformation visualization data: {e}")
        return {"nodes": [], "edges": [], "metadata": {"error": str(e)}}


def get_complete_graph_data(dal: CategoryDAL, mode: str) -> Dict[str, Any]:
    """Get complete graph visualization data showing all entities."""
    try:
        categories = dal.list_categories()
        functors = dal.list_functors()
        nat_trans = dal.list_natural_transformations()
        
        nodes = []
        edges = []
        
        # Add all categories
        for cat in categories:
            nodes.append({
                'id': f"cat_{cat['ID']}",
                'label': cat['name'],
                'title': f"Category: {cat['name']}\n{cat['description']}",
                'color': NODE_STYLES['Category']['color'],
                'shape': NODE_STYLES['Category']['shape'],
                'size': NODE_STYLES['Category']['size']
            })
        
        # Add all functors
        for functor in functors:
            nodes.append({
                'id': f"func_{functor['ID']}",
                'label': functor['name'],
                'title': f"Functor: {functor['name']}\n{functor['description']}",
                'color': NODE_STYLES['Functor']['color'],
                'shape': NODE_STYLES['Functor']['shape'],
                'size': NODE_STYLES['Functor']['size']
            })
        
        # Add all natural transformations
        for nt in nat_trans:
            nodes.append({
                'id': f"nt_{nt['ID']}",
                'label': nt['name'],
                'title': f"Natural Transformation: {nt['name']}\n{nt['description']}",
                'color': NODE_STYLES['Natural_Transformation']['color'],
                'shape': NODE_STYLES['Natural_Transformation']['shape'],
                'size': NODE_STYLES['Natural_Transformation']['size']
            })
        
        metadata = {
            'total_entities': len(nodes),
            'categories': len(categories),
            'functors': len(functors),
            'natural_transformations': len(nat_trans),
            'mode': mode
        }
        
        return {"nodes": nodes, "edges": edges, "metadata": metadata}
        
    except Exception as e:
        logger.error(f"Failed to get complete graph data: {e}")
        return {"nodes": [], "edges": [], "metadata": {"error": str(e)}}


def create_pyvis_network(nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]], config: Dict[str, Any]) -> Network:
    """
    Create and configure PyVis Network object.
    
    Args:
        nodes: List of node dictionaries
        edges: List of edge dictionaries  
        config: Configuration options
        
    Returns:
        Configured PyVis Network object
    """
    try:
        # Create network with configuration
        net = Network(
            height=config.get('height', '600px'),
            width=config.get('width', '100%'),
            bgcolor=config.get('bgcolor', '#ffffff'),
            font_color=config.get('font_color', '#000000'),
            directed=config.get('directed', True)
        )
        
        # Configure physics
        net.set_options("""
        {
          "physics": {
            "enabled": true,
            "stabilization": {"iterations": 100},
            "barnesHut": {
              "gravitationalConstant": -8000,
              "centralGravity": 0.3,
              "springLength": 95,
              "springConstant": 0.04,
              "damping": 0.09
            }
          },
          "interaction": {
            "hover": true,
            "selectConnectedEdges": true
          },
          "layout": {
            "improvedLayout": true
          }
        }
        """)
        
        # Add nodes
        for node in nodes:
            net.add_node(
                node['id'],
                label=node['label'],
                title=node.get('title', ''),
                color=node.get('color', '#97C2FC'),
                shape=node.get('shape', 'circle'),
                size=node.get('size', 20)
            )
        
        # Add edges
        for edge in edges:
            net.add_edge(
                edge['from'],
                edge['to'],
                label=edge.get('label', ''),
                title=edge.get('title', ''),
                color=edge.get('color', '#2B7CE9'),
                width=edge.get('width', 1),
                arrows=edge.get('arrows', 'to'),
                dashes=edge.get('dashes', False)
            )
        
        return net
        
    except Exception as e:
        logger.error(f"Failed to create PyVis network: {e}")
        raise


def render_visualization(dal: CategoryDAL, entity_type: str, entity_id: Optional[int] = None) -> None:
    """
    Render the interactive visualization in Streamlit.
    
    Args:
        dal: Data access layer instance
        entity_type: Type of entity to visualize
        entity_id: Specific entity ID (None for all)
    """
    try:
        # Visualization controls
        st.subheader("Visualization Controls")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            mode = st.selectbox(
                "Visualization Mode",
                ['standard', 'meta', 'complete'],
                help="Standard: Mathematical view, Meta: Show all relationships, Complete: All entities"
            )
        
        with col2:
            layout = st.selectbox(
                "Layout",
                ['force_directed', 'hierarchical', 'circular'],
                help="Graph layout algorithm"
            )
        
        with col3:
            show_labels = st.checkbox("Show Edge Labels", value=True)
        
        # Configuration
        config = {
            'height': '600px',
            'width': '100%',
            'bgcolor': '#ffffff',
            'font_color': '#000000',
            'directed': True,
            'layout': layout,
            'show_labels': show_labels
        }
        
        # Get visualization data
        viz_data = get_visualization_data(dal, entity_type, entity_id, mode)
        
        if 'error' in viz_data['metadata']:
            st.error(f"Visualization error: {viz_data['metadata']['error']}")
            return
        
        # Show metadata
        metadata = viz_data['metadata']
        if entity_type == "Category":
            st.info(f"**{metadata.get('category_name', 'Unknown')}**: {metadata.get('object_count', 0)} objects, {metadata.get('morphism_count', 0)} morphisms")
        elif entity_type == "Functor":
            st.info(f"**Functors**: {metadata.get('category_count', 0)} categories, {metadata.get('functor_count', 0)} functors")
        elif entity_type == "Natural Transformation":
            st.info(f"**Natural Transformations**: {metadata.get('functor_count', 0)} functors, {metadata.get('natural_transformation_count', 0)} transformations")
        
        # Check if there's data to visualize
        if not viz_data['nodes']:
            st.warning("No data to visualize. Create some entities first!")
            return
        
        # Create and render network
        net = create_pyvis_network(viz_data['nodes'], viz_data['edges'], config)
        
        # Generate HTML and display
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as tmp_file:
            net.save_graph(tmp_file.name)
            
        # Read and display the HTML
        with open(tmp_file.name, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Display in Streamlit
        st.components.v1.html(html_content, height=650, scrolling=True)
        
        # Export options
        st.subheader("Export Options")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Download HTML", key="export_html"):
                with open(tmp_file.name, 'r', encoding='utf-8') as f:
                    st.download_button(
                        label="Download Visualization",
                        data=f.read(),
                        file_name=f"visualization_{entity_type.lower()}.html",
                        mime="text/html"
                    )
        
        with col2:
            if st.button("Save as PNG", key="export_png"):
                st.info("PNG export functionality coming soon")
        
        # Cleanup
        Path(tmp_file.name).unlink(missing_ok=True)
        
    except Exception as e:
        st.error(f"Failed to render visualization: {e}")
        logger.error(f"Visualization render error: {e}")


def render_visualization_statistics(dal: CategoryDAL) -> None:
    """Render visualization statistics and entity counts."""
    try:
        categories = dal.list_categories()
        functors = dal.list_functors()
        nat_trans = dal.list_natural_transformations()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Categories", len(categories))
        
        with col2:
            total_objects = sum(len(dal.get_objects_in_category(cat['ID'])) for cat in categories)
            st.metric("Objects", total_objects)
        
        with col3:
            total_morphisms = sum(len(dal.get_morphisms_in_category(cat['ID'])) for cat in categories)
            st.metric("Morphisms", total_morphisms)
        
        with col4:
            st.metric("Functors", len(functors))
        
    except Exception as e:
        st.error(f"Failed to load statistics: {e}")
