#!/usr/bin/env python3
"""
Demo data creation script for Codices application.
Creates sample category theory data for testing and demonstration.
"""

from kuzu_DAL import CategoryDAL, initialize_schema
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_demo_data():
    """Create comprehensive demo data for the application."""
    
    # Initialize database
    print("Initializing database...")
    initialize_schema()
    dal = CategoryDAL()
    
    # Create categories
    print("Creating categories...")
    sets_id = dal.create_category("Sets", "Category of sets and functions")
    groups_id = dal.create_category("Groups", "Category of groups and group homomorphisms")
    rings_id = dal.create_category("Rings", "Category of rings and ring homomorphisms")
    
    # Create objects in Sets category
    print("Creating objects in Sets category...")
    empty_set = dal.create_object("∅", sets_id, "Empty set")
    finite_set_a = dal.create_object("A", sets_id, "Finite set A = {1, 2, 3}")
    finite_set_b = dal.create_object("B", sets_id, "Finite set B = {a, b}")
    natural_numbers = dal.create_object("ℕ", sets_id, "Natural numbers")
    
    # Create morphisms in Sets category
    print("Creating morphisms in Sets category...")
    inclusion = dal.create_morphism("ι", empty_set, finite_set_a, sets_id, "Inclusion of empty set")
    function_f = dal.create_morphism("f", finite_set_a, finite_set_b, sets_id, "Function f: A → B")
    embedding = dal.create_morphism("emb", finite_set_a, natural_numbers, sets_id, "Embedding A ↪ ℕ")
    
    # Create objects in Groups category
    print("Creating objects in Groups category...")
    trivial_group = dal.create_object("1", groups_id, "Trivial group")
    cyclic_3 = dal.create_object("ℤ₃", groups_id, "Cyclic group of order 3")
    symmetric_3 = dal.create_object("S₃", groups_id, "Symmetric group on 3 elements")
    integers = dal.create_object("ℤ", groups_id, "Additive group of integers")
    
    # Create morphisms in Groups category
    print("Creating morphisms in Groups category...")
    trivial_map = dal.create_morphism("0", trivial_group, cyclic_3, groups_id, "Trivial homomorphism")
    inclusion_z3 = dal.create_morphism("inc", cyclic_3, symmetric_3, groups_id, "Inclusion ℤ₃ ↪ S₃")
    quotient = dal.create_morphism("π", integers, cyclic_3, groups_id, "Quotient map ℤ → ℤ₃")
    
    # Create objects in Rings category
    print("Creating objects in Rings category...")
    zero_ring = dal.create_object("0", rings_id, "Zero ring")
    integers_ring = dal.create_object("ℤ", rings_id, "Ring of integers")
    rationals = dal.create_object("ℚ", rings_id, "Field of rational numbers")
    
    # Create morphisms in Rings category
    print("Creating morphisms in Rings category...")
    zero_map = dal.create_morphism("0", zero_ring, integers_ring, rings_id, "Zero homomorphism")
    inclusion_q = dal.create_morphism("ι", integers_ring, rationals, rings_id, "Inclusion ℤ ↪ ℚ")
    
    # Create functors between categories
    print("Creating functors...")
    forgetful_groups = dal.create_functor("U", groups_id, sets_id, "Forgetful functor Groups → Sets")
    forgetful_rings = dal.create_functor("U", rings_id, groups_id, "Forgetful functor Rings → Groups (multiplicative)")
    
    # Create natural transformation
    print("Creating natural transformations...")
    nat_trans = dal.create_natural_transformation("η", forgetful_groups, forgetful_groups, "Identity natural transformation")
    
    print("\nDemo data creation complete!")
    print(f"Created:")
    print(f"  - 3 categories")
    print(f"  - {len(dal.get_objects_in_category(sets_id)) + len(dal.get_objects_in_category(groups_id)) + len(dal.get_objects_in_category(rings_id))} objects")
    print(f"  - {len(dal.get_morphisms_in_category(sets_id)) + len(dal.get_morphisms_in_category(groups_id)) + len(dal.get_morphisms_in_category(rings_id))} morphisms")
    print(f"  - 2 functors")
    print(f"  - 1 natural transformation")
    print("\nYou can now run: streamlit run codices.py")


if __name__ == "__main__":
    create_demo_data()
