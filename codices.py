import streamlit as st
from kuzu_DAL import CategoryDAL, initialize_schema
from visualization import render_visualization, render_visualization_statistics
import logging

# Configure page
st.set_page_config(
    page_title="Codices - Category Theory Visualizer",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@st.cache_resource
def get_dal():
    """Initialize and cache the data access layer."""
    try:
        initialize_schema()
        return CategoryDAL()
    except Exception as e:
        st.error(f"Failed to initialize database: {e}")
        st.stop()


def init_session_state():
    """Initialize session state variables."""
    if 'selected_entity_type' not in st.session_state:
        st.session_state.selected_entity_type = "Category"
    
    if 'selected_entity_id' not in st.session_state:
        st.session_state.selected_entity_id = None
    
    if 'selected_tab' not in st.session_state:
        st.session_state.selected_tab = "Components"
    
    if 'in_transaction' not in st.session_state:
        st.session_state.in_transaction = False
    
    if 'form_mode' not in st.session_state:
        st.session_state.form_mode = None
    
    if 'editing_entity' not in st.session_state:
        st.session_state.editing_entity = None
    
    if 'transaction_changes' not in st.session_state:
        st.session_state.transaction_changes = []
    
    if 'preview_mode' not in st.session_state:
        st.session_state.preview_mode = False
    
    if 'transaction_history' not in st.session_state:
        st.session_state.transaction_history = []


def render_sidebar():
    """Render the sidebar with entity selection and actions."""
    st.sidebar.title("🔗 Codices")
    
    # Entity type selector
    st.sidebar.subheader("Entity Type")
    entity_types = ["Category", "Functor", "Natural Transformation"]
    selected_type = st.sidebar.radio(
        "Select entity type:",
        entity_types,
        index=entity_types.index(st.session_state.selected_entity_type),
        key="entity_type_selector"
    )
    
    if selected_type != st.session_state.selected_entity_type:
        st.session_state.selected_entity_type = selected_type
        st.session_state.selected_entity_id = None
        st.rerun()
    
    # Entity list
    st.sidebar.subheader(f"{selected_type} List")
    render_entity_list(selected_type)
    
    # Entity actions
    st.sidebar.subheader("Actions")
    render_entity_actions(selected_type)
    
    # Session management
    st.sidebar.subheader("Session")
    render_session_management()


def render_entity_list(entity_type):
    """Render the list of entities for the selected type."""
    dal = get_dal()
    
    try:
        if entity_type == "Category":
            entities = dal.list_categories()
        elif entity_type == "Functor":
            entities = dal.list_functors()
        elif entity_type == "Natural Transformation":
            entities = dal.list_natural_transformations()
        else:
            entities = []
        
        if not entities:
            st.sidebar.write(f"No {entity_type.lower()}s found")
            return
        
        # Create selection list
        entity_names = [f"{e['name']} (ID: {e['ID']})" for e in entities]
        
        if st.session_state.selected_entity_id is not None:
            # Find current selection index
            try:
                current_entity = next(e for e in entities if e['ID'] == st.session_state.selected_entity_id)
                current_index = entities.index(current_entity)
            except (StopIteration, ValueError):
                current_index = 0
        else:
            current_index = 0
        
        selected_index = st.sidebar.selectbox(
            f"Select {entity_type.lower()}:",
            range(len(entity_names)),
            format_func=lambda i: entity_names[i],
            index=current_index,
            key=f"{entity_type}_selector"
        )
        
        if selected_index is not None:
            st.session_state.selected_entity_id = entities[selected_index]['ID']
            
    except Exception as e:
        st.sidebar.error(f"Error loading {entity_type.lower()}s: {e}")


def render_entity_actions(entity_type):
    """Render action buttons for the selected entity type."""
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if st.button("Create New", key=f"create_{entity_type}"):
            st.session_state.form_mode = "create"
            st.session_state.editing_entity = None
            st.rerun()
    
    with col2:
        if st.session_state.selected_entity_id is not None:
            if st.button("Edit", key=f"edit_{entity_type}"):
                st.session_state.form_mode = "edit"
                st.session_state.editing_entity = st.session_state.selected_entity_id
                st.rerun()
    
    if st.session_state.selected_entity_id is not None:
        if st.button("Delete", key=f"delete_{entity_type}", type="secondary"):
            st.session_state.form_mode = "delete"
            st.rerun()


def render_session_management():
    """Render enhanced transaction control buttons with change tracking."""
    dal = get_dal()
    
    # Transaction mode selector
    st.sidebar.subheader("Transaction Mode")
    transaction_mode = st.sidebar.radio(
        "Mode:",
        ["Auto-save", "Manual Transaction"],
        index=1 if st.session_state.in_transaction else 0,
        help="Auto-save: Changes saved immediately. Manual: Use transactions for batch operations."
    )
    
    # Auto-start transaction if switched to manual mode
    if transaction_mode == "Manual Transaction" and not st.session_state.in_transaction:
        try:
            dal.begin_transaction()
            st.session_state.in_transaction = True
            st.session_state.transaction_changes = []
            add_transaction_change("Switched to manual transaction mode")
            st.rerun()
        except Exception as e:
            st.sidebar.error(f"Failed to start transaction: {e}")
    
    # Auto-commit if switched to auto-save mode
    elif transaction_mode == "Auto-save" and st.session_state.in_transaction:
        try:
            dal.commit_transaction()
            st.session_state.in_transaction = False
            st.session_state.transaction_changes = []
            st.session_state.preview_mode = False
            st.sidebar.success("Auto-committed pending changes")
            st.rerun()
        except Exception as e:
            st.sidebar.error(f"Failed to auto-commit: {e}")
    
    # Transaction status with change count
    if st.session_state.in_transaction:
        change_count = len(st.session_state.transaction_changes)
        st.sidebar.success(f"🔄 Transaction Active ({change_count} changes)")
        
        # Show preview toggle
        st.session_state.preview_mode = st.sidebar.checkbox(
            "Preview Mode", 
            value=st.session_state.preview_mode,
            help="Preview changes before committing"
        )
        
        # Show change summary if in preview mode
        if st.session_state.preview_mode and st.session_state.transaction_changes:
            with st.sidebar.expander("📋 Recent Changes", expanded=False):
                for i, change in enumerate(st.session_state.transaction_changes[-3:], 1):  # Show last 3 changes
                    st.sidebar.write(f"{i}. {change}")
                if len(st.session_state.transaction_changes) > 3:
                    st.sidebar.write(f"... and {len(st.session_state.transaction_changes) - 3} more")
    else:
        st.sidebar.info("💾 Auto-save Mode")
    
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if st.button("Begin Transaction", disabled=st.session_state.in_transaction):
            try:
                dal.begin_transaction()
                st.session_state.in_transaction = True
                st.session_state.transaction_changes = []
                st.sidebar.success("Transaction started")
                add_transaction_change("Started new transaction")
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"Failed to start transaction: {e}")
    
    with col2:
        if st.button("Commit", disabled=not st.session_state.in_transaction):
            try:
                if st.session_state.preview_mode and st.session_state.transaction_changes:
                    # Show commit confirmation in preview mode
                    st.sidebar.warning("⚠️ Confirm commit with preview below")
                    return
                
                dal.commit_transaction()
                change_count = len(st.session_state.transaction_changes)
                
                # Add to history
                if st.session_state.transaction_changes:
                    st.session_state.transaction_history.append({
                        'changes': st.session_state.transaction_changes.copy(),
                        'count': change_count,
                        'timestamp': 'Now'  # Could use datetime for real timestamps
                    })
                
                st.session_state.in_transaction = False
                st.session_state.transaction_changes = []
                st.session_state.preview_mode = False
                st.sidebar.success(f"✅ {change_count} changes committed")
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"Failed to commit: {e}")
    
    if st.session_state.in_transaction:
        col3, col4 = st.sidebar.columns(2)
        
        with col3:
            if st.button("Rollback", type="secondary"):
                try:
                    dal.rollback_transaction()
                    change_count = len(st.session_state.transaction_changes)
                    st.session_state.in_transaction = False
                    st.session_state.transaction_changes = []
                    st.session_state.preview_mode = False
                    st.sidebar.success(f"↩️ {change_count} changes rolled back")
                    st.rerun()
                except Exception as e:
                    st.sidebar.error(f"Failed to rollback: {e}")
        
        with col4:
            if st.session_state.preview_mode and st.session_state.transaction_changes:
                if st.button("Confirm Commit", type="primary", key="confirm_commit"):
                    try:
                        dal.commit_transaction()
                        change_count = len(st.session_state.transaction_changes)
                        
                        # Add to history
                        if st.session_state.transaction_changes:
                            st.session_state.transaction_history.append({
                                'changes': st.session_state.transaction_changes.copy(),
                                'count': change_count,
                                'timestamp': 'Now'
                            })
                        
                        st.session_state.in_transaction = False
                        st.session_state.transaction_changes = []
                        st.session_state.preview_mode = False
                        st.sidebar.success(f"✅ {change_count} changes committed")
                        st.rerun()
                    except Exception as e:
                        st.sidebar.error(f"Failed to commit: {e}")


