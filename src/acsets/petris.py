"""
In this model, we define a schema for petri nets, and then a subclass of acset
with some convenience methods.
"""
from acsets import SCHEMAS_DIRECTORY, ACSet, Attr, AttrType, Hom, Ob, Schema

Species = Ob(name="S", title="Species")
Transition = Ob(name="T", title="Transition")
Input = Ob(name="I", title="Input")
Output = Ob(name="O", title="Output")

hom_it = Hom(name="it", dom=Input, codom=Transition, title="Input transition morphism")
hom_is = Hom(name="is", dom=Input, codom=Species, title="Input species morphism")
hom_ot = Hom(name="ot", dom=Output, codom=Transition, title="Output transition morphism")
hom_os = Hom(name="os", dom=Output, codom=Species, title="Output species morphism")

Name = AttrType(name="Name", ty=str, title="Name")
Concentration = AttrType(name="Concentration", ty=int, title="Concentration")
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

SchPetriNet = Schema(
    "PetriNet",
    [Species, Transition, Input, Output],
    [hom_it, hom_is, hom_ot, hom_os],
    [],
    [],
)
SchLabelledPetriNet = Schema(
    "LabelledPetriNet",
    [Species, Transition, Input, Output],
    [hom_it, hom_is, hom_ot, hom_os],
    [Name],
    [attr_sname, attr_tname],
)
SchReactionNet = Schema(
    "ReactionNet",
    [Species, Transition, Input, Output],
    [hom_it, hom_is, hom_ot, hom_os],
    [Concentration, Rate],
    [attr_concentration, attr_rate],
)
SchLabelledReactionNet = Schema(
    "LabelledReactionNet",
    [Species, Transition, Input, Output],
    [hom_it, hom_is, hom_ot, hom_os],
    [Name, Concentration, Rate],
    [attr_sname, attr_concentration, attr_tname, attr_rate],
)
SchPropertyPetriNet = Schema(
    "PropertyPetriNet",
    [Species, Transition, Input, Output],
    [hom_it, hom_is, hom_ot, hom_os],
    [Prop],
    [attr_sprop, attr_tprop],
)
SchPropertyLabelledPetriNet = Schema(
    "PropertyLabelledPetriNet",
    [Species, Transition, Input, Output],
    [hom_it, hom_is, hom_ot, hom_os],
    [Name, Prop],
    [attr_sname, attr_sprop, attr_tname, attr_tprop],
)
SchPropertyReactionNet = Schema(
    "PropertyReactionNet",
    [Species, Transition, Input, Output],
    [hom_it, hom_is, hom_ot, hom_os],
    [Concentration, Rate, Prop],
    [attr_concentration, attr_sprop, attr_rate, attr_tprop],
)
SchPropertyLabelledReactionNet = Schema(
    "PropertyLabelledReactionNet",
    [Species, Transition, Input, Output],
    [hom_it, hom_is, hom_ot, hom_os],
    [Name, Concentration, Rate, Prop],
    [attr_sname, attr_concentration, attr_sprop, attr_tname, attr_rate, attr_tprop],
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
        schema_file = "{}.json".format(schema.name)
        schema.write_schema(
            SCHEMAS_DIRECTORY.joinpath(schema_file),
            uri="https://raw.githubusercontent.com/AlgebraicJulia/py-acsets/main/src/acsets/schemas/{}".format(
                schema_file
            ),
        )
