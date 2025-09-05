import pytest

from kuzu_DAL import CategoryDAL
from visualization import get_visualization_data


class TestNTVisualizationDetail:
    def test_nt_detail_components_and_overlay(self, dal: CategoryDAL):
        # Build minimal scenario
        c = dal.create_category("Cnv", "domain")
        d = dal.create_category("Dnv", "codomain")
        X = dal.create_object("X", c)
        Y = dal.create_object("Y", c)
        FX = dal.create_object("FX", d)
        FY = dal.create_object("FY", d)
        GX = dal.create_object("GX", d)
        GY = dal.create_object("GY", d)
        f = dal.create_morphism("f", X, Y, c)
        Ff = dal.create_morphism("Ff", FX, FY, d)
        Gf = dal.create_morphism("Gf", GX, GY, d)
        aX = dal.create_morphism("aX", FX, GX, d)
        aY = dal.create_morphism("aY", FY, GY, d)

        F_id = dal.create_functor("Fnt", c, d)
        G_id = dal.create_functor("Gnt", c, d)
        dal.add_functor_morphism_mapping(F_id, f, Ff)
        dal.add_functor_morphism_mapping(G_id, f, Gf)

        nt_id = dal.create_natural_transformation("alphaNT", F_id, G_id)
        dal.add_nt_component(nt_id, X, aX)
        dal.add_nt_component(nt_id, Y, aY)

        # Components edges
        viz = get_visualization_data(dal, "Natural Transformation", None, "nt-detail")
        alpha_titles = [e.get("title", "") for e in viz["edges"] if 'α_X' in e.get('title', '')]
        assert any("aX" in t or "aY" in t for t in alpha_titles)

        # Overlay edges F(f) and G(f)
        overlay = {"nt_id": nt_id, "morphism_id": f}
        viz_overlay = get_visualization_data(dal, "Natural Transformation", None, "nt-detail", overlay=overlay)
        labels = [e.get("label", "") for e in viz_overlay["edges"]]
        assert "F(f)" in labels
        assert "G(f)" in labels