def add_transaction_change(description: str):
    """Add a change description to the transaction log."""
    if 'transaction_changes' not in st.session_state:
        st.session_state.transaction_changes = []
    
    st.session_state.transaction_changes.append(description)
    
    # Auto-suggest transaction mode for complex operations
    if (not st.session_state.in_transaction and 
        len(st.session_state.get('recent_changes', [])) > 2):
        st.info("💡 Consider using Manual Transaction mode for complex operations")


def suggest_transaction_usage():
    """Show transaction usage suggestions based on current context."""
    if st.session_state.selected_entity_type == "Category" and st.session_state.selected_entity_id is not None:
        dal = get_dal()
        try:
            objects = dal.get_objects_in_category(st.session_state.selected_entity_id)
            morphisms = dal.get_morphisms_in_category(st.session_state.selected_entity_id)
            
            if len(objects) > 5 or len(morphisms) > 10:
                if not st.session_state.in_transaction:
                    st.info("💡 Tip: Use Manual Transaction mode when working with large categories")
        except Exception:
            pass


def render_preview_panel():
    """Render the transaction preview panel."""
    st.subheader("🔍 Transaction Preview")
    
    if not st.session_state.transaction_changes:
        st.info("No changes in current transaction")
        return
    
    st.write(f"**{len(st.session_state.transaction_changes)} changes pending:**")
    
    # Show all changes in an organized way
    for i, change in enumerate(st.session_state.transaction_changes, 1):
        if change.startswith("Created"):
            st.write(f"✅ {i}. {change}")
        elif change.startswith("Updated"):
            st.write(f"✏️ {i}. {change}")
        elif change.startswith("Deleted"):
            st.write(f"❌ {i}. {change}")
        else:
            st.write(f"📝 {i}. {change}")
    
    # Transaction summary
    creates = sum(1 for c in st.session_state.transaction_changes if c.startswith("Created"))
    updates = sum(1 for c in st.session_state.transaction_changes if c.startswith("Updated"))
    deletes = sum(1 for c in st.session_state.transaction_changes if c.startswith("Deleted"))
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Created", creates)
    with col2:
        st.metric("Updated", updates)
    with col3:
        st.metric("Deleted", deletes)
    
    # Warning if significant changes
    if deletes > 0:
        st.warning("⚠️ This transaction includes deletions. These cannot be undone after commit.")
    
    if len(st.session_state.transaction_changes) > 10:
        st.info("💡 Large transaction detected. Consider committing in smaller batches.")


