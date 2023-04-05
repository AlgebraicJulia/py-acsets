"""Tests for schema."""

import json
import unittest
from pathlib import Path

from acsets import ACSet, Attr, AttrType, CatlabSchema, Hom, Ob, Schema
from acsets.petris import SchPetri

HERE = Path(__file__).parent.resolve()
PETRI_SCHEMA_PATH = HERE.joinpath("petri_schema.json")


class TestSchema(unittest.TestCase):
    """Tests for the schema."""

    def test_hom(self):
        """Test transforming Ob objects when instantiating a Hom."""
        ob_transition = Ob(name="T", title="Transition")
        ob_input = Ob(name="I", title="Input")
        hom_it = Hom(
            name="it", dom=ob_input, codom=ob_transition, title="Input transition morphism"
        )
        self.assertEqual(ob_input.name, hom_it.dom)
        self.assertEqual(ob_transition.name, hom_it.codom)

    def test_attr(self):
        """Test transforming Ob objects when instantiating an Attr."""
        attr_type_name = AttrType(name="Name", ty=str, title="Name")
        ob_species = Ob(name="S", title="Species")
        attr_sname = Attr(
            name="sname",
            dom=ob_species,
            codom=attr_type_name,
            title="Species name",
            description="An attribute representing the name of a species.",
        )
        self.assertEqual(ob_species.name, attr_sname.dom)

    def test_loading(self):
        """Test loading a schema from a JSON file."""
        schema = CatlabSchema.parse_file(PETRI_SCHEMA_PATH)
        self.assertEqual(
            SchPetri.schema.json(),
            schema.json(),
        )

    def test_writing(self):
        """Test writing a schema works as expected."""
        expected = json.loads(PETRI_SCHEMA_PATH.read_text())
        actual = json.loads(SchPetri.schema.json())
        self.assertEqual(expected, actual)

    def test_round_trip(self):
        """Test writing, reading, then instantiating."""
        obj = json.loads(SchPetri.schema.json())
        sir = ACSet.from_obj(name="petri", obj=obj)
        s, i, r = sir.add_parts("S", 3)
        self.assertIsInstance(s, int)
