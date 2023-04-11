"""
In this model, we define a schema for petri nets, and then a subclass of acset
with some convenience methods.
"""
from pathlib import Path

from acsets import (
    CATLAB_SCHEMAS_DIRECTORY,
    HERE,
    JSON_SCHEMAS_DIRECTORY,
    ACSet,
    Attr,
    AttrType,
    Hom,
    Ob,
    Schema,
)

Species = Ob(name="S", title="Species")
Transition = Ob(name="T", title="Transition")
Input = Ob(name="I", title="Input")
Output = Ob(name="O", title="Output")

hom_it = Hom(name="it", dom=Input, codom=Transition, title="Input transition morphism")
hom_is = Hom(name="is", dom=Input, codom=Species, title="Input species morphism")
hom_ot = Hom(name="ot", dom=Output, codom=Transition, title="Output transition morphism")
hom_os = Hom(name="os", dom=Output, codom=Species, title="Output species morphism")

petri_obs = [Species, Transition, Input, Output]
petri_homs = [hom_it, hom_is, hom_ot, hom_os]

Name = AttrType(name="Name", ty=str, title="Name")
Concentration = AttrType(name="Concentration", ty=float, title="Concentration")
Rate = AttrType(name="Rate", ty=float, title="Rate")
Prop = AttrType(name="Prop", ty=dict, title="Property")

attr_sname = Attr(
    name="sname",
    dom=Species,
    codom=Name,
    title="Species name",
    description="An attribute representing the name of a species.",
)
attr_concentration = Attr(
    name="concentration",
    dom=Species,
    codom=Concentration,
    title="Species concentration",
    description="An attribute representing the concentration of a species.",
)
attr_sprop = Attr(
    name="sprop",
    dom=Species,
    codom=Prop,
    title="Species properties",
    description="An attribute representing the properties of a species.",
)
attr_tname = Attr(
    name="tname",
    dom=Transition,
    codom=Name,
    title="Transition name",
    description="An attribute representing the name of a transition.",
)
attr_rate = Attr(
    name="rate",
    dom=Transition,
    codom=Rate,
    title="Transition rate",
    description="An attribute representing the rate of a transition.",
)
attr_tprop = Attr(
    name="tprop",
    dom=Transition,
    codom=Prop,
    title="Transition properties",
    description="An attribute representing the properties of a transition.",
)

labelled_ats = [Name]
labelled_attrs = [attr_sname, attr_tname]

rxn_ats = [Concentration, Rate]
rxn_attrs = [attr_concentration, attr_rate]

prop_ats = [Prop]
prop_attrs = [attr_sprop, attr_tprop]

SchPetriNet = Schema(
    "PetriNet",
    petri_obs,
    petri_homs,
    [],
    [],
)
SchLabelledPetriNet = Schema(
    "LabelledPetriNet", petri_obs, petri_homs, labelled_ats, labelled_attrs
)
SchReactionNet = Schema("ReactionNet", petri_obs, petri_homs, rxn_ats, rxn_attrs)
SchLabelledReactionNet = Schema(
    "LabelledReactionNet", petri_obs, petri_homs, labelled_ats + rxn_ats, labelled_attrs + rxn_attrs
)
SchPropertyPetriNet = Schema("PropertyPetriNet", petri_obs, petri_homs, prop_ats, prop_attrs)
SchPropertyLabelledPetriNet = Schema(
    "PropertyLabelledPetriNet",
    petri_obs,
    petri_homs,
    labelled_ats + prop_ats,
    labelled_attrs + prop_attrs,
)
SchPropertyReactionNet = Schema(
    "PropertyReactionNet", petri_obs, petri_homs, rxn_ats + prop_ats, rxn_attrs + prop_attrs
)
SchPropertyLabelledReactionNet = Schema(
    "PropertyLabelledReactionNet",
    petri_obs,
    petri_homs,
    labelled_ats + rxn_ats + prop_ats,
    labelled_attrs + rxn_attrs + prop_attrs,
)


class Petri(ACSet):
    """
    A subclass of ACSet customized for petri nets.

    .. code-block::

        sir = Petri()
        s,i,r = sir.add_species(3)
        sir.set_subpart(s,attr_sname,"susceptible")
        sir.set_subpart(s,attr_sprop, { "uuid": "dae22e85-d941-4156-b559-d153a44356f3" })
        inf = sir.add_transitions([([s,i],[i,i])])
        sir.set_subpart(inf,attr_tname,"infection")
        sir.set_subpart(inf,attr_tprop, { "uuid": "bba26d0e-3ce5-41e5-ac0e-6be35535d534" })
    """

    def __init__(self, name="Petri", schema=SchPropertyLabelledReactionNet):
        """Initialize a new petri net."""
        super(Petri, self).__init__(schema.name, schema)

    def add_species(self, n: int) -> range:
        """Add `n` number of species to the petri net

        Args:
            n:  The number of species to add to the petri net.

        Returns:
            A range of the indexes of the species that were inserted into the petri net.
        """
        return self.add_parts(Species, n)

    def add_transitions(self, transitions: list[tuple[list[int], list[int]]]) -> range:
        """Add transitions to the petri net

        Args:
            transitions: A list of tuples where each tuple has two items: the first is a list of the input species and the second is a list of the output species.

        Returns:
            A range of the of the indexes of the transitions that were inserted into the petri net.
        """
        ts = self.add_parts(Transition, len(transitions))
        for t, (ins, outs) in zip(ts, transitions):
            for s in ins:
                arc = self.add_part(Input)
                self.set_subpart(arc, hom_it, t)
                self.set_subpart(arc, hom_is, s)
            for s in outs:
                arc = self.add_part(Output)
                self.set_subpart(arc, hom_ot, t)
                self.set_subpart(arc, hom_os, s)
        return ts


if __name__ == "__main__":
    for schema in [
        SchPetriNet,
        SchLabelledPetriNet,
        SchReactionNet,
        SchLabelledReactionNet,
        SchPropertyPetriNet,
        SchPropertyLabelledPetriNet,
        SchPropertyReactionNet,
        SchPropertyLabelledReactionNet,
    ]:
        schema_filename = "{}.json".format(schema.name)
        CATLAB_SCHEMAS_DIRECTORY.joinpath(schema_filename).write_text(
            schema.schema.json(indent=2, ensure_ascii=False, sort_keys=True)
        )
        jsonschema_path = JSON_SCHEMAS_DIRECTORY.joinpath(schema_filename)
        schema.write_schema(
            JSON_SCHEMAS_DIRECTORY.joinpath(jsonschema_path),
            uri="https://raw.githubusercontent.com/AlgebraicJulia/py-acsets/main/src/acsets/{}".format(
                Path(jsonschema_path).relative_to(HERE)
            ),
        )
