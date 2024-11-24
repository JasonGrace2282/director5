# Django Extensions

We include a lot of django plugins to make development easier.

## django-debug-toolbar

In `DEBUG`, there's a little box on the side of the screen that says "DJ". Click
to expand that, and you can enable different options for profiling, validating,
and looking at queries!

## django-browser-reload

With this plugin, every time you change a template, it will rerender it and update your
browser tab *without having to reload*!

## django-fastdev

This plugin does a lot of boring stuff that's really helpful, like validating templates,
improving startup time, and improving error messages for `reverse` and `QuerySet.get`.

## django-watchfiles

This reduces memory usage by swapping out the default django `stat`-based reloader
for a custom one based off of `watchfiles`.

## django-extensions

This package comes with a LOT of useful features: check out [their docs](https://django-extensions.readthedocs.io/en/latest/).

### Better Error Page

When using `manage.py runserver_plus` (the default in the docker container), the error page
is swapped out to use Werkzeug. This gives us a [lot more](https://django-extensions.readthedocs.io/en/latest/runserver_plus.html#usage)
debugging possibilities. For example, we can view the source code that raised an
error, and even run an interactive debugging console!

### Better shell

`django-extensions` has a replacement for `manage.py shell`: `manage.py shell_plus`!
This autoimports all the models in the django application.

## django-linear-migrations

This will produce a merge conflict if two migrations with the same number are created,
warning you that there is something that needs to be fixed.

It also comes with helpful commands to fix the migrations, such as

```bash
uv run ./manage.py rebase_migration <app_label>
```
