# API Reference - Category Theory DAL

## CategoryDAL Class

The `CategoryDAL` class provides a comprehensive data access layer for managing category theory entities in a Kuzu graph database.

### Initialization

```python
dal = CategoryDAL(db_path="./kuzu_db")
```

### Transaction Management

- `begin_transaction()`: Start a new transaction for preview mode
- `commit_transaction()`: Commit current transaction to persistent storage  
- `rollback_transaction()`: Rollback current transaction, discarding all changes

### Category Operations

- `create_category(name: str, description: str = "") -> int`: Create a new category
- `get_category(category_id: int) -> Optional[Dict[str, Any]]`: Get category by ID
- `list_categories() -> List[Dict[str, Any]]`: List all categories
- `update_category(category_id: int, name: str = None, description: str = None) -> bool`: Update category properties
- `delete_category(category_id: int) -> bool`: Delete category and all contained entities

### Object Operations

- `create_object(name: str, category_id: int, description: str = "") -> int`: Create an object within a category
- `get_object(object_id: int) -> Optional[Dict[str, Any]]`: Get object by ID
- `get_objects_in_category(category_id: int) -> List[Dict[str, Any]]`: Get all objects in a category
- `update_object(object_id: int, name: str = None, description: str = None) -> bool`: Update object properties
- `delete_object(object_id: int) -> bool`: Delete object and all related morphisms

### Morphism Operations

- `create_morphism(name: str, source_id: int, target_id: int, category_id: int, description: str = "") -> int`: Create a morphism between objects
- `get_morphisms_in_category(category_id: int) -> List[Dict[str, Any]]`: Get all morphisms in a category

### Functor Operations

- `create_functor(name: str, source_cat_id: int, target_cat_id: int, description: str = "") -> int`: Create a functor between categories
- `add_functor_object_mapping(functor_id: int, source_obj_id: int, target_obj_id: int) -> bool`: Add object mapping for a functor

### Natural Transformation Operations

- `create_natural_transformation(name: str, source_functor_id: int, target_functor_id: int, description: str = "") -> int`: Create a natural transformation between functors

### Validation

- `validate_category_structure(category_id: int) -> List[str]`: Validate the mathematical structure of a category

## Utility Functions

- `initialize_schema(db_path: str = "./kuzu_db") -> None`: Initialize the complete database schema
- `create_table(connection: kuzu.Connection, label: str, definition: Dict[str, str], rel: bool = False) -> None`: Create database tables
