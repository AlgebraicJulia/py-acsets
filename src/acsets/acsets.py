"""
In this module, we define schemas and acsets.
"""

import json
import os
from pathlib import Path
from typing import Any, Mapping, Optional, Union

from pydantic import BaseModel, Field, create_model, validator

HERE = Path(__file__).parent.resolve()
SCHEMAS_DIRECTORY = HERE.joinpath("schemas")
CATLAB_SCHEMAS_DIRECTORY = SCHEMAS_DIRECTORY.joinpath("catlab")
JSON_SCHEMAS_DIRECTORY = SCHEMAS_DIRECTORY.joinpath("jsonschema")


class HashableBaseModel(BaseModel):
    """An extension of BaseModel with an implementation of __hash__"""

    def __hash__(self):
        return hash((type(self),) + tuple(self.__dict__.values()))


class Ob(HashableBaseModel):
    """
    This class represents objects in schemas. In an acset, there is a table for
    each object in the schema.

    For instance, in the schema for graphs, there are two objects, `Ob("V")` and
    `Ob("E")` for the tables of vertices and edges, respectively
    """

    name: str = Field(..., description="The name of the object")
    title: Optional[str] = Field(description="The human-readable label for the object")
    description: Optional[str] = Field(description="A long-form description of the object")

    class Config:
        """pydantic config"""

        allow_mutation = False


class Hom(HashableBaseModel):
    """
    This class represents morphisms in schemas. In an acset, the table corresponding
    to an object `x` has a foreign key column for every morphism in the schema that
    has a domain (`dom`) of `x`, that has ids that reference rows in the table for
    the codomain (`codom`).

    For instance, in the schema for graphs, there are two morphisms `Hom("src", E, V)`
    and `Hom("tgt", E, V)`.
    """

    name: str = Field(description="The name of the morphism.")
    dom: str = Field(title="domain", description="The object of the domain.")
    codom: str = Field(title="codomain", description="The object of the codomain.")
    title: Optional[str] = Field(description="The human-readable label for the morphism")
    description: Optional[str] = Field(description="A long-form description of the morphism")

    @validator("dom", pre=True)
    def dom_string(cls, ob: Union[str, Ob]):
        """Validate domain inputs to string

        Args:
            ob: either a string of the object name or the object

        Returns:
            the string representation of the object
        """
        return ob.name if isinstance(ob, Ob) else ob

    @validator("codom", pre=True)
    def codom_string(cls, ob: Union[str, Ob]):
        """Validate codomain inputs to string

        Args:
            ob: either a string of the object name or the object

        Returns:
            the string representation of the object
        """
        return ob.name if isinstance(ob, Ob) else ob

    class Config:
        """pydandic config"""

        allow_mutation = False


def _look_up_type(s: str) -> type:
    """Look up the appropriate type from a string."""
    import builtins

    if hasattr(builtins, s):
        return getattr(builtins, s)

    raise NotImplementedError("non-builtin data types are not yet implemented")


class AttrType(HashableBaseModel):
    """
    This class represents attribute types in schemas. An attribute type is the "codomain"
    of attributes. In an acset, each attrtype is associated with a type. But in general,
    acsets are "polymorphic" over the types of their attributes.

    For instance, in the schema for Petri nets, there is an attribute type `Name
    = AttrType("Name")`. Typically, we might associate this to the type `str`,
    for single names. However, we might also want a Petri net where each
    transition, for instance, has a tuple of strings as its name.
    """

    name: str = Field(description="The name of the attribute type.")
    ty: type = Field(
        description="The type assigned to the attribute type. Use a string referring to the Python type"
    )
    title: Optional[str] = None
    description: Optional[str] = None

    @validator("ty", pre=True)
    def evaluate_type(cls, ty: Union[str, type]):
        """Populate the parsed value of the type."""
        return _look_up_type(ty) if isinstance(ty, str) else ty

    class Config:
        """pydandic config"""

        allow_mutation = False
        json_encoders = {
            type: lambda e: e.__qualname__,
        }


