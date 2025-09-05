import kuzu
import logging
from typing import Dict, List, Optional, Any, Union

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _get_query_result(result: Any) -> Any:
    """Helper function to extract QueryResult from connection.execute() return value."""
    if isinstance(result, list):
        return result[0]
    return result


def initialize_schema(db_path: str = "./kuzu_db") -> None:
    """
    Initialize the complete database schema for category theory entities.
    
    Args:
        db_path: Path to the Kuzu database directory
    """
    try:
        db = kuzu.Database(db_path)
        conn = kuzu.Connection(db)
        
        # Create node tables
        conn.execute("CREATE NODE TABLE IF NOT EXISTS Category(ID SERIAL PRIMARY KEY, name STRING, description STRING)")
        conn.execute("CREATE NODE TABLE IF NOT EXISTS Object(ID SERIAL PRIMARY KEY, name STRING, description STRING)")
        conn.execute("CREATE NODE TABLE IF NOT EXISTS Morphism(ID SERIAL PRIMARY KEY, name STRING, description STRING, is_identity BOOLEAN)")
        conn.execute("CREATE NODE TABLE IF NOT EXISTS Functor(ID SERIAL PRIMARY KEY, name STRING, description STRING)")
        conn.execute("CREATE NODE TABLE IF NOT EXISTS Natural_Transformation(ID SERIAL PRIMARY KEY, name STRING, description STRING)")
        conn.execute("CREATE NODE TABLE IF NOT EXISTS Datatype(ID SERIAL PRIMARY KEY, literal STRING, description STRING)")
        
        # Create relationship tables
        conn.execute("CREATE REL TABLE IF NOT EXISTS morphism_source(FROM Morphism TO Object)")
        conn.execute("CREATE REL TABLE IF NOT EXISTS morphism_target(FROM Morphism TO Object)")
        conn.execute("CREATE REL TABLE IF NOT EXISTS functor_source(FROM Functor TO Category)")
        conn.execute("CREATE REL TABLE IF NOT EXISTS functor_target(FROM Functor TO Category)")
        conn.execute("CREATE REL TABLE IF NOT EXISTS category_objects(FROM Category TO Object)")
        conn.execute("CREATE REL TABLE IF NOT EXISTS category_morphisms(FROM Category TO Morphism)")
        
        # Functor mapping relationships (explicit storage)
        conn.execute("CREATE REL TABLE IF NOT EXISTS functor_object_map(FROM Object TO Object, via_functor_id INT)")
        conn.execute("CREATE REL TABLE IF NOT EXISTS functor_morphism_map(FROM Morphism TO Morphism, via_functor_id INT)")
        
        # Natural transformation relationships
        conn.execute("CREATE REL TABLE IF NOT EXISTS nat_trans_source(FROM Natural_Transformation TO Functor)")
        conn.execute("CREATE REL TABLE IF NOT EXISTS nat_trans_target(FROM Natural_Transformation TO Functor)")
        conn.execute("CREATE REL TABLE IF NOT EXISTS nat_trans_components(FROM Natural_Transformation TO Morphism, at_object_id INT)")
        
        logger.info("Database schema initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize schema: {e}")
        raise


