from collections import namedtuple
from inspect import currentframe
from typing import Any, Dict

from pydantic import BaseSettings

try:
    from pydantic.main import ModelMetaclass
except ImportError:  # pragma: no cover
    ModelMetaclass = type(BaseSettings)

__version__ = "0.1.0"
__version_info__ = namedtuple("VersionInfo", ("major", "minor", "micro"))(
    *map(int, __version__.split("."))
)

__all__ = ["DryEnvMeta", "populate_globals"]


class DryEnvMeta(ModelMetaclass):
    def __new__(mcs, name, bases, namespace):
        Config = namespace.setdefault("Config", type("Config", (), {}))
        if not hasattr(Config, "env_prefix"):
            if name.lower() == "root":
                Config.env_prefix = ""
            else:
                Config.env_prefix = name + "_"

        cls = super().__new__(mcs, name, bases, namespace)
        if not getattr(Config, "auto_init", True):
            return cls
        else:
            return cls()


class DryEnv(BaseSettings, metaclass=DryEnvMeta):
    """
    Base class for declaring configuration from environment variables.
    See the README: https://github.com/alexmojaki/dryenv
    and the pydantic documentation for BaseSettings: https://pydantic-docs.helpmanual.io/usage/settings/

    For example, instead of writing:

        # settings.py

        import os

        DATABASE_HOST = os.getenv("DATABASE_HOST", "localhost")
        DATABASE_USERNAME = os.getenv("DATABASE_USERNAME", "admin")
        DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD", "secretpassword")
        DATABASE_TIMEOUT = int(os.getenv("DATABASE_TIMEOUT", 10))
        DATABASE_PERSIST_CONNECTION = os.getenv("DATABASE_PERSIST_CONNECTION", "true").lower() == "true"

        # database.py

        import settings

        connection = connect(
            host=settings.DATABASE_HOST,
            username=settings.DATABASE_USERNAME,
            password=settings.DATABASE_PASSWORD,
            timeout=settings.DATABASE_TIMEOUT,
            persist_connection=settings.DATABASE_PERSIST_CONNECTION,
        )

    write:

        # settings.py

        from dryenv import DryEnv

        class DATABASE(DryEnv):
            HOST = "localhost"
            USERNAME = "admin"
            PASSWORD = "secretpassword"
            TIMEOUT = 10
            PERSIST_CONNECTION = True

        # database.py

        from settings import DATABASE

        connection = connect(
            host=DATABASE.HOST,
            username=DATABASE.USERNAME,
            password=DATABASE.PASSWORD,
            timeout=DATABASE.TIMEOUT,
            persist_connection=DATABASE.PERSIST_CONNECTION,
        )
    """

    class Config:
        auto_init = False
        env_prefix = ""

    def prefixed_dict(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Similar to pydantic's `dict()`, but the `env_prefix` is included in the keys,
        so they match the original environment variable names.

        For example:

            class DATABASE(DryEnv):
                HOST = "localhost"
                USERNAME = "admin"

            assert DATABASE.dict() == {"HOST": "localhost", "USERNAME": "admin"}
            assert DATABASE.prefixed_dict() == {"DATABASE_HOST": "localhost", "DATABASE_USERNAME": "admin"}
        """
        return {
            self.Config.env_prefix + k: v for k, v in self.dict(*args, **kwargs).items()
        }

    def __call__(self, *args, **kwargs) -> "DryEnv":
        """
        Instantiate this class as if you were calling the class itself.
        """
        return type(self)(*args, **kwargs)


def populate_globals(globs=None):
    """
    Search for instances of `DryEnv` in the global variables in the calling context
    and then update the global variables with the `prefixed_dict()` of those `DryEnv` isntances.
    For example, this code::

        class DATABASE(DryEnv):
            HOST = "localhost"
            USERNAME = "admin"

        populate_globals()

    will result in global variables `DATABASE_HOST` and `DATABASE_USERNAME`.

    This is useful in e.g. Django where settings need to be declared at the global level.

    You can pass your own dict for the function to use instead of the current global variables.
    """
    if globs is None:
        globs = currentframe().f_back.f_globals

    for cls in list(globs.values()):
        if isinstance(cls, DryEnv):
            globs.update(cls.prefixed_dict())