class Attr(HashableBaseModel):
    """
    This class represents attributes in schemas. An attribute corresponds to a
    non-foreign-key column in the table for its domain (`dom`).

    For instance, in the schema for Petri nets, we have `Attr("sname", Species, Name)`
    which is the attribute that stores the name of a species in a Petri net.
    """

    name: str = Field(title="name", description="The name of the attribute.")
    dom: str = Field(title="domain", description="The object in the domain.")
    codom: str = Field(title="codomain", description="The attribute type in the codomain")
    title: Optional[str] = None
    description: Optional[str] = None

    @validator("dom", pre=True)
    def dom_string(cls, ob: Union[str, Ob]):
        """Validate domain inputs to string

        Args:
            ob: either a string of the object name or the object

        Returns:
            the string representation of the object
        """
        return ob.name if isinstance(ob, Ob) else ob

    @validator("codom", pre=True)
    def codom_string(cls, at: Union[str, AttrType]):
        """Validate codomain inputs to string

        Args:
            ob: either a string of the AttrType name or the AttrType object

        Returns:
            the string representation of the AttrType
        """
        return at.name if isinstance(at, AttrType) else at

    class Config:
        """pydandic config"""

        allow_mutation = False
        json_encoders = {
            type: lambda e: e.__qualname__,
        }


Property = Union[Hom, Attr]


class VersionSpec(HashableBaseModel):
    """
    We use this version spec to version the serialization format, so that if we
    change the serialization format, we can migrate old serializations into new
    ones.
    """

    ACSetSchema: str
    Catlab: str

    class Config:
        """pydandic config"""

        allow_mutation = False


VERSION_SPEC = VersionSpec(ACSetSchema="0.0.1", Catlab="0.14.12")


class CatlabSchema(HashableBaseModel):
    """
    This schema is carefully laid out so that the JSON produced/consumed will be
    compatible with Catlab schemas. However, the user should not use this; instead
    the user should use the Schema class, which is below.
    """

    Ob: list[Ob]
    Hom: list[Hom]
    AttrType: list[AttrType]
    Attr: list[Attr]
    version: VersionSpec = Field(default=VERSION_SPEC)

    class Config:
        """pydandic config"""

        allow_mutation = False
        json_encoders = {
            type: lambda e: e.__qualname__,
        }


