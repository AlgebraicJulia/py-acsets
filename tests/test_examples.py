"""Test that the examples are valid."""

import json
import unittest

import jsonschema
from acsets.schemas import EXAMPLES, CATLAB, JSONSCHEMA


class TestExamples(unittest.TestCase):
    """Test all examples are valid wrt their related schema."""

    def test_examples_valid(self):
        """Test examples."""
        for example in EXAMPLES.glob("*.json"):
            with self.subTest(example=example.name):
                jsonschema_path = JSONSCHEMA.joinpath(example.name)
                self.assertTrue(
                    jsonschema_path.is_file(), msg="No corresponding JSON schema for example"
                )
                jsonschema_obj = json.loads(jsonschema_path.read_text())
                example_obj = json.loads(example.read_text())
                jsonschema.validate(instance=example_obj, schema=jsonschema_obj)
