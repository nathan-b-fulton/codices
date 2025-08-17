# Technical Specifications

## Technology Stack

### Core Technologies
- **Python**: 3.8+ (for modern type hints and features)
- **Kuzu**: Graph database engine
- **Streamlit**: Web application framework
- **PyVis**: Network visualization library

### Development Dependencies
- **pytest**: Testing framework
- **pytest-cov**: Coverage reporting
- **black**: Code formatting
- **mypy**: Type checking
- **ruff**: Linting

### Optional Enhancements
- **pydantic**: Data validation and serialization
- **loguru**: Enhanced logging
- **streamlit-option-menu**: Better sidebar navigation
- **streamlit-ace**: Code editor component (for advanced users)

## Database Schema Specification

### Node Types
```sql
-- Categories
CREATE NODE TABLE Category(
    ID SERIAL PRIMARY KEY,
    name STRING NOT NULL UNIQUE,
    description STRING,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Objects within categories
CREATE NODE TABLE Object(
    ID SERIAL PRIMARY KEY,
    name STRING NOT NULL,
    description STRING,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Morphisms (arrows between objects)
CREATE NODE TABLE Morphism(
    ID SERIAL PRIMARY KEY,
    name STRING NOT NULL,
    description STRING,
    is_identity BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Functors (mappings between categories)
CREATE NODE TABLE Functor(
    ID SERIAL PRIMARY KEY,
    name STRING NOT NULL,
    description STRING,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Natural transformations
CREATE NODE TABLE Natural_Transformation(
    ID SERIAL PRIMARY KEY,
    name STRING NOT NULL,
    description STRING,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Data types for object properties
CREATE NODE TABLE Datatype(
    ID SERIAL PRIMARY KEY,
    literal STRING NOT NULL UNIQUE,
    description STRING
);
```

### Relationship Types
```sql
-- Category membership
CREATE REL TABLE category_objects(FROM Category TO Object, MANY_ONE);
CREATE REL TABLE category_morphisms(FROM Category TO Morphism, MANY_ONE);

-- Morphism structure
CREATE REL TABLE morphism_source(FROM Morphism TO Object, MANY_ONE);
CREATE REL TABLE morphism_target(FROM Morphism TO Object, MANY_ONE);

-- Morphism composition (for composite morphisms)
CREATE REL TABLE morphism_composition(
    FROM Morphism TO Morphism, 
    component_order INT,
    MANY_MANY
);

-- Functor structure
CREATE REL TABLE functor_source(FROM Functor TO Category, MANY_ONE);
CREATE REL TABLE functor_target(FROM Functor TO Category, MANY_ONE);

-- Functor mappings
CREATE REL TABLE functor_object_map(
    FROM Object TO Object,
    via_functor_id INT,
    MANY_MANY
);
CREATE REL TABLE functor_morphism_map(
    FROM Morphism TO Morphism,
    via_functor_id INT,
    MANY_MANY
);

-- Natural transformation structure
CREATE REL TABLE nat_trans_source(FROM Natural_Transformation TO Functor, MANY_ONE);
CREATE REL TABLE nat_trans_target(FROM Natural_Transformation TO Functor, MANY_ONE);

-- Natural transformation components
CREATE REL TABLE nat_trans_components(
    FROM Natural_Transformation TO Morphism,
    at_object_id INT,
    MANY_MANY
);

-- Object properties
CREATE REL TABLE object_property(
    FROM Object TO Datatype,
    property_name STRING,
    property_value STRING,
    MANY_MANY
);
```

## API Specification

### CategoryDAL Class Interface
```python
class CategoryDAL:
    def __init__(self, db_path: str):
        """Initialize connection to Kuzu database"""
        
    # Transaction management
    def begin_transaction(self) -> None:
        """Start a new transaction"""
        
    def commit_transaction(self) -> None:
        """Commit current transaction"""
        
    def rollback_transaction(self) -> None:
        """Rollback current transaction"""
    
    # Category operations
    def create_category(self, name: str, description: str = "") -> int:
        """Create new category, return ID"""
        
    def get_category(self, category_id: int) -> Optional[dict]:
        """Get category by ID"""
        
    def update_category(self, category_id: int, name: str = None, description: str = None) -> bool:
        """Update category properties"""
        
    def delete_category(self, category_id: int) -> bool:
        """Delete category and all contained entities"""
        
    def list_categories(self) -> List[dict]:
        """List all categories"""
    
    # Object operations
    def create_object(self, name: str, category_id: int, description: str = "") -> int:
        """Create object within category"""
        
    def get_objects_in_category(self, category_id: int) -> List[dict]:
        """Get all objects in category"""
        
    # Morphism operations
    def create_morphism(self, name: str, source_id: int, target_id: int, 
                       category_id: int, description: str = "") -> int:
        """Create morphism between objects"""
        
    def get_morphisms_in_category(self, category_id: int) -> List[dict]:
        """Get all morphisms in category"""
    
    # Functor operations
    def create_functor(self, name: str, source_cat_id: int, target_cat_id: int,
                      description: str = "") -> int:
        """Create functor between categories"""
        
    def add_functor_object_mapping(self, functor_id: int, source_obj_id: int, target_obj_id: int) -> bool:
        """Add object mapping for functor"""
        
    # Natural transformation operations
    def create_natural_transformation(self, name: str, source_functor_id: int, 
                                    target_functor_id: int, description: str = "") -> int:
        """Create natural transformation"""
        
    # Validation utilities
    def validate_category_structure(self, category_id: int) -> List[str]:
        """Return list of validation errors for category"""
        
    def validate_functor_laws(self, functor_id: int) -> List[str]:
        """Validate functor preserves composition and identity"""
```