class Schema:
    """
    This is a schema for an acset. Every acset needs a schema, to restrict the allowed
    operations to ensure consistency.
    """

    name: str
    schema: CatlabSchema
    model: type[BaseModel]
    ob_models: dict[Ob, type[BaseModel]]

    def __init__(
        self,
        name: str,
        obs: list[Ob],
        homs: list[Hom],
        attrtypes: list[AttrType],
        attrs: list[Attr],
    ) -> None:
        """Initialize a schema object.

        Args:
            name: The name of the schema.
            obs: A list of of objects (`Ob`).
            homs: A list of morphisms (`Hom`).
            attrtypes: A list of attribute types (`AttrType`).
            attrs: A list of attributes (`Attr`).
        """
        self.name = name
        self.schema = CatlabSchema(
            version=VERSION_SPEC, Ob=obs, Hom=homs, AttrType=attrtypes, Attr=attrs
        )
        ob_models = {
            ob: create_model(
                ob.name,
                **{
                    prop.name: (Union[self.valtype(prop), None], Field(title=ob.title, description=ob.description))
                    for prop in self.props_outof(ob)
                },
            )
            for ob in obs
        }
        self.ob_models = ob_models
        self.model = create_model(
            self.name, **{ob.name: (list[ob_models[ob]], ...) for ob in self.obs}  # type: ignore
        )

    def valtype(self, prop: Property):
        """Resolve the python type of a given property

        Args:
            prop: Either a Hom  object or a AttrTyp object

        Returns:
            The Property value type
        """
        return int if isinstance(prop, Hom) else next(at for at in self.schema.AttrType if at.name == prop.codom).ty

    def valid_value(self, prop: Property, val):
        """Verify if a given value is valid for a given property

        Args:
            val (any): the value to check if valid
            prop: the Property object

        Returns:
            true if the value is valid for the given property, false otherwise
        """
        return isinstance(val, self.valtype(prop))

    @classmethod
    def from_catlab(cls, name: str, catlab_schema: CatlabSchema) -> "Schema":
        """Get a schema from a CatLab schema."""
        return cls(
            name=name,
            obs=catlab_schema.Ob,
            homs=catlab_schema.Hom,
            attrs=catlab_schema.Attr,
            attrtypes=catlab_schema.AttrType,
        )

    def make_schema(self, uri: Optional[str] = None):
        """Make a JSON schema dictionary object representing this schema.

        :param uri: The URI where the JSON file that corresponds to this schema lives
        :returns: A dictionary with the JSON schema inside it that can be written with
            :func:`json.dump`.
        """
        # TODO add description
        schema = self.model.schema()
        schema["$schema"] = "http://json-schema.org/draft-07/schema#"
        if uri is not None:
            schema["$id"] = uri
        return schema

    def write_schema(
        self,
        path,
        uri: Optional[str] = None,
    ) -> None:
        """Write a JSON schema to a file path."""
        schema = self.make_schema(uri=uri)
        schema_str = json.dumps(schema, indent=2, ensure_ascii=False, sort_keys=True)
        path = Path(path).expanduser().resolve()
        path.write_text(schema_str)

    @property
    def obs(self):
        """Get the objects of the schema

        Returns:
            A list of of `Ob`\s
        """
        return self.schema.Ob

    @property
    def homs(self):
        """Get the morphisms of the schema

        Returns:
            A list of of `Hom`\s
        """
        return self.schema.Hom

    @property
    def attrtypes(self):
        """Get the attribute types of the schema

        Returns:
            A list of of `AttrType`\s
        """
        return self.schema.AttrType

    @property
    def attrs(self):
        """Get the attributes of the schema

        Returns:
            A list of of `Attr`\s
        """
        return self.schema.Attr

    def props_outof(self, ob: Ob) -> list[Property]:
        """Get all of the properties with the domain of `ob` in the schema.

        Args:
            ob: An `Ob` object that is in the schema.

        Returns:
            A list of `Hom` and `Attr` objects where `ob` is in the domain of the properties.
        """
        return list(filter(lambda f: f.dom == ob.name, self.homs + self.attrs))

    def homs_outof(self, ob: Ob) -> list[Property]:
        """Get all of the morphisms that the given object `ob` maps to in the schema.

        Args:
            ob: An `Ob` object that is in the schema.

        Returns:
            A list of `Hom` objects where `ob` is in the domain of the morphism.
        """
        return list(filter(lambda f: f.dom == ob.name, self.homs))

    def attrs_outof(self, ob: Ob) -> list[Property]:
        """Get all of the attributes that the given object `ob` maps to in the schema.

        Args:
            ob: An `Ob` object that is in the schema.

        Returns:
            A list of `Attr` objects where `ob` is in the domain of the attribute.
        """
        return list(filter(lambda f: f.dom == ob.name, self.attrs))

    def from_string(self, s: str):
        """Get the appropriate object, morphism, attribute type, or attribute from the schema by name.

        Args:
            s: The name of the schema element that you want to retrieve.

        Returns:
            The `Ob`/`Hom`/`AttrType`/`Attr` object that has the name `s` or `None` if no names match.
        """
        x = next((x for x in self.obs if x.name == s), None)
        if x != None:
            return x
        x = next((x for x in self.homs if x.name == s), None)
        if x != None:
            return x
        x = next((x for x in self.attrtypes if x.name == s), None)
        if x != None:
            return x
        x = next((x for x in self.attrs if x.name == s), None)
        if x != None:
            return x