class CategoryDAL:
    """
    Data Access Layer for Category Theory entities.
    Provides CRUD operations and transaction management for mathematical categories.
    """
    
    def __init__(self, db_path: str = "./kuzu_db"):
        """
        Initialize the data access layer.
        
        Args:
            db_path: Path to the Kuzu database directory
        """
        self.db_path = db_path
        self.db = kuzu.Database(db_path)
        self.conn = kuzu.Connection(self.db)
        self.transaction_active = False
        
    def begin_transaction(self) -> None:
        """Start a new transaction for preview mode."""
        if not self.transaction_active:
            self.conn.execute("BEGIN TRANSACTION")
            self.transaction_active = True
            logger.info("Transaction started")
    
    def commit_transaction(self) -> None:
        """Commit current transaction to persistent storage."""
        if self.transaction_active:
            self.conn.execute("COMMIT")
            self.transaction_active = False
            logger.info("Transaction committed")
    
    def rollback_transaction(self) -> None:
        """Rollback current transaction, discarding all changes."""
        if self.transaction_active:
            self.conn.execute("ROLLBACK")
            self.transaction_active = False
            logger.info("Transaction rolled back")
    
    # Category operations
    def create_category(self, name: str, description: str = "") -> int:
        """
        Create a new category.
        
        Args:
            name: Category name (must be unique)
            description: Optional description
            
        Returns:
            ID of the created category
        """
        try:
            # Check if category with this name already exists
            existing_categories = self.list_categories()
            for cat in existing_categories:
                if cat['name'] == name:
                    raise ValueError(f"Category '{name}' already exists with ID {cat['ID']}")
            
            result = self.conn.execute(
                "CREATE (c:Category {name: $name, description: $description}) RETURN c.ID",
                {"name": name, "description": description}
            )
            query_result = _get_query_result(result)
            row = query_result.get_next()  # type: ignore
            category_id = int(row[0])  # type: ignore
            logger.info(f"Created category '{name}' with ID {category_id}")
            return category_id
        except Exception as e:
            logger.error(f"Failed to create category '{name}': {e}")
            raise
    
    def get_category(self, category_id: int) -> Optional[Dict[str, Any]]:
        """
        Get category by ID.
        
        Args:
            category_id: Category ID
            
        Returns:
            Category dictionary or None if not found
        """
        try:
            result = self.conn.execute(
                "MATCH (c:Category) WHERE c.ID = $id RETURN c.ID, c.name, c.description",
                {"id": category_id}
            )
            query_result = _get_query_result(result)
            if query_result.has_next():  # type: ignore
                row = query_result.get_next()  # type: ignore
                return {
                    "ID": int(row[0]),  # type: ignore
                    "name": str(row[1]),  # type: ignore
                    "description": str(row[2])  # type: ignore
                }
            return None
        except Exception as e:
            logger.error(f"Failed to get category {category_id}: {e}")
            raise
    
    def list_categories(self) -> List[Dict[str, Any]]:
        """
        List all categories.
        
        Returns:
            List of category dictionaries
        """
        try:
            result = self.conn.execute("MATCH (c:Category) RETURN c.ID, c.name, c.description ORDER BY c.name")
            query_result = _get_query_result(result)
            categories = []
            while query_result.has_next():  # type: ignore
                row = query_result.get_next()  # type: ignore
                categories.append({
                    "ID": int(row[0]),  # type: ignore
                    "name": str(row[1]),  # type: ignore
                    "description": str(row[2])  # type: ignore
                })
            return categories
        except Exception as e:
            logger.error(f"Failed to list categories: {e}")
            raise
    
    def update_category(self, category_id: int, name: Optional[str] = None, description: Optional[str] = None) -> bool:
        """
        Update category properties.
        
        Args:
            category_id: Category ID
            name: New name (optional)
            description: New description (optional)
            
        Returns:
            True if update successful
        """
        try:
            if name is not None:
                # Check if another category with this name already exists
                existing_categories = self.list_categories()
                for cat in existing_categories:
                    if cat['name'] == name and cat['ID'] != category_id:
                        raise ValueError(f"Category '{name}' already exists with ID {cat['ID']}")
                
                self.conn.execute(
                    "MATCH (c:Category) WHERE c.ID = $id SET c.name = $name",
                    {"id": category_id, "name": str(name)}
                )
            if description is not None:
                self.conn.execute(
                    "MATCH (c:Category) WHERE c.ID = $id SET c.description = $description",
                    {"id": category_id, "description": str(description)}
                )
            logger.info(f"Updated category {category_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update category {category_id}: {e}")
            raise
    
    def delete_category(self, category_id: int) -> bool:
        """
        Delete category and all contained entities.
        
        Args:
            category_id: Category ID
            
        Returns:
            True if deletion successful
        """
        try:
            # Delete all morphisms in category first
            self.conn.execute(
                "MATCH (c:Category)-[:category_morphisms]->(m:Morphism) WHERE c.ID = $id DETACH DELETE m",
                {"id": category_id}
            )
            
            # Delete all objects in category
            self.conn.execute(
                "MATCH (c:Category)-[:category_objects]->(o:Object) WHERE c.ID = $id DETACH DELETE o",
                {"id": category_id}
            )
            
            # Delete the category itself
            self.conn.execute(
                "MATCH (c:Category) WHERE c.ID = $id DETACH DELETE c",
                {"id": category_id}
            )
            
            logger.info(f"Deleted category {category_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete category {category_id}: {e}")
            raise
    
    # Object operations
    def create_object(self, name: str, category_id: int, description: str = "") -> int:
        """
        Create an object within a category.
        
        Args:
            name: Object name
            category_id: ID of the containing category
            description: Optional description
            
        Returns:
            ID of the created object
        """
        try:
            # Check if object with this name already exists in the category
            existing_objects = self.get_objects_in_category(category_id)
            for obj in existing_objects:
                if obj['name'] == name:
                    raise ValueError(f"Object '{name}' already exists in category {category_id} with ID {obj['ID']}")
            
            # Create the object
            result = self.conn.execute(
                "CREATE (o:Object {name: $name, description: $description}) RETURN o.ID",
                {"name": name, "description": description}
            )
            query_result = _get_query_result(result)
            row = query_result.get_next()  # type: ignore
            object_id = int(row[0])  # type: ignore
            
            # Link to category
            self.conn.execute(
                "MATCH (c:Category), (o:Object) WHERE c.ID = $cat_id AND o.ID = $obj_id CREATE (c)-[:category_objects]->(o)",
                {"cat_id": category_id, "obj_id": object_id}
            )
            
            logger.info(f"Created object '{name}' with ID {object_id} in category {category_id}")
            return object_id
        except Exception as e:
            logger.error(f"Failed to create object '{name}': {e}")
            raise
    
    def get_object(self, object_id: int) -> Optional[Dict[str, Any]]:
        """
        Get object by ID.
        
        Args:
            object_id: Object ID
            
        Returns:
            Object dictionary or None if not found
        """
        try:
            result = self.conn.execute(
                "MATCH (o:Object) WHERE o.ID = $id RETURN o.ID, o.name, o.description",
                {"id": object_id}
            )
            query_result = _get_query_result(result)
            if query_result.has_next():  # type: ignore
                row = query_result.get_next()  # type: ignore
                return {
                    "ID": int(row[0]),  # type: ignore
                    "name": str(row[1]),  # type: ignore
                    "description": str(row[2])  # type: ignore
                }
            return None
        except Exception as e:
            logger.error(f"Failed to get object {object_id}: {e}")
            raise
    
    def get_objects_in_category(self, category_id: int) -> List[Dict[str, Any]]:
        """
        Get all objects in a category.
        
        Args:
            category_id: Category ID
            
        Returns:
            List of object dictionaries
        """
        try:
            result = self.conn.execute(
                "MATCH (c:Category)-[:category_objects]->(o:Object) WHERE c.ID = $id RETURN o.ID, o.name, o.description ORDER BY o.name",
                {"id": category_id}
            )
            query_result = _get_query_result(result)
            objects = []
            while query_result.has_next():  # type: ignore
                row = query_result.get_next()  # type: ignore
                objects.append({
                    "ID": int(row[0]),  # type: ignore
                    "name": str(row[1]),  # type: ignore
                    "description": str(row[2])  # type: ignore
                })
            return objects
        except Exception as e:
            logger.error(f"Failed to get objects in category {category_id}: {e}")
            raise
    
    def update_object(self, object_id: int, name: Optional[str] = None, description: Optional[str] = None) -> bool:
        """
        Update object properties.
        
        Args:
            object_id: Object ID
            name: New name (optional)
            description: New description (optional)
            
        Returns:
            True if update successful
        """
        try:
            if name is not None:
                self.conn.execute(
                    "MATCH (o:Object) WHERE o.ID = $id SET o.name = $name",
                    {"id": object_id, "name": str(name)}
                )
            if description is not None:
                self.conn.execute(
                    "MATCH (o:Object) WHERE o.ID = $id SET o.description = $description",
                    {"id": object_id, "description": str(description)}
                )
            logger.info(f"Updated object {object_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update object {object_id}: {e}")
            raise
    
    def delete_object(self, object_id: int) -> bool:
        """
        Delete object and all related morphisms.
        
        Args:
            object_id: Object ID
            
        Returns:
            True if deletion successful
        """
        try:
            # Delete all morphisms that use this object as source or target
            self.conn.execute(
                "MATCH (m:Morphism)-[:morphism_source|morphism_target]->(o:Object) WHERE o.ID = $id DETACH DELETE m",
                {"id": object_id}
            )
            
            # Delete the object itself using DETACH DELETE
            self.conn.execute(
                "MATCH (o:Object) WHERE o.ID = $id DETACH DELETE o",
                {"id": object_id}
            )
            
            logger.info(f"Deleted object {object_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete object {object_id}: {e}")
            raise
    
    # Morphism operations
    def create_morphism(self, name: str, source_id: int, target_id: int, category_id: int, description: str = "") -> int:
        """
        Create a morphism between objects in a category.
        
        Args:
            name: Morphism name
            source_id: Source object ID
            target_id: Target object ID
            category_id: Category ID
            description: Optional description
            
        Returns:
            ID of the created morphism
        """
        try:
            # Check if morphism with this name already exists in the category
            existing_morphisms = self.get_morphisms_in_category(category_id)
            for morph in existing_morphisms:
                if morph['name'] == name:
                    raise ValueError(f"Morphism '{name}' already exists in category {category_id} with ID {morph['ID']}")
            
            # Create the morphism
            result = self.conn.execute(
                "CREATE (m:Morphism {name: $name, description: $description, is_identity: false}) RETURN m.ID",
                {"name": name, "description": description}
            )
            query_result = _get_query_result(result)
            row = query_result.get_next()  # type: ignore
            morphism_id = int(row[0])  # type: ignore
            
            # Link to category
            self.conn.execute(
                "MATCH (c:Category), (m:Morphism) WHERE c.ID = $cat_id AND m.ID = $morph_id CREATE (c)-[:category_morphisms]->(m)",
                {"cat_id": category_id, "morph_id": morphism_id}
            )
            
            # Set source and target
            self.conn.execute(
                "MATCH (m:Morphism), (o:Object) WHERE m.ID = $morph_id AND o.ID = $obj_id CREATE (m)-[:morphism_source]->(o)",
                {"morph_id": morphism_id, "obj_id": source_id}
            )
            self.conn.execute(
                "MATCH (m:Morphism), (o:Object) WHERE m.ID = $morph_id AND o.ID = $obj_id CREATE (m)-[:morphism_target]->(o)",
                {"morph_id": morphism_id, "obj_id": target_id}
            )
            
            logger.info(f"Created morphism '{name}' with ID {morphism_id}")
            return morphism_id
        except Exception as e:
            logger.error(f"Failed to create morphism '{name}': {e}")
            raise
    
    def get_morphisms_in_category(self, category_id: int) -> List[Dict[str, Any]]:
        """
        Get all morphisms in a category.
        
        Args:
            category_id: Category ID
            
        Returns:
            List of morphism dictionaries with source/target object info
        """
        try:
            result = self.conn.execute(
                """MATCH (c:Category)-[:category_morphisms]->(m:Morphism) WHERE c.ID = $id
                   OPTIONAL MATCH (m)-[:morphism_source]->(s:Object)
                   OPTIONAL MATCH (m)-[:morphism_target]->(t:Object)
                   RETURN m.ID, m.name, m.description, m.is_identity, s.name, t.name ORDER BY m.name""",
                {"id": category_id}
            )
            query_result = _get_query_result(result)
            morphisms = []
            while query_result.has_next():  # type: ignore
                row = query_result.get_next()  # type: ignore
                morphisms.append({
                    "ID": int(row[0]),  # type: ignore
                    "name": str(row[1]),  # type: ignore
                    "description": str(row[2]),  # type: ignore
                    "is_identity": bool(row[3]),  # type: ignore
                    "source_object": str(row[4]) if row[4] is not None else None,  # type: ignore
                    "target_object": str(row[5]) if row[5] is not None else None  # type: ignore
                })
            return morphisms
        except Exception as e:
            logger.error(f"Failed to get morphisms in category {category_id}: {e}")
            raise
    
    # Functor operations
    def create_functor(self, name: str, source_cat_id: int, target_cat_id: int, description: str = "") -> int:
        """
        Create a functor between categories.
        
        Args:
            name: Functor name
            source_cat_id: Source category ID
            target_cat_id: Target category ID
            description: Optional description
            
        Returns:
            ID of the created functor
        """
        try:
            result = self.conn.execute(
                "CREATE (f:Functor {name: $name, description: $description}) RETURN f.ID",
                {"name": name, "description": description}
            )
            query_result = _get_query_result(result)
            row = query_result.get_next()  # type: ignore
            functor_id = int(row[0])  # type: ignore
            
            # Link to source and target categories
            self.conn.execute(
                "MATCH (f:Functor), (c:Category) WHERE f.ID = $func_id AND c.ID = $cat_id CREATE (f)-[:functor_source]->(c)",
                {"func_id": functor_id, "cat_id": source_cat_id}
            )
            self.conn.execute(
                "MATCH (f:Functor), (c:Category) WHERE f.ID = $func_id AND c.ID = $cat_id CREATE (f)-[:functor_target]->(c)",
                {"func_id": functor_id, "cat_id": target_cat_id}
            )
            
            logger.info(f"Created functor '{name}' with ID {functor_id}")
            return functor_id
        except Exception as e:
            logger.error(f"Failed to create functor '{name}': {e}")
            raise
    
    def list_functors(self) -> List[Dict[str, Any]]:
        """
        List all functors.
        
        Returns:
            List of functor dictionaries with source/target category info
        """
        try:
            result = self.conn.execute(
                """MATCH (f:Functor)
                   OPTIONAL MATCH (f)-[:functor_source]->(sc:Category)
                   OPTIONAL MATCH (f)-[:functor_target]->(tc:Category)
                   RETURN f.ID, f.name, f.description, sc.name, tc.name, sc.ID, tc.ID ORDER BY f.name"""
            )
            query_result = _get_query_result(result)
            functors = []
            while query_result.has_next():  # type: ignore
                row = query_result.get_next()  # type: ignore
                functors.append({
                    "ID": int(row[0]),  # type: ignore
                    "name": str(row[1]),  # type: ignore
                    "description": str(row[2]),  # type: ignore
                    "source_category": str(row[3]) if row[3] is not None else None,  # type: ignore
                    "target_category": str(row[4]) if row[4] is not None else None,  # type: ignore
                    "source_category_id": int(row[5]) if row[5] is not None else None,  # type: ignore
                    "target_category_id": int(row[6]) if row[6] is not None else None  # type: ignore
                })
            return functors
        except Exception as e:
            logger.error(f"Failed to list functors: {e}")
            raise
    
    def create_natural_transformation(self, name: str, source_functor_id: int, target_functor_id: int, description: str = "") -> int:
        """
        Create a natural transformation between functors.
        
        Args:
            name: Natural transformation name
            source_functor_id: Source functor ID
            target_functor_id: Target functor ID
            description: Optional description
            
        Returns:
            ID of the created natural transformation
        """
        try:
            result = self.conn.execute(
                "CREATE (nt:Natural_Transformation {name: $name, description: $description}) RETURN nt.ID",
                {"name": name, "description": description}
            )
            query_result = _get_query_result(result)
            row = query_result.get_next()  # type: ignore
            nt_id = int(row[0])  # type: ignore
            
            # Link to source and target functors
            self.conn.execute(
                "MATCH (nt:Natural_Transformation), (f:Functor) WHERE nt.ID = $nt_id AND f.ID = $src_id CREATE (nt)-[:nat_trans_source]->(f)",
                {"nt_id": nt_id, "src_id": source_functor_id}
            )
            self.conn.execute(
                "MATCH (nt:Natural_Transformation), (f:Functor) WHERE nt.ID = $nt_id AND f.ID = $tgt_id CREATE (nt)-[:nat_trans_target]->(f)",
                {"nt_id": nt_id, "tgt_id": target_functor_id}
            )
            
            logger.info(f"Created natural transformation '{name}' with ID {nt_id}")
            return nt_id
        except Exception as e:
            logger.error(f"Failed to create natural transformation '{name}': {e}")
            raise
    
    def list_natural_transformations(self) -> List[Dict[str, Any]]:
        """
        List all natural transformations.
        
        Returns:
            List of natural transformation dictionaries including linked functors when available
        """
        try:
            result = self.conn.execute(
                """MATCH (nt:Natural_Transformation)
                   OPTIONAL MATCH (nt)-[:nat_trans_source]->(sf:Functor)
                   OPTIONAL MATCH (nt)-[:nat_trans_target]->(tf:Functor)
                   RETURN nt.ID, nt.name, nt.description, sf.ID, sf.name, tf.ID, tf.name
                   ORDER BY nt.name"""
            )
            query_result = _get_query_result(result)
            nat_trans = []
            while query_result.has_next():  # type: ignore
                row = query_result.get_next()  # type: ignore
                nat_trans.append({
                    "ID": int(row[0]),  # type: ignore
                    "name": str(row[1]),  # type: ignore
                    "description": str(row[2]),  # type: ignore
                    "source_functor_id": int(row[3]) if row[3] is not None else None,  # type: ignore
                    "source_functor": str(row[4]) if row[4] is not None else None,  # type: ignore
                    "target_functor_id": int(row[5]) if row[5] is not None else None,  # type: ignore
                    "target_functor": str(row[6]) if row[6] is not None else None  # type: ignore
                })
            return nat_trans
        except Exception as e:
            logger.error(f"Failed to list natural transformations: {e}")
            raise
    
    def add_functor_object_mapping(self, functor_id: int, source_obj_id: int, target_obj_id: int) -> bool:
        """Add object mapping ensuring objects belong to functor's domain/codomain."""
        try:
            self.conn.execute(
                """
                MATCH (f:Functor) WHERE f.ID = $fid
                OPTIONAL MATCH (f)-[:functor_source]->(sc:Category)
                OPTIONAL MATCH (f)-[:functor_target]->(tc:Category)
                MATCH (s:Object) WHERE s.ID = $sid
                MATCH (t:Object) WHERE t.ID = $tid
                WITH f, sc, tc, s, t
                MATCH (sc)-[:category_objects]->(s)
                MATCH (tc)-[:category_objects]->(t)
                CREATE (s)-[:functor_object_map {via_functor_id: $fid}]->(t)
                """,
                {"fid": functor_id, "sid": source_obj_id, "tid": target_obj_id}
            )
            logger.info(f"Added functor object mapping F#{functor_id}: {source_obj_id} -> {target_obj_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to add functor object mapping: {e}")
            raise

    def remove_functor_object_mapping(self, functor_id: int, source_obj_id: int) -> bool:
        """Remove object mapping for a given source object under a functor."""
        try:
            self.conn.execute(
                """
                MATCH (s:Object)-[r:functor_object_map]->(:Object)
                WHERE r.via_functor_id = $fid AND s.ID = $sid
                DELETE r
                """,
                {"fid": functor_id, "sid": source_obj_id}
            )
            logger.info(f"Removed functor object mapping F#{functor_id}: {source_obj_id} -> *")
            return True
        except Exception as e:
            logger.error(f"Failed to remove functor object mapping: {e}")
            raise

    def get_functor_object_mappings(self, functor_id: int) -> List[Dict[str, Any]]:
        """List object mappings for a functor with names/IDs."""
        try:
            result = self.conn.execute(
                """
                MATCH (s:Object)-[r:functor_object_map]->(t:Object)
                WHERE r.via_functor_id = $fid
                RETURN s.ID, s.name, t.ID, t.name
                ORDER BY s.name
                """,
                {"fid": functor_id}
            )
            qr = _get_query_result(result)
            mappings: List[Dict[str, Any]] = []
            while qr.has_next():  # type: ignore
                row = qr.get_next()  # type: ignore
                mappings.append({
                    "source_object_id": int(row[0]),
                    "source_object": str(row[1]),
                    "target_object_id": int(row[2]),
                    "target_object": str(row[3]),
                })
            return mappings
        except Exception as e:
            logger.error(f"Failed to list functor object mappings: {e}")
            raise

    def add_functor_morphism_mapping(self, functor_id: int, source_morph_id: int, target_morph_id: int) -> bool:
        """Add morphism mapping ensuring morphisms belong to functor's domain/codomain."""
        try:
            self.conn.execute(
                """
                MATCH (f:Functor) WHERE f.ID = $fid
                OPTIONAL MATCH (f)-[:functor_source]->(sc:Category)
                OPTIONAL MATCH (f)-[:functor_target]->(tc:Category)
                MATCH (sm:Morphism) WHERE sm.ID = $smid
                MATCH (tm:Morphism) WHERE tm.ID = $tmid
                WITH f, sc, tc, sm, tm
                MATCH (sc)-[:category_morphisms]->(sm)
                MATCH (tc)-[:category_morphisms]->(tm)
                CREATE (sm)-[:functor_morphism_map {via_functor_id: $fid}]->(tm)
                """,
                {"fid": functor_id, "smid": source_morph_id, "tmid": target_morph_id}
            )
            logger.info(f"Added functor morphism mapping F#{functor_id}: {source_morph_id} -> {target_morph_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to add functor morphism mapping: {e}")
            raise

    def remove_functor_morphism_mapping(self, functor_id: int, source_morph_id: int) -> bool:
        """Remove morphism mapping for a given source morphism under a functor."""
        try:
            self.conn.execute(
                """
                MATCH (sm:Morphism)-[r:functor_morphism_map]->(:Morphism)
                WHERE r.via_functor_id = $fid AND sm.ID = $smid
                DELETE r
                """,
                {"fid": functor_id, "smid": source_morph_id}
            )
            logger.info(f"Removed functor morphism mapping F#{functor_id}: {source_morph_id} -> *")
            return True
        except Exception as e:
            logger.error(f"Failed to remove functor morphism mapping: {e}")
            raise

    def get_functor_morphism_mappings(self, functor_id: int) -> List[Dict[str, Any]]:
        """List morphism mappings for a functor with names/IDs."""
        try:
            result = self.conn.execute(
                """
                MATCH (sm:Morphism)-[r:functor_morphism_map]->(tm:Morphism)
                WHERE r.via_functor_id = $fid
                OPTIONAL MATCH (sm)-[:morphism_source]->(ss:Object)
                OPTIONAL MATCH (sm)-[:morphism_target]->(st:Object)
                OPTIONAL MATCH (tm)-[:morphism_source]->(ts:Object)
                OPTIONAL MATCH (tm)-[:morphism_target]->(tt:Object)
                RETURN sm.ID, sm.name, ss.name, st.name, tm.ID, tm.name, ts.name, tt.name
                ORDER BY sm.name
                """,
                {"fid": functor_id}
            )
            qr = _get_query_result(result)
            mappings: List[Dict[str, Any]] = []
            while qr.has_next():  # type: ignore
                row = qr.get_next()  # type: ignore
                mappings.append({
                    "source_morphism_id": int(row[0]),
                    "source_morphism": str(row[1]),
                    "source_from": str(row[2]) if row[2] is not None else None,
                    "source_to": str(row[3]) if row[3] is not None else None,
                    "target_morphism_id": int(row[4]),
                    "target_morphism": str(row[5]),
                    "target_from": str(row[6]) if row[6] is not None else None,
                    "target_to": str(row[7]) if row[7] is not None else None,
                })
            return mappings
        except Exception as e:
            logger.error(f"Failed to list functor morphism mappings: {e}")
            raise

    def add_nt_component(self, nt_id: int, at_object_id: int, component_morphism_id: int) -> bool:
        """
        Add a component morphism α_X for natural transformation at object X.
        Enforces that X is in the source category of the linked functors and the morphism is in the target category.
        """
        try:
            # Create component relationship only if typing holds
            self.conn.execute(
                """
                MATCH (nt:Natural_Transformation)-[:nat_trans_source]->(:Functor)-[:functor_source]->(srcCat:Category),
                      (nt)-[:nat_trans_target]->(:Functor)-[:functor_target]->(tgtCat:Category),
                      (x:Object), (m:Morphism)
                WHERE nt.ID = $nt_id AND x.ID = $x_id AND m.ID = $m_id
                  AND (srcCat)-[:category_objects]->(x)
                  AND (tgtCat)-[:category_morphisms]->(m)
                CREATE (nt)-[:nat_trans_components {at_object_id: $x_id}]->(m)
                """,
                {"nt_id": nt_id, "x_id": at_object_id, "m_id": component_morphism_id}
            )
            logger.info(f"Added NT component for nt={nt_id} at X={at_object_id} using morphism={component_morphism_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to add natural transformation component: {e}")
            raise

    def remove_nt_component(self, nt_id: int, at_object_id: int) -> bool:
        """Remove component morphism for a specific object X."""
        try:
            self.conn.execute(
                """
                MATCH (nt:Natural_Transformation)-[r:nat_trans_components]->(:Morphism)
                WHERE nt.ID = $nt_id AND r.at_object_id = $x_id
                DELETE r
                """,
                {"nt_id": nt_id, "x_id": at_object_id}
            )
            logger.info(f"Removed NT component for nt={nt_id} at X={at_object_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to remove natural transformation component: {e}")
            raise

    def get_nt_components(self, nt_id: int) -> List[Dict[str, Any]]:
        """List components α_X for a natural transformation with basic labels."""
        try:
            result = self.conn.execute(
                """
                MATCH (nt:Natural_Transformation)-[r:nat_trans_components]->(m:Morphism)
                OPTIONAL MATCH (m)-[:morphism_source]->(s:Object)
                OPTIONAL MATCH (m)-[:morphism_target]->(t:Object)
                WHERE nt.ID = $nt_id
                RETURN r.at_object_id, m.ID, m.name, s.ID, s.name, t.ID, t.name
                ORDER BY r.at_object_id
                """,
                {"nt_id": nt_id}
            )
            query_result = _get_query_result(result)
            components: List[Dict[str, Any]] = []
            while query_result.has_next():  # type: ignore
                row = query_result.get_next()  # type: ignore
                components.append({
                    "at_object_id": int(row[0]) if row[0] is not None else None,  # type: ignore
                    "morphism_id": int(row[1]),  # type: ignore
                    "morphism_name": str(row[2]),  # type: ignore
                    "source_object_id": int(row[3]) if row[3] is not None else None,  # type: ignore
                    "source_object": str(row[4]) if row[4] is not None else None,  # type: ignore
                    "target_object_id": int(row[5]) if row[5] is not None else None,  # type: ignore
                    "target_object": str(row[6]) if row[6] is not None else None,  # type: ignore
                })
            return components
        except Exception as e:
            logger.error(f"Failed to list NT components for nt={nt_id}: {e}")
            raise

    def validate_nt_structure(self, nt_id: int) -> List[str]:
        """Validate that components are well-typed relative to linked functors' domain/codomain."""
        errors: List[str] = []
        try:
            # Retrieve linked functors and categories
            result = self.conn.execute(
                """
                MATCH (nt:Natural_Transformation)
                OPTIONAL MATCH (nt)-[:nat_trans_source]->(sf:Functor)-[:functor_source]->(srcCat:Category)
                OPTIONAL MATCH (nt)-[:nat_trans_target]->(tf:Functor)-[:functor_target]->(tgtCat:Category)
                WHERE nt.ID = $nt_id
                RETURN srcCat.ID, tgtCat.ID
                """,
                {"nt_id": nt_id}
            )
            qr = _get_query_result(result)
            if not qr.has_next():  # type: ignore
                return ["Natural transformation not found"]
            row = qr.get_next()  # type: ignore
            src_cat_id = int(row[0]) if row[0] is not None else None
            tgt_cat_id = int(row[1]) if row[1] is not None else None
            if src_cat_id is None or tgt_cat_id is None:
                errors.append("Natural transformation must be linked to source and target functors with categories")
                return errors

            # Check every component typing with categories
            result2 = self.conn.execute(
                """
                MATCH (nt:Natural_Transformation)-[r:nat_trans_components]->(m:Morphism)
                WHERE nt.ID = $nt_id
                OPTIONAL MATCH (srcCat:Category)-[:category_objects]->(x:Object)
                WHERE srcCat.ID = $src_cat AND x.ID = r.at_object_id
                OPTIONAL MATCH (tgtCat:Category)-[:category_morphisms]->(m)
                WHERE tgtCat.ID = $tgt_cat
                RETURN r.at_object_id IS NULL AS badX, m.ID IS NULL AS badM, r.at_object_id
                """,
                {"nt_id": nt_id, "src_cat": src_cat_id, "tgt_cat": tgt_cat_id}
            )
            qr2 = _get_query_result(result2)
            while qr2.has_next():  # type: ignore
                r = qr2.get_next()  # type: ignore
                bad_x = bool(r[0])
                bad_m = bool(r[1])
                x_id = r[2]
                if bad_x:
                    errors.append(f"Component at object ID {x_id} is not in the source category")
                if bad_m:
                    errors.append(f"Component morphism for object ID {x_id} is not in the target category")
            return errors
        except Exception as e:
            logger.error(f"Failed to validate natural transformation {nt_id}: {e}")
            return [f"Validation failed: {e}"]

    def validate_naturality(self, nt_id: int) -> List[str]:
        """
        Best-effort naturality check for α: F ⇒ G.
        For each component α_X and each morphism f: X→Y in the source category C where α_Y and
        mappings F(f), G(f) exist, verify the square is well-typed:
        G(f) ∘ α_X and α_Y ∘ F(f) are both F(X) → G(Y). Equality is not provable in this schema;
        we report shape compatibility and missing data.
        """
        messages: List[str] = []
        try:
            # Get linked functors and their categories
            res = self.conn.execute(
                """
                MATCH (nt:Natural_Transformation)
                OPTIONAL MATCH (nt)-[:nat_trans_source]->(F:Functor)-[:functor_source]->(C:Category)
                OPTIONAL MATCH (nt)-[:nat_trans_source]->(F)-[:functor_target]->(D1:Category)
                OPTIONAL MATCH (nt)-[:nat_trans_target]->(G:Functor)-[:functor_target]->(D2:Category)
                WHERE nt.ID = $nt_id
                RETURN F.ID, G.ID, C.ID, D1.ID, D2.ID
                """,
                {"nt_id": nt_id}
            )
            qr = _get_query_result(res)
            if not qr.has_next():  # type: ignore
                return ["Natural transformation not found"]
            row = qr.get_next()  # type: ignore
            F_id = row[0]
            G_id = row[1]
            C_id = row[2]
            D1_id = row[3]
            D2_id = row[4]
            if F_id is None or G_id is None or C_id is None or D1_id is None or D2_id is None:
                return ["Missing linked functors or categories; cannot check naturality"]
            if int(D1_id) != int(D2_id):
                return ["Functor codomains differ; naturality undefined"]
            D_id = int(D1_id)
            F_id = int(F_id)
            G_id = int(G_id)
            C_id = int(C_id)

            # Build maps of α components by object ID
            comps = self.get_nt_components(nt_id)
            alpha_by_X = {c["at_object_id"]: c for c in comps if c.get("at_object_id") is not None}

            # Iterate morphisms f: X->Y in C
            res2 = self.conn.execute(
                """
                MATCH (c:Category)-[:category_morphisms]->(f:Morphism)
                WHERE c.ID = $cid
                OPTIONAL MATCH (f)-[:morphism_source]->(x:Object)
                OPTIONAL MATCH (f)-[:morphism_target]->(y:Object)
                RETURN f.ID, f.name, x.ID, x.name, y.ID, y.name
                """,
                {"cid": C_id}
            )
            qr2 = _get_query_result(res2)
            while qr2.has_next():  # type: ignore
                r = qr2.get_next()  # type: ignore
                f_id = int(r[0])
                f_name = str(r[1])
                X_id = r[2]
                X_name = r[3]
                Y_id = r[4]
                Y_name = r[5]
                if X_id is None or Y_id is None:
                    continue
                X_id = int(X_id)
                Y_id = int(Y_id)

                # Need α_X and α_Y
                aX = alpha_by_X.get(X_id)
                aY = alpha_by_X.get(Y_id)
                if aX is None or aY is None:
                    messages.append(f"Skipping f={f_name}: missing α_X or α_Y")
                    continue

                # Retrieve F(f) and G(f)
                resF = self.conn.execute(
                    """
                    MATCH (sm:Morphism)-[r:functor_morphism_map]->(tm:Morphism)
                    WHERE r.via_functor_id = $fid AND sm.ID = $smid
                    OPTIONAL MATCH (tm)-[:morphism_source]->(tms:Object)
                    OPTIONAL MATCH (tm)-[:morphism_target]->(tmt:Object)
                    RETURN tm.ID, tm.name, tms.name, tmt.name
                    """,
                    {"fid": F_id, "smid": f_id}
                )
                resG = self.conn.execute(
                    """
                    MATCH (sm:Morphism)-[r:functor_morphism_map]->(tm:Morphism)
                    WHERE r.via_functor_id = $gid AND sm.ID = $smid
                    OPTIONAL MATCH (tm)-[:morphism_source]->(tms:Object)
                    OPTIONAL MATCH (tm)-[:morphism_target]->(tmt:Object)
                    RETURN tm.ID, tm.name, tms.name, tmt.name
                    """,
                    {"gid": G_id, "smid": f_id}
                )
                qF = _get_query_result(resF)
                qG = _get_query_result(resG)
                if not qF.has_next() or not qG.has_next():  # type: ignore
                    messages.append(f"Skipping f={f_name}: missing F(f) or G(f) mapping")
                    continue
                Ff = qF.get_next()  # type: ignore
                Gf = qG.get_next()  # type: ignore
                Ff_src, Ff_tgt = Ff[2], Ff[3]
                Gf_src, Gf_tgt = Gf[2], Gf[3]

                # We can only check shape compatibility of the square
                # α_X: F(X) -> G(X)
                # α_Y: F(Y) -> G(Y)
                # G(f): G(X) -> G(Y)
                # F(f): F(X) -> F(Y)
                # For shape, need labels for α_X and α_Y
                aX_src = aX.get("source_object")
                aX_tgt = aX.get("target_object")
                aY_src = aY.get("source_object")
                aY_tgt = aY.get("target_object")
                shape_ok = (Gf_src == aX_tgt) and (Gf_tgt == aY_tgt) and (aY_src == Ff_tgt) and (aX_src == Ff_src)
                if shape_ok:
                    messages.append(f"Square for f={f_name} is well-typed (cannot prove equality)")
                else:
                    messages.append(f"Square for f={f_name} not well-typed: check component/mapping sources/targets")

            if not messages:
                messages.append("No morphisms found to check")
            return messages
        except Exception as e:
            logger.error(f"Naturality validation failed for nt={nt_id}: {e}")
            return [f"Validation failed: {e}"]

    def validate_category_structure(self, category_id: int) -> List[str]:
        """
        Validate the mathematical structure of a category.
        
        Args:
            category_id: Category ID to validate
            
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        try:
            # Check that all objects have identity morphisms
            result = self.conn.execute(
                """MATCH (c:Category)-[:category_objects]->(o:Object)
                   WHERE c.ID = $id
                   OPTIONAL MATCH (c)-[:category_morphisms]->(m:Morphism)
                   WHERE m.is_identity = true AND (m)-[:morphism_source]->(o) AND (m)-[:morphism_target]->(o)
                   RETURN o.name, m.ID""",
                {"id": category_id}
            )
            
            query_result = _get_query_result(result)
            while query_result.has_next():  # type: ignore
                row = query_result.get_next()  # type: ignore
                obj_name, morph_id = str(row[0]), row[1]  # type: ignore
                if morph_id is None:
                    errors.append(f"Object '{obj_name}' missing identity morphism")
            
            return errors
        except Exception as e:
            logger.error(f"Failed to validate category {category_id}: {e}")
            return [f"Validation failed: {e}"]
