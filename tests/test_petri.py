# -*- coding: utf-8 -*-

"""Test serialization."""

import importlib
import os
import tempfile
import unittest

from acsets import ACSet, Attr, AttrType, Hom, Ob, mira, petris

PYDANTIC_1 = importlib.metadata.version("pydantic").startswith("1.")


class TestSerialization(unittest.TestCase):
    """A test case for testing serialization."""

    def test_metadata(self):
        """Test metadata availability."""
        schema = petris.SchPropertyLabelledReactionNet
        for elements in [
            schema.schema.Ob,
            schema.schema.Hom,
            schema.schema.Attr,
            schema.schema.AttrType,
        ]:
            for elements in elements:
                self.assertIsNotNone(elements.name)
                self.assertIsNotNone(elements.title)

    def test_serialization(self):
        """Test serialization round trip."""
        for cls_name, cls, schema in [
            ("Petri", petris.Petri, petris.SchPropertyLabelledReactionNet),
            ("MiraNet", mira.MiraNet, mira.SchMira),
        ]:
            sir = cls()
            self.assertIsInstance(sir, petris.Petri)
            s, i, r = sir.add_species(3)
            inf, rec = sir.add_transitions([([s, i], [i, i]), ([i], [r])])

            pd_sir = sir.export_pydantic()
            self.assertEqual(pd_sir.S[1].id, 2)
            serialized = sir.to_json_str()
            deserialized = cls.import_pydantic(cls_name, schema, pd_sir)
            pd_sir2 = deserialized.export_pydantic()
            reserialized = deserialized.to_json_str()
            deserialized2 = cls.read_json(cls_name, schema, reserialized)
            rereserialized = deserialized2.to_json_str()

            self.assertEqual(pd_sir2, pd_sir)
            self.assertEqual(serialized, reserialized)
            self.assertEqual(reserialized, rereserialized)

    def test_ob(self):
        """Test instantiating a hom."""
        ob1, ob2 = Ob(name="ob1"), Ob(name="ob2")
        hom1 = Hom(name="hom1", dom=ob1, codom=ob2)
        self.assertIsInstance(hom1.dom, str)
        self.assertIsInstance(hom1.codom, str)

    @unittest.skipUnless(
        PYDANTIC_1, reason="This functionality can not be made cross-compatible AFAIK"
    )
    def test_write_schema(self):
        """Test writing the schema does not error."""
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "petri.json")
            petris.SchPropertyLabelledReactionNet.write_schema(path)