class ACSet:
    """
    An acset consists of a collection of tables, one for every object in the schema.

    The rows of the tables are called "parts", and the cells of the rows are called "subparts".

    One can get all of the parts corresponding to an object, add parts, get the subparts,
    and set the subparts. Removing parts is currently unsupported.
    """

    name: str
    schema: Schema
    _parts: dict[Ob, int]
    _subparts: dict[Property, dict[int, Any]]
    _name_to_ob: Mapping[str, Ob]

    def __init__(self, name: str, schema: Schema):
        """Initialize a new ACSet.

        Args:
            name: The name of the ACSset.
            schema: The schema of the ACSet.
        """
        self.name = name
        self.schema = schema
        self._parts = {ob: 0 for ob in schema.obs}
        self._subparts = {f: {} for f in schema.homs + schema.attrs}
        self._name_to_ob = {ob.name: ob for ob in schema.obs}

    @classmethod
    def from_obj(cls, *, name: str, obj) -> "ACSet":
        """Make an ACSet from a JSON object representing its schema.

        :param name: The name of the acset
        :param obj:
            A JSON object representing the acset, to be
            loaded through :class:`CatlabSchema`
        :returns: An acset object

        You can get an example ACSets schema definition from the testing suite
        and load it over the web with the following code:

        .. code-block:: python

            import requests

            url = "https://github.com/AlgebraicJulia/py-acsets/blob/main/tests/petri_schema.json"
            obj = requests.get(url).json()
            sir = ACSet.from_obj(name="petri", obj=obj)
            s, i, r = sir.add_parts("S", 3)
        """
        catlab_schema = CatlabSchema.parse_obj(obj)
        schema = Schema.from_catlab(name=name, catlab_schema=catlab_schema)
        return cls(name=name, schema=schema)

    @classmethod
    def from_file(cls, *, name: str, path: os.PathLike) -> "ACSet":
        """Make an ACSet from a file with the JSON representing its schema.

        :param name: The name of the acset
        :param path: A path to the file
        :returns: An acset object

        For example, if you have a JSON file representing the Petri Net
        schema, you can load it and start working with:

        .. code-block:: python

            path = ...
            sir = ACSet.from_file(name="petri", path=path)
            s, i, r = sir.add_parts("S", 3)
        """
        with open(path) as file:
            obj = json.load(file)
        return cls.from_obj(name=name, obj=obj)

    def add_parts(self, ob: Union[str, Ob], n: int) -> range:
        """Add `n` parts to an object in the ACset.

        Args:
            ob: The object in the ACSet to add parts to.
            n: The number of parts to be added.

        Returns:
            A range of the indexes of the new parts added to the object.
        """
        if isinstance(ob, str):
            ob = self._name_to_ob[ob]
        assert ob in self.schema.obs
        i = self._parts[ob]
        self._parts[ob] += n
        return range(i, i + n)

    def add_part(self, ob: Union[str, Ob]) -> int:
        """Add a single part to an object in the ACSet

        Args:
            ob: The object in the ACSet to add a part to.

        Returns:
            The index of the new part added to the object.
        """
        return self.add_parts(ob, 1)[0]

    def set_subpart(self, i: int, f: Property, x: Any):
        """Modify a morphism or attribute for a row in a table of the ACSet.

        Args:
            i: The row index for the property mapping to be added to.
            f: The `Hom` or `Attr` to modify.
            x: A valid type for the given `Hom` or `Attr` to set the value or `None` to delete the property.
        """
        if x is None:
            if self.has_subpart(i, f):
                del self._subparts[f][i]
        else:
            assert self.schema.valid_value(f, x)
            self._subparts[f][i] = x

    def has_subpart(self, i: int, f: Property):
        """Check if a property exists for a given row in a table of the ACSset.

        Args:
            i: The row index for the property mapping to be added to.
            f: The `Hom` or `Attr` to check for.

        Returns:
            `True` if the property `f` exists on row `i` or `False` if it doesn't.
        """
        return i in self._subparts[f].keys()

    def subpart(self, i: int, f: Property, oneindex=False):
        """Get the subpart of a part in an ACSet

        Args:
            oneindex (boolean): Whether or not to return the index starting at 1 or 0, default is `False` which is zero-indexed
            i: The part that you are indexing.
            f: The `Hom` or `Attr` to retrieve.

        Returns:
            The subpart of the ACset.
        """
        if oneindex and type(f) == Hom:
            return self._subparts[f][i] + 1
        else:
            return self._subparts[f][i]

    def nparts(self, ob: Ob) -> int:
        """Get the number of rows in a given table of the ACSet.

        Args:
            ob: The object in the ACSet.

        Returns:
            The number of rows in `ob`.
        """
        assert ob in self.schema.obs
        return self._parts[ob]

    def parts(self, ob: Ob) -> range:
        """Get all of the row indexes in a given table of the ACSet.

        Args:
            ob: The object in the ACSet.

        Returns:
            The range of all of the rows in `ob`.
        """
        return range(0, self.nparts(ob))

    def incident(self, x: Any, f: Property) -> list[int]:
        """Get all of the subparts incident to a part in the ACset.

        Args:
            x: The subpart to look for.
            f: The `Hom` or `Attr` mapping to search.

        Returns:
            A list indexes.
        """
        assert self.schema.valid_value(f, x)
        return list(
            filter(
                lambda i: self.subpart(i, f) == x,
                self.parts(Ob(name=f.dom, title=None, description=None)),
            )
        )

    def prop_dict(self, ob: Ob, i: int) -> dict[str, Any]:
        """Get a dictionary of all subparts for a given row in a table.

        Args:
            ob: The object in the ACSet to index.
            i: The row in `ob`.

        Returns:
            A dictionary mapping property name to the value
        """
        return {
            f.name: self.subpart(i, f, oneindex=True)
            for f in self.schema.props_outof(ob)
            if self.has_subpart(i, f)
        }

    def export_pydantic(self):
        """Serialize the ACSet to a pydantic model.

        Returns:
            The pydantic model of the serialized ACSet.
        """
        return self.schema.model(
            **{
                ob.name: [
                    self.schema.ob_models[ob](**self.prop_dict(ob, i)) for i in self.parts(ob)
                ]
                for ob in self.schema.obs
            }
        )

    @classmethod
    def import_pydantic(cls, name: str, schema: Schema, d: Any):
        """Deserialize a pydantic model to an ACSet with a given `Schema`

        Args:
            schema: The `Schema` of the ACSet that is defined by the pydantic model.
            d: The pydantic model object.

        Returns:
            The deserialized ACSet object.
        """
        acs = cls(name, schema)

        assert type(d) == schema.model

        for ob in schema.obs:
            for props in d.__dict__[ob.name]:
                i = acs.add_part(ob)
                for f in schema.homs_outof(ob):
                    acs.set_subpart(i, f, props.__dict__[f.name] - 1)
                for f in schema.attrs_outof(ob):
                    acs.set_subpart(i, f, props.__dict__[f.name])

        return acs

    def to_json_obj(self):
        """Serialize the ACSet to a JSON object.

        Returns:
            The JSON object of the serialized ACSet.
        """
        return self.export_pydantic().dict()

    def to_json_file(self, fname, *args, **kwargs):
        """Serialize the ACSet to a JSON file.

        Args:
            fname: The file name to write the JSON to.
        """
        with open(fname, "w") as fh:
            fh.write(self.to_json_str(*args, **kwargs))

    def to_json_str(self, *args, **kwargs):
        """Serialize the ACSet to a JSON string.

        Returns:
            The JSON string of the serialized ACSet.
        """
        return self.export_pydantic().json(*args, **kwargs)

    @classmethod
    def read_json(cls, name: str, schema: Schema, s: str):
        """Deserialize a JSON string to an ACSet with a given `Schema`.

        Args:
            name: The name of the ACSset.
            schema: The `Schema` of the ACSet that is defined in the given JSON.
            s: The JSON string

        Returns:
            The deserialized ACSet object.
        """
        return cls.import_pydantic(name, schema, schema.model.parse_obj(json.loads(s)))
