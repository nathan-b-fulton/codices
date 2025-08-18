# Codices - Category Theory Visualizer

🔗 **A complete interactive application for mathematical category theory**

Codices is a Streamlit-based application that enables mathematicians, students, and researchers to create, edit, and visualize category theory structures using an intuitive graphical interface backed by a Kuzu graph database.

## ✨ Features

- 🏗️ **Complete CRUD Interface**: Create and manage categories, objects, morphisms, functors, and natural transformations
- 🌐 **Interactive Visualizations**: Real-time PyVis graph displays with multiple visualization modes
- 🔄 **Advanced Transaction System**: Preview/commit/rollback functionality with change tracking
- ✅ **Mathematical Validation**: Automated validation of category theory laws and constraints
- 📊 **Multiple Display Modes**: Standard mathematical view, structural meta view, and system overview
- 💾 **Flexible Save Options**: Auto-save mode or manual transaction batching
- 📁 **Export Capabilities**: Download visualizations and mathematical structures
- 🧪 **Comprehensive Testing**: Full test suite with performance benchmarks

## 🚀 Quick Start

### Installation

```bash
# Clone or download the project
cd codices

# Install dependencies
pip install -r requirements.txt

# Create sample data (optional)
python demo_data.py

# Launch the application
streamlit run codices.py
```

The application will open in your browser at `http://localhost:8501`

### First Steps

1. **Create a Category**: Select "Category" in sidebar → "Create New" → Enter details
2. **Add Objects**: Go to Components tab → "Add Object" → Define mathematical entities  
3. **Create Morphisms**: "Add Morphism" → Select source/target objects → Save
4. **Visualize**: Switch to Visualization tab → Explore your mathematical structure
5. **Use Transactions**: Switch to "Manual Transaction" mode for complex operations

## 📋 System Requirements

- **Python**: 3.8+ (3.10+ recommended)
- **Operating System**: Windows, macOS, Linux
- **Browser**: Chrome, Firefox, Safari (for visualization)
- **Memory**: 512MB+ (1GB+ for large structures)
- **Storage**: 50MB+ for application and database

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit     │    │   Data Access   │    │   Kuzu Graph    │
│   Frontend      │────│   Layer (DAL)   │────│   Database      │
│   (codices.py)  │    │  (kuzu_DAL.py)  │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
          │
          │
┌─────────────────┐
│   PyVis         │
│   Visualization │
│ (visualization.py)
└─────────────────┘
```

## 📚 Documentation

- **[User Guide](docs/user_guide.md)**: Complete interface and workflow guide
- **[API Reference](docs/api_reference.md)**: Technical API documentation
- **[Mathematical Background](docs/mathematical_background.md)**: Category theory concepts and examples
- **[Developer Guide](docs/developer_guide.md)**: Setup and development information

## 🧪 Testing

Run the complete test suite:

```bash
# All tests
pytest

# With coverage report
pytest --cov=. --cov-report=html

# Specific test categories
pytest tests/test_dal.py          # Data access layer tests
pytest tests/test_visualization.py # Visualization tests
pytest tests/test_integration.py   # Integration and performance tests
```

**Current Test Coverage**: 41+ tests covering all major functionality

## 🎯 Use Cases

### Research Mathematics
- **Model Abstract Categories**: Represent theoretical constructions
- **Verify Proofs**: Use visualizations for diagram chasing
- **Explore Functors**: Study relationships between mathematical areas
- **Test Conjectures**: Build examples and counterexamples

### Education
- **Interactive Learning**: Visual introduction to category theory
- **Concept Exploration**: Hands-on experience with abstract concepts  
- **Assignment Creation**: Generate exercises and examples
- **Proof Visualization**: Make abstract proofs concrete

### Applied Mathematics
- **System Modeling**: Represent complex systems categorically
- **Data Analysis**: Use categorical structures for data organization
- **Algorithm Design**: Develop category-theoretic algorithms
- **Interdisciplinary Research**: Connect different mathematical areas

## 🔧 Development

### Project Structure

```
codices/
├── codices.py              # Main Streamlit application
├── kuzu_DAL.py            # Data access layer
├── visualization.py       # PyVis visualization system
├── demo_data.py           # Sample data generation
├── requirements.txt       # Python dependencies
├── pytest.ini           # Test configuration
├── docs/                 # Documentation
│   ├── README.md
│   ├── user_guide.md
│   ├── api_reference.md
│   ├── mathematical_background.md
│   └── developer_guide.md
├── tests/                # Test suite
│   ├── test_dal.py
│   ├── test_visualization.py
│   ├── test_integration.py
│   ├── test_transaction_ui.py
│   └── conftest.py
└── planning/             # Original planning documents
```

### Technology Stack

- **Backend**: Python 3.8+, Kuzu graph database
- **Frontend**: Streamlit web framework
- **Visualization**: PyVis network graphs
- **Testing**: pytest with coverage reporting
- **Development**: black, mypy, ruff for code quality

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Run the test suite
5. Submit a pull request

## 📈 Performance

**Benchmarks** (on moderate hardware):
- **Small Categories** (<10 objects): <100ms operations
- **Medium Categories** (10-50 objects): <500ms operations  
- **Large Categories** (50-100 objects): <2s operations
- **Visualization Generation**: <3s for graphs with <100 nodes
- **Transaction Operations**: <200ms commit/rollback

## 🔮 Future Enhancements

### Planned Features
- **3D Visualizations**: For complex natural transformations
- **LaTeX Export**: Generate publication-ready diagrams
- **Collaborative Editing**: Multi-user support
- **Plugin System**: Extensible functionality
- **Advanced Validation**: Full mathematical law enforcement

### Research Directions
- **Higher Category Theory**: 2-categories, ∞-categories
- **Homotopy Type Theory**: Integration with proof assistants
- **Applied Category Theory**: Real-world system modeling
- **Category Theory Databases**: Native categorical data storage

## 📄 License

This project is developed for educational and research purposes. See LICENSE file for details.

## 🤝 Support

- **Documentation**: Check the docs/ directory for detailed guides
- **Issues**: Report bugs and feature requests on GitHub
- **Discussion**: Join category theory and mathematical software communities
- **Academic Use**: Citation information available in CITATION.md

## 🏆 Acknowledgments

- **Category Theory Community**: For mathematical foundations and inspiration
- **Kuzu Database**: For providing an excellent graph database system
- **Streamlit**: For enabling rapid development of mathematical applications
- **PyVis**: For interactive network visualization capabilities

---

**Codices** - Making category theory interactive, visual, and accessible.

*"The best way to understand category theory is to work with it."*
