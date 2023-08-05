# dryenv

[![Build Status](https://travis-ci.org/alexmojaki/dryenv.svg?branch=master)](https://travis-ci.org/alexmojaki/dryenv) [![Coverage Status](https://coveralls.io/repos/github/alexmojaki/dryenv/badge.svg?branch=master)](https://coveralls.io/github/alexmojaki/dryenv?branch=master) [![Supports Python versions 3.6+](https://img.shields.io/pypi/pyversions/dryenv.svg)](https://pypi.python.org/pypi/dryenv)

Simple configuration with environment variables and pydantic, without repeating yourself!

    pip install dryenv

- [Basic usage](#basic-usage)
- [Based on pydantic.](#based-on-pydantic)
- [Configuring DryEnv](#configuring-dryenv)
- [Additional features](#additional-features)
- [Usage with Django and PyCharm](#usage-with-django-and-pycharm)

## Basic usage

For example, instead of writing:

```python
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
```

write:

```python
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
```

or even:

```python
# settings.py

from dryenv import DryEnv

class DATABASE(DryEnv):
    # Looking up environment variables is case-insensitive
    host = "localhost"
    username = "admin"
    password = "secretpassword"
    timeout = 10
    persist_connection = True

# database.py

from settings import DATABASE

connection = connect(**DATABASE.dict())
```

## Based on pydantic.

`DryEnv` is a thin wrapper around [`pydantic.BaseSettings`](https://pydantic-docs.helpmanual.io/usage/settings/), which does most of the heavy lifting. `DryEnv` makes things a little neater and more convenient by automatically:

1. Setting `env_prefix` based on the class name, unless the class name is `Root` (case insensitive) in which case the prefix is empty.
2. Instantiating the class to trigger the environment lookups.

For example, this:

```python
from dryenv import DryEnv

class DATABASE(DryEnv):
    HOST = "localhost"
    USERNAME = "admin"
    PASSWORD = "secretpassword"
    TIMEOUT = 10
    PERSIST_CONNECTION = True
```

is roughly equivalent to:

```python
from pydantic import BaseSettings

class DATABASE(BaseSettings):
    class Config:
        env_prefix = "DATABASE_"

    HOST = "localhost"
    USERNAME = "admin"
    PASSWORD = "secretpassword"
    TIMEOUT = 10
    PERSIST_CONNECTION = True

DATABASE = DATABASE()
```

Here are the most important points about what pydantic provides:

1. You can omit the default value and just declare a variable with a type annotation, e.g. `HOST: str`. This makes the setting required.
2. Variables will be parsed based on their type, which is determined by the annotation or the default value.
3. For most simple field types (such as int, float, str, etc.), the environment variable value is parsed the same way it would be if passed directly to the initialiser (as a string). Booleans are parsed more intelligently, [see here](https://pydantic-docs.helpmanual.io/usage/types/#booleans). Complex types like list, set, dict, and sub-models are populated from the environment by treating the environment variable's value as a JSON-encoded string.

For more information [read the pydantic documentation](https://pydantic-docs.helpmanual.io/usage/settings/).

This package could quite easily be part of pydantic itself. If you'd like that, [vote on the issue here](https://github.com/samuelcolvin/pydantic/issues/1450).

## Configuring DryEnv

You can override the automatic `env_prefix` setting by either:

- Naming your class `Root` (case insensitive) in which case the prefix is empty, or
- Setting `env_prefix` as normal under the `Config` class.

You can turn off the automatic instantiation by setting `auto_init = False` in the `Config`.

You can instantiate `DryEnv` yourself with your own constructor arguments by simply calling it as if it were the class. You can also access the class itself as normal with `type()`.

## Additional features

The instance method **`DryEnv.prefixed_dict()`** is similar to pydantic's `dict()`, but the `env_prefix` is included in the keys, so they match the original environment variable names.

For example:

```python
class DATABASE(DryEnv):
    HOST = "localhost"
    USERNAME = "admin"

assert DATABASE.dict() == {"HOST": "localhost", "USERNAME": "admin"}
assert DATABASE.prefixed_dict() == {"DATABASE_HOST": "localhost", "DATABASE_USERNAME": "admin"}
```

The function **`populate_globals()`** will search for instances of `DryEnv` in the global variables in the calling context and then update the global variables with the `prefixed_dict()` of those `DryEnv` isntances. For example, if you called `populate_globals()` after the example above, `DATABASE_HOST` and `DATABASE_USERNAME` would become global variables. This is useful in e.g. Django where settings need to be declared at the global level. You can pass your own dict for the function to use instead of the current global variables.

## Usage with Django and PyCharm

If you use PyCharm with the Django integration, it's able to intelligently inspect and navigate to values in `django.conf.settings`...most of the time. For some reason a class declared in `settings.py` doesn't work, so you can't navigate to the definition of a `DryEnv` or autocomplete its values. To work around this, I suggest you:

1. Declare appropriate settings in a different file e.g. `simple_settings.py`.
2. Import values from there in your apps instead of `django.conf.settings` so that PyCharm understands them.
3. In your `settings.py`, write `from simple_settings import *` and call `populate_globals()` in one of the settings files. This will allow Django and libraries to find settings like `DEBUG` and `SECRET_KEY` at the global level while letting you define them with `dryenv` and then forgetting about them.

Alternatively, you can add the line `DATABASE = DATABASE` or `DATABASE = DATABASE()` and then PyCharm will recognise this as a normal variable instead of a class.