## File Organization

```
codices/
├── codices.py                 # Main Streamlit application
├── kuzu_DAL.py               # Enhanced data access layer
├── visualization.py          # PyVis visualization module
├── utils.py                  # Utility functions
├── requirements.txt          # Python dependencies
├── README.md                 # Project overview
├── planning/                 # Planning documents (current folder)
├── docs/                     # Documentation
│   ├── api_reference.md      # DAL API documentation
│   ├── user_guide.md         # GUI user guide
│   ├── mathematical_background.md
│   └── developer_guide.md
├── tests/                    # Test suite
│   ├── test_dal.py          # DAL unit tests
│   ├── test_visualization.py # Visualization tests
│   ├── test_gui.py          # GUI integration tests
│   ├── conftest.py          # Test fixtures
│   └── test_data/           # Sample test data
└── scripts/                  # Development scripts
    ├── setup_dev.py         # Development environment setup
    └── run_tests.py         # Test execution script
```

## Configuration Management

### Environment Configuration
```python
# config.py
import os
from typing import Dict, Any

class Config:
    # Database settings
    DB_PATH: str = os.getenv('KUZU_DB_PATH', './kuzu_db')
    
    # GUI settings  
    PAGE_TITLE: str = "Codices - Category Theory Visualizer"
    PAGE_ICON: str = "🔗"
    LAYOUT: str = "wide"
    
    # Visualization settings
    VIS_WIDTH: int = 800
    VIS_HEIGHT: int = 600
    DEFAULT_LAYOUT: str = "force_directed"
    
    # Performance settings
    MAX_NODES_PER_VISUALIZATION: int = 500
    CACHE_TTL_SECONDS: int = 300
```

## Performance Requirements

### Response Time Targets
- **Database Operations**: <100ms for simple queries, <500ms for complex queries
- **Visualization Generation**: <2 seconds for graphs with <200 nodes
- **GUI Interactions**: <50ms response time for form submissions
- **Transaction Operations**: <200ms for commit/rollback

### Scalability Targets
- **Categories**: Support up to 100 categories
- **Objects per Category**: Up to 1000 objects
- **Morphisms per Category**: Up to 5000 morphisms
- **Functors**: Up to 500 functors between categories
- **Concurrent Users**: Single-user application (Phase 1)

## Security Considerations

### Data Protection
- Input validation and sanitization for all user inputs
- Protection against SQL injection (via Kuzu parameter binding)
- File system access controls for database files

### Session Management
- Secure session state handling
- Transaction isolation
- Cleanup of temporary data

## Technical Implementation Decisions

1. **Database Architecture**: Embedded with future-ready design
   - Embedded Kuzu database for prototype simplicity
   - Design patterns support future remote connection capability
   - Robust connection handling and graceful failure recovery

2. **Caching Implementation**: Comprehensive read-operation caching
   - Streamlit decorators for all read operations
   - Automatic cache invalidation on write commits
   - Manual cache reset in advanced options menu
   - Performance monitoring for cache hit rates

3. **Error Recovery**: Manual repair with diagnostic interface
   - Data validation and repair interface for detected inconsistencies
   - Manual repair sufficient for prototype scope
   - Kuzu transaction support handles connection failures
   - Clear error reporting and recovery guidance

4. **Logging Architecture**: Dual-level logging system
   - Production level: warnings, errors, and commit summaries only
   - Debug level: verbose logging available via advanced options toggle
   - Log file location documented in user guide
   - Structured logging for better analysis

5. **Configuration Management**: Hybrid GUI/file approach
   - TOML-based configuration file for persistence
   - GUI settings interface for user-friendly access
   - Environment variable overrides for deployment flexibility
   - Complete documentation of all configuration options

6. **Backup Strategy**: Manual backup for prototype
   - On-demand backup functionality through GUI
   - Simple file-based backup system
   - Automatic backup deferred to future versions
   - Import/restore capabilities included

7. **Extensibility Design**: Fixed functionality with clean architecture
   - No plugin architecture for prototype
   - Clean separation of concerns enables future extensions
   - Meta-category support planned for long-term extensibility
   - Well-documented extension points

8. **API Readiness**: REST-compatible design patterns
   - DAL designed with future API exposure in mind
   - Clean separation between business logic and presentation
   - Request/response patterns suitable for REST endpoints
   - Authentication hooks prepared for future implementation