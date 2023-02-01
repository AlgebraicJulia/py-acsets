import json
from typing import Union

from pydantic import BaseModel, create_model


class Ob(HashableBaseModel):
    """
    This class represents objects in schemas. In an acset, there is a table for
    each object in the schema.

    For instance, in the schema for graphs, there are two objects, `Ob("V")` and
    `Ob("E")` for the tables of vertices and edges, respectively
    """
    name: str

    def __init__(self, name: str) -> None:
        super(Ob, self).__init__(name=name)

    class Config:
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
    name: str
    dom: Ob
    codom: Ob

    def __init__(self, name: str, dom: Ob, codom: Ob) -> None:
        super(Hom, self).__init__(name=name, dom=dom, codom=codom)

    def valid_value(self, x: any) -> bool:
        return type(x) == int

    def valtype(self) -> type:
        return int

    class Config:
        allow_mutation = False


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
    name: str

    def __init__(self, name: str) -> None:
        super(AttrType, self).__init__(name=name)

    class Config:
        allow_mutation = False


class Attr(HashableBaseModel):
    """
    This class represents attributes in schemas. An attribute corresponds to a
    non-foreign-key column in the table for its domain (`dom`).

    For instance, in the schema for Petri nets, we have `Attr("sname", Species, Name)`
    which is the attribute that stores the name of a species in a Petri net.
    """
    name: str
    dom: Ob
    codom: AttrType

    def __init__(self, name: str, dom: Ob, codom: AttrType) -> None:
        super(Attr, self).__init__(name=name, dom=dom, codom=codom)

    def valid_value(self, x: any) -> bool:
        return type(x) == self.codom.ty

    def valtype(self) -> type:
        return self.codom.ty

    class Config:
        allow_mutation = False


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
        allow_mutation = False


VERSION_SPEC = VersionSpec(ACSetSchema="0.0.1", Catlab="0.14.12")


class CatlabSchema(HashableBaseModel):
    """
    This schema is carefully laid out so that the JSON produced/consumed will be
    compatible with Catlab schemas. However, the user should not use this; instead
    the user should use the Schema class, which is below.
    """
    version: VersionSpec
    obs: list[Ob]
    homs: list[Hom]
    attrtypes: list[AttrType]
    attrs: list[Attr]

    def __init__(
        self,
        name: str,
        obs: list[Ob],
        homs: list[Hom],
        attrtypes: list[AttrType],
        attrs: list[Attr],
    ) -> None:
        super(CatlabSchema, self).__init__(
            version=VERSION_SPEC, obs=obs, homs=homs, attrtypes=attrtypes, attrs=attrs
        )

    class Config:
        allow_mutation = False


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
        self.name = name
        self.schema = CatlabSchema(VERSION_SPEC, obs, homs, attrtypes, attrs)
        self.ob_models = {
            ob: create_model(
                ob.name,
                **{prop.name: (Union[prop.valtype(), None], None) for prop in self.props_outof(ob)},
            )
            for ob in obs
        }
        self.model = create_model(
            self.name, **{ob.name: (list[self.ob_models[ob]], ...) for ob in self.obs}
        )

    @property
    def obs(self):
        return self.schema.obs

    @property
    def homs(self):
        return self.schema.homs

    @property
    def attrtypes(self):
        return self.schema.attrtypes

    @property
    def attrs(self):
        return self.schema.attrs

    def props_outof(self, ob: Ob) -> list[Property]:
        return filter(lambda f: f.dom == ob, self.homs + self.attrs)

    def homs_outof(self, ob: Ob) -> list[Property]:
        return filter(lambda f: f.dom == ob, self.homs)

    def attrs_outof(self, ob: Ob) -> list[Property]:
        return filter(lambda f: f.dom == ob, self.attrs)

    def from_string(self, s: str):
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
    _subparts: dict[Property, dict[int, any]]

    def __init__(self, name: str, schema: Schema):
        self.name = name
        self.schema = schema
        self._parts = {ob: 0 for ob in schema.obs}
        self._subparts = {f: {} for f in schema.homs + schema.attrs}

    def add_parts(self, ob: Ob, n: int) -> range:
        assert ob in self.schema.obs
        i = self._parts[ob]
        self._parts[ob] += n
        return range(i, i + n)

    def add_part(self, ob: Ob) -> int:
        return self.add_parts(ob, 1)[0]

    def set_subpart(self, i: int, f: Property, x: any):
        if x == None:
            if self.has_subpart(i, f):
                del self._subparts[f][i]
        else:
            assert f.valid_value(x)
            self._subparts[f][i] = x

    def has_subpart(self, i: int, f: Property):
        return i in self._subparts[f].keys()

    def subpart(self, i: int, f: Property, oneindex=False):
        if oneindex and type(f) == Hom:
            return self._subparts[f][i] + 1
        else:
            return self._subparts[f][i]

    def nparts(self, ob: Ob) -> int:
        assert ob in self.schema.obs
        return self._parts[ob]

    def parts(self, ob: Ob) -> range:
        return range(0, self.nparts(ob))

    def incident(self, x: any, f: Property) -> list[int]:
        assert f.valid_value(x)
        return filter(lambda i: self.subpart(i, f) == x, self.parts(f.dom))

    def prop_dict(self, ob: Ob, i: int) -> dict[str, any]:
        return {
            f.name: self.subpart(i, f, oneindex=True)
            for f in self.schema.props_outof(ob)
            if self.has_subpart(i, f)
        }

    def export_pydantic(self):
        return self.schema.model(
            **{
                ob.name: [
                    self.schema.ob_models[ob](**self.prop_dict(ob, i)) for i in self.parts(ob)
                ]
                for ob in self.schema.obs
            }
        )

    @classmethod
    def import_pydantic(cls, schema: Schema, d: any):
        acs = cls(schema)

        assert type(d) == schema.model

        for ob in schema.obs:
            for props in d.__dict__[ob.name]:
                i = acs.add_part(ob)
                for f in schema.homs_outof(ob):
                    acs.set_subpart(i, f, props.__dict__[f.name] - 1)
                for f in schema.attrs_outof(ob):
                    acs.set_subpart(i, f, props.__dict__[f.name])

        return acs

    def write_json(self):
        return self.export_pydantic().json()

    @classmethod
    def read_json(cls, schema: Schema, s: str):
        return cls.import_pydantic(schema, schema.model.parse_obj(json.loads(s)))
