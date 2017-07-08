# -*- coding: utf-8 -*-
#
# Copyright (c), 2016, SISSA (International School for Advanced Studies).
# All rights reserved.
# This file is distributed under the terms of the MIT License.
# See the file 'LICENSE' in the root directory of the present
# distribution, or http://opensource.org/licenses/MIT.
#
# @author Davide Brunato <brunato@sissa.it>
#
from ..core import ElementData, etree_element
from ..exceptions import XMLSchemaValidationError, XMLSchemaAttributeError
from ..utils import check_type
from ..qnames import (
    get_qname, reference_to_qname, local_name, XSD_GROUP_TAG, XSD_ATTRIBUTE_GROUP_TAG,
    XSD_SEQUENCE_TAG, XSD_ALL_TAG, XSD_CHOICE_TAG, XSD_ANY_ATTRIBUTE_TAG,
    XSD_ATTRIBUTE_TAG, XSD_COMPLEX_CONTENT_TAG, XSD_RESTRICTION_TAG, XSD_COMPLEX_TYPE_TAG,
    XSD_EXTENSION_TAG, XSD_ANY_TYPE, XSD_SIMPLE_CONTENT_TAG, XSD_ANY_SIMPLE_TYPE
)
from ..xsdbase import (
    get_xsd_attribute, get_xsd_bool_attribute, get_xsd_derivation_attribute, ValidatorMixin
)
from .component import XsdAnnotated
from .attributes import XsdAttributeGroup

XSD_MODEL_GROUP_TAGS = {XSD_GROUP_TAG, XSD_SEQUENCE_TAG, XSD_ALL_TAG, XSD_CHOICE_TAG}


