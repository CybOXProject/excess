"""
xs.element
------------

Implementation of xs:element
"""

from collections import MutableSequence

from .compat import etree, UnicodeMixin
from .core import _Component, _DataType
from .simpletypes import _SimpleType


class _InnerList(MutableSequence):
    """Used to maintain a "typed" list.

    Ensures that each element added to the list is of the right type, or
    can be converted to the correct type.
    """
    _contained_type = object

    def __init__(self, type_=None):
        if not issubclass(type_, _DataType):
            raise TypeError("'%s' is not a valid SimpleType or ComplexType" %
                            type_)
        self._type = type_
        self._inner = []

    def __repr__(self):
        return self._inner.__repr__()

    def __getitem__(self, key):
        return self._inner.__getitem__(key)

    def __setitem__(self, key, value):
        value = self._type.check_value(value)
        self._inner.__setitem__(key, value)

    def __delitem__(self, key):
        self._inner.__delitem__(key)

    def __len__(self):
        return len(self._inner)

    def insert(self, idx, value):
        value = self._type.check_value(value)
        self._inner.insert(idx, value)


class Element(UnicodeMixin, _Component):
    """Python representation of an xs:element.

    This should be used when defining the content of a `ComplexType` (as part
    of an xs.Sequence or xs.Choice).

    To define an element which occurs at the top level of a schema, use the
    `TopLevelElement` class.
    """

    def __init__(self, name, type_, default=None):
        """Create a new Element.

        If `value` is not `None`, it must be of type `type_`.
        """
        super(Element, self).__init__(name, type_, default=default)
        #TODO: add other xs:element-specific properties

    def __call__(self, value=None):
        """Pseudo-factory to create instances of this type of element.

        If defined, `value` must be of the correct type.
        """
        return TopLevelElement(self.name, self.type_, value=value)

    def __unicode__(self):
        return "{0.name} ({0.type_.__name__})".format(self)

    @property
    def multiple(self):
        #TODO: support maxOccurs>1
        return False


class TopLevelElement(Element):
    """An Element which is not part of a ComplexType"""

    def __init__(self, *args, **kwargs):
        """Create a top-level schema element.

        You do not need to specify a value on creation, but it needs to be
        specified before calling to_etree.
        """
        value = kwargs.pop('value', None)
        super(TopLevelElement, self).__init__(*args, **kwargs)
        self.value = value

    @property
    def value(self):
        """
        The value contained in this TopLevelElement.
        """
        return self._value

    @value.setter
    def value(self, value):
        """
        Set the value of this TopLevelElement.

        `value` must be either None or the proper type for this Element
        """
        if value is None:
            self._value = None
        else:
            self._value = self.type_.check_value(value)

    def __getattr__(self, name):
        """Allow accessing the attributes of a contained complexType.

        If 'name' is not an attribute of the `Element` class itself,
        assume it is a property of the contained ComplexType object.
        """
        return getattr(self.value, name)

    def __setattr__(self, name, value):
        """ Allow setting the attributes of the contained complexType.
        """
        if name in ('name', 'type_', 'default', '_default', 'value', '_value'):
            object.__setattr__(self, name, value)
        else:
            # Create a contained object of the Element's type.
            if self.value is None:
                self.value = self.type_()
            object.__setattr__(self.value, name, value)

    def to_etree(self):
        if self.value is None:
            raise ValueError("Element has not been given a value")

        return self.type_.to_etree(self.name, self.value)

    def to_xml(self):
        return etree.tostring(self.to_etree())
