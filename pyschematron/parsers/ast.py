from __future__ import annotations

__author__ = 'Robbert Harms'
__date__ = '2022-10-06'
__maintainer__ = 'Robbert Harms'
__email__ = 'robbert@xkls.nl'
__licence__ = 'GPL v3'

import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal


class SchematronNode:
    """Base class for all Schematron AST nodes."""


@dataclass(slots=True)
class Schema(SchematronNode):
    """Representation of a <schema> tag."""
    variables: list[Variable]
    phases: list[Phase]
    patterns: list[Pattern]
    namespaces: list[Namespace]
    title: str | None = None
    default_phase: str | None = None
    query_binding: str | None = None


@dataclass(slots=True)
class Namespace(SchematronNode):
    """Representation of an `<ns>` tag."""
    prefix: str
    uri: str


@dataclass(slots=True)
class Phase(SchematronNode):
    """Representation of a `<phase>` tag."""
    id: str
    active: list[str]
    variables: list[Variable]


@dataclass(slots=True, kw_only=True)
class Pattern(SchematronNode):
    """Abstract representation of a <pattern> tag.

    This can not be instantiated as is, one needs to load one of the subclasses for concrete or abstract patterns.

    Be reminded that the order of the rules matters. According to the Schematron definition, each node in an XML shall
    never be checked for multiple rules in one pattern. In the case of multiple matching rules, only the first matching
    rule is applied.
    """
    id: str | None = None


@dataclass(slots=True)
class ConcretePattern(Pattern):
    """A concrete pattern, this neither extends another pattern or is an abstract pattern"""
    rules: list[Rule] = field(default_factory=list)
    variables: list[Variable] = field(default_factory=list)


@dataclass(slots=True, kw_only=True)
class Rule(SchematronNode):
    """Abstract representation of a <rule> tag.

    This can not be instantiated as is, rather instantiate one of the subclasses for concrete, abstract,
    or external rules.

    Args:
        checks: the list of report and assert items in this rule
        variables: the list of `<let>` variable declarations in this rule
        paragraphs: list of paragraphs
        flag: name of the flag to which this test belongs, is set to True when this test is fired
        fpi: formal public identifier, a system-independent ID of this test
        icon: reference to a graphic file to be used in the error message
        role: a description of the error message or the rule
        see: a URI or URL referencing background information
        subject: an xpath string referencing the node to which we assign an error message
        xml_lang: the default natural language for this node
        xml_space: defines how whitespace must be handled for this element.
    """
    checks: list[Check] = field(default_factory=list)
    variables: list[Variable] = field(default_factory=list)
    paragraphs: list[Paragraph] = field(default_factory=list)
    extends: list[Extends] = field(default_factory=list)
    flag: str | None = None
    fpi: str | None = None
    icon: str | None = None
    role: str | None = None
    see: str | None = None
    subject: XPath | None = None
    xml_lang: str | None = None
    xml_space: Literal['default', 'preserve'] | None = None


@dataclass(slots=True)
class ConcreteRule(Rule):
    """Representation of a concrete <rule> tag (e.g. not abstract).

    Args:
        context: the attribute with the rule's context
        id: the identifier of this test (optional)
    """
    context: XPath
    id: str | None = None


@dataclass(slots=True)
class AbstractRule(Rule):
    """Representation of an abstract <rule> tag.

    Args:
        id: the identifier of this test (required)
    """
    id: str


@dataclass(slots=True)
class ExternalRule(Rule):
    """Representation of an <rule> loaded from an external file using extends."""
    id: str | None = None


@dataclass(slots=True)
class Extends(SchematronNode):
    """Base class for <extends> tag representations used to extend a Rule with another rule."""


@dataclass(slots=True)
class ExtendsById(Extends):
    """Represents an <extends> tag which points to an abstract rule in this Schema.

    Args:
        id_pointer: the identifier of a Rule inside the Schematron to which we refer
    """
    id_pointer: str


@dataclass(slots=True)
class ExtendsExternal(Extends):
    """Represents an <extends> tag which has an AbstractRule loaded from another file.

    Args:
        rule: an ExternalRule loaded from another file.
        path: the path from which the rule was loaded
    """
    rule: ExternalRule
    file_path: Path


@dataclass(slots=True)
class Check(SchematronNode):
    """Base class for `<assert>` and `<report>` elements.

    Args:
        test: the attribute with the test condition
        content: the mixed text content, can contain `<emph>`, `<span>`, `<dir>`,
            `<value-of>`, and `<name>` as flat text.

        diagnostics: list of IDs referencing a diagnostic elements
        flag: name of the flag to which this test belongs, is set to True when this test is fired
        fpi: formal public identifier, a system-independent ID of this test
        icon: reference to a graphic file to be used in the error message
        id: the identifier of this test
        properties: list of identifiers of property items
        role: a description of the error message or the rule
        see: a URI or URL referencing background information
        subject: an xpath string referencing the node to which we assign an error message
        xml_lang: the default natural language for this node
        xml_space: defines how whitespace must be handled for this element.
    """
    test: XPath
    content: str
    diagnostics: list[str] | None = None
    flag: str | None = None
    fpi: str | None = None
    icon: str | None = None
    id: str | None = None
    properties: list[str] | None = None
    role: str | None = None
    see: str | None = None
    subject: XPath | None = None
    xml_lang: str | None = None
    xml_space: Literal['default', 'preserve'] | None = None


@dataclass(slots=True)
class Assert(Check):
    """Representation of an `<assert>` tag."""


@dataclass(slots=True)
class Report(Check):
    """Representation of a `<report>` tag."""


@dataclass(slots=True)
class Variable(SchematronNode):
    """Abstract representation of a `<let>` tag.

    Args:
        name: the name attribute
    """
    name: str


@dataclass(slots=True)
class XPathVariable(Variable):
    """Representation of a `<let>` tag with an XPath value attribute.

    Args:
        name: the name attribute
        value: the value attribute
    """
    value: XPath


@dataclass(slots=True)
class XMLVariable(Variable):
    """Representation of a `<let>` tag with the value loaded from the node's content.

    Args:
        name: the name attribute
        value: the content of the `<let>` element.
    """
    value: str


@dataclass(slots=True)
class Paragraph(SchematronNode):
    """Representation of a `<p>` tag.

    Args:
        content: the rich content of this paragraph
        class_: the class attribute
        icon: the icon attribute
        id: the identifier
    """
    content: str
    class_: str | None = None
    icon: str | None = None
    id: str | None = None


@dataclass(slots=True)
class XPath(SchematronNode):
    """Representation of an XPath for in use in the Schematron AST nodes"""
    xpath: str
