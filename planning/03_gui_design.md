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

## Questions for GUI Implementation

1. **Auto-save vs Manual Save**: Should form changes be auto-saved or require explicit save action?

   Only manual save (commit to kuzu) is required for this prototype.

2. **Bulk Operations**: Should the GUI support bulk creation/editing of objects and morphisms?

   Yes, via .csv upload in a documented format.

3. **Import/Export**: Should there be GUI options to import/export category definitions?

   Yes, similar to above.

4. **Undo/Redo**: Beyond transaction rollback, should there be step-by-step undo functionality?

   Yes.

5. **Advanced Editing**: Should there be a "code view" for advanced users to edit entities via text/JSON?

   Yes.

6. **Keyboard Shortcuts**: What keyboard shortcuts would improve workflow efficiency?

   Add object, add morphism, delete selected, any others you think appropriate based on common design patterns.

7. **Mobile Support**: Should the layout be responsive for tablet/mobile use?

  Tablet and mobile support are out of scope for this prototype.

8. **Theme Support**: Should the app support light/dark themes or custom styling?

   It should offer a light theme and a dark one, but custom themes are out of scope for this prototype.