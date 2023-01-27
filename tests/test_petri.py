# -*- coding: utf-8 -*-

"""Test serialization."""

import unittest

from acsets import petris


class TestSerialization(unittest.TestCase):
    """A test case for testing serialization."""

    def test_serialization(self):
        """Test serialization round trip."""
        sir = petris.Petri()
        s, i, r = sir.add_species(3)
        inf, rec = sir.add_transitions([([s, i], [i, i]), ([i], [r])])

        pd_sir = sir.export_pydantic()
        serialized = sir.write_json()
        deserialized = petris.Petri.import_pydantic(petris.SchPetri, pd_sir)
        pd_sir2 = deserialized.export_pydantic()
        reserialized = deserialized.write_json()
        deserialized2 = petris.Petri.read_json(petris.SchPetri, reserialized)
        rereserialized = deserialized2.write_json()

        self.assertEqual(pd_sir2, pd_sir)
        self.assertEqual(serialized, reserialized)
        self.assertEqual(reserialized, rereserialized)
