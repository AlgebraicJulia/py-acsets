"""This script turns all the catlab schemata into json schemata"""

from pathlib import Path
from acsets import (
    CATLAB_SCHEMAS_DIRECTORY,
    ACSet,
    Attr,
    AttrType,
    CatlabSchema,
    Hom,
    Ob,
    petris,
    Schema,
)

HERE = Path(__file__).parent.resolve()
CATLAB = HERE.joinpath("catlab")
JSONSCHEMA = HERE.joinpath("jsonschema")


def main():
    """Convert any Catlab schemas into JSON schemas"""
    for catlab_path in CATLAB.glob("*.json"):
        jsonschema_path = JSONSCHEMA.joinpath(catlab_path.name)
        if jsonschema_path.is_file():
            continue
        print(f"Parsing Catlab Schema from {catlab_path}")
        catlab_schema = CatlabSchema.parse_file(catlab_path)
        print("Getting Schema from Catlab schema")
        schema = Schema.from_catlab(catlab_path.name, catlab_schema)
        schema.write_schema(
            jsonschema_path,
            uri="https://raw.githubusercontent.com/AlgebraicJulia/py-acsets/main/src/acsets/jsonschema/{}".format(
                Path(jsonschema_path).relative_to(HERE)
            ),
        )


if __name__ == "__main__":
    main()
