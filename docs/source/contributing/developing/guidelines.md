# Guidelines

## Documentation

The documentation is written in MyST-Markdown. When making changes, be
sure to build it in strict mode, to make sure everything works

```bash
cd docs
uv run just html-strict
```

While you could in theory use reStructuredText to write documentation,
markdown is strongly preferred as it's (subjectively) more intuitive.

## Docstrings

### Manager

Docstrings for classes and functions in the Manager should follow
the [Google Docstring format](https://gist.github.com/redlotus/3bc387c2591e3e908c9b63b97b11d24e).

For example, a function that divides two numbers might be written as such

```python
def divide(a: float, b: float) -> float:
    """Divides two numbers.

    This is an extremely complicated function with a longer
    description needed.

    .. caution::

      This will throw a :class:`.ZeroDivisionError` if the denominator is zero.

    Args:
        a: The numerator.
        b: The denominator.

    Returns:
        The result of the division.
    """
    return a / b
```

### Orchestrator

The orchestrator uses [FastAPI](https://fastapi.tiangolo.com/) to autogenerate it's API documentation.
`fastapi` parses docstrings as markdown, so instead of using reStructuredText directives you will
need to use markdown.
