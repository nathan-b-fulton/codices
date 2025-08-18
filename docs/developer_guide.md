# Developer Guide - Codices Development Setup

## Development Environment Setup

### Prerequisites

- **Python 3.8+** (3.10+ recommended)
- **Git** for version control
- **Modern browser** (Chrome, Firefox, Safari) for testing
- **Text editor/IDE** with Python support

### Quick Setup

```bash
# Clone the repository
git clone <repository-url>
cd codices

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database and create demo data
python demo_data.py

# Run tests to verify setup
pytest

# Start development server
streamlit run codices.py
```

### Development Dependencies

```bash
# Install additional development tools
pip install black mypy ruff pytest-cov

# Code formatting
black .

# Type checking  
mypy kuzu_DAL.py codices.py visualization.py

# Linting
ruff check .
```

## Architecture Overview

### Core Components

1. **Data Access Layer (kuzu_DAL.py)**
   - Database schema management
   - CRUD operations for all entity types
   - Transaction management
   - Mathematical validation

2. **Main Application (codices.py)**
   - Streamlit web interface
   - User interaction handling
   - Session state management
   - Form rendering and validation

3. **Visualization System (visualization.py)**
   - PyVis network generation
   - Data transformation pipeline
   - Multiple display modes
   - Export functionality

### Design Patterns

**Repository Pattern**: DAL abstracts database operations
**Factory Pattern**: Entity creation with proper relationships
**Observer Pattern**: Session state management for UI consistency
**Strategy Pattern**: Multiple visualization modes
**Command Pattern**: Transaction change tracking

### Database Design

**Node-Centric Approach**: All entities stored as nodes, relationships as edges
**2-Category Storage**: Preserves full mathematical structure
**1-Category Display**: Simplifies visualization for users

## Code Organization

### File Structure

```
codices/
├── Core Application Files
│   ├── codices.py              # Main Streamlit app
│   ├── kuzu_DAL.py            # Data access layer  
│   ├── visualization.py       # Visualization system
│   └── demo_data.py           # Sample data generator
├── Configuration
│   ├── requirements.txt       # Dependencies
│   ├── pytest.ini           # Test configuration
│   └── .gitignore           # Git ignore rules
├── Documentation
│   └── docs/
│       ├── README.md
│       ├── user_guide.md
│       ├── api_reference.md
│       ├── mathematical_background.md
│       └── developer_guide.md
├── Testing
│   └── tests/
│       ├── conftest.py           # Test fixtures
│       ├── test_dal.py          # DAL unit tests
│       ├── test_visualization.py # Visualization tests
│       ├── test_integration.py   # Integration tests
│       └── test_transaction_ui.py # Transaction tests
└── Planning (Reference)
    └── planning/               # Original planning documents
```

### Coding Conventions

**Python Style**:
- Follow PEP 8 with black formatting
- Use type hints throughout
- Comprehensive docstrings for all functions
- Descriptive variable names

**Mathematical Naming**:
- Use standard category theory notation (f, g, α, β)
- Clear descriptions for complex structures
- Unicode mathematical symbols supported

**Database Naming**:
- Snake_case for database entities
- Descriptive relationship names
- Consistent ID patterns

## Development Workflows

### Adding New Features

1. **Plan the Feature**
   - Update planning documents if needed
   - Define API requirements
   - Consider UI impact

2. **Implement Backend**
   - Add DAL methods if needed
   - Include proper error handling
   - Add transaction support

3. **Implement Frontend**
   - Add UI components to codices.py
   - Update session state management
   - Add form validation

4. **Add Tests**
   - Unit tests for new functionality
   - Integration tests for complex features
   - UI interaction tests if applicable

5. **Update Documentation**
   - API reference for new methods
   - User guide for new features
   - Examples and tutorials

### Testing Strategy

**Unit Tests**: Individual component testing
```bash
pytest tests/test_dal.py -v
```

**Integration Tests**: Full workflow testing
```bash
pytest tests/test_integration.py -v
```

**Performance Tests**: Load and timing validation
```bash
pytest tests/test_integration.py::TestPerformance -v
```

**Visual Testing**: Manual verification of UI components
```bash
streamlit run codices.py
# Test all UI interactions manually
```

### Database Development