def render_main_content():
    """Render the main content area with tabs."""
    # Handle form modes first
    if st.session_state.form_mode == "create":
        render_create_form()
        return
    elif st.session_state.form_mode == "edit":
        render_edit_form()
        return
    elif st.session_state.form_mode == "delete":
        render_delete_confirmation()
        return
    elif st.session_state.form_mode == "create_object":
        render_object_form()
        return
    elif st.session_state.form_mode == "create_morphism":
        render_morphism_form()
        return
    elif st.session_state.form_mode == "edit_object":
        render_object_form(edit_mode=True)
        return
    elif st.session_state.form_mode == "edit_morphism":
        render_morphism_form(edit_mode=True)
        return
    elif st.session_state.form_mode in ["delete_object", "delete_morphism"]:
        render_entity_delete_confirmation()
        return
    
    # Show preview panel if in preview mode
    if st.session_state.get('preview_mode', False) and st.session_state.get('in_transaction', False):
        render_preview_panel()
        st.divider()
    
    # Main tabs
    tab1, tab2, tab3 = st.tabs(["📋 Components", "🌐 Visualization", "📚 Documentation"])
    
    with tab1:
        render_components_tab()
    
    with tab2:
        render_visualization_tab()
    
    with tab3:
        render_documentation_tab()


def render_create_form():
    """Render entity creation form."""
    st.header(f"Create New {st.session_state.selected_entity_type}")
    
    if st.session_state.selected_entity_type == "Category":
        render_category_form()
    elif st.session_state.selected_entity_type == "Functor":
        render_functor_form()
    elif st.session_state.selected_entity_type == "Natural Transformation":
        render_natural_transformation_form()
    
    # Cancel button
    if st.button("Cancel", key="cancel_create"):
        st.session_state.form_mode = None
        st.rerun()


def render_edit_form():
    """Render entity editing form."""
    st.header(f"Edit {st.session_state.selected_entity_type}")
    
    if st.session_state.selected_entity_type == "Category":
        render_category_form(edit_mode=True)
    elif st.session_state.selected_entity_type == "Functor":
        render_functor_form(edit_mode=True)
    elif st.session_state.selected_entity_type == "Natural Transformation":
        render_natural_transformation_form(edit_mode=True)
    
    # Cancel button
    if st.button("Cancel", key="cancel_edit"):
        st.session_state.form_mode = None
        st.rerun()


def render_delete_confirmation():
    """Render delete confirmation dialog."""
    entity_type = st.session_state.selected_entity_type
    entity_id = st.session_state.selected_entity_id
    
    dal = get_dal()
    
    # Get entity details
    try:
        if entity_type == "Category":
            entity = dal.get_category(entity_id)
        else:
            entity = None
        
        if not entity:
            st.error("Entity not found")
            st.session_state.form_mode = None
            st.rerun()
            return
        
        st.header("⚠️ Confirm Deletion")
        st.warning(f"Are you sure you want to delete {entity_type.lower()} '{entity['name']}'?")
        
        if entity_type == "Category":
            objects = dal.get_objects_in_category(entity_id)
            morphisms = dal.get_morphisms_in_category(entity_id)
            st.write(f"This will also delete {len(objects)} objects and {len(morphisms)} morphisms.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Delete", key="confirm_delete", type="primary"):
                try:
                    if entity_type == "Category":
                        dal.delete_category(entity_id)
                    st.success(f"{entity_type} deleted successfully")
                    add_transaction_change(f"Deleted {entity_type.lower()} '{entity['name']}'")
                    st.session_state.selected_entity_id = None
                    st.session_state.form_mode = None
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to delete {entity_type.lower()}: {e}")
        
        with col2:
            if st.button("Cancel", key="cancel_delete"):
                st.session_state.form_mode = None
                st.rerun()
                
    except Exception as e:
        st.error(f"Error loading entity details: {e}")
        st.session_state.form_mode = None


def render_category_form(edit_mode=False):
    """Render category creation/editing form."""
    dal = get_dal()
    
    # Load existing data if editing
    if edit_mode and st.session_state.editing_entity:
        try:
            category = dal.get_category(st.session_state.editing_entity)
            if not category:
                st.error("Category not found")
                return
            initial_name = category['name']
            initial_description = category['description']
        except Exception as e:
            st.error(f"Failed to load category: {e}")
            return
    else:
        initial_name = ""
        initial_description = ""
    
    # Form fields
    with st.form(key="category_form"):
        name = st.text_input("Name", value=initial_name, placeholder="Enter category name")
        description = st.text_area("Description", value=initial_description, placeholder="Enter category description")
        
        col1, col2 = st.columns(2)
        
        with col1:
            submitted = st.form_submit_button("Save Category", type="primary")
        
        with col2:
            cancelled = st.form_submit_button("Cancel")
        
        if cancelled:
            st.session_state.form_mode = None
            st.rerun()
        
        if submitted:
            if not name.strip():
                st.error("Category name is required")
                return
            
            try:
                if edit_mode:
                    dal.update_category(st.session_state.editing_entity, name=name, description=description)
                    st.success("Category updated successfully")
                    add_transaction_change(f"Updated category '{name}'")
                else:
                    category_id = dal.create_category(name, description)
                    st.success(f"Category '{name}' created with ID {category_id}")
                    st.session_state.selected_entity_id = category_id
                    add_transaction_change(f"Created category '{name}' (ID: {category_id})")
                
                st.session_state.form_mode = None
                st.rerun()
                
            except Exception as e:
                if "already exists" in str(e):
                    st.error(f"❌ Name conflict: {e}")
                    st.info("💡 Try using a different name or check the entity list in the sidebar")
                else:
                    st.error(f"Failed to save category: {e}")


