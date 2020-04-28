# dryenv

[![Build Status](https://travis-ci.org/alexmojaki/dryenv.svg?branch=master)](https://travis-ci.org/alexmojaki/dryenv) [![Coverage Status](https://coveralls.io/repos/github/alexmojaki/dryenv/badge.svg?branch=master)](https://coveralls.io/github/alexmojaki/dryenv?branch=master) [![Supports Python versions 3.6+](https://img.shields.io/pypi/pyversions/dryenv.svg)](https://pypi.python.org/pypi/dryenv)

Simple configuration with environment variables and pydantic, without repeating yourself!

For example, instead of writing:

```python
# settings.py

import os

DATABASE_HOST = os.getenv("DATABASE_HOST", "localhost")
DATABASE_USERNAME = os.getenv("DATABASE_USERNAME", "admin")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD", "secretpassword")

# database.py

import settings

connection = connect(
    host=settings.DATABASE_HOST,
    username=settings.DATABASE_USERNAME,
    password=settings.DATABASE_PASSWORD,
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

# database.py

from settings import DATABASE

connection = connect(
    host=DATABASE.HOST,
    username=DATABASE.USERNAME,
    password=DATABASE.PASSWORD,
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

# database.py

from settings import DATABASE

connection = connect(**DATABASE.dict())
```

`DryEnv` is simply a thin wrapper around [`pydantic.BaseSettings`](https://pydantic-docs.helpmanual.io/usage/settings/), which does most of the heavy lifting. `DryEnv` just makes things a little neater and more convenient by automatically:

1. Setting `env_prefix` based on the class name.
2. Instantiating the class to trigger the environment lookups.
 
For example, this:

```python
from dryenv import DryEnv

class DATABASE(DryEnv):
    HOST = "localhost"
    USERNAME = "admin"
    PASSWORD = "secretpassword"
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

DATABASE = DATABASE()
```
