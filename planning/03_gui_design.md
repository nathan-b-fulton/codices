# GUI Design and Implementation Plan

## Streamlit App Structure (codices.py)

### Main Layout
```
┌─────────────────┬─────────────────────────────────────────┐
│   SIDEBAR       │            MAIN CONTENT AREA            │
│                 │                                         │
│ Entity Selector │  ┌─────────────────────────────────────┐ │
│ - Categories    │  │           TAB AREA                  │ │
│ - Functors      │  │                                     │ │
│ - Nat. Trans.   │  │  Components | Visualization | Docs  │ │
│                 │  │                                     │ │
│ Selected:       │  └─────────────────────────────────────┘ │
│ [Category X]    │                                         │
│                 │  ┌─────────────────────────────────────┐ │
│ Actions:        │  │        TAB CONTENT AREA             │ │
│ [Create New]    │  │                                     │ │
│ [Edit]          │  │    (Dynamic based on selected tab)  │ │
│ [Delete]        │  │                                     │ │
│                 │  └─────────────────────────────────────┘ │
│ Session:        │                                         │
│ [Commit]        │  ┌─────────────────────────────────────┐ │
│ [Rollback]      │  │         STATUS AREA                 │ │
│                 │  │                                     │ │
└─────────────────┴─────────────────────────────────────────┘
```

## Sidebar Components

### 1. Entity Type Selector
- Radio buttons or dropdown for selecting entity type (Category, Functor, Natural Transformation)
- Updates the entity list below based on selection

### 2. Entity List
- Dynamic list showing entities of selected type
- Each item shows name and brief description
- Click to select, shows details in main area
- Highlight currently selected entity

### 3. Entity Actions
- **Create New**: Opens creation form in main area
- **Edit**: Opens edit form for selected entity
- **Delete**: Confirmation dialog then deletes entity
- **Duplicate**: Creates copy of selected entity

### 4. Session Management
- **Transaction Status**: Shows if in transaction mode
- **Commit**: Saves all changes to persistent database
- **Rollback**: Discards all changes since last commit
- **Preview Mode Toggle**: Shows what changes would be made

## Main Content Tabs

### Tab 1: Components
Shows the internal structure of the selected entity:

#### For Categories:
- **Objects Section**
  - List of objects in category
  - Add/Edit/Delete object buttons
  - Object properties (name, description, datatypes)

- **Morphisms Section**
  - List of morphisms in category
  - Add/Edit/Delete morphism buttons
  - Source/Target object selectors
  - Composition visualization (if applicable)

#### For Functors:
- **Object Mappings**
  - Table showing source object → target object mappings
  - Add/Edit mappings interface

- **Morphism Mappings**
  - Table showing source morphism → target morphism mappings
  - Validation that mappings preserve composition

#### For Natural Transformations:
- **Component Morphisms**
  - List of morphisms that form the natural transformation
  - Validation that naturality squares commute

### Tab 2: Visualization
- Interactive graph display using PyVis
- Different layout options (hierarchical, force-directed, circular)
- Zoom and pan controls
- Toggle edge labels on/off
- Export visualization options

### Tab 3: Documentation
- Embedded markdown viewer
- Context-sensitive help based on selected entity type
- Usage examples and mathematical definitions

## Form Components

### Entity Creation/Edit Forms

#### Category Form
```
Name: [text input]
Description: [textarea]
[ ] Auto-create identity morphisms for objects
[Cancel] [Save]
```

#### Object Form
```
Name: [text input]
Description: [textarea]
Parent Category: [dropdown - disabled if editing]
Properties:
  - Type: [dropdown of datatypes] Value: [text input] [Add]
  [Remove buttons for existing properties]
[Cancel] [Save]
```

#### Morphism Form
```
Name: [text input]
Description: [textarea]
Parent Category: [dropdown - disabled if editing]
Source Object: [dropdown]
Target Object: [dropdown]
[Cancel] [Save]
```

#### Functor Form
```
Name: [text input]
Description: [textarea]
Source Category: [dropdown]
Target Category: [dropdown]

Object Mappings:
[Dynamic table with source/target dropdowns]
[Add Mapping] [Remove]

Morphism Mappings:
[Dynamic table showing morphism mappings]
[Auto-generate from object mappings] [Manual edit]

[Cancel] [Save]
```

#### Natural Transformation Form
```
Name: [text input]
Description: [textarea]
Source Functor: [dropdown]
Target Functor: [dropdown]

Component Morphisms:
[Table showing required morphisms for each object]
[Validate Naturality]

[Cancel] [Save]
```

## State Management

### Session State Variables
```python
# Selected entities
st.session_state.selected_entity_type = "Category"
st.session_state.selected_entity_id = None
st.session_state.selected_tab = "Components"

# Transaction state
st.session_state.in_transaction = False
st.session_state.transaction_changes = []

# Form state
st.session_state.editing_entity = None
st.session_state.form_mode = None  # "create", "edit", None
```

### Data Caching
- Use `@st.cache_data` for expensive database queries
- Cache category structures for visualization
- Invalidate cache on data modifications

## User Interaction Flows

### Creating a New Category
1. Select "Category" in sidebar
2. Click "Create New"
3. Fill out category form in main area
4. Save (added to transaction)
5. Category appears in sidebar list
6. Can now add objects and morphisms

### Adding Objects to Category
1. Select category in sidebar
2. Go to "Components" tab
3. In Objects section, click "Add Object"
4. Fill out object form
5. Save (added to transaction)
6. Object appears in category's object list

### Creating Functors
1. Must have at least 2 categories created
2. Select "Functor" in sidebar
3. Click "Create New"
4. Select source and target categories
5. Define object mappings
6. Auto-generate or manually define morphism mappings
7. Validate functor laws
8. Save (added to transaction)

## Error Handling and Validation

### Input Validation
- Required field validation
- Name uniqueness within scope
- Mathematical constraint validation
- Circular dependency detection

### Error Display
- Use `st.error()` for validation errors
- `st.warning()` for potential issues
- `st.success()` for successful operations

## GUI Implementation Decisions

1. **Save Strategy**: Manual save with transaction support
   - Changes stored in transaction state until explicit commit
   - Prevents accidental data loss and enables preview functionality
   - Clear visual feedback for unsaved changes

2. **Bulk Operations**: CSV-based bulk import/export
   - Upload/download functionality for objects and morphisms
   - Documented CSV format for data exchange
   - Error reporting for invalid bulk data

3. **Data Exchange**: GUI-integrated import/export
   - Export current category/functor to standard formats
   - Import validation with clear error messages
   - Support for mathematical notation in exported files

4. **Edit History**: Step-by-step undo beyond transactions
   - Maintain edit history within transaction scope
   - Undo/redo buttons in GUI for granular control
   - Clear visual indication of undo stack state

5. **Advanced Interface**: Code view for power users
   - JSON/text editor for direct entity manipulation
   - Syntax highlighting and validation
   - Switch between form view and code view

6. **Keyboard Navigation**: Essential shortcuts implemented
   - Ctrl+N: Add object, Ctrl+M: Add morphism, Del: Delete selected
   - Ctrl+Z/Y: Undo/redo, Ctrl+S: Commit transaction
   - Tab navigation and form field shortcuts

7. **Platform Support**: Desktop-focused design
   - Optimized for desktop browser use (Chrome primary)
   - Mobile/tablet support deferred to future versions
   - Wide layout assumes adequate screen real estate

8. **Visual Themes**: Dual theme support
   - Light and dark theme options in settings
   - Theme preference saved in session state
   - Custom themes beyond light/dark not implemented