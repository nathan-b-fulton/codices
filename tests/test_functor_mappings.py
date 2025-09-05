import pytest

from kuzu_DAL import CategoryDAL, initialize_schema
from visualization import get_visualization_data


class TestFunctorMappings:
    def test_object_mappings_add_list_remove(self, dal: CategoryDAL):
        # Categories and objects
        c = dal.create_category("C", "source")
        d = dal.create_category("D", "target")
        x = dal.create_object("X", c, "X in C")
        y = dal.create_object("Y", c, "Y in C")
        fx = dal.create_object("FX", d, "F(X) in D")
        fy = dal.create_object("FY", d, "F(Y) in D")

        # Functor
        fid = dal.create_functor("F", c, d, "F: C->D")

        # Add mapping X->FX
        ok = dal.add_functor_object_mapping(fid, x, fx)
        assert ok is True
        maps = dal.get_functor_object_mappings(fid)
        assert len(maps) == 1
        assert maps[0]["source_object"] == "X"
        assert maps[0]["target_object"] == "FX"

        # Attempt invalid mapping: object not in target category
        other_cat = dal.create_category("E", "else")
        ez = dal.create_object("Z", other_cat, "Z in E")
        # Should not create due to typing; list remains unchanged
        dal.add_functor_object_mapping(fid, x, ez)
        maps_after = dal.get_functor_object_mappings(fid)
        assert len(maps_after) == 1

        # Remove mapping
        ok = dal.remove_functor_object_mapping(fid, x)
        assert ok is True
        maps_final = dal.get_functor_object_mappings(fid)
        assert maps_final == []

    def test_morphism_mappings_add_list_remove(self, dal: CategoryDAL):
        # Categories, objects, morphisms
        c = dal.create_category("C2", "source2")
        d = dal.create_category("D2", "target2")
        x = dal.create_object("X", c)
        y = dal.create_object("Y", c)
        fx = dal.create_object("FX", d)
        fy = dal.create_object("FY", d)
        f = dal.create_morphism("f", x, y, c, "f: X->Y")
        ff = dal.create_morphism("Ff", fx, fy, d, "F(f): FX->FY")

        # Functor
        fid = dal.create_functor("F2", c, d, "F2: C2->D2")

        # Add mapping f->Ff
        ok = dal.add_functor_morphism_mapping(fid, f, ff)
        assert ok is True
        mm = dal.get_functor_morphism_mappings(fid)
        assert len(mm) == 1
        m = mm[0]
        assert m["source_morphism"] == "f"
        assert m["target_morphism"] == "Ff"
        assert m["source_from"] == "X" and m["source_to"] == "Y"
        assert m["target_from"] == "FX" and m["target_to"] == "FY"

        # Remove
        ok = dal.remove_functor_morphism_mapping(fid, f)
        assert ok is True
        assert dal.get_functor_morphism_mappings(fid) == []
