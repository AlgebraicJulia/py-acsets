from .petris import Petri
from .acsets import ACSet, Attr, AttrType, Hom, Ob, Schema

Species = Ob("S")
Transition = Ob("T")
Input = Ob("I")
Output = Ob("O")

hom_it = Hom("it", Input, Transition)
hom_is = Hom("is", Input, Species)
hom_ot = Hom("ot", Output, Transition)
hom_os = Hom("os", Output, Species)

# Attribute types
Name = AttrType("Name", str)
Value = AttrType("Value", float)
JsonStr = AttrType("JsonStr", str)
XmlStr = AttrType("XmlStr", str)
SymPyStr = AttrType("SymPyStr", str)

# Species attributes
attr_sname = Attr("sname", Species, Name)
attr_ids = Attr("mira_ids", Species, JsonStr)
attr_context = Attr("mira_context", Species, JsonStr)
attr_concept = Attr("mira_concept", Species, JsonStr)
attr_initial = Attr("mira_initial_value", Species, Value)

# Transition attributes
attr_pname = Attr("parameter_name", Transition, Name)
attr_pval = Attr("parameter_value", Transition, Value)
attr_tname = Attr("tname", Transition, Name)
attr_rate_law = Attr("mira_rate_law", Transition, SymPyStr)
attr_rate_mathml = Attr("mira_rate_law_mathml", Transition, XmlStr)
attr_template = Attr("mira_template", Transition, JsonStr)
attr_parameters = Attr("mira_parameters", Transition, JsonStr)

SchMira = Schema(
    name="MiraNet",
    obs=[Species, Transition, Input, Output],
    homs=[hom_it, hom_is, hom_ot, hom_os],
    attrtypes=[Name, Value, JsonStr, XmlStr, SymPyStr],
    attrs=[attr_sname, attr_tname, attr_pname, attr_pval,
           attr_ids, attr_context, attr_concept, attr_initial,
           attr_rate_law, attr_rate_mathml, attr_template,
           attr_parameters],
)

class MiraNet(Petri):

    schema = SchMira
    def __init__(self, name="MiraNet", schema=SchMira):
        super(MiraNet, self).__init__(name, schema)