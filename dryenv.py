from collections import namedtuple
from inspect import currentframe

from pydantic import BaseSettings

try:
    from pydantic.main import ModelMetaclass
except ImportError:
    ModelMetaclass = type(BaseSettings)

__version__ = '0.0.1'
__version_info__ = namedtuple(
    'VersionInfo', ('major', 'minor', 'micro')
)(*map(int, __version__.split('.')))


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
    class Config:
        auto_init = False
        env_prefix = ""

    def prefixed_dict(self, *args, **kwargs):
        return {
            self.Config.env_prefix + k: v
            for k, v in self.dict(*args, **kwargs).items()
        }

    def __call__(self, *args, **kwargs):
        return type(self)(*args, **kwargs)


def populate_globals(globs=None):
    if globs is None:
        globs = currentframe().f_back.f_globals

    for cls in list(globs.values()):
        if isinstance(cls, DryEnv):
            globs.update(cls.prefixed_dict())
