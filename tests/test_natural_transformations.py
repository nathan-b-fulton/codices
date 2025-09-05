import pytest

from kuzu_DAL import CategoryDAL


class TestNaturalTransformationsDAL:
    def test_nt_linkage_and_components_and_structure(self, dal: CategoryDAL):
        # Build domain and codomain
        c = dal.create_category("C", "domain")
        d = dal.create_category("D", "codomain")
        # Objects in C
        X = dal.create_object("X", c)
        Y = dal.create_object("Y", c)
        # Objects in D (images)
        FX = dal.create_object("F(X)", d)
        FY = dal.create_object("F(Y)", d)
        GX = dal.create_object("G(X)", d)
        GY = dal.create_object("G(Y)", d)
        # Morphism in C
        f = dal.create_morphism("f", X, Y, c, "f: X->Y")
        # Morphisms in D for F and G
        Ff = dal.create_morphism("F(f)", FX, FY, d)
        Gf = dal.create_morphism("G(f)", GX, GY, d)
        # Components in D
        aX = dal.create_morphism("aX", FX, GX, d)
        aY = dal.create_morphism("aY", FY, GY, d)

        # Functors F,G: C->D
        F_id = dal.create_functor("F", c, d)
        G_id = dal.create_functor("G", c, d)

        # Map morphisms under F and G
        dal.add_functor_morphism_mapping(F_id, f, Ff)
        dal.add_functor_morphism_mapping(G_id, f, Gf)

        # Create α: F => G and add components
        nt_id = dal.create_natural_transformation("alpha", F_id, G_id, "alpha: F=>G")
        # Add components α_X and α_Y
        dal.add_nt_component(nt_id, X, aX)
        dal.add_nt_component(nt_id, Y, aY)

        # Linkage present in listing
        nts = dal.list_natural_transformations()
        created = next(nt for nt in nts if nt["ID"] == nt_id)
        assert created["source_functor_id"] == F_id
        assert created["target_functor_id"] == G_id

        # Components list
        comps = dal.get_nt_components(nt_id)
        at_objs = {c["at_object_id"] for c in comps}
        assert X in at_objs and Y in at_objs

        # Structure validation
        errs = dal.validate_nt_structure(nt_id)
        assert errs == []

        # Naturality validation (shape)
        msgs = dal.validate_naturality(nt_id)
        matching = [m for m in msgs if "Square for f" in m]
        assert any("well-typed" in m for m in matching), msgs

    def test_naturality_missing_mapping_report(self, dal: CategoryDAL):
        # Build domain and codomain
        c = dal.create_category("C2", "domain2")
        d = dal.create_category("D2", "codomain2")
        # Objects C
        X = dal.create_object("X", c)
        Y = dal.create_object("Y", c)
        # Objects D
        FX = dal.create_object("FX", d)
        FY = dal.create_object("FY", d)
        GX = dal.create_object("GX", d)
        GY = dal.create_object("GY", d)
        # Morphism f
        f = dal.create_morphism("f", X, Y, c)
        # Morphisms in D
        Ff = dal.create_morphism("Ff", FX, FY, d)
        Gf = dal.create_morphism("Gf", GX, GY, d)
        aX = dal.create_morphism("aX", FX, GX, d)
        aY = dal.create_morphism("aY", FY, GY, d)

        # Functors
        F_id = dal.create_functor("F2", c, d)
        G_id = dal.create_functor("G2", c, d)
        # Only map under F
        dal.add_functor_morphism_mapping(F_id, f, Ff)

        nt_id = dal.create_natural_transformation("alpha2", F_id, G_id)
        dal.add_nt_component(nt_id, X, aX)
        dal.add_nt_component(nt_id, Y, aY)

        msgs = dal.validate_naturality(nt_id)
        assert any("missing F(f) or G(f)" in m for m in msgs)
