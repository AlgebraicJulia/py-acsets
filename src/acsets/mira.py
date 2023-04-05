"""
This module implements a schema for what we call MiraNet, an extension
of the Petri net model with additional attributes and metadata.
"""

from .acsets import Attr, AttrType, Hom, Ob, Schema
from .petris import Petri

Species = Ob(name="S", title="Species")
Transition = Ob(name="T", title="Transition")
Input = Ob(name="I", title="Input")
Output = Ob(name="O", title="Output")

hom_it = Hom(name="it", dom=Input, codom=Transition, title="Input transition morphism")
hom_is = Hom(name="is", dom=Input, codom=Species, title="Input species morphism")
hom_ot = Hom(name="ot", dom=Output, codom=Transition, title="Output transition morphism")
hom_os = Hom(name="os", dom=Output, codom=Species, title="Output species morphism")

# Attribute types
Name = AttrType(name="Name", ty=str, title="Name")
Value = AttrType(name="Value", ty=float)
JsonStr = AttrType(name="JsonStr", ty=str, description="A string a serialized JSON object")
XmlStr = AttrType(
    name="XmlStr", ty=str, description="A string representing an XML object as a string"
)
SymPyStr = AttrType(
    name="SymPyStr",
    ty=str,
    description="A string representing an expression in the SymPy "
    "Python package's internal domain specific language (DSL).",
)

# Species attributes
attr_sname = Attr(
    name="sname",
    dom=Species,
    codom=Name,
    title="Species name",
    description="An attribute representing the name of a species.",
)
attr_ids = Attr(name="mira_ids", dom=Species, codom=JsonStr)
attr_context = Attr(name="mira_context", dom=Species, codom=JsonStr)
attr_concept = Attr(name="mira_concept", dom=Species, codom=JsonStr)
attr_initial = Attr(name="mira_initial_value", dom=Species, codom=Value)

# Transition attributes
attr_tname = Attr(
    name="tname",
    dom=Transition,
    codom=Name,
    title="Transition name",
    description="An attribute representing the name of a transition.",
)
attr_pname = Attr(name="parameter_name", dom=Transition, codom=Name)
attr_pval = Attr(name="parameter_value", dom=Transition, codom=Value)
attr_template_type = Attr(name="template_type", dom=Transition, codom=Name)
attr_rate_law = Attr(name="mira_rate_law", dom=Transition, codom=SymPyStr)
attr_rate_mathml = Attr(name="mira_rate_law_mathml", dom=Transition, codom=XmlStr)
attr_template = Attr(name="mira_template", dom=Transition, codom=JsonStr)
attr_parameters = Attr(name="mira_parameters", dom=Transition, codom=JsonStr)

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
