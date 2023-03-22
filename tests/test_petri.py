# -*- coding: utf-8 -*-

"""Test serialization."""

import unittest

from acsets import Hom, Ob, petris


class TestSerialization(unittest.TestCase):
    """A test case for testing serialization."""

    def test_serialization(self):
        """Test serialization round trip."""
        sir = petris.Petri()
        s, i, r = sir.add_species(3)
        inf, rec = sir.add_transitions([([s, i], [i, i]), ([i], [r])])

        pd_sir = sir.export_pydantic()
        serialized = sir.to_json_str()
        deserialized = petris.Petri.import_pydantic("Petri", petris.SchPetri, pd_sir)
        pd_sir2 = deserialized.export_pydantic()
        reserialized = deserialized.to_json_str()
        deserialized2 = petris.Petri.read_json("Petri", petris.SchPetri, reserialized)
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
