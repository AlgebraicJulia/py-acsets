"""
In this model, we define a schema for petri nets, and then a subclass of acset
with some convenience methods.
"""
from acsets import SCHEMAS_DIRECTORY, ACSet, Attr, AttrType, Hom, Ob, Schema

Species = Ob("S", title="Species")
Transition = Ob("T", title="Transition")
Input = Ob("I", title="Input")
Output = Ob("O", title="Output")

hom_it = Hom("it", Input, Transition, title="Input transition morphism")
hom_is = Hom("is", Input, Species, title="Input species morphism")
hom_ot = Hom("ot", Output, Transition, title="Output transition morphism")
hom_os = Hom("os", Output, Species, title="Output species morphism")

Name = AttrType("Name", str, title="Name")

attr_sname = Attr(
    "sname",
    Species,
    Name,
    title="Species name",
    description="An attribute representing the name of a species.",
)
attr_tname = Attr(
    "tname",
    Transition,
    Name,
    title="Transition name",
    description="An attribute representing the name of a transition.",
)

SchPetri = Schema(
    "Petri",
    [Species, Transition, Input, Output],
    [hom_it, hom_is, hom_ot, hom_os],
    [Name],
    [attr_sname, attr_tname],
)


class Petri(ACSet):
    """
    A subclass of ACSet customized for petri nets.

    .. code-block::

        sir = Petri()
        s,i,r = sir.add_species(3)
        sir.set_subpart(s,attr_sname,"susceptible")
        inf = sir.add_transitions([([s,i],[i,i])])
        sir.set_subpart(inf,attr_tname,"infection")  sir = Petri()
    """

    def __init__(self, name="Petri", schema=SchPetri):
        """Initialize a new petri net."""
        super(Petri, self).__init__(name, schema)

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
        for (t, (ins, outs)) in zip(ts, transitions):
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
    SchPetri.write_schema(
        SCHEMAS_DIRECTORY.joinpath("petri.json"),
        uri="https://raw.githubusercontent.com/AlgebraicJulia/py-acsets/main/src/acsets/schemas/petri.json",
    )
