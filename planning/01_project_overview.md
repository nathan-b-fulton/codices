# Project Overview: Codices - Mathematical Category Theory App Prototype

## Project Description
A prototype of a Streamlit-based application for creating, editing, and visualizing mathematical categories using Kuzu graph database as the backend. The app supports category theory concepts including categories, objects, morphisms, functors, and natural transformations.

## High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit     │    │   Data Access   │    │   Kuzu Graph    │
│   Frontend      │────│   Layer (DAL)   │────│   Database      │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │
         │
┌─────────────────┐
│   PyVis         │
│   Visualization │
│                 │
└─────────────────┘
```

## Core Components

1. **Data Access Layer (kuzu_DAL.py)**
   - Graph database schema definition
   - CRUD operations for all entity types
   - Transaction management for edit sessions

2. **Main Streamlit App (codices.py)**
   - User interface with sidebar navigation
   - Entity editing forms
   - Transaction controls (commit/rollback)

3. **Visualization Module**
   - PyVis integration for graph rendering
   - Multiple visualization modes for different entity types

4. **Documentation System**
   - Backend API documentation
   - GUI user guide
   - README with project overview

## Key Design Principles

1. **2-Category Storage with 1-Category Display**
   - Store morphisms/functors/natural transformations as nodes
   - Display them as edges in visualizations when appropriate

2. **Hierarchical Creation Model**
   - Categories must be created first
   - Objects and morphisms belong to categories
   - Functors connect categories
   - Natural transformations connect functors

3. **Transaction-Based Editing**
   - All edits occur in transactions
   - User can preview changes before committing
   - Rollback capability for cancelled edits

## Design Decisions Made

1. **Data Persistence**: Single persistent database focused approach
   - Simplifies architecture and deployment
   - Sufficient for prototype scope and single-user use

2. **User Management**: Single-user application
   - Reduces complexity around session management and data isolation
   - Allows focus on core mathematical functionality

3. **Import/Export**: Future enhancement priority
   - CSV upload/download for bulk operations will be supported
   - Standard mathematical format support deferred to later versions

4. **Mathematical Validation**: Permissive mode for prototype
   - Focus on structural correctness over strict mathematical law enforcement
   - Tool functionality prioritized over mathematical rigor initially

5. **Performance Scale**: Small to medium scale focus
   - Categories: < 100
   - Objects/Morphisms: < 10,000 each
   - Optimization for larger scales deferred to future iterations

6. **Entity Extensibility**: Fixed schema approach
   - Current defined fields sufficient for mathematical modeling
   - Avoids dynamic schema complexity
