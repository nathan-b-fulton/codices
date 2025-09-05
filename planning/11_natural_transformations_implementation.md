# Natural Transformations: Implementation Plan (Editor + Visualization)

## Current State
- Schema includes Natural_Transformation node, but no edges to functors or component morphisms.
- DAL supports `create_natural_transformation()` and `list_natural_transformations()` only.
- GUI lists natural transformations; editor and components tabs are placeholders.
- Visualization shows placeholder edges between functors.

## Goals
- Full CRUD for Natural Transformations α: F ⇒ G where F, G: C → D.
- Streamlit editor to create/edit α, attach component morphisms α_X: F(X) → G(X).
- Best-effort naturality checking and clear UI feedback.
- Visualization that connects functors and (optionally) shows component squares.

## Data Model Additions

### Relationships
- nat_trans_source(FROM Natural_Transformation TO Functor)
- nat_trans_target(FROM Natural_Transformation TO Functor)
- nat_trans_components(FROM Natural_Transformation TO Morphism, at_object_id INT)

Notes
- α must link to two functors F and G that share the same source and target categories.
- Each component α_X must be a morphism in the target category D with source F(X) and target G(X).
- `at_object_id` stores the object X in C for which this component is defined.

### Derived Constraints (checked in code)
- Domain/codomain of F and G match: src(F)=src(G)=C and tgt(F)=tgt(G)=D.
- For every object X in C that is included in α’s components, α_X: F(X) → G(X) is in D.
- Optional completeness: offer a toggle to require components for all objects in C.
- Naturality (best effort): for each f: X→Y in C with mapped morphisms F(f), G(f), require G(f) ∘ α_X = α_Y ∘ F(f).

## DAL API Surface

### Creation and retrieval
```python
create_natural_transformation(name: str, source_functor_id: int, target_functor_id: int, description: str = "") -> int
get_natural_transformation(nt_id: int) -> Optional[Dict[str, Any]]
list_natural_transformations() -> List[Dict[str, Any]]
list_natural_transformations_between(source_functor_id: int, target_functor_id: int) -> List[Dict[str, Any]]
```

### Component management
```python
add_nt_component(nt_id: int, at_object_id: int, component_morphism_id: int) -> bool
remove_nt_component(nt_id: int, at_object_id: int) -> bool
get_nt_components(nt_id: int) -> List[Dict[str, Any]]  # returns at_object, morphism, src_obj, tgt_obj
```

### Updates and deletion
```python
update_natural_transformation(nt_id: int, name: str | None = None, description: str | None = None) -> bool
delete_natural_transformation(nt_id: int) -> bool  # cascades component edges only
```

### Validation utilities
```python
validate_nt_structure(nt_id: int) -> List[str]   # F,G domains/codomains align; components well-typed
validate_naturality(nt_id: int) -> List[str]     # check squares commute where data available
```

### Query Sketches (Kuzu)
- Link to functors:
```sql
MATCH (nt:Natural_Transformation),(f:Functor)
WHERE nt.ID=$ntid AND f.ID=$fid
CREATE (nt)-[:nat_trans_source]->(f)
```
- Add component:
```sql
MATCH (nt:Natural_Transformation),(m:Morphism),(x:Object)
WHERE nt.ID=$ntid AND m.ID=$mid AND x.ID=$xid
CREATE (nt)-[:nat_trans_components {at_object_id:$xid}]->(m)
```
- List components (with labels):
```sql
MATCH (nt:Natural_Transformation)-[r:nat_trans_components]->(m:Morphism)
OPTIONAL MATCH (m)-[:morphism_source]->(s:Object)
OPTIONAL MATCH (m)-[:morphism_target]->(t:Object)
RETURN r.at_object_id, m.ID, m.name, s.name, t.name
ORDER BY r.at_object_id
```

## Streamlit Editor UX (codices.py)

### Create/Edit Natural Transformation Form
- Fields: name, description, source functor F (select), target functor G (select). Disable pairs where domains/codomains mismatch.
- Components section:
  - For each object X in C (source category of F,G): show a row with:
    - Label "X", dropdown of target-category morphisms m with source F(X) and target G(X).
    - If no candidate exists, show warning and quick-create button that opens a modal to add a new morphism in D with pre-filled source/target.
  - Controls: Add missing rows (if not all objects listed), Remove component, Validate Naturality.
- Modes:
  - Minimal: allow sparse components (for partial α), but show completeness status.
  - Strict (optional toggle): require component for each object in C before save.
- Transaction integration: every component add/remove logged; commit/rollback as standard.

### Components Tab for Natural Transformation
- Summary: name, description, F and G pretty labels (C→D).
- Components table: X | α_X label | F(X) | G(X).
- Buttons: Edit α, Validate Naturality.
- Naturality results: list of squares checked with pass/fail; explain missing data (e.g., missing F(f) or G(f)).

