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

        serialized = sir.write_json()
        deserialized = petris.Petri.read_json(petris.SchPetri, serialized)
        reserialized = deserialized.write_json()

        self.assertEqual(serialized, reserialized)
