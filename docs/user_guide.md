# User Guide - Codices Category Theory Visualizer

## Getting Started

Codices is an interactive application for working with mathematical category theory. This guide will help you understand how to use all the features effectively.

## Interface Overview

### Main Layout

```
┌─────────────────┬─────────────────────────────────────────┐
│   SIDEBAR       │            MAIN CONTENT AREA            │
│                 │                                         │
│ Entity Selector │  ┌─────────────────────────────────────┐ │
│ Transaction     │  │           TAB AREA                  │ │
│ Controls        │  │  Components | Visualization | Docs │ │
│                 │  └─────────────────────────────────────┘ │
│ Selected Entity │                                         │
│ Actions         │  ┌─────────────────────────────────────┐ │
│                 │  │        TAB CONTENT AREA             │ │
└─────────────────┴─────────────────────────────────────────┘
```

### Sidebar Components

1. **Entity Type Selector**: Choose between Categories, Functors, and Natural Transformations
2. **Entity List**: Shows all entities of the selected type
3. **Action Buttons**: Create, Edit, Delete operations
4. **Transaction Controls**: Manage save operations

### Main Content Tabs

1. **Components**: View and edit entity structure and relationships
2. **Visualization**: Interactive graph displays
3. **Documentation**: Help, reference materials, and transaction history

## Working with Categories

### Creating Your First Category

1. Select "Category" in the sidebar
2. Click "Create New"
3. Enter a name (e.g., "Sets") and description
4. Click "Save Category"

Your new category will appear in the sidebar list.

### Adding Objects to Categories

1. Select a category from the sidebar
2. Go to the "Components" tab
3. In the Objects section, click "Add Object"
4. Enter object name and description
5. Save the object

Objects represent the fundamental entities in your mathematical structure.

### Creating Morphisms

Morphisms are arrows between objects representing relationships or functions.

1. Ensure your category has at least 2 objects
2. In the Components tab, click "Add Morphism"
3. Enter a name for the morphism
4. Select source and target objects
5. Save the morphism

**Tips:**
- Use descriptive names like "f: A → B"
- Mathematical symbols are supported (α, β, γ, etc.)
- Identity morphisms are automatically created for objects

## Working with Functors

Functors map between categories, preserving structure.

### Creating Functors

1. Ensure you have at least 2 categories
2. Select "Functor" in the sidebar
3. Click "Create New"
4. Choose source and target categories
5. Save the functor

### Understanding Functor Visualizations

- Categories appear as large nodes
- Functors appear as arrows between categories
- Use the visualization tab to see functor relationships

## Transaction Management

Codices offers two transaction modes for different workflows:

### Auto-save Mode (Default)
- Changes are saved immediately
- Best for: Simple operations, learning, exploration
- No risk of data loss
- Cannot undo changes

### Manual Transaction Mode
- Changes are batched until you commit
- Best for: Complex operations, large changes, careful work
- Preview changes before saving
- Can rollback all changes

### Using Manual Transactions

1. In the sidebar, select "Manual Transaction" mode
2. Make your changes (create, edit, delete entities)
3. Enable "Preview Mode" to see all pending changes
4. Click "Commit" to save or "Rollback" to discard

### Preview Mode Features

When enabled, Preview Mode shows:
- Complete list of pending changes
- Change categories (✅ Created, ✏️ Updated, ❌ Deleted)
- Transaction summary with counts
- Safety warnings for deletions

## Visualization Features

### Visualization Modes

**Standard Mode**: Mathematical View
- Objects shown as nodes
- Morphisms shown as edges
- Clean, mathematical representation

**Meta Mode**: Structural View  
- All entities shown as nodes
- All relationships shown as edges
- Reveals internal database structure

**Complete Mode**: System Overview
- Shows all categories, functors, natural transformations
- Useful for understanding global structure

### Visualization Controls

- **Layout**: Choose force-directed, hierarchical, or circular layouts
- **Labels**: Toggle edge labels on/off
- **Zoom/Pan**: Use mouse to navigate large graphs
- **Export**: Download visualizations as HTML files

### Reading Visualizations

**Node Colors:**
- 🔴 Red boxes: Categories
- 🔵 Blue circles: Objects  
- 🔺 Blue triangles: Morphisms (in meta mode)
- 💎 Green diamonds: Functors
- ⭐ Yellow stars: Natural Transformations

