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

## Questions for Clarification

1. **Data Persistence**: Should the app support multiple graph databases or focus on a single persistent database?

   For this prototype, a single persistent database is sufficient.

2. **User Management**: Is this a single-user application or should it support multiple users/sessions?

   For this prototype, a single-user application is sufficient.

3. **Import/Export**: Should the app support importing/exporting category definitions to/from standard formats?

   This would be a useful extension, but is not required for the prototype.

4. **Validation**: What level of mathematical validation should be enforced (e.g., composition laws, functor laws)?

   This is outside the scope of the prototype, but definitely worth exploring in the future.

5. **Performance**: What is the expected scale (number of categories, objects, morphisms)?

   The scale will be relatively small for the first few rounds of development, with categories probably limited to < 100, objects and morphisms < 10000 each. We will refactor to handle larger scale if needed.

6. **Extensibility**: Should the system support custom properties or attributes on entities?

No, we don't want to be declaring more tables as part of populating the data. The currently defined fields should suffice.
