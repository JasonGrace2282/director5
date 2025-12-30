from functools import wraps


def guidelines_not_required(view_func):
    """Decorator to disable the :class:`RequireGuidelinesMiddleware` for a view"""
    def wrapped_view(*args, **kwargs):
        return view_func(*args, **kwargs)

    wrapped_view._skip_guidelines_middleware = True
    return wraps(view_func)(wrapped_view)
