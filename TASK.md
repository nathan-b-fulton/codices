# Task: Build a Streamlit app for working with graph presentations of categories

## Objective
Build a Streamlit app for specifying and visualizing categories in the mathematical sense. This should include creating and editing categories, objects, morphisms, functors, and natural transformations. It should also include visualizations made using pyvis.

## Components
- A Data Access Layer the specifies the schema for an underlying kuzu graph database, and provides an interface for adding:
   - Nodes
      - categories
      - objects
      - morphisms
      - functors
      - natural transformations
   - Edges
      - source and target edges linking morphisms, functors, and natural transformations to objects, categories, and functors respectively
      - inclusion edges specifying the components of categories, functors, and natural transformations
      - property edges for connecting an object to the datatype of an associated property
- A Streamlit-based GUI for users to add or edit all of the entities listed above.
   - The left sidebar should be focused on selecting, creating, editing and deleting categories, functors, and natural transformations.
   - The first tab in the main body of the GUI should show the components of a selected category, functor, or natural transformation, so that the specific elements and mappings between them can be added or edited.
- A visualization tab that shows a selected category, functor, or natural transformation using pyvis.
- A documention tab that provides a Markdown overview of the GUI components and the intended usage for each one.
- A set of unit tests covering all backend functionality, and any GUI functionality tractable to unit testing.

## Steps
1. Review the existing `kuzu_DAL.py` file, which specifies the basic database schema.
   - Improve this file by adding documentation strings and other improvements that are common Python best practice.
   - Extend the file to include accessors for creating, editing, and deleting the types of nodes and edges specified in the schema.
   - Use the kuzu transactions functionality so that the user can modify the graph without writing to the persistent storage on disk, and then either commit or roll back the changes.
2. Document the backend schema and its interface in files placed in a `docs/` directory.
3. Create the main Streamlit file, which should be called "codices.py", and establish the basic GUI layout.
4. Implement all editing functionality described above, ensuring that the ability to edit, view, and then commit or roll back is exposed at the GUI level.
5. Implement the visualization tab using pyvis.
6. Document the GUI in the `docs/` directory, and summarize in a `README` file in the main directory.
7. Write unit tests.
8. Run unit test suite and address failures.

## Design notes
- The underlying graph schema presents the data as 2-categories, meaning that morphisms, functors, and natural transformations are stored as nodes with edges linking them to their source and target. 
   - But the editing and visualization in the GUI should not always show them this way:
      - Morphisms should be shown as edges when they are displayed as connecting objects in categories.
      - Functors should be shown as edges when they are displayed as connecting categories.
      - Natural Transformations should be shown as edges when they are displayed as connecting functors.
   - The edges connecting categories, functors, and natural transformations to their elements should not be shown as edges in visualizations.
      - They are for simplifying queries to gather the elements of those structures.
      - A structure should be selected using a dropdown in the sidebar, and then the elements should be displayed in the main area.
- It should not be possible to create objects and morphisms independent of categories.
   - The user must create a category first...
   - ...and then they can create objects within it, and connect them with morphisms.
   - Then, functors can be created connecting the categories...
   - ...and natural tranformations connecting the morphisms.