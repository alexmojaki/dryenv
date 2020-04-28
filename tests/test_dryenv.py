import os

from dryenv import DryEnv, populate_globals

os.environ.update(
    STUFF_FOO="3",
    STUFF_BAR="4",
    STUFF_SPAM="5",
    TOP="False",
    PRE_P1="100",
)


class Root(DryEnv):
    TOP = True


class STUFF(DryEnv):
    FOO = 1
    BAR = 2
    DEFAULTED = 0


class CUSTOM_PREFIX(DryEnv):
    class Config:
        env_prefix = "PRE_"

    P1 = 9


class stuff(DryEnv):
    foo = 1
    bar = 2
    defaulted = 0


populate_globals()


def test_stuff():
    assert type(STUFF) is type(STUFF())
    assert isinstance(STUFF, DryEnv)

    for stuff_obj in [STUFF, STUFF()]:
        assert stuff_obj.FOO == 3
        assert stuff_obj.BAR == 4
        assert stuff_obj.DEFAULTED == 0
        assert stuff_obj.dict() == {
            "FOO": 3,
            "BAR": 4,
            "DEFAULTED": 0,
        }
        assert stuff_obj.prefixed_dict() == {
            "STUFF_FOO": 3,
            "STUFF_BAR": 4,
            "STUFF_DEFAULTED": 0,
        }


def test_root():
    assert Root.TOP is False
    assert Root().dict() == Root().prefixed_dict() == {"TOP": False}


def test_custom_prefix():
    assert CUSTOM_PREFIX.P1 == 100
    assert CUSTOM_PREFIX().dict() == {"P1": 100}
    assert CUSTOM_PREFIX().prefixed_dict() == {"PRE_P1": 100}


# noinspection PyUnresolvedReferences
def test_populate_globals():
    assert STUFF_FOO == 3
    assert STUFF_BAR == 4
    assert STUFF_DEFAULTED == 0
    assert TOP is False
    assert PRE_P1 == 100


def test_case_insensitivity():
    assert stuff.foo == 3
    assert stuff.bar == 4
    assert stuff.defaulted == 0
    assert stuff().dict() == {
        "foo": 3,
        "bar": 4,
        "defaulted": 0,
    }
    assert stuff().prefixed_dict() == {
        "stuff_foo": 3,
        "stuff_bar": 4,
        "stuff_defaulted": 0,
    }
