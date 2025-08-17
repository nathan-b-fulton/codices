# Data Access Layer (DAL) Planning

## Current State Analysis

The existing `kuzu_DAL.py` file provides:
- Basic schema definition for nodes and relationships
- Simple table creation functions
- Database initialization

## Issues Identified in Current Implementation

1. **Duplicate relationship keys**: The `rel_tables` dict has multiple entries with the same key (`'source'`, `'target'`, `'includes'`)
2. **Missing documentation**: Functions lack proper docstrings
3. **No CRUD operations**: Only table creation is implemented
4. **No transaction support**: Required for the preview/commit/rollback functionality
5. **No error handling**: Database operations should handle failures gracefully

## Required Enhancements

### 1. Schema Fixes
- Fix duplicate keys in `rel_tables` by using unique relationship names
- Add proper relationship naming (e.g., `morphism_source`, `morphism_target`, `functor_source`, etc.)

### 2. CRUD Operations Needed
```python
# Node operations
create_category(name, description) -> int
create_object(name, description, category_id) -> int
create_morphism(name, description, source_obj_id, target_obj_id, category_id) -> int
create_functor(name, description, source_cat_id, target_cat_id) -> int
create_natural_transformation(name, description, source_functor_id, target_functor_id) -> int

# Read operations
get_category(category_id) -> dict
get_objects_in_category(category_id) -> List[dict]
get_morphisms_in_category(category_id) -> List[dict]
get_functors_for_category(category_id) -> List[dict]
get_natural_transformations_for_functor(functor_id) -> List[dict]

# Update operations
update_category(category_id, name=None, description=None) -> bool
update_object(object_id, name=None, description=None) -> bool
# ... similar for other entities

# Delete operations (with cascade handling)
delete_category(category_id) -> bool
delete_object(object_id) -> bool
# ... similar for other entities
```

### 3. Transaction Management
```python
class CategorySession:
    def __init__(self, db_path):
        self.db = kuzu.Database(db_path)
        self.conn = kuzu.Connection(db)
        self.transaction = None
    
    def begin_transaction(self):
        # Start transaction for preview mode
    
    def commit_transaction(self):
        # Commit changes to persistent storage
    
    def rollback_transaction(self):
        # Discard all changes in current session
```

### 4. Query Utilities
- Functions to build complex queries for getting related entities
- Validation functions to ensure category theory constraints
- Helper functions for visualization data preparation

## Schema Improvements

### Fixed Relationship Schema
```python
rel_tables = {
    'morphism_source': {'from': 'Morphism', 'to': 'Object', 'uniqueness': 'MANY_ONE'},
    'morphism_target': {'from': 'Morphism', 'to': 'Object', 'uniqueness': 'MANY_ONE'},
    'functor_morphism_component_source': {'from': 'Morphism', 'to': 'Morphism', 'uniqueness': 'MANY_ONE'},
    'functor_morphism_component_target': {'from': 'Morphism', 'to': 'Morphism', 'uniqueness': 'MANY_ONE'},
    'functor_source': {'from': 'Functor', 'to': 'Category', 'uniqueness': 'MANY_ONE'},
    'functor_target': {'from': 'Functor', 'to': 'Category', 'uniqueness': 'MANY_ONE'},
    'nat_trans_source': {'from': 'Natural_Transformation', 'to': 'Functor', 'uniqueness': 'MANY_ONE'},
    'nat_trans_target': {'from': 'Natural_Transformation', 'to': 'Functor', 'uniqueness': 'MANY_ONE'},
    'category_objects': {'from': 'Category', 'to': 'Object', 'uniqueness': 'ONE_MANY'},
    'category_morphisms': {'from': 'Category', 'to': 'Morphism', 'uniqueness': 'ONE_MANY'},
    'functor_morphisms': {'from': 'Functor', 'to': 'Morphism', 'uniqueness': 'ONE_MANY'},
    'nat_trans_morphisms': {'from': 'Natural_Transformation', 'to': 'Morphism', 'uniqueness': 'ONE_MANY'},
    'object_property': {'from': 'Object', 'to': 'Datatype', 'fieldName': 'STRING'}
}
```

## Data Validation Requirements

1. **Category Constraints**
   - Objects must belong to exactly one category
   - Morphisms must connect objects within the same category
   - Identity morphisms should be automatically created for each object

2. **Functor Constraints**
   - Must map objects from source to target category
   - Must preserve composition and identity

3. **Natural Transformation Constraints**
   - Source and target functors must have same domain and codomain
   - Must respect functor mappings

## Implementation Decisions

1. **Composition Storage**: Hybrid approach selected
   - Compute compositions on-demand with Streamlit caching
   - Store frequently used compositions for performance
   - Cache invalidation on morphism changes

2. **Identity Morphisms**: Automatic management
   - Created automatically when objects are added
   - Deleted automatically when objects are removed
   - User cannot directly edit identity morphisms

3. **Functor Mappings**: Full explicit storage
   - Every object and morphism mapping stored explicitly
   - Uses same source/target relationship pattern as morphisms
   - Enables detailed validation and visualization

4. **Validation Level**: Mathematical law enforcement
   - DAL enforces structural constraints (foreign keys, uniqueness)
   - Mathematical validation (associativity, identity) implemented as separate validation layer
   - Validation can be bypassed for advanced users if needed

5. **Performance**: Comprehensive caching strategy
   - Cache all read operations using Streamlit decorators
   - Automatic cache invalidation on writes
   - Manual cache reset option in advanced settings

6. **Backup/Versioning**: On-demand backup support
   - Manual backup functionality through GUI
   - Simple file-based backup system
   - No automatic versioning for prototype
