"""
This module implements a schema for what we call MiraNet, an extension
of the Petri net model with additional attributes and metadata.
"""

from .acsets import Attr, AttrType, Hom, Ob, Schema
from .petris import Petri

Species = Ob("S", title="Species")
Transition = Ob("T", title="Transition")
Input = Ob("I", title="Input")
Output = Ob("O", title="Output")

hom_it = Hom("it", Input, Transition, title="Input transition morphism")
hom_is = Hom("is", Input, Species, title="Input species morphism")
hom_ot = Hom("ot", Output, Transition, title="Output transition morphism")
hom_os = Hom("os", Output, Species, title="Output species morphism")

# Attribute types
Name = AttrType("Name", str, title="Name")
Value = AttrType("Value", float)
JsonStr = AttrType("JsonStr", str, description="A string a serialized JSON object")
XmlStr = AttrType("XmlStr", str, description="A string representing an XML object as a string")
SymPyStr = AttrType(
    "SymPyStr",
    str,
    description="A string representing an expression in the SymPy "
    "Python package's internal domain specific language (DSL).",
)

# Species attributes
attr_sname = Attr(
    "sname",
    Species,
    Name,
    title="Species name",
    description="An attribute representing the name of a species.",
)
attr_ids = Attr("mira_ids", Species, JsonStr)
attr_context = Attr("mira_context", Species, JsonStr)
attr_concept = Attr("mira_concept", Species, JsonStr)
attr_initial = Attr("mira_initial_value", Species, Value)

# Transition attributes
attr_tname = Attr(
    "tname",
    Transition,
    Name,
    title="Transition name",
    description="An attribute representing the name of a transition.",
)
attr_pname = Attr("parameter_name", Transition, Name)
attr_pval = Attr("parameter_value", Transition, Value)
attr_template_type = Attr("template_type", Transition, Name)
attr_rate_law = Attr("mira_rate_law", Transition, SymPyStr)
attr_rate_mathml = Attr("mira_rate_law_mathml", Transition, XmlStr)
attr_template = Attr("mira_template", Transition, JsonStr)
attr_parameters = Attr("mira_parameters", Transition, JsonStr)

SchMira = Schema(
    name="MiraNet",
    obs=[Species, Transition, Input, Output],
    homs=[hom_it, hom_is, hom_ot, hom_os],
    attrtypes=[Name, Value, JsonStr, XmlStr, SymPyStr],
    attrs=[
        attr_sname,
        attr_tname,
        attr_pname,
        attr_pval,
        attr_ids,
        attr_context,
        attr_concept,
        attr_initial,
        attr_template_type,
        attr_rate_law,
        attr_rate_mathml,
        attr_template,
        attr_parameters,
    ],
)


class MiraNet(Petri):
    """A subclass of Petri customized for MiraNet."""

    schema = SchMira

    def __init__(self, name="MiraNet", schema=SchMira):
        """Initialize a new MiraNet."""
        super(MiraNet, self).__init__(name, schema)
