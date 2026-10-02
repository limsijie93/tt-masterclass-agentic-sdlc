"""myapp — the deliberately minimal service the worked example is written against.

It exists to be broken in five specific ways (see docs/demos.md), and for nothing else. It is
not a product: no auth, no migrations, no deployment, no front end. Read
example/PROJ-142/README.md for the ticket it is shaped by.

Layers, enforced by .importlinter and not by this docstring:

    myapp.api  ->  myapp.service  ->  myapp.repo

myapp.tasks sits outside that order: it may call myapp.service and must never reach back up
into myapp.api. Both rules are contracts in .importlinter.
"""

__all__ = ["__version__"]

__version__ = "0.1.0"