def render_functor_form(edit_mode=False):
    """Render functor creation/editing form."""
    st.header("Edit Functor" if edit_mode else "Create New Functor")
    
    dal = get_dal()
    
    try:
        categories = dal.list_categories()
        
        if len(categories) < 2:
            st.warning("Need at least 2 categories to create functors")
            if st.button("Cancel"):
                st.session_state.form_mode = None
                st.rerun()
            return
        
        with st.form(key="functor_form"):
            name = st.text_input("Functor Name", placeholder="Enter functor name")
            description = st.text_area("Description", placeholder="Enter functor description")
            
            # Category selectors
            category_options = {cat['ID']: f"{cat['name']} (ID: {cat['ID']})" for cat in categories}
            category_ids = list(category_options.keys())
            
            source_cat_id = st.selectbox(
                "Source Category",
                category_ids,
                format_func=lambda x: category_options[x],
                key="functor_source_selector"
            )
            
            target_cat_id = st.selectbox(
                "Target Category",
                category_ids,
                format_func=lambda x: category_options[x],
                key="functor_target_selector"
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                submitted = st.form_submit_button("Save Functor" if edit_mode else "Create Functor", type="primary")
            
            with col2:
                cancelled = st.form_submit_button("Cancel")
            
            if cancelled:
                st.session_state.form_mode = None
                st.rerun()
            
            if submitted:
                if not name.strip():
                    st.error("Functor name is required")
                    return
                
                try:
                    if edit_mode:
                        st.info("Functor editing functionality coming soon")
                    else:
                        functor_id = dal.create_functor(name, source_cat_id, target_cat_id, description)
                        st.success(f"Functor '{name}' created with ID {functor_id}")
                        st.session_state.selected_entity_id = functor_id
                        add_transaction_change(f"Created functor '{name}' (ID: {functor_id})")
                    
                    st.session_state.form_mode = None
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Failed to save functor: {e}")
                    
    except Exception as e:
        st.error(f"Error loading categories: {e}")


def render_natural_transformation_form(edit_mode=False):
    """Render natural transformation creation/editing form."""
    st.header("Edit Natural Transformation" if edit_mode else "Create New Natural Transformation")
    
    dal = get_dal()
    
    try:
        functors = dal.list_functors()
        if not functors or len(functors) < 2:
            st.warning("Need at least 2 functors to create a natural transformation")
            if st.button("Cancel"):
                st.session_state.form_mode = None
                st.rerun()
            return
        
        # Build functor options and show only compatible pairs (same source/target categories)
        functor_options = {f['ID']: f"{f['name']} (C: {f.get('source_category','?')} → D: {f.get('target_category','?')})" for f in functors}
        
        with st.form(key="nat_trans_form"):
            name = st.text_input("Natural Transformation Name", placeholder="Enter name")
            description = st.text_area("Description", placeholder="Enter description")
            
            # Source functor selector
            src_functor_id = st.selectbox(
                "Source Functor (F)",
                list(functor_options.keys()),
                format_func=lambda x: functor_options[x],
                key="nt_src_functor_selector"
            )
            
            # Filter target functors to those with same domain/codomain
            src_functor = next((f for f in functors if f['ID'] == src_functor_id), None)
            if src_functor is None:
                st.error("Selected source functor not found")
                return
            
            compatible_targets = [
                f for f in functors
                if f['ID'] != src_functor_id and
                   f.get('source_category_id') == src_functor.get('source_category_id') and
                   f.get('target_category_id') == src_functor.get('target_category_id')
            ]
            if not compatible_targets:
                st.warning("No compatible target functors with same domain and codomain")
            target_ids = [f['ID'] for f in compatible_targets] or list(functor_options.keys())
            
            tgt_functor_id = st.selectbox(
                "Target Functor (G)",
                target_ids,
                format_func=lambda x: functor_options[x],
                key="nt_tgt_functor_selector"
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                submitted = st.form_submit_button("Save Natural Transformation" if edit_mode else "Create Natural Transformation", type="primary")
            
            with col2:
                cancelled = st.form_submit_button("Cancel")
            
            if cancelled:
                st.session_state.form_mode = None
                st.rerun()
            
            if submitted:
                if not name.strip():
                    st.error("Name is required")
                    return
                try:
                    if edit_mode:
                        st.info("Editing natural transformations coming soon")
                    else:
                        nt_id = dal.create_natural_transformation(name, src_functor_id, tgt_functor_id, description)
                        st.success(f"Natural transformation '{name}' created with ID {nt_id}")
                        st.session_state.selected_entity_id = nt_id
                        add_transaction_change(f"Created natural transformation '{name}' (ID: {nt_id})")
                    st.session_state.form_mode = None
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to save natural transformation: {e}")
    except Exception as e:
        st.error(f"Error in natural transformation form: {e}")


def render_object_form(edit_mode=False):
    """Render object creation/editing form."""
    st.header("Edit Object" if edit_mode else "Create New Object")
    
    dal = get_dal()
    category_id = st.session_state.parent_category
    
    try:
        category = dal.get_category(category_id)
        if not category:
            st.error("Parent category not found")
            return
        
        # Load existing data if editing
        if edit_mode and st.session_state.editing_entity:
            try:
                obj = dal.get_object(st.session_state.editing_entity)
                if not obj:
                    st.error("Object not found")
                    return
                initial_name = obj['name']
                initial_description = obj['description']
            except Exception as e:
                st.error(f"Failed to load object: {e}")
                return
        else:
            initial_name = ""
            initial_description = ""
        
        st.info(f"{'Editing' if edit_mode else 'Creating'} object in category: {category['name']}")
        
        with st.form(key="object_form"):
            name = st.text_input("Object Name", value=initial_name, placeholder="Enter object name")
            description = st.text_area("Description", value=initial_description, placeholder="Enter object description")
            
            col1, col2 = st.columns(2)
            
            with col1:
                submitted = st.form_submit_button("Save Object" if edit_mode else "Create Object", type="primary")
            
            with col2:
                cancelled = st.form_submit_button("Cancel")
            
            if cancelled:
                st.session_state.form_mode = None
                st.rerun()
            
            if submitted:
                if not name.strip():
                    st.error("Object name is required")
                    return
                
                try:
                    if edit_mode:
                        dal.update_object(st.session_state.editing_entity, name=name, description=description)
                        st.success("Object updated successfully")
                        add_transaction_change(f"Updated object '{name}'")
                    else:
                        object_id = dal.create_object(name, category_id, description)
                        st.success(f"Object '{name}' created with ID {object_id}")
                        add_transaction_change(f"Created object '{name}' (ID: {object_id})")
                    
                    st.session_state.form_mode = None
                    st.rerun()
                    
                except Exception as e:
                    if "already exists" in str(e):
                        st.error(f"❌ Name conflict: {e}")
                        st.info("💡 Try using a different name within this category")
                    else:
                        st.error(f"Failed to save object: {e}")
                    
    except Exception as e:
        st.error(f"Error loading category: {e}")


def render_morphism_form(edit_mode=False):
    """Render morphism creation/editing form."""
    st.header("Edit Morphism" if edit_mode else "Create New Morphism")
    
    dal = get_dal()
    category_id = st.session_state.parent_category
    
    try:
        category = dal.get_category(category_id)
        objects = dal.get_objects_in_category(category_id)
        
        if not category:
            st.error("Parent category not found")
            return
        
        if len(objects) < 2:
            st.warning("Need at least 2 objects in category to create morphisms")
            if st.button("Cancel"):
                st.session_state.form_mode = None
                st.rerun()
            return
        
        # Load existing data if editing
        if edit_mode and st.session_state.editing_entity:
            try:
                # Get morphism details
                morphisms = dal.get_morphisms_in_category(category_id)
                morph = next((m for m in morphisms if m['ID'] == st.session_state.editing_entity), None)
                if not morph:
                    st.error("Morphism not found")
                    return
                initial_name = morph['name']
                initial_description = morph['description']
                # Note: For editing, we'll show current source/target but won't allow changing them
            except Exception as e:
                st.error(f"Failed to load morphism: {e}")
                return
        else:
            initial_name = ""
            initial_description = ""
        
        st.info(f"{'Editing' if edit_mode else 'Creating'} morphism in category: {category['name']}")
        
        with st.form(key="morphism_form"):
            name = st.text_input("Morphism Name", value=initial_name, placeholder="Enter morphism name")
            description = st.text_area("Description", value=initial_description, placeholder="Enter morphism description")
            
            if not edit_mode:
                # Object selectors - only for creation
                object_options = {obj['ID']: f"{obj['name']} (ID: {obj['ID']})" for obj in objects}
                object_ids = list(object_options.keys())
                
                source_id = st.selectbox(
                    "Source Object",
                    object_ids,
                    format_func=lambda x: object_options[x],
                    key="source_selector"
                )
                
                target_id = st.selectbox(
                    "Target Object", 
                    object_ids,
                    format_func=lambda x: object_options[x],
                    key="target_selector"
                )
            else:
                # Show current source/target for editing but don't allow changes
                if 'morph' in locals():
                    st.info(f"Source: {morph.get('source_object', 'Unknown')} → Target: {morph.get('target_object', 'Unknown')}")
                    st.caption("Source and target cannot be changed when editing")
            
            col1, col2 = st.columns(2)
            
            with col1:
                submitted = st.form_submit_button("Save Morphism" if edit_mode else "Create Morphism", type="primary")
            
            with col2:
                cancelled = st.form_submit_button("Cancel")
            
            if cancelled:
                st.session_state.form_mode = None
                st.rerun()
            
            if submitted:
                if not name.strip():
                    st.error("Morphism name is required")
                    return
                
                try:
                    if edit_mode:
                        # For morphisms, we only update name and description
                        st.info("Morphism update functionality coming soon")
                        st.session_state.form_mode = None
                    else:
                        morphism_id = dal.create_morphism(name, source_id, target_id, category_id, description)
                        st.success(f"Morphism '{name}' created with ID {morphism_id}")
                        add_transaction_change(f"Created morphism '{name}' (ID: {morphism_id})")
                        st.session_state.form_mode = None
                        st.rerun()
                    
                except Exception as e:
                    if "already exists" in str(e):
                        st.error(f"❌ Name conflict: {e}")
                        st.info("💡 Try using a different name for this morphism")
                    else:
                        st.error(f"Failed to save morphism: {e}")
                    
    except Exception as e:
        st.error(f"Error loading category data: {e}")


def render_entity_delete_confirmation():
    """Render delete confirmation for objects and morphisms."""
    form_mode = st.session_state.form_mode
    entity_id = st.session_state.editing_entity
    
    dal = get_dal()
    
    try:
        if form_mode == "delete_object":
            entity = dal.get_object(entity_id)
            entity_type = "object"
        elif form_mode == "delete_morphism":
            # Get morphism from category morphisms
            category_id = st.session_state.get('parent_category')
            if category_id is not None:
                morphisms = dal.get_morphisms_in_category(category_id)
                entity = next((m for m in morphisms if m['ID'] == entity_id), None)
            else:
                entity = None
            entity_type = "morphism"
        else:
            entity = None
            entity_type = "unknown"
        
        if not entity:
            st.error(f"{entity_type.title()} not found")
            st.session_state.form_mode = None
            st.rerun()
            return
        
        st.header("⚠️ Confirm Deletion")
        st.warning(f"Are you sure you want to delete {entity_type} '{entity['name']}'?")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Delete", key="confirm_entity_delete", type="primary"):
                try:
                    if form_mode == "delete_object":
                        dal.delete_object(entity_id)
                        st.success("Object deleted successfully")
                        add_transaction_change(f"Deleted object '{entity['name']}'")
                    elif form_mode == "delete_morphism":
                        st.info("Morphism deletion functionality coming soon")
                        add_transaction_change(f"Attempted to delete morphism '{entity['name']}'")
                    
                    st.session_state.form_mode = None
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to delete {entity_type}: {e}")
        
        with col2:
            if st.button("Cancel", key="cancel_entity_delete"):
                st.session_state.form_mode = None
                st.rerun()
                
    except Exception as e:
        st.error(f"Error loading {entity_type} details: {e}")
        st.session_state.form_mode = None


def render_components_tab():
    """Render the components tab showing entity details."""
    if st.session_state.selected_entity_id is None:
        st.info("Select an entity from the sidebar to view its components")
        return
    
    entity_type = st.session_state.selected_entity_type
    entity_id = st.session_state.selected_entity_id
    dal = get_dal()
    
    try:
        if entity_type == "Category":
            render_category_components(dal, entity_id)
        elif entity_type == "Functor":
            render_functor_components(dal, entity_id)
        elif entity_type == "Natural Transformation":
            render_natural_transformation_components(dal, entity_id)
            
    except Exception as e:
        st.error(f"Error loading {entity_type.lower()} components: {e}")


def render_category_components(dal, category_id):
    """Render category components (objects and morphisms)."""
    try:
        category = dal.get_category(category_id)
        if not category:
            st.error("Category not found")
            return
        
        st.header(f"Category: {category['name']}")
        if category['description']:
            st.write(category['description'])
        
        # Show transaction usage suggestion
        suggest_transaction_usage()
        
        # Objects section
        st.subheader("Objects")
        objects = dal.get_objects_in_category(category_id)
        
        if objects:
            for obj in objects:
                with st.expander(f"📦 {obj['name']}"):
                    st.write(f"**ID:** {obj['ID']}")
                    if obj['description']:
                        st.write(f"**Description:** {obj['description']}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"Edit", key=f"edit_obj_{obj['ID']}"):
                            st.session_state.form_mode = "edit_object"
                            st.session_state.editing_entity = obj['ID']
                            st.session_state.parent_category = category_id
                            st.rerun()
                    with col2:
                        if st.button(f"Delete", key=f"delete_obj_{obj['ID']}"):
                            st.session_state.form_mode = "delete_object"
                            st.session_state.editing_entity = obj['ID']
                            st.rerun()
        else:
            st.write("No objects in this category")
        
        if st.button("Add Object", key="add_object"):
            st.session_state.form_mode = "create_object"
            st.session_state.parent_category = category_id
            st.rerun()
        
        # Morphisms section
        st.subheader("Morphisms")
        morphisms = dal.get_morphisms_in_category(category_id)
        
        if morphisms:
            for morph in morphisms:
                with st.expander(f"🔗 {morph['name']}"):
                    st.write(f"**ID:** {morph['ID']}")
                    if morph['description']:
                        st.write(f"**Description:** {morph['description']}")
                    if morph['source_object'] and morph['target_object']:
                        st.write(f"**Arrow:** {morph['source_object']} → {morph['target_object']}")
                    if morph['is_identity']:
                        st.write("**Type:** Identity morphism")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"Edit", key=f"edit_morph_{morph['ID']}"):
                            st.session_state.form_mode = "edit_morphism"
                            st.session_state.editing_entity = morph['ID']
                            st.session_state.parent_category = category_id
                            st.rerun()
                    with col2:
                        if st.button(f"Delete", key=f"delete_morph_{morph['ID']}"):
                            st.session_state.form_mode = "delete_morphism"
                            st.session_state.editing_entity = morph['ID']
                            st.rerun()
        else:
            st.write("No morphisms in this category")
        
        if st.button("Add Morphism", key="add_morphism"):
            st.session_state.form_mode = "create_morphism"
            st.session_state.parent_category = category_id
            st.rerun()
            
    except Exception as e:
        st.error(f"Error loading category components: {e}")


def render_functor_components(dal, functor_id):
    """Render functor components (mappings)."""
    try:
        functors = dal.list_functors()
        functor = next((f for f in functors if f['ID'] == functor_id), None)
        
        if not functor:
            st.error("Functor not found")
            return
        
        st.header(f"Functor: {functor['name']}")
        if functor['description']:
            st.write(functor['description'])
        
        st.write(f"**Source Category:** {functor['source_category']}")
        st.write(f"**Target Category:** {functor['target_category']}")
        
        src_cat_id = functor.get('source_category_id')
        tgt_cat_id = functor.get('target_category_id')
        if src_cat_id is None or tgt_cat_id is None:
            st.info("This functor is missing source/target category links.")
            return
        
        # Object mappings
        st.subheader("Object Mappings")
        try:
            obj_maps = dal.get_functor_object_mappings(functor_id)
            if obj_maps:
                for m in obj_maps:
                    st.write(f"{m['source_object']} → {m['target_object']}")
                    with st.expander(f"Manage mapping: {m['source_object']}"):
                        if st.button("Remove", key=f"remove_fobj_{functor_id}_{m['source_object_id']}"):
                            try:
                                dal.remove_functor_object_mapping(functor_id, m['source_object_id'])
                                st.success("Mapping removed")
                                add_transaction_change(f"Removed object mapping {m['source_object']} from functor '{functor['name']}'")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Failed to remove mapping: {e}")
            else:
                st.info("No object mappings defined")
            
            # Add mapping form
            src_objs = dal.get_objects_in_category(src_cat_id)
            tgt_objs = dal.get_objects_in_category(tgt_cat_id)
            with st.form(key=f"add_obj_map_{functor_id}"):
                src_opts = {o['ID']: f"{o['name']} (ID: {o['ID']})" for o in src_objs}
                tgt_opts = {o['ID']: f"{o['name']} (ID: {o['ID']})" for o in tgt_objs}
                src_sel = st.selectbox("Source object (in source category)", list(src_opts.keys()), format_func=lambda x: src_opts[x])
                tgt_sel = st.selectbox("Target object (in target category)", list(tgt_opts.keys()), format_func=lambda x: tgt_opts[x])
                colx, coly = st.columns(2)
                with colx:
                    add_obj_map = st.form_submit_button("Add Mapping", type="primary")
                with coly:
                    cancel_obj_map = st.form_submit_button("Cancel")
                if cancel_obj_map:
                    st.experimental_rerun()
                if add_obj_map:
                    try:
                        dal.add_functor_object_mapping(functor_id, src_sel, tgt_sel)
                        st.success("Object mapping added")
                        add_transaction_change(f"Added object mapping to functor '{functor['name']}'")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to add object mapping: {e}")
        except Exception as e:
            st.error(f"Error loading object mappings: {e}")
        
        st.divider()
        
        # Morphism mappings
        st.subheader("Morphism Mappings")
        try:
            morph_maps = dal.get_functor_morphism_mappings(functor_id)
            if morph_maps:
                for m in morph_maps:
                    st.write(f"{m['source_morphism']} ({m['source_from']} → {m['source_to']}) → {m['target_morphism']} ({m['target_from']} → {m['target_to']})")
                    with st.expander(f"Manage mapping: {m['source_morphism']}"):
                        if st.button("Remove", key=f"remove_fmorph_{functor_id}_{m['source_morphism_id']}"):
                            try:
                                dal.remove_functor_morphism_mapping(functor_id, m['source_morphism_id'])
                                st.success("Mapping removed")
                                add_transaction_change(f"Removed morphism mapping {m['source_morphism']} from functor '{functor['name']}'")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Failed to remove mapping: {e}")
            else:
                st.info("No morphism mappings defined")
            
            # Add mapping form
            src_morphs = dal.get_morphisms_in_category(src_cat_id)
            tgt_morphs = dal.get_morphisms_in_category(tgt_cat_id)
            with st.form(key=f"add_morph_map_{functor_id}"):
                src_mopts = {mm['ID']: f"{mm['name']} ({mm.get('source_object','?')} → {mm.get('target_object','?')})" for mm in src_morphs}
                tgt_mopts = {mm['ID']: f"{mm['name']} ({mm.get('source_object','?')} → {mm.get('target_object','?')})" for mm in tgt_morphs}
                src_m_sel = st.selectbox("Source morphism (in source category)", list(src_mopts.keys()), format_func=lambda x: src_mopts[x])
                tgt_m_sel = st.selectbox("Target morphism (in target category)", list(tgt_mopts.keys()), format_func=lambda x: tgt_mopts[x])
                colm1, colm2 = st.columns(2)
                with colm1:
                    add_morph_map = st.form_submit_button("Add Mapping", type="primary")
                with colm2:
                    cancel_morph_map = st.form_submit_button("Cancel")
                if cancel_morph_map:
                    st.experimental_rerun()
                if add_morph_map:
                    try:
                        dal.add_functor_morphism_mapping(functor_id, src_m_sel, tgt_m_sel)
                        st.success("Morphism mapping added")
                        add_transaction_change(f"Added morphism mapping to functor '{functor['name']}'")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to add morphism mapping: {e}")
        except Exception as e:
            st.error(f"Error loading morphism mappings: {e}")
        
    except Exception as e:
        st.error(f"Error loading functor components: {e}")


def render_natural_transformation_components(dal, nt_id):
    """Render natural transformation components."""
    try:
        nat_trans = dal.list_natural_transformations()
        nt = next((n for n in nat_trans if n['ID'] == nt_id), None)
        
        if not nt:
            st.error("Natural transformation not found")
            return
        
        st.header(f"Natural Transformation: {nt['name']}")
        if nt['description']:
            st.write(nt['description'])
        
        # Show linked functors if available
        src = nt.get('source_functor') or nt.get('source_functor_id')
        tgt = nt.get('target_functor') or nt.get('target_functor_id')
        if src or tgt:
            st.write(f"Functors: F = {src} ⇒ G = {tgt}")
        else:
            st.info("This natural transformation is not yet linked to functors.")
        
        st.subheader("Component Morphisms")
        
        # Determine source/target categories via linked functors
        functors = dal.list_functors()
        src_functor = next((f for f in functors if f['ID'] == nt.get('source_functor_id')), None)
        tgt_functor = next((f for f in functors if f['ID'] == nt.get('target_functor_id')), None)
        if src_functor and tgt_functor:
            src_cat_id = src_functor.get('source_category_id')
            tgt_cat_id = tgt_functor.get('target_category_id')
            
            # List existing components
            components = dal.get_nt_components(nt_id)
            if components:
                for comp in components:
                    with st.expander(f"α at X ID {comp['at_object_id']} → {comp['morphism_name']}"):
                        st.write(f"Morphism: {comp['morphism_name']} ({comp['source_object']} → {comp['target_object']})")
                        col_a, col_b = st.columns(2)
                        with col_a:
                            if st.button("Remove", key=f"remove_nt_comp_{nt_id}_{comp['at_object_id']}"):
                                try:
                                    dal.remove_nt_component(nt_id, comp['at_object_id'])
                                    st.success("Component removed")
                                    add_transaction_change(f"Removed NT component at object ID {comp['at_object_id']}")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Failed to remove component: {e}")
            else:
                st.info("No components defined yet")
            
            st.divider()
            st.subheader("Add Component α_X")
            try:
                src_objects = dal.get_objects_in_category(src_cat_id)
                tgt_morphisms = dal.get_morphisms_in_category(tgt_cat_id)
                
                with st.form(key="nt_add_component_form"):
                    # Object X selector
                    obj_opts = {o['ID']: f"{o['name']} (ID: {o['ID']})" for o in src_objects}
                    obj_id = st.selectbox("Object X in source category", list(obj_opts.keys()), format_func=lambda x: obj_opts[x])
                    
                    # Morphism selector (in target category)
                    morph_opts = {m['ID']: f"{m['name']} ({m.get('source_object','?')} → {m.get('target_object','?')})" for m in tgt_morphisms}
                    morph_id = st.selectbox("Component morphism in target category", list(morph_opts.keys()), format_func=lambda x: morph_opts[x])
                    
                    colc1, colc2 = st.columns(2)
                    with colc1:
                        add_submitted = st.form_submit_button("Add Component", type="primary")
                    with colc2:
                        cancel_add = st.form_submit_button("Cancel")
                    if cancel_add:
                        st.rerun()
                    if add_submitted:
                        try:
                            dal.add_nt_component(nt_id, obj_id, morph_id)
                            st.success("Component added")
                            add_transaction_change(f"Added NT component at X={obj_id} using morphism ID {morph_id}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to add component: {e}")
            except Exception as e:
                st.error(f"Failed to load component options: {e}")
            
            st.divider()
            st.subheader("Validate")
            if st.button("Validate Structure", key=f"validate_nt_struct_{nt_id}"):
                issues = dal.validate_nt_structure(nt_id)
                if issues:
                    for msg in issues:
                        st.warning(msg)
                else:
                    st.success("Structure valid")
            if st.button("Validate Naturality", key=f"validate_nt_nat_{nt_id}"):
                msgs = dal.validate_naturality(nt_id)
                for msg in msgs:
                    st.info(msg)
        else:
            st.info("Components require linked functors with categories.")
        
    except Exception as e:
        st.error(f"Error loading natural transformation components: {e}")


def render_visualization_tab():
    """Render the visualization tab."""
    st.header("🌐 Visualization")
    
    dal = get_dal()
    
    # Show overall statistics
    render_visualization_statistics(dal)
    
    st.divider()
    
    # Render visualization based on selected entity
    entity_type = st.session_state.selected_entity_type
    entity_id = st.session_state.selected_entity_id
    
    if entity_type == "Category" and entity_id is not None:
        # Show category-specific visualization
        render_visualization(dal, entity_type, entity_id)
    elif entity_type in ["Functor", "Natural Transformation"]:
        # Show functor/natural transformation visualization
        render_visualization(dal, entity_type, None)
    else:
        # Show complete graph visualization
        st.subheader("Complete System Overview")
        render_visualization(dal, "Complete", None)


def render_documentation_tab():
    """Render the documentation tab."""
    st.header("📚 Documentation")
    
    # Sub-tabs for documentation sections
    doc_tab1, doc_tab2, doc_tab3 = st.tabs(["📖 Mathematical Reference", "📝 Transaction History", "🚀 Getting Started"])
    
    with doc_tab1:
        render_mathematical_reference()
    
    with doc_tab2:
        render_transaction_history()
    
    with doc_tab3:
        render_getting_started_guide()


def render_mathematical_reference():
    """Render mathematical reference documentation."""
    entity_type = st.session_state.selected_entity_type
    
    if entity_type == "Category":
        st.markdown("""
        ### Categories
        
        A **category** consists of:
        - A collection of **objects**
        - A collection of **morphisms** (arrows) between objects
        - **Composition** of morphisms
        - **Identity** morphisms for each object
        
        #### Mathematical Laws
        - **Associativity**: (f ∘ g) ∘ h = f ∘ (g ∘ h)
        - **Identity**: f ∘ id = f = id ∘ f
        """)
    
    elif entity_type == "Functor":
        st.markdown("""
        ### Functors
        
        A **functor** F: C → D between categories C and D consists of:
        - A mapping of objects: F(X) for each object X in C
        - A mapping of morphisms: F(f) for each morphism f in C
        
        #### Mathematical Laws
        - **Preserve composition**: F(g ∘ f) = F(g) ∘ F(f)
        - **Preserve identity**: F(id_X) = id_{F(X)}
        """)
    
    elif entity_type == "Natural Transformation":
        st.markdown("""
        ### Natural Transformations
        
        A **natural transformation** α: F ⇒ G between functors F, G: C → D consists of:
        - A morphism α_X: F(X) → G(X) for each object X in C
        
        #### Mathematical Laws
        - **Naturality**: G(f) ∘ α_X = α_Y ∘ F(f) for all f: X → Y
        """)


def render_transaction_history():
    """Render transaction history."""
    st.subheader("Transaction History")
    
    if not st.session_state.transaction_history:
        st.info("No completed transactions yet")
        return
    
    # Show recent transactions
    st.write(f"**{len(st.session_state.transaction_history)} completed transactions:**")
    
    for i, transaction in enumerate(reversed(st.session_state.transaction_history), 1):
        with st.expander(f"Transaction {len(st.session_state.transaction_history) - i + 1}: {transaction['count']} changes"):
            for change in transaction['changes']:
                if change.startswith("Created"):
                    st.write(f"✅ {change}")
                elif change.startswith("Updated"):
                    st.write(f"✏️ {change}")
                elif change.startswith("Deleted"):
                    st.write(f"❌ {change}")
                else:
                    st.write(f"📝 {change}")
    
    # Clear history button
    if st.button("Clear History", key="clear_transaction_history"):
        st.session_state.transaction_history = []
        st.success("Transaction history cleared")
        st.rerun()


def render_getting_started_guide():
    """Render getting started guide."""
    st.subheader("Getting Started with Codices")
    
    st.markdown("""
    ### Quick Start Guide
    
    1. **Create a Category**
       - Select "Category" in the sidebar
       - Click "Create New"
       - Enter a name and description
       - Save the category
    
    2. **Add Objects**
       - Select your category
       - Go to "Components" tab
       - Click "Add Object"
       - Enter object details
    
    3. **Create Morphisms**
       - Ensure you have at least 2 objects
       - Click "Add Morphism"
       - Select source and target objects
       - Save the morphism
    
    4. **Visualize**
       - Go to "Visualization" tab
       - Choose visualization mode
       - Explore your category structure
    
    5. **Transaction Management**
       - Use "Auto-save" for immediate changes
       - Use "Manual Transaction" for batch operations
       - Enable "Preview Mode" to review changes before commit
    
    ### Tips
    - 💡 Use transactions for complex operations
    - 🔍 Enable preview mode to see all changes before committing
    - 📊 Check the visualization tab to understand your structures
    - 📝 Use descriptive names for better organization
    """)


def main():
    """Main application entry point."""
    init_session_state()
    
    # Render sidebar
    render_sidebar()
    
    # Render main content
    render_main_content()


if __name__ == "__main__":
    main()
