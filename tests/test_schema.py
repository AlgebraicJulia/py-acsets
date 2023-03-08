"""Tests for schema."""

import json
import unittest
from pathlib import Path

from acsets import CatlabSchema
from acsets.petris import SchPetri

HERE = Path(__file__).parent.resolve()
PETRI_SCHEMA_PATH = HERE.joinpath("petri_schema.json")


class TestSchema(unittest.TestCase):
    """Tests for the schema."""

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
