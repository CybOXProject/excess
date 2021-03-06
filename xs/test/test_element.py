import pytest

import xs


def test_element_str():
    element = xs.Element("lastname", xs.String)
    assert str(element) == "lastname (String)"


def test_create_top_level_element():
    name = xs.TopLevelElement("lastname", xs.String, value="Refnes")
    assert name.value == "Refnes"
    assert xs.serialize(name) == b"<lastname>Refnes</lastname>"


def test_create_top_level_element_from_element():
    name_element = xs.Element("lastname", xs.String)
    name = name_element("Refnes")

    assert isinstance(name, xs.TopLevelElement)
    assert name.value == "Refnes"
    assert type(name.value) == xs.compat.str
    assert xs.serialize(name) == b"<lastname>Refnes</lastname>"


def test_error_when_exporting_empty_top_level_element():
    name_element = xs.TopLevelElement("lastname", xs.String)

    with pytest.raises(ValueError):
        xs.serialize(name_element)

def test_create_inner_list():
    with pytest.raises(TypeError):
        # _InnerList requires a type argument
        foo = xs.element._InnerList()

    with pytest.raises(TypeError):
        foo = xs.element._InnerList("a")

def test_inner_list_repr():
    """Test that the string representation of an _InnerList matches a list."""
    integer_list = xs.element._InnerList(xs.Integer)
    integer_list.append(1)
    integer_list.append(2)
    assert repr(integer_list._inner) == repr(integer_list)


def test_add_to_inner_list():
    integer_list = xs.element._InnerList(xs.Integer)
    integer_list.append(1)
    integer_list.append(2)
    integer_list.append("3")

    with pytest.raises(ValueError):
        integer_list.append("a")

def test_add_complex_type_to_inner_list():
    class DictionaryItem(xs.ComplexType):
        content = xs.Sequence(
            xs.Element("key", xs.String),
            xs.Element("value", xs.String),
        )

    dictionary = xs.element._InnerList(DictionaryItem)
    d1 = DictionaryItem()
    d1.key = "foo"
    d1.value = "bar"
    d2 = DictionaryItem()
    d2.key = "foo2"
    d2.value = "baz"
    dictionary.extend([d1, d2])
    assert 2 == len(dictionary)

def test_inner_list_max_len():
    int_list = xs.element._InnerList(xs.Integer, max_len=xs.UNBOUNDED)
    int_list = xs.element._InnerList(xs.Integer, max_len=0)
    int_list = xs.element._InnerList(xs.Integer, max_len="3")

    with pytest.raises(ValueError):
        int_list = xs.element._InnerList(xs.Integer, max_len="a")
    with pytest.raises(ValueError):
        int_list = xs.element._InnerList(xs.Integer, max_len=-1)

    int_list = xs.element._InnerList(xs.Integer, max_len=3)
    int_list.append(1)
    int_list.append(2)
    int_list.append(3)
    assert 3 == len(int_list)

    with pytest.raises(IndexError):
        int_list.insert(0, 4)

    with pytest.raises(IndexError):
        int_list.append(4)
    with pytest.raises(IndexError):
        int_list.extend([4])

    int_list[0] = 4

    assert 3 == len(int_list)

def test_inner_list_eq():
    int_list = xs.element._InnerList(xs.Integer)
    int_list2 = xs.element._InnerList(xs.Integer)
    posint_list = xs.element._InnerList(xs.PositiveInteger)

    assert int_list == int_list2
    assert posint_list != int_list # lists have different types
    int_list.append(1)
    assert int_list == [1]
    assert int_list == [1.0] # int 1 and float 1.0 will be implictly compared.
    assert int_list != int_list2

    int_list2.append(1.0)
    assert int_list == int_list2

    posint_list.append(1)
    assert posint_list != int_list # lists have different types

    # These should never be equal to other "types" of objects
    assert int_list != object()
    assert int_list != True
    assert int_list != int

def test_invalid_element_ref():
    with pytest.raises(ValueError):
        xs.Element()

    with pytest.raises(ValueError):
        xs.Element("A string")

    with pytest.raises(ValueError):
        xs.Element(type_=xs.Integer)

def test_element_ref():
    element = xs.Element("lastname", xs.String, default="foo")
    elementref = xs.Element(ref=element, default="foo2", min_occurs=0)
    assert element.default == "foo"
    assert elementref.default == "foo2"
    assert element._min_occurs == 1
    assert elementref._min_occurs == 0

    element.name = "newname"
    assert elementref.name == "lastname"
    element.type_ = xs.Decimal
    assert elementref.type_ == xs.String
