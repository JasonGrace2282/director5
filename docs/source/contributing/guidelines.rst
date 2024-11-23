##########
Guidelines
##########

Documentation
-------------
The documentation is written in reStructuredText (``rst``). When making changes, be
sure to build it in strict mode, to make sure everything works::

  cd docs
  uv run just html-strict


Docstrings
^^^^^^^^^^

Manager
=======
Docstrings for classes and functions in the Manager should follow
the `Google Docstring format <https://gist.github.com/redlotus/3bc387c2591e3e908c9b63b97b11d24e>`_.

For example, a function that divides two numbers might be written as such

.. code-block:: python

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


Orchestrator
============

The orchestrator uses `fastapi <https://fastapi.tiangolo.com/>`_ to autogenerate it's API documentation.
``fastapi`` parses docstrings as markdown, so instead of using reStructuredText directives you will
need to use markdown. However, the same docstring format applies. For example, the previous
``divide`` function would be written as

.. code-block:: python

   class FloatResponse(BaseModel):
      result: float

   @router.get("/divide")
   def divide(a: float, b: float) -> FloatResponse:
      """Divides two numbers.

      This is an extremely complicated function with a longer
      description needed.

      ```{caution}
      This will return with a status 500 if the denominator is zero.
      ```
      """
      return FloatResponse(result=a/b)

Note that you do not have to repeat the arguments or parameters, as fastapi will
handle that automatically (just give them a descriptive name).