**Schema Changes**:
1. Update `node_tables` and `rel_tables` in kuzu_DAL.py
2. Add migration logic if needed
3. Update `initialize_schema()` function
4. Test with fresh database

**Query Optimization**:
1. Profile slow queries using logging
2. Add appropriate indexes
3. Use transaction batching for bulk operations
4. Cache expensive read operations

### UI Development

**Streamlit Best Practices**:
- Use session state for persistence
- Cache expensive operations with `@st.cache_data`
- Avoid recomputation with proper key management
- Handle browser refresh gracefully

**Form Design**:
- Validate inputs before submission
- Provide clear error messages
- Use appropriate input widgets
- Support keyboard navigation

### Visualization Development

**PyVis Integration**:
- Test with different data sizes
- Optimize layout algorithms
- Support multiple export formats
- Handle edge cases gracefully

**Performance Optimization**:
- Limit node counts for large graphs
- Use progressive loading for complex structures
- Cache visualization generation
- Optimize data transformation pipeline

## Debugging

### Common Issues

**Database Connection Problems**:
```bash
# Check database path
ls -la kuzu_db/

# Verify schema initialization
python -c "from kuzu_DAL import initialize_schema; initialize_schema()"
```

**Streamlit Session Issues**:
```bash
# Clear streamlit cache
streamlit cache clear

# Check session state
# Add debug prints in codices.py
```

**Visualization Problems**:
```bash
# Test PyVis independently
python -c "from pyvis.network import Network; net = Network(); print('PyVis OK')"

# Check data transformation
python -c "from visualization import get_visualization_data; print('Viz OK')"
```

### Development Tools

**Logging Configuration**:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Profiling**:
```python
import cProfile
cProfile.run('your_function_call()')
```

**Database Inspection**:
```python
# Direct database queries for debugging
dal = CategoryDAL()
result = dal.conn.execute("MATCH (n) RETURN n LIMIT 10")
```

## Performance Optimization

### Database Performance
- Use transactions for batch operations
- Index frequently queried fields
- Limit result set sizes
- Use prepared statements for repeated queries

### Application Performance
- Cache expensive computations
- Lazy load visualization data
- Optimize Streamlit rerun patterns
- Profile critical code paths

### Memory Management
- Clean up temporary files
- Limit visualization node counts
- Use generators for large datasets
- Monitor session state size

## Deployment

### Local Development
```bash
streamlit run codices.py --server.headless false
```

### Production Deployment
```bash
# Install production dependencies
pip install -r requirements.txt

# Set environment variables
export KUZU_DB_PATH="/path/to/production/db"

# Run with production settings
streamlit run codices.py --server.headless true --server.port 8501
```

### Docker Deployment (Future)
```dockerfile
# Dockerfile example for future containerization
FROM python:3.10-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . /app
WORKDIR /app
CMD ["streamlit", "run", "codices.py"]
```

## Contributing

### Code Quality Standards

- **Test Coverage**: Maintain >90% coverage
- **Type Safety**: Use mypy for type checking
- **Code Style**: Follow black formatting
- **Documentation**: Update docs for all changes

### Pull Request Process

1. Create feature branch from main
2. Implement changes with tests
3. Run full test suite
4. Update documentation
5. Submit PR with clear description

### Code Review Checklist

- [ ] All tests pass
- [ ] New functionality has tests
- [ ] Documentation updated
- [ ] No performance regressions
- [ ] UI changes tested manually
- [ ] Mathematical correctness verified

## Advanced Development

### Custom Visualization Modes

```python
# Add new visualization mode in visualization.py
def get_custom_visualization_data(dal, entity_id, mode):
    # Implement custom data transformation
    pass

# Register in get_visualization_data()
```

### Database Schema Extensions

```python
# Add new node type
node_tables['NewEntityType'] = {
    'ID': 'SERIAL PRIMARY KEY',
    'name': 'STRING',
    'custom_field': 'STRING'
}

# Add relationships
rel_tables['new_relationship'] = {
    'from': 'NewEntityType', 
    'to': 'ExistingType'
}
```

### UI Component Development

```python
# Add new form component
def render_new_entity_form():
    with st.form("new_entity_form"):
        # Form fields
        name = st.text_input("Name")
        
        if st.form_submit_button("Save"):
            # Handle submission
            pass
```

This guide provides the foundation for contributing to and extending the Codices category theory system.
