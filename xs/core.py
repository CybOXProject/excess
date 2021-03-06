"""
xs.core
-------
Foundational types for the `xs` library

These do not correspond to actual types in the XML Schema Definition language,
but are rather used to encapsulate common functionality.  These should not
be used outside the xs library.
"""


class _DataType(object):
    """Base class for both simple and complex types."""

    @classmethod
    def check_value(cls, value):
        """Test whether `value` is valid for this type.

        This function should either convert `value` to a suitable value or
        raise a ValueError.
        """
        if not isinstance(value, cls):
            msg = "%s (type: %s) is not a %s" % (value, type(value), cls)
            raise ValueError(msg)
        return value


class _Component(object):
    """Base class for Element and Attribute.

    This corresponds roughly to a "Declaration Component" as defined in XML
    Schema.
    """

    def __init__(self, name, type_, default=None):
        if not name:
            raise ValueError("Name must be provided")
        if not type_:
            raise ValueError("Type must be provided")
        self.name = name
        self.type_ = type_
        self.default = default

    @property
    def default(self):
        """Return the default value of this element."""
        return self._get_default()

    def _get_default(self):
        if self._default is not None:
            return self._default
        else:
            return None

    @default.setter
    def default(self, value):
        self._default = value


    @property
    def multiple(self):
        raise NotImplementedError
