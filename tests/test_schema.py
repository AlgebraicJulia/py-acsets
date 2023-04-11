"""Tests for schema."""

import json
import tempfile
import unittest
from pathlib import Path

from acsets import CATLAB_SCHEMAS_DIRECTORY, ACSet, Attr, AttrType, CatlabSchema, Hom, Ob, petris

TESTING_SCHEMA = petris.SchPropertyLabelledReactionNet
PETRI_SCHEMA_PATH = CATLAB_SCHEMAS_DIRECTORY.joinpath("{}.json".format(TESTING_SCHEMA.name))


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
            TESTING_SCHEMA.schema.json(),
            schema.json(),
        )

    def test_writing(self):
        """Test writing a schema works as expected."""
        expected = json.loads(PETRI_SCHEMA_PATH.read_text())
        actual = json.loads(TESTING_SCHEMA.schema.json())
        self.assertEqual(expected, actual)

    def test_round_trip(self):
        """Test writing, reading, then instantiating."""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory).resolve().joinpath("petri.json")
            path.write_text(TESTING_SCHEMA.schema.json())
            sir = ACSet.from_file(name="petri", path=path)
            s, i, r = sir.add_parts("S", 3)
            self.assertIsInstance(s, int)