### Error Handling
- Prevent selecting morphisms outside target category D.
- Ensure selected component’s source/target match F(X), G(X).
- On functor pair change (F,G), clear incompatible components.

## Visualization Enhancements (visualization.py)

### Natural Transformation View (standard)
- Nodes: functors (diamond) with tooltips C→D.
- Edges: natural transformations (orange) between functor nodes.
- Edge tooltip: name and components count.

### Natural Transformation Detail Mode (nt-detail)
- For selected α: render for a subset of objects X ⊆ C:
  - Two aligned columns: left for F(X) nodes, right for G(X) nodes in D; draw component edges α_X between columns.
  - Optionally overlay G(f) and F(f) for selected f: X→Y to display the commuting square and highlight pass/fail.
- Alternative single-diagram variant: cluster layout in target category D; draw α_X edges between corresponding F(X) and G(X) nodes.

### NT-detail Square Overlay (planned)
- Objective: visually emphasize the commuting square for a selected morphism f: X → Y.
- UI
  - In nt-detail mode, add a toggle “Show square overlay” (default on when a morphism is selected).
  - Reuse the existing NT selector and morphism selector; display a legend for colors and statuses.
- Visualization
  - Nodes involved: F(X), F(Y), G(X), G(Y). Edges involved: α_X, α_Y, F(f), G(f) (already overlaid).
  - Shading strategy (PyVis-compatible):
    - MVP: approximate the square using semi-transparent, dashed auxiliary edges connecting the four nodes (FX↔GX, GX↔GY, GY↔FY, FY↔FX) with low width and alpha to simulate a highlighted region.
    - Enhance node emphasis by increasing node border width and adding color halos on the four nodes.
    - If feasible later, explore custom HTML/CSS overlay or background canvas draw for a true shaded polygon.
  - Color coding based on validation outcome:
    - Green: well-typed square (shape compatible) per `validate_naturality`.
    - Amber: missing data (α components or F(f)/G(f) not present) with explanatory tooltip.
    - Red: shape not compatible (sources/targets mismatch) per `validate_naturality`.
  - Annotations: edge tooltips include specific objects (e.g., F(f): F(X) → F(Y)); square tooltip summarizes status.
- Validation coupling
  - Call `validate_naturality(nt_id)` once on selection; parse the message for the chosen f to determine status (well-typed / missing data / not well-typed).
  - Do not attempt equality checking; this is a visualization/shape aid only.
- Performance
  - Compute overlay only for the selected NT and morphism; no impact on other modes.
  - Cache read-heavy queries via existing `@st.cache_data`; invalidate on NT or mapping edits.
- Acceptance Criteria
  - When a NT and morphism are selected in nt-detail: the square is highlighted with color reflecting validation status; tooltips explain status; legend is visible.
  - Toggling overlay hides/shows auxiliary edges without affecting base components.

### Category/Complete Views
- In complete/meta modes, include α as star nodes with structural edges to component morphisms (meta only), consistent with the 2-category storage principle.

## Tests to Add (planning)
- DAL
  - create/list/get/delete natural transformations linking proper functors
  - add/remove/get components with typing checks
  - structure validation catches mismatched domains/codomains and bad component typing
  - naturality validator reports non-commuting squares and missing data
- Visualization
  - standard view: nt edges appear between correct functors with proper tooltip
  - nt-detail data builder returns aligned pairs for selected objects
- GUI (manual or mocked)
  - form prevents invalid functor pairs
  - component dropdowns only show valid morphisms in D for F(X)→G(X)
  - quick-create morphism path pre-fills F(X), G(X)

## Acceptance Criteria
- Can create α: F ⇒ G selecting valid F, G with same C and D.
- Can attach per-object components α_X; typing enforced by UI and DAL.
- Naturality can be checked; results surfaced in UI as warnings (per permissive mode).
- Visualization shows α between functors; detail mode displays component edges.

## Rollout Phases
- Phase A: CRUD for Natural_Transformation entity + get/update/delete + link to F,G.
- Phase B: Components DAL + UI for α_X with typing enforcement.
- Phase C: Naturality validator; UI presentation of results.
- Phase D: Visualization (standard + nt-detail mode).

## Risks and Mitigations
- Large C (many objects): paginate component rows; filter; lazy-load candidates.
- Missing F(X)/G(X) or mapped morphisms: present actionable warnings and quick-create helpers.
- Naturality check complexity: scope to pairs where both F(f) and G(f) mappings exist; warn-only.

## Developer Notes
- Use existing logging and typing conventions; follow transaction preview patterns.
- Avoid new dependencies.
- Keep visualization API consistent with current `get_visualization_data` patterns; add modes guarded by feature flags.
