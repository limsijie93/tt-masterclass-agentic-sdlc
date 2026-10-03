"""myapp: a small reporting and billing service.

No auth, no migrations, no deployment, no front end. One SQLite database per connection.

Layers, enforced by .importlinter and not by this docstring:

    myapp.api  ->  myapp.service  ->  myapp.repo

myapp.tasks sits outside that order: it may call myapp.service and must never reach back up
into myapp.api. Both rules are contracts in .importlinter.
"""

__all__ = ["__version__"]

__version__ = "0.1.0"
