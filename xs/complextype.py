import inspect

from .attribute import Attribute
from .compat import etree
from .core import _DataType


class ComplexType(_DataType):

    # User-defined ComplexType subclasses should define all the attributes
    # of the class in this list, in the order they should appear in XML output.
    attributes = []

    # User-defined ComplexType subclasses should define the content of their
    # complexContent as this variable.  For now, it should alwasy be an
    # xs.Sequence instance
    content = None

    def __init__(self):
        self._fields = {}

    def __getattr__(self, name):
        """Retrieve the value of a component from the ComplexType.

        This allows the "dot syntax" to work dynamically for ComplexTypes.
        """
        cls = self.__class__
        components = cls._component_dict()

        if name == "_fields":
            raise Exception("Shouldn't be here")
        if name in self._fields:
            return self._fields[name]
        elif name in components:
            component = components[name]
            # Automatically return the default value for any component which
            # has not been explicitly set. This saves storage and time to
            # instantiate a new instance of a ComplexType.
            default = component.default
            # For embedded _InnerLists, we want each instance of this class
            # to have it's own copy of the list, so set it here.
            if component.multiple:
                self._fields[name] = default
            return default
        else:
            msg = "%s is not a valid component of a %s" % (name, cls.__name__)
            raise AttributeError(msg)

    def __setattr__(self, name, value):
        """Set the value of a component from the ComplexType.

        This allows the "dot syntax" to work dynamically for ComplexTypes.
        """
        cls = self.__class__
        components = cls._component_dict()

        if name == "_fields":
            object.__setattr__(self, name, value)
        elif name in components:
            component = components[name]
            if component.multiple:
                # If setting, we are overwriting any existing value
                new_value = component.default
                # TODO: support other iterables
                if isinstance(value, list):
                    new_value.extend(value)
                else:
                    new_value.append(value)
                self._fields[name] = new_value
            else:
                self._fields[name] = component.type_.check_value(value)
        else:
            msg = "%s is not a valid component of a %s" % (name, cls.__name__)
            raise AttributeError(msg)

    @classmethod
    def _component_dict(cls):
        """Return a dictionary mapping names to the corresponding Component.

        This allows xs.Attributes and xs.Elements to be accessed identically,
        and does not require the user to know the hierarchy of xs.Sequence
        or xs.Choice groups present in the ComplexType's content.
        """
        try:
            return cls.__components
        except AttributeError:
            # Add all xs.Attributes to the component dictionary
            components = dict((attr.name, attr) for attr in cls.attributes)
            if cls.content:
                # Add all components from the ComplexType's content.
                components.update(cls.content.component_dict)
            # Memoize
            cls.__components = components
        return cls.__components