**Edge Styles:**
- Solid arrows: Mathematical relationships (morphisms, functors)
- Dashed lines: Structural relationships (containment)
- Different colors indicate relationship types

## Advanced Features

### Mathematical Validation

The system can validate category theory laws:

1. Select a category
2. The system automatically checks for:
   - Identity morphisms for all objects
   - Proper composition structures
   - Functor law preservation

Validation errors appear in the Components tab.

### Working with Large Structures

For categories with many objects/morphisms:

1. Use Manual Transaction mode for efficiency
2. Enable Preview Mode to review large changes
3. Consider breaking complex operations into smaller transactions
4. Use the visualization filters to focus on specific parts

### Export and Import

**Export Options:**
- Visualization HTML files
- PNG images (coming soon)
- Mathematical data formats (future)

**Import Options:**
- Currently manual entry only
- CSV import planned for future versions

## Best Practices

### Naming Conventions

- **Categories**: Descriptive names (Sets, Groups, TopologicalSpaces)
- **Objects**: Clear identifiers (A, B, X, Y, or descriptive names)
- **Morphisms**: Mathematical notation (f, g, α, β) with descriptions
- **Functors**: Standard notation (F, G, U for forgetful)

### Workflow Recommendations

1. **Start Simple**: Begin with small categories to understand the system
2. **Use Transactions**: For complex operations, use manual transaction mode
3. **Preview Changes**: Always use preview mode for important work
4. **Validate Regularly**: Check category structure validation
5. **Visualize Often**: Use visualizations to understand your structures

### Organization Tips

- Create categories for different mathematical contexts
- Use clear descriptions for complex structures
- Group related work in single transactions
- Export visualizations for documentation

## Troubleshooting

### Common Issues

**"Category 'X' already exists"**
- Names must be unique within their scope
- Choose a different name or edit the existing entity
- Check the entity list in the sidebar for existing names

**"No data to visualize"**
- Create some objects and morphisms in your category
- Check that you've selected the correct entity in the sidebar

**"Transaction failed"**
- Check for invalid operations (non-existent references)
- Try rolling back and starting fresh
- Verify database permissions

**"Visualization not loading"**
- Check browser console for JavaScript errors
- Try refreshing the page
- Ensure all required dependencies are installed

### Name Uniqueness Rules

**Categories**: Must have globally unique names
**Objects**: Must have unique names within their category (can repeat across categories)
**Morphisms**: Must have unique names within their category (can repeat across categories)
**Functors**: Names can repeat (distinguished by source/target categories)
**Natural Transformations**: Names can repeat (distinguished by source/target functors)

### Getting Help

1. Check the Mathematical Reference in the Documentation tab
2. Review Transaction History for previous operations
3. Use the Getting Started guide for step-by-step instructions
4. Check the API Reference for detailed technical information

## Mathematical Background

### Category Theory Basics

A **category** consists of:
- Objects (entities)
- Morphisms (arrows between objects)  
- Composition operation for morphisms
- Identity morphisms for each object

### Laws and Constraints

The system enforces these mathematical laws:
- **Associativity**: (h ∘ g) ∘ f = h ∘ (g ∘ f)
- **Identity**: f ∘ id = f = id ∘ f
- **Functor Laws**: Preserve composition and identity
- **Naturality**: Natural transformations commute with morphisms

### Advanced Concepts

**Functors** map between categories while preserving structure:
- Map objects to objects
- Map morphisms to morphisms
- Preserve composition and identity

**Natural Transformations** provide mappings between functors:
- Systematic way to transform one functor into another
- Must satisfy naturality conditions
- Enable comparison of different functors

## Examples

### Example 1: Category of Sets

```
Category: Sets
Objects: A = {1,2}, B = {a,b,c}, C = {x}
Morphisms: 
  f: A → B (function mapping)
  g: B → C (function mapping)
  h: A → C (composition g∘f)
```

### Example 2: Forgetful Functor

```
Source Category: Groups
Target Category: Sets
Functor: U (forgetful)

U maps:
- Group G → Underlying set |G|
- Homomorphism φ → Function φ
```

This guide provides the foundation for effectively using Codices for category theory work, research, and education.
