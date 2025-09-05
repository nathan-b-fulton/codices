# Functors: Implementation Plan (Editor + Visualization)

## Current State
- Schema includes Functor node and functor_source/functor_target rel tables.
- DAL supports `create_functor()` and `list_functors()` only.
- GUI lists functors, but editor forms and components tab are placeholders.
- Visualization shows categories as nodes and functors as edges.

## Goals
- Full CRUD for Functor with explicit object/morphism mappings.
- Streamlit editor to create/edit functors, manage mappings, and validate.
- Visualization enhancements to inspect mappings and highlight preservation laws.

## Data Model Additions

### Relationships
- functor_source(FROM Functor TO Category)
- functor_target(FROM Functor TO Category)
- functor_object_map(FROM Object TO Object, via_functor_id INT)
- functor_morphism_map(FROM Morphism TO Morphism, via_functor_id INT)

Notes
- Object and morphism map edges are many-many with an attribute `via_functor_id` to disambiguate multiple functors between the same categories.
- Enforce that object source belongs to functor.source and target belongs to functor.target; same for morphisms.

### Derived Constraints (checked in code)
- Domain/codomain categories of all mappings must match the functor’s source/target.
- Identity preservation: if id_X exists in source category, there must be id_{F(X)} in target and map(id_X) = id_{F(X)}.
- Composition preservation: for composable g∘f, ensure F(g∘f) = F(g)∘F(f) when all components are present.

## DAL API Surface

### Creation and retrieval
```python
create_functor(name: str, source_cat_id: int, target_cat_id: int, description: str = "") -> int
get_functor(functor_id: int) -> Optional[Dict[str, Any]]
list_functors() -> List[Dict[str, Any]]
list_functors_between(source_cat_id: int, target_cat_id: int) -> List[Dict[str, Any]]
```

### Mapping management
```python
add_functor_object_mapping(functor_id: int, src_obj_id: int, dst_obj_id: int) -> bool
remove_functor_object_mapping(functor_id: int, src_obj_id: int) -> bool
get_functor_object_mappings(functor_id: int) -> List[Dict[str, Any]]

add_functor_morphism_mapping(functor_id: int, src_morph_id: int, dst_morph_id: int) -> bool
remove_functor_morphism_mapping(functor_id: int, src_morph_id: int) -> bool
get_functor_morphism_mappings(functor_id: int) -> List[Dict[str, Any]]
```

### Updates and deletion
```python
update_functor(functor_id: int, name: str | None = None, description: str | None = None) -> bool
delete_functor(functor_id: int) -> bool  # cascades delete mapping edges only
```

### Validation utilities
```python
validate_functor_structure(functor_id: int) -> List[str]  # domain/codomain/mapping existence
validate_functor_laws(functor_id: int) -> List[str]       # composition + identity preservation (best-effort)
```

### Query Sketches (Kuzu)
- Insert object map:
```sql
MATCH (f:Functor),(s:Object),(t:Object)
WHERE f.ID=$fid AND s.ID=$sid AND t.ID=$tid
CREATE (s)-[:functor_object_map {via_functor_id:$fid}]->(t)
```
- List object maps:
```sql
MATCH (s:Object)-[m:functor_object_map]->(t:Object)
WHERE m.via_functor_id=$fid
RETURN s.ID, s.name, t.ID, t.name
ORDER BY s.name
```

## Streamlit Editor UX (codices.py)

### Create/Edit Functor Form
- Fields: name, description, source category (select), target category (select).
- After basic fields, show two sections with dynamic tables:
  - Object mappings: rows of [source object dropdown] → [target object dropdown]
  - Morphism mappings: rows of [source morphism dropdown] → [target morphism dropdown]
- Actions:
  - Add mapping row / Remove row.
  - Auto-suggest object mappings by name (opt-in button): pairs objects with identical names.
  - Auto-generate morphism mappings based on object mappings: for each source morphism f: X→Y, if F(X), F(Y) chosen and a target morphism g: F(X)→F(Y) exists (by name or unique), propose g.
  - Validate button: runs structure + law validations, shows warnings in permissive mode.
- Transaction integration: all mapping adds/removes are appended to change log; commit/rollback behaves as elsewhere.

### Components Tab for Functor
- Summary: name, description, source category, target category.
- Object mappings table (read-only with Edit button to jump into edit form).
- Morphism mappings table (read-only with Edit button).
- Validation results area with on-demand check.

### Error Handling
- Prevent mapping across wrong categories (disable dropdown choices that don’t belong to proper category).
- On duplicate mapping for same source item, warn and require explicit override (remove first).
- For large categories, paginate mapping lists.

## Visualization Enhancements (visualization.py)

### Functor View (existing baseline)
- Nodes: categories; Edges: functors.
- Enhancement: enrich edge tooltip with counts and sample mappings:
  - title: "Functor F: C→D\nObjects mapped: k\nMorphisms mapped: m".
- Optional mode "functor-detail":
  - Show two clusters for source and target categories with objects as nodes; draw dashed structural edges; draw mapping edges as thin gray links between clusters; still keep a main functor edge between category nodes for context.

### Complete Graph View
- Include functor nodes as diamond shapes as currently; no change required for MVP.

## Tests to Add (planning)
- DAL
  - add/remove/get object mappings
  - add/remove/get morphism mappings
  - deletion cascade of functor removes mappings
  - validate_functor_structure catches cross-category mapping
  - validate_functor_laws reports missing identity preservation and mismatched compositions
- Visualization
  - functor edge tooltip includes counts
  - functor-detail mode produces two clusters and correct mapping edges
- GUI (manual or mocked)
  - form validates and prevents wrong-category selections
  - auto-suggest and auto-generate produce expected proposals on simple fixtures

## Acceptance Criteria
- Can create a functor F: C→D and persist it.
- Can add object and morphism mappings through the UI; persisted and visible in components tab.
- Validation runs and reports issues without blocking save (per permissive mode).
- Visualization shows functor edge between categories; optional detail mode renders mapping overview.

## Rollout Phases
- Phase A: CRUD for Functor entity (done) + get_functor, update, delete.
- Phase B: Object mappings DAL + UI (create/list/remove) with validation of categories.
- Phase C: Morphism mappings DAL + UI + auto-generate from object mappings.
- Phase D: Validation utilities for laws; surface results in UI.
- Phase E: Visualization enhancements (tooltips + functor-detail mode).

## Risks and Mitigations
- Large categories → mapping tables heavy: implement pagination and search; use `@st.cache_data` for reads; invalidate on commit.
- Ambiguous morphism mapping when multiple candidates exist: require manual selection; auto-generate produces suggestions only.
- Mathematical validation cost: best-effort, warn-only in MVP.

## Developer Notes
- Mirror existing coding style: logging via module logger, typed signatures, docstrings.
- Reuse transact/preview pattern already present in codices.py.
- No new dependencies. Keep PyVis usage consistent with existing styles.
