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
def get_visualization_data(_dal: CategoryDAL, entity_type: str, entity_id: Optional[int] = None, mode: str = 'standard', overlay: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Query database and return data structure for visualization.
    
    Args:
        dal: Data access layer instance
        entity_type: Type of entity to visualize
        entity_id: Specific entity ID (None for all)
        mode: Visualization mode ('standard', 'complete', 'meta', 'functor-detail', 'nt-detail')
        overlay: Optional selection details (e.g., {'nt_id': int, 'morphism_id': int})
        
    Returns:
        Dictionary with nodes, edges, and metadata
    """
    try:
        if entity_type == "Category" and entity_id is not None:
            return get_category_visualization_data(_dal, entity_id, mode)
        elif entity_type == "Functor":
            return get_functor_visualization_data(_dal, mode)
        elif entity_type == "Natural Transformation":
            return get_natural_transformation_visualization_data(_dal, mode, overlay)
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
        
        nodes: List[Dict[str, Any]] = []
        edges: List[Dict[str, Any]] = []
        
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
        
        # Add functors as edges between categories, with tooltip counts
        for functor in functors:
            if functor['source_category'] and functor['target_category']:
                source_cat_id = next((cat['ID'] for cat in categories if cat['name'] == functor['source_category']), None)
                target_cat_id = next((cat['ID'] for cat in categories if cat['name'] == functor['target_category']), None)
                
                if source_cat_id is not None and target_cat_id is not None:
                    try:
                        obj_map_count = len(dal.get_functor_object_mappings(functor['ID']))
                        morph_map_count = len(dal.get_functor_morphism_mappings(functor['ID']))
                    except Exception:
                        obj_map_count = 0
                        morph_map_count = 0
                    edges.append({
                        'from': f"cat_{source_cat_id}",
                        'to': f"cat_{target_cat_id}",
                        'label': functor['name'],
                        'title': f"Functor: {functor['name']}\n{functor['description']}\nObjects mapped: {obj_map_count}\nMorphisms mapped: {morph_map_count}",
                        'color': EDGE_STYLES['functor']['color'],
                        'width': EDGE_STYLES['functor']['width'],
                        'arrows': EDGE_STYLES['functor']['arrows']
                    })
        
        # Functor-detail mode: show object nodes per category and mapping edges
        if mode == 'functor-detail':
            for functor in functors:
                src_id = functor.get('source_category_id')
                tgt_id = functor.get('target_category_id')
                if src_id is None or tgt_id is None:
                    continue
                src_objs = dal.get_objects_in_category(src_id)
                tgt_objs = dal.get_objects_in_category(tgt_id)
                # Add object nodes with category-specific IDs to avoid collisions
                for o in src_objs:
                    nodes.append({
                        'id': f"obj_{src_id}_{o['ID']}",
                        'label': o['name'],
                        'title': f"{functor['source_category']}:{o['name']}",
                        'color': NODE_STYLES['Object']['color'],
                        'shape': NODE_STYLES['Object']['shape'],
                        'size': NODE_STYLES['Object']['size']
                    })
                for o in tgt_objs:
                    nodes.append({
                        'id': f"obj_{tgt_id}_{o['ID']}",
                        'label': o['name'],
                        'title': f"{functor['target_category']}:{o['name']}",
                        'color': NODE_STYLES['Object']['color'],
                        'shape': NODE_STYLES['Object']['shape'],
                        'size': NODE_STYLES['Object']['size']
                    })
                # Mapping edges
                try:
                    obj_maps = dal.get_functor_object_mappings(functor['ID'])
                    for m in obj_maps:
                        edges.append({
                            'from': f"obj_{src_id}_{m['source_object_id']}",
                            'to': f"obj_{tgt_id}_{m['target_object_id']}",
                            'label': functor['name'],
                            'title': f"{functor['name']}: {m['source_object']} → {m['target_object']}",
                            'color': '#95a5a6',
                            'width': 1,
                            'arrows': 'to'
                        })
                except Exception:
                    pass
        
        metadata = {
            'category_count': len(categories),
            'functor_count': len(functors),
            'mode': mode
        }
        
        return {"nodes": nodes, "edges": edges, "metadata": metadata}
        
    except Exception as e:
        logger.error(f"Failed to get functor visualization data: {e}")
        return {"nodes": [], "edges": [], "metadata": {"error": str(e)}}


def get_natural_transformation_visualization_data(dal: CategoryDAL, mode: str, overlay: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
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
            src_id = nt.get('source_functor_id')
            tgt_id = nt.get('target_functor_id')
            if src_id is not None and tgt_id is not None:
                edges.append({
                    'from': f"func_{src_id}",
                    'to': f"func_{tgt_id}",
                    'label': nt['name'],
                    'title': f"Natural Transformation: {nt['name']}\n{nt.get('description','')}",
                    'color': EDGE_STYLES['natural_transformation']['color'],
                    'width': EDGE_STYLES['natural_transformation']['width'],
                    'arrows': EDGE_STYLES['natural_transformation']['arrows']
                })
        
        # nt-detail mode: render components α_X between F(X) and G(X)
        if mode == 'nt-detail':
            for nt in nat_trans:
                comps = dal.get_nt_components(nt['ID'])
                for comp in comps:
                    src_obj_id = comp.get('source_object_id')
                    tgt_obj_id = comp.get('target_object_id')
                    src_obj_label = comp.get('source_object') or 'F(X)'
                    tgt_obj_label = comp.get('target_object') or 'G(X)'
                    if src_obj_id is not None:
                        nodes.append({
                            'id': f"nt_{nt['ID']}_obj_{src_obj_id}",
                            'label': src_obj_label,
                            'title': f"F(X): {src_obj_label}",
                            'color': NODE_STYLES['Object']['color'],
                            'shape': NODE_STYLES['Object']['shape'],
                            'size': NODE_STYLES['Object']['size']
                        })
                    if tgt_obj_id is not None:
                        nodes.append({
                            'id': f"nt_{nt['ID']}_obj_{tgt_obj_id}",
                            'label': tgt_obj_label,
                            'title': f"G(X): {tgt_obj_label}",
                            'color': NODE_STYLES['Object']['color'],
                            'shape': NODE_STYLES['Object']['shape'],
                            'size': NODE_STYLES['Object']['size']
                        })
                    if src_obj_id is not None and tgt_obj_id is not None:
                        edges.append({
                            'from': f"nt_{nt['ID']}_obj_{src_obj_id}",
                            'to': f"nt_{nt['ID']}_obj_{tgt_obj_id}",
                            'label': nt['name'],
                            'title': f"α_X: {comp.get('morphism_name','α')}\n{src_obj_label} → {tgt_obj_label}",
                            'color': '#e67e22',
                            'width': 2,
                            'arrows': 'to'
                        })
                # Overlay selected commuting square if provided
                if overlay and overlay.get('nt_id') == nt['ID'] and overlay.get('morphism_id') is not None:
                    try:
                        # Lookup functors and source category
                        F = next((f for f in functors if f['ID'] == nt.get('source_functor_id')), None)
                        G = next((f for f in functors if f['ID'] == nt.get('target_functor_id')), None)
                        if F and G:
                            src_cat_id = F.get('source_category_id')
                            # Resolve morphism f: X->Y and their object IDs
                            res = dal.conn.execute(
                                """MATCH (c:Category)-[:category_morphisms]->(f:Morphism)
                                       WHERE c.ID = $cid AND f.ID = $fid
                                       OPTIONAL MATCH (f)-[:morphism_source]->(x:Object)
                                       OPTIONAL MATCH (f)-[:morphism_target]->(y:Object)
                                       RETURN x.ID, x.name, y.ID, y.name""",
                                {"cid": src_cat_id, "fid": int(overlay['morphism_id'])}
                            )
                            qr = _get_query_result(res)
                            if qr.has_next():  # type: ignore
                                row = qr.get_next()  # type: ignore
                                X_id, X_name, Y_id, Y_name = row[0], row[1], row[2], row[3]
                                # Render nodes for F(X), F(Y), G(X), G(Y) using components if present, else labels
                                # Alpha edges already drawn if components exist
                                # Draw F(f) and G(f) edges between appropriate nodes
                                # Resolve target morphisms of F and G
                                qF = dal.conn.execute(
                                    """MATCH (sm:Morphism)-[r:functor_morphism_map]->(tm:Morphism)
                                           WHERE r.via_functor_id = $fid AND sm.ID = $smid
                                           OPTIONAL MATCH (tm)-[:morphism_source]->(tms:Object)
                                           OPTIONAL MATCH (tm)-[:morphism_target]->(tmt:Object)
                                           RETURN tm.ID, tms.ID, tmt.ID, tms.name, tmt.name""",
                                    {"fid": F['ID'], "smid": int(overlay['morphism_id'])}
                                )
                                qG = dal.conn.execute(
                                    """MATCH (sm:Morphism)-[r:functor_morphism_map]->(tm:Morphism)
                                           WHERE r.via_functor_id = $gid AND sm.ID = $smid
                                           OPTIONAL MATCH (tm)-[:morphism_source]->(tms:Object)
                                           OPTIONAL MATCH (tm)-[:morphism_target]->(tmt:Object)
                                           RETURN tm.ID, tms.ID, tmt.ID, tms.name, tmt.name""",
                                    {"gid": G['ID'], "smid": int(overlay['morphism_id'])}
                                )
                                qF = _get_query_result(qF)
                                qG = _get_query_result(qG)
                                if qF.has_next() and qG.has_next():  # type: ignore
                                    rF = qF.get_next()  # type: ignore
                                    rG = qG.get_next()  # type: ignore
                                    F_src_id, F_tgt_id, F_src_name, F_tgt_name = rF[1], rF[2], rF[3], rF[4]
                                    G_src_id, G_tgt_id, G_src_name, G_tgt_name = rG[1], rG[2], rG[3], rG[4]
                                    # Ensure nodes exist
                                    def ensure_node(node_id: str, label: str, title: str):
                                        if not any(n['id'] == node_id for n in nodes):
                                            nodes.append({
                                                'id': node_id,
                                                'label': label,
                                                'title': title,
                                                'color': NODE_STYLES['Object']['color'],
                                                'shape': NODE_STYLES['Object']['shape'],
                                                'size': NODE_STYLES['Object']['size']
                                            })
                                    n_FX = f"nt_{nt['ID']}_obj_{F_src_id}"
                                    n_FY = f"nt_{nt['ID']}_obj_{F_tgt_id}"
                                    n_GX = f"nt_{nt['ID']}_obj_{G_src_id}"
                                    n_GY = f"nt_{nt['ID']}_obj_{G_tgt_id}"
                                    ensure_node(n_FX, F_src_name or 'F(X)', f"F(X): {F_src_name}")
                                    ensure_node(n_FY, F_tgt_name or 'F(Y)', f"F(Y): {F_tgt_name}")
                                    ensure_node(n_GX, G_src_name or 'G(X)', f"G(X): {G_src_name}")
                                    ensure_node(n_GY, G_tgt_name or 'G(Y)', f"G(Y): {G_tgt_name}")
                                    # Add F(f) and G(f) overlay edges
                                    edges.append({
                                        'from': n_FX,
                                        'to': n_FY,
                                        'label': 'F(f)',
                                        'title': f"F(f): {F_src_name} → {F_tgt_name}",
                                        'color': '#3498db',
                                        'width': 2,
                                        'arrows': 'to'
                                    })
                                    edges.append({
                                        'from': n_GX,
                                        'to': n_GY,
                                        'label': 'G(f)',
                                        'title': f"G(f): {G_src_name} → {G_tgt_name}",
                                        'color': '#9b59b6',
                                        'width': 2,
                                        'arrows': 'to'
                                    })
                    except Exception:
                        pass
        
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
        
        # Configure physics based on layout
        layout_type = config.get('layout', 'force_directed')
        
        if layout_type == 'hierarchical':
            physics_config = {
                "physics": {
                    "enabled": False
                },
                "layout": {
                    "hierarchical": {
                        "enabled": True,
                        "direction": "UD",
                        "sortMethod": "directed"
                    }
                }
            }
        elif layout_type == 'circular':
            physics_config = {
                "physics": {
                    "enabled": False
                },
                "layout": {
                    "randomSeed": 42
                }
            }
        elif layout_type == 'manual':
            physics_config = {
                "physics": {
                    "enabled": False
                },
                "interaction": {
                    "dragNodes": True,
                    "dragView": True,
                    "zoomView": True
                }
            }
        else:  # force_directed
            # Use physics_strength parameter to adjust force
            strength = config.get('physics_strength', 0.5)
            physics_config = {
                "physics": {
                    "enabled": True,
                    "stabilization": {"iterations": 100},
                    "barnesHut": {
                        "gravitationalConstant": -2000 * strength,  # Adjustable based on slider
                        "centralGravity": 0.1 * strength,           # Adjustable
                        "springLength": 120,                        # Keep constant
                        "springConstant": 0.02 * strength,          # Adjustable  
                        "damping": 0.15 + (0.1 * (1 - strength))    # More damping = easier dragging
                    }
                }
            }
        
        # Common interaction settings (unless overridden by manual layout)
        if "interaction" not in physics_config:
            physics_config["interaction"] = {
                "hover": True,
                "selectConnectedEdges": True,
                "dragNodes": True,
                "dragView": True,
                "zoomView": True,
                "multiselect": True,
                "tooltipDelay": 200
            }
        
        # Apply the configuration
        import json
        net.set_options(json.dumps(physics_config))
        
        # Add nodes with layout-specific positioning
        import math
        
        for i, node in enumerate(nodes):
            # Use default node size
            display_size = node.get('size', 20)
            
            node_config = {
                'label': node['label'],
                'title': node.get('title', ''),
                'color': node.get('color', '#97C2FC'),
                'shape': node.get('shape', 'circle'),
                'size': display_size
            }
            
            # Add position for circular layout
            if layout_type == 'circular' and len(nodes) > 1:
                angle = 2 * math.pi * i / len(nodes)
                # Adjust radius based on number of nodes for better spacing
                radius = max(150, 50 + (len(nodes) * 15))
                x = radius * math.cos(angle)
                y = radius * math.sin(angle)
                node_config['x'] = x
                node_config['y'] = y
                node_config['physics'] = False  # Fix position for circular layout
            elif layout_type == 'manual':
                # For manual layout, let PyVis use default positioning but disable physics
                node_config['physics'] = False
            
            net.add_node(node['id'], **node_config)
        
        # Add edges with conditional labels
        show_labels = config.get('show_labels', True)
        
        for edge in edges:
            edge_config = {
                'title': edge.get('title', ''),
                'color': edge.get('color', '#2B7CE9'),
                'width': edge.get('width', 1),
                'arrows': edge.get('arrows', 'to'),
                'dashes': edge.get('dashes', False)
            }
            
            # Only add label if show_labels is enabled
            if show_labels and edge.get('label'):
                edge_config['label'] = edge['label']
            
            net.add_edge(edge['from'], edge['to'], **edge_config)
        
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
        
        col1, col2, col3, col4 = st.columns(4)
        
        # Help toggles section
        help_col1, help_col2 = st.columns(2)
        
        # Add layout information with toggle
        if 'show_layout_help' not in st.session_state:
            st.session_state.show_layout_help = False
        
        with help_col1:
            if st.button("ℹ️ Layout Help" if not st.session_state.show_layout_help else "❌ Close Help", 
                         key="toggle_layout_help"):
                st.session_state.show_layout_help = not st.session_state.show_layout_help
                st.rerun()
        
        # Add zoom info toggle
        if 'show_zoom_info' not in st.session_state:
            st.session_state.show_zoom_info = False
        
        with help_col2:
            if st.button("🔍 Zoom Info" if not st.session_state.show_zoom_info else "❌ Close Zoom", 
                         key="toggle_zoom_info"):
                st.session_state.show_zoom_info = not st.session_state.show_zoom_info
                st.rerun()
        
        if st.session_state.show_layout_help:
            st.info("""
            **Layout Options:**
            - **Force-directed**: Spring physics simulation (adjustable strength)
            - **Hierarchical**: Tree-like structure for directed graphs
            - **Circular**: Nodes arranged in a circle
            - **Manual**: No physics - drag nodes freely
            """)
            st.info("""
            **Interaction Tips:**
            - Drag nodes to reposition (works best with lower physics strength)
            - Scroll to zoom in/out
            - Click and drag background to pan
            - Hover over nodes/edges for details
            """)
        
        if st.session_state.show_zoom_info:
            st.info("""
            **Zoom & Navigation:**
            - **Mouse wheel**: Zoom in/out
            - **Click + drag background**: Pan view
            - **Click + drag nodes**: Reposition (in force-directed/manual modes)
            - **Double-click**: Focus on node
            """)
        
        with col1:
            mode = st.selectbox(
                "Visualization Mode",
                ['standard', 'meta', 'functor-detail', 'nt-detail', 'complete'],
                help="Standard: Mathematical view, Meta: Show all relationships, Functor-detail: object/morphism mappings, NT-detail: α components, Complete: All entities"
            )
        
        with col2:
            layout = st.selectbox(
                "Layout",
                ['force_directed', 'hierarchical', 'circular', 'manual'],
                help="Force: Spring physics, Hierarchical: Tree structure, Circular: Even distribution, Manual: Free positioning"
            )
        
        with col3:
            show_labels = st.checkbox("Show Edge Labels", value=True)
        
        with col4:
            if layout == 'force_directed':
                physics_strength = st.slider(
                    "Physics Strength", 
                    min_value=0.1, 
                    max_value=2.0, 
                    value=0.5, 
                    step=0.1,
                    help="Lower = easier to drag nodes"
                )
            else:
                physics_strength = 0.5  # Default value
        
        # Configuration
        config = {
            'height': '600px',
            'width': '100%',
            'bgcolor': '#ffffff',
            'font_color': '#000000',
            'directed': True,
            'layout': layout,
            'show_labels': show_labels,
            'physics_strength': physics_strength
        }
        
        # Optional NT-detail overlay selection
        overlay = None
        if entity_type == "Natural Transformation" and mode == 'nt-detail':
            try:
                nts = dal.list_natural_transformations()
                if nts:
                    nt_options = {nt['ID']: nt['name'] for nt in nts}
                    selected_nt = st.selectbox("Natural Transformation", list(nt_options.keys()), format_func=lambda x: nt_options[x])
                    # Resolve source category via source functor
                    functors = dal.list_functors()
                    F = next((f for f in functors if f['ID'] == next((n.get('source_functor_id') for n in nts if n['ID'] == selected_nt), None)), None)
                    if F and F.get('source_category_id') is not None:
                        morphs = dal.get_morphisms_in_category(F['source_category_id'])
                        if morphs:
                            morph_options = {m['ID']: f"{m['name']} ({m.get('source_object','?')} → {m.get('target_object','?')})" for m in morphs}
                            selected_m = st.selectbox("Morph. f: X → Y (overlay square)", list(morph_options.keys()), format_func=lambda x: morph_options[x])
                            overlay = {'nt_id': selected_nt, 'morphism_id': selected_m}
            except Exception:
                overlay = None
        
        # Get visualization data
        viz_data = get_visualization_data(dal, entity_type, entity_id, mode, overlay=overlay)
        
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
            # Direct download button
            with open(tmp_file.name, 'r', encoding='utf-8') as f:
                st.download_button(
                    label="📄 Download HTML",
                    data=f.read(),
                    file_name=f"codices_visualization_{entity_type.lower()}_{layout}.html",
                    mime="text/html",
                    help="Download interactive HTML visualization"
                )
        
        with col2:
            if st.button("📊 Export Info", key="export_info"):
                st.info("""
                **Export Options:**
                - **HTML**: Interactive visualization (recommended)
                - **PNG**: Static image (use browser screenshot for now)
                - **SVG**: Vector graphics (future feature)
                - **Data**: JSON export of graph data (future feature)
                """)
        
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
