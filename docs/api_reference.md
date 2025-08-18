# API Reference - Codices Category Theory System

## Core Components

### CategoryDAL Class

The `CategoryDAL` class provides a comprehensive data access layer for managing category theory entities in a Kuzu graph database.

#### Initialization

```python
from kuzu_DAL import CategoryDAL, initialize_schema

# Initialize database schema
initialize_schema("./my_database")

# Create DAL instance
dal = CategoryDAL(db_path="./my_database")
```

#### Transaction Management

The DAL supports ACID transactions for safe batch operations:

```python
# Start transaction
dal.begin_transaction()

try:
    # Perform multiple operations
    cat_id = dal.create_category("MyCategory", "Description")
    obj_id = dal.create_object("MyObject", cat_id, "Object description")
    
    # Commit all changes
    dal.commit_transaction()
except Exception as e:
    # Rollback on error
    dal.rollback_transaction()
    raise
```

**Methods:**
- `begin_transaction() -> None`: Start a new transaction for preview mode
- `commit_transaction() -> None`: Commit current transaction to persistent storage  
- `rollback_transaction() -> None`: Rollback current transaction, discarding all changes

#### Category Operations

Categories are the top-level mathematical structures containing objects and morphisms.

```python
# Create category
cat_id = dal.create_category("Sets", "Category of sets and functions")

# Get category
category = dal.get_category(cat_id)
print(f"Category: {category['name']} - {category['description']}")

# List all categories
categories = dal.list_categories()

# Update category
dal.update_category(cat_id, name="FiniteSets", description="Category of finite sets")

# Delete category (cascades to all contained entities)
dal.delete_category(cat_id)
```

**Methods:**
- `create_category(name: str, description: str = "") -> int`: Create a new category
- `get_category(category_id: int) -> Optional[Dict[str, Any]]`: Get category by ID
- `list_categories() -> List[Dict[str, Any]]`: List all categories
- `update_category(category_id: int, name: Optional[str] = None, description: Optional[str] = None) -> bool`: Update category properties
- `delete_category(category_id: int) -> bool`: Delete category and all contained entities

#### Object Operations

Objects are the entities within categories that morphisms connect.

```python
# Create object within category
obj_id = dal.create_object("Point", cat_id, "A point in space")

# Get object details
obj = dal.get_object(obj_id)

# Get all objects in category
objects = dal.get_objects_in_category(cat_id)

# Update object
dal.update_object(obj_id, name="Vector", description="A vector in space")

# Delete object (also deletes related morphisms)
dal.delete_object(obj_id)
```

**Methods:**
- `create_object(name: str, category_id: int, description: str = "") -> int`: Create an object within a category
- `get_object(object_id: int) -> Optional[Dict[str, Any]]`: Get object by ID
- `get_objects_in_category(category_id: int) -> List[Dict[str, Any]]`: Get all objects in a category
- `update_object(object_id: int, name: Optional[str] = None, description: Optional[str] = None) -> bool`: Update object properties
- `delete_object(object_id: int) -> bool`: Delete object and all related morphisms

#### Morphism Operations

Morphisms are arrows between objects within a category.

```python
# Create morphism between objects
morph_id = dal.create_morphism("f", source_obj_id, target_obj_id, cat_id, "Function f")

# Get all morphisms in category
morphisms = dal.get_morphisms_in_category(cat_id)

# Morphism data includes source/target object names
for morph in morphisms:
    print(f"{morph['name']}: {morph['source_object']} → {morph['target_object']}")
```

**Methods:**
- `create_morphism(name: str, source_id: int, target_id: int, category_id: int, description: str = "") -> int`: Create a morphism between objects
- `get_morphisms_in_category(category_id: int) -> List[Dict[str, Any]]`: Get all morphisms in a category

#### Functor Operations

Functors are mappings between categories.

```python
# Create functor between categories
functor_id = dal.create_functor("F", source_cat_id, target_cat_id, "Forgetful functor")

# List all functors
functors = dal.list_functors()

# Add object mappings (for complete functor definition)
dal.add_functor_object_mapping(functor_id, source_obj_id, target_obj_id)
```

**Methods:**
- `create_functor(name: str, source_cat_id: int, target_cat_id: int, description: str = "") -> int`: Create a functor between categories
- `list_functors() -> List[Dict[str, Any]]`: List all functors with source/target category info
- `add_functor_object_mapping(functor_id: int, source_obj_id: int, target_obj_id: int) -> bool`: Add object mapping for a functor

#### Natural Transformation Operations

Natural transformations are mappings between functors.

```python
# Create natural transformation between functors
nt_id = dal.create_natural_transformation("α", source_functor_id, target_functor_id, "Natural transformation α")

# List all natural transformations
nat_trans = dal.list_natural_transformations()
```

**Methods:**
- `create_natural_transformation(name: str, source_functor_id: int, target_functor_id: int, description: str = "") -> int`: Create a natural transformation between functors
- `list_natural_transformations() -> List[Dict[str, Any]]`: List all natural transformations

#### Validation

Mathematical validation ensures category theory laws are respected.

```python
# Validate category structure
errors = dal.validate_category_structure(cat_id)
if errors:
    print("Validation errors found:")
    for error in errors:
        print(f"  - {error}")
else:
    print("Category structure is valid")
```

**Methods:**
- `validate_category_structure(category_id: int) -> List[str]`: Validate the mathematical structure of a category

### Visualization Module

The visualization module provides interactive graph rendering using PyVis.

#### Basic Usage

```python
from visualization import render_visualization, get_visualization_data

# Render visualization in Streamlit app
render_visualization(dal, "Category", category_id)

# Get raw visualization data
viz_data = get_visualization_data(dal, "Category", category_id, "standard")
nodes = viz_data['nodes']
edges = viz_data['edges']
metadata = viz_data['metadata']
```

#### Visualization Modes

- **Standard Mode**: Mathematical view (objects as nodes, morphisms as edges)
- **Meta Mode**: Structural view (all entities as nodes, all relationships as edges)
- **Complete Mode**: System overview (all categories, functors, natural transformations)

## Error Handling

All API methods use Python exceptions for error handling:

```python
try:
    cat_id = dal.create_category("MyCategory", "Description")
except Exception as e:
    print(f"Failed to create category: {e}")
```

Common exceptions:
- `ValueError`: Invalid parameters or constraints violated
- `RuntimeError`: Database operation failures
- `Exception`: General errors (network, permissions, etc.)

## Performance Considerations

- **Caching**: Visualization data is cached automatically
- **Transactions**: Use for batch operations to improve performance
- **Large Categories**: Consider pagination for categories with >100 entities
- **Validation**: Expensive for large structures, use selectively

## Database Schema

The system uses a Kuzu graph database with the following node types:
- `Category`: Top-level mathematical structures
- `Object`: Entities within categories  
- `Morphism`: Arrows between objects
- `Functor`: Mappings between categories
- `Natural_Transformation`: Mappings between functors
- `Datatype`: For object properties

Relationships connect these entities according to category theory principles.

## Utility Functions

- `initialize_schema(db_path: str = "./kuzu_db") -> None`: Initialize the complete database schema