class XsdComplexType(XsdAnnotated, ValidatorMixin):
    """
    Class for XSD 1.0 'complexType' definitions.
    
    <complexType
      abstract = boolean : false
      block = (#all | List of (extension | restriction))
      final = (#all | List of (extension | restriction))
      id = ID
      mixed = boolean : false
      name = NCName
      {any attributes with non-schema namespace . . .}>
      Content: (annotation?, (simpleContent | complexContent | 
      ((group | all | choice | sequence)?, ((attribute | attributeGroup)*, anyAttribute?))))
    </complexType>
    """
    def __init__(self, elem, schema, name=None, content_type=None, attributes=None,
                 derivation=None, mixed=None, is_global=False):
        self.derivation = derivation
        super(XsdComplexType, self).__init__(elem, schema, name, is_global)

        if not hasattr(self, 'content_type'):
            if content_type is None:
                raise XMLSchemaAttributeError("undefined 'content_type' attribute for %r." % self)
            self.content_type = content_type
        if not hasattr(self, 'attributes'):
            if attributes is None:
                raise XMLSchemaAttributeError("undefined 'attributes' attribute for %r." % self)
            self.attributes = attributes
        if not hasattr(self, 'mixed'):
            if mixed is None:
                raise XMLSchemaAttributeError("undefined 'mixed' attribute for %r." % self)
            self.mixed = mixed

    def __setattr__(self, name, value):
        if name == 'content_type':
            check_type(value, self.BUILDERS.simple_type_class, self.BUILDERS.group_class)
        elif name == 'attributes':
            check_type(value, XsdAttributeGroup)
        super(XsdComplexType, self).__setattr__(name, value)

    def _parse(self):
        super(XsdComplexType, self)._parse()
        elem = self.elem
        if elem.tag == XSD_RESTRICTION_TAG:
            return  # a local restriction is already parsed by the caller

        self.mixed = get_xsd_bool_attribute(elem, 'mixed', default=False)
        self._parse_properties('abstract', 'block', 'final')

        try:
            self.name = get_qname(self.target_namespace, elem.attrib['name'])
        except KeyError:
            self.name = None
        else:
            if not self.is_global:
                self._parse_error("attribute 'name' not allowed for a local complexType", elem)

        self.derivation = None
        self.mixed = elem.get('mixed') in ('true', '1')

        content_elem = self._parse_component(elem, required=False, strict=False)
        if content_elem is None or content_elem.tag in \
                {XSD_ATTRIBUTE_TAG, XSD_ATTRIBUTE_GROUP_TAG, XSD_ANY_ATTRIBUTE_TAG}:
            #
            # complexType with empty content
            self.content_type = self.BUILDERS.build_any_content_group(self.schema)
            self.attributes = self.BUILDERS.attribute_group_class(elem, self.schema)

        elif content_elem.tag in {XSD_GROUP_TAG, XSD_SEQUENCE_TAG, XSD_ALL_TAG, XSD_CHOICE_TAG}:
            #
            # complexType with child elements
            self.content_type = self.BUILDERS.group_class(content_elem, self.schema, mixed=self.mixed)
            self.attributes = self.BUILDERS.attribute_group_class(elem, self.schema)

        elif content_elem.tag == XSD_SIMPLE_CONTENT_TAG:
            if 'mixed' in content_elem.attrib:
                self._parse_error("'mixed' attribute not allowed with simpleContent", content_elem)

            derivation_elem = self._parse_derivation_elem(content_elem)
            if derivation_elem is None:
                return

            base_type = self._parse_base_type(derivation_elem)
            if derivation_elem.tag == XSD_RESTRICTION_TAG:
                self._parse_simple_content_restriction(derivation_elem, base_type)
            else:
                self._parse_simple_content_extension(derivation_elem, base_type)

        elif content_elem.tag == XSD_COMPLEX_CONTENT_TAG:
            #
            # complexType with complexContent restriction/extension
            if 'mixed' in content_elem.attrib:
                self.mixed = content_elem.attrib['mixed'] in ('true', '1')

            derivation_elem = self._parse_derivation_elem(content_elem)
            if derivation_elem is None:
                return

            base_type = self._parse_base_type(derivation_elem, complex_content=True)
            if derivation_elem.tag == XSD_RESTRICTION_TAG:
                self._parse_complex_content_restriction(derivation_elem, base_type)
            else:
                self._parse_complex_content_extension(derivation_elem, base_type)

        else:
            # self._parse_error("unexpected tag %r for complexType content:" % content_elem.tag, self)
            self.content_type = self.BUILDERS.build_any_content_group(self.schema)
            self.attributes = self.BUILDERS.build_any_attribute_group(self.schema)

    def _parse_derivation_elem(self, elem):
        derivation_elem = self._parse_component(elem, required=False)
        if getattr(derivation_elem, 'tag', None) not in (XSD_RESTRICTION_TAG, XSD_EXTENSION_TAG):
            self._parse_error("restriction or extension tag expected", derivation_elem)
            self.content_type = self.BUILDERS.build_any_content_group(self.schema)
            self.attributes = self.BUILDERS.build_any_attribute_group(self.schema)
            return

        self.derivation = local_name(derivation_elem.tag)
        if self.derivation in self.final:
            self._parse_error("%r derivation not allowed for %r." % (self.derivation, self))
        return derivation_elem

    def _parse_base_type(self, elem, complex_content=False):
        try:
            content_base = get_xsd_attribute(elem, 'base')
        except KeyError:
            self._parse_error("'base' attribute required", elem)
            return self.maps.lookup_type(XSD_ANY_TYPE)

        base_qname = reference_to_qname(content_base, self.namespaces)
        try:
            base_type = self.maps.lookup_type(base_qname)
        except KeyError:
            self._parse_error("missing base type %r" % base_qname, elem)
            if complex_content:
                return self.maps.lookup_type(XSD_ANY_TYPE)
            else:
                return self.maps.lookup_type(XSD_ANY_SIMPLE_TYPE)
        else:
            if complex_content and base_type.is_simple():
                self._parse_error("a complexType ancestor required: %r" % base_type, elem)
                return self.maps.lookup_type(XSD_ANY_TYPE)
            else:
                return base_type

    def _parse_simple_content_restriction(self, elem, base_type):
        # simpleContent restriction: the base type must be a complexType with a simple
        # content or a complex content with a mixed and emptiable content.
        if base_type.is_simple():
            self._parse_error("a complexType ancestor required: %r" % base_type, elem)
            self.content_type = self.BUILDERS.build_any_content_group(self.schema)
        elif base_type.has_simple_content() or base_type.mixed and base_type.is_emptiable():
            self.content_type = self.BUILDERS.restriction_class(elem, self.schema)
        else:
            self._parse_error("with simple content cannot restrict an empty or "
                              "an element-only content type ", base_type.elem)
            self.content_type = self.BUILDERS.build_any_content_group(self.schema)

        self.attributes = self.BUILDERS.attribute_group_class(elem, self.schema)

    def _parse_simple_content_extension(self, elem, base_type):
        # simpleContent extension: the base type must be a simpleType or a complexType
        # with simple content.
        child = self._parse_component(elem, required=False, strict=False)
        if child is not None and child.tag not in \
                {XSD_ATTRIBUTE_GROUP_TAG, XSD_ATTRIBUTE_TAG, XSD_ANY_ATTRIBUTE_TAG}:
            self._parse_error("unexpected tag %r." % child.tag, child)

        if base_type.is_simple():
            self.content_type = base_type
            self.attributes = self.BUILDERS.attribute_group_class(elem, self.schema)
        else:
            if base_type.has_simple_content():
                self.content_type = base_type.content_type
            else:
                self._parse_error("base type %r has not simple content." % base_type, elem)
                self.content_type = self.BUILDERS.build_any_content_group(self.schema)

            self.attributes = self.BUILDERS.attribute_group_class(
                elem=elem,
                schema=self.schema,
                derivation='extension',
                base_attributes=base_type.attributes
            )

    def _parse_complex_content_restriction(self, elem, base_type):
        # complexContent restriction: the base type must be a complexType with a complex
        # content.
        group_elem = self._parse_component(elem, required=False, strict=False)
        if group_elem is not None and group_elem.tag in XSD_MODEL_GROUP_TAGS:
            self.content_type = self.BUILDERS.group_class(group_elem, self.schema, mixed=self.mixed)
            if self.content_type.model != base_type.content_type.model:
                self._parse_error(
                    "content model differ from base type: %r" % base_type.content_type.model, elem
                )
        else:
            # Empty content model
            self.content_type = self.BUILDERS.group_class(elem, self.schema, mixed=self.mixed)

        if base_type.is_element_only() and self.content_type.mixed:
            self._parse_error(
                "derived a mixed content from a base type that has element-only content.", elem
            )
        elif base_type.is_empty() and not self.content_type.is_empty():
            self._parse_error(
                "derived an empty content from base type that has not empty content.", elem
            )

        if not base_type.is_empty():
            for item in self.content_type:
                try:
                    if not any([item.is_restriction(other) for other in base_type.content_type]):
                        self._parse_error("% is not a restriction.", elem)
                except AttributeError:
                    continue

        self.attributes = self.BUILDERS.attribute_group_class(
            elem=elem,
            schema=self.schema,
            derivation='restriction',
            base_attributes=base_type.attributes
        )

    def _parse_complex_content_extension(self, elem, base_type):
        # complexContent extension: base type must be a complex type with complex content.
        # A dummy sequence group is added if the base type has not empty content model.
        # Ref: https://www.w3.org/TR/2012/REC-xmlschema11-1-20120405/#sec-cos-ct-extends
        if base_type.is_simple() or base_type.has_simple_content():
            self._parse_error("base %r is simple or has a simple content." % base_type, elem)
            base_type = self.maps.lookup_type(XSD_ANY_TYPE)

        if base_type.content_type.model == XSD_ALL_TAG:
            self._parse_error("XSD 1.0 do not allows 'ALL' group extensions", elem)

        group_elem = self._parse_component(elem, required=False, strict=False)
        if base_type.is_empty():
            # Empty model extension: don't create a nested group.
            if group_elem is not None and group_elem.tag in XSD_MODEL_GROUP_TAGS:
                self.content_type = self.BUILDERS.group_class(group_elem, self.schema, mixed=self.mixed)
            else:
                # Empty content model
                self.content_type = self.BUILDERS.group_class(elem, self.schema, mixed=self.mixed)
        else:
            dummy_elem = etree_element(XSD_SEQUENCE_TAG)
            self.content_type = self.BUILDERS.group_class(dummy_elem, self.schema)
            if group_elem is not None and group_elem.tag in XSD_MODEL_GROUP_TAGS:
                xsd_group = self.BUILDERS.group_class(group_elem, self.schema, mixed=self.mixed)
                self.content_type.append(base_type.content_type)
                self.content_type.append(xsd_group)
            else:
                self.content_type.append(base_type.content_type)

            if base_type.mixed != self.mixed:
                self._parse_error(
                    "base has a different content type (mixed=%r)." % base_type.mixed, elem)
                self.mixed = base_type.mixed

        self.attributes = self.BUILDERS.attribute_group_class(
            elem=elem,
            schema=self.schema,
            derivation='extension',
            base_attributes=base_type.attributes
        )

    @property
    def built(self):
        return self.content_type.built and self.attributes.built

    @property
    def validation_attempted(self):
        if self.built:
            return 'full'
        elif self.attributes.validation_attempted == 'partial':
            return 'partial'
        elif self.content_type.validation_attempted == 'partial':
            return 'partial'
        else:
            return 'none'

    @property
    def admitted_tags(self):
        if self.is_global:
            return {XSD_COMPLEX_TYPE_TAG}
        else:
            return {XSD_COMPLEX_TYPE_TAG, XSD_RESTRICTION_TAG}

    @staticmethod
    def is_simple():
        return False

    @staticmethod
    def is_complex():
        return True

    def is_empty(self):
        return self.content_type.is_empty()

    def is_emptiable(self):
        return self.content_type.is_emptiable()

    def has_simple_content(self):
        try:
            return self.content_type.is_simple()
        except AttributeError:
            return False

    def has_mixed_content(self):
        try:
            return self.content_type.mixed
        except AttributeError:
            return False

    def is_element_only(self):
        try:
            return not self.content_type.mixed
        except AttributeError:
            return False

    @property
    def abstract(self):
        return get_xsd_bool_attribute(self.elem, 'abstract', default=False)

    @property
    def block(self):
        return get_xsd_derivation_attribute(self.elem, 'block', ('extension', 'restriction'))

    @property
    def final(self):
        return get_xsd_derivation_attribute(self.elem, 'final', ('extension', 'restriction'))

    def iter_components(self, xsd_classes=None):
        if xsd_classes is None or isinstance(self, xsd_classes):
            yield self
        if not self.attributes.is_global:
            for obj in self.attributes.iter_components(xsd_classes):
                yield obj
        if not self.content_type.is_global:
            for obj in self.content_type.iter_components(xsd_classes):
                yield obj

    @staticmethod
    def get_facet(*args, **kwargs):
        return None

    def admit_simple_restriction(self):
        if 'restriction' in self.final:
            return False
        else:
            return self.has_simple_content() or self.mixed and self.is_emptiable()

    def has_restriction(self):
        return self.derivation is False

    def has_extension(self):
        return self.derivation is True

    def iter_decode(self, elem, validation='lax', **kwargs):
        """
        Generator method for decoding complexType elements. A 3-tuple (simple content,
        complex content, attributes) containing the decoded parts is returned, eventually
        preceded by a sequence of validation/decode errors.
        """
        # Decode attributes
        for result in self.attributes.iter_decode(elem, validation, **kwargs):
            if isinstance(result, XMLSchemaValidationError):
                yield result
            else:
                attributes = result
                break
        else:
            attributes = None

        if self.has_simple_content():
            # Decode a simple content element
            if len(elem):
                yield XMLSchemaValidationError(
                    self, elem, "a simple content element can't has child elements."
                )
            if elem.text is not None:
                text = elem.text or kwargs.pop('default', '')
                for result in self.content_type.iter_decode(text, validation, **kwargs):
                    if isinstance(result, XMLSchemaValidationError):
                        yield result
                    else:
                        yield result, None, attributes
            else:
                yield None, None, attributes
        else:
            # Decode a complex content element
            for result in self.content_type.iter_decode(elem, validation, **kwargs):
                if isinstance(result, XMLSchemaValidationError):
                    yield result
                else:
                    yield None, result, attributes

    def iter_encode(self, data, validation='lax', **kwargs):
        # Encode attributes
        for result in self.attributes.iter_encode(data.attributes, validation, **kwargs):
            if isinstance(result, XMLSchemaValidationError):
                yield result
            else:
                attributes = result
                break
        else:
            attributes = ()

        if self.has_simple_content():
            # Encode a simple content element
            if data.text is None:
                yield ElementData(None, None, data.content, attributes)
            else:
                for result in self.content_type.iter_encode(data.text, validation, **kwargs):
                    if isinstance(result, XMLSchemaValidationError):
                        yield result
                    else:
                        yield ElementData(None, result, data.content, attributes)
        else:
            # Encode a complex content element
            for result in self.content_type.iter_encode(data.content, validation, **kwargs):
                if isinstance(result, XMLSchemaValidationError):
                    yield result
                else:
                    yield ElementData(None, result[0], result[1], attributes)


class Xsd11ComplexType(XsdComplexType):
    """
    Class for XSD 1.1 'complexType' definitions.

    <complexType
      abstract = boolean : false
      block = (#all | List of (extension | restriction))
      final = (#all | List of (extension | restriction))
      id = ID
      mixed = boolean
      name = NCName
      defaultAttributesApply = boolean : true
      {any attributes with non-schema namespace . . .}>
      Content: (annotation?, (simpleContent | complexContent | (openContent?, 
      (group | all | choice | sequence)?, ((attribute | attributeGroup)*, anyAttribute?), assert*)))
    </complexType>
    """
    pass
