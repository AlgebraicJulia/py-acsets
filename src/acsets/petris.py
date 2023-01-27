from acsets import ACSet, Attr, AttrType, Hom, Ob, Schema

Species = Ob("S")
Transition = Ob("T")
Input = Ob("I")
Output = Ob("O")

hom_it = Hom("it", Input, Transition)
hom_is = Hom("is", Input, Species)
hom_ot = Hom("ot", Output, Transition)
hom_os = Hom("os", Output, Species)

Name = AttrType("Name", str)

attr_sname = Attr("sname", Species, Name)
attr_tname = Attr("tname", Transition, Name)

SchPetri = Schema(
    "Petri",
    [Species, Transition, Input, Output],
    [hom_it, hom_is, hom_ot, hom_os],
    [Name],
    [attr_sname, attr_tname]
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
    def __init__(self, schema=SchPetri):
        super(Petri, self).__init__("Petri", schema)

    def add_species(self, n: int) -> range:
        return self.add_parts(Species, n)

    def add_transitions(self, transitions: list[tuple[list[int], list[int]]]) -> range:
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
