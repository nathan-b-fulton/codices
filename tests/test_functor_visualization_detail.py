import pytest

from kuzu_DAL import CategoryDAL
from visualization import get_visualization_data


class TestFunctorVisualizationDetail:
    def test_functor_detail_shows_object_mapping_edges(self, dal: CategoryDAL):
        # Setup categories and objects
        c = dal.create_category("Cviz", "source")
        d = dal.create_category("Dviz", "target")
        x = dal.create_object("X", c)
        y = dal.create_object("Y", c)
        fx = dal.create_object("FX", d)
        fy = dal.create_object("FY", d)

        fid = dal.create_functor("Fviz", c, d)
        dal.add_functor_object_mapping(fid, x, fx)

        viz = get_visualization_data(dal, "Functor", None, "functor-detail")
        # Should include mapping edge titled with functor name and mapping
        titles = [e.get("title", "") for e in viz["edges"]]
        assert any("Fviz:" in t and "X" in t and "FX" in t for t in titles)

    def test_functor_edge_tooltip_counts(self, dal: CategoryDAL):
        # Setup minimal functor with one object mapping
        c = dal.create_category("Cs", "source")
        d = dal.create_category("Ds", "target")
        x = dal.create_object("X", c)
        fx = dal.create_object("FX", d)
        fid = dal.create_functor("Fs", c, d)
        dal.add_functor_object_mapping(fid, x, fx)

        viz = get_visualization_data(dal, "Functor", None, "standard")
        # Find functor edge tooltip and assert counts mention
        titles = [e.get("title", "") for e in viz["edges"]]
        assert any("Objects mapped:" in t for t in titles)
