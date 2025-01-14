# Setting up a Development Environment

## Docker

The first step is to install [docker compose](https://docs.docker.com/compose/install/).

After that, to start the development environment, simply run the following:

```bash
cd dev/docker
docker swarm init
docker compose build
docker compose up
```

And navigate to http://127.0.0.1:8080 to see the website in action!
To check out the documentation of the orchestrator (AKA the API docs),
head over to http://127.0.0.1:8000.

On future runs, you can simply run `docker compose up` to start the environment.

````{tip}
To run a set of commands in the docker containers, simply do:

```bash
cd dev/docker
# replace director_django with the service to run it in
docker exec -it director_django /bin/bash
```
For example, to create some basic users for development, run
```bash
docker exec -it director_django ./manage.py create_debug_users
```
````

## Local Development

Some things are just easier to debug locally than on docker. We use [uv](https://docs.astral.sh/uv/)
to manage our dependencies. Check out [their docs](https://docs.astral.sh/uv/getting-started/installation/)
for how to install it.

````{admonition} Installing uv
Some linux distributions already package `uv`, such as Arch Linux.
As such, it may be better to install it with your linux distributions package manager.

Alternatively, if you don't want to install it system-wide, you can install it
with pip

```bash
pip install uv
```
````

After that, you can install the dependencies with `uv sync`.

It will install `python` for you if you don't have it installed yet.
Then you can do e.g. `uv run pre-commit run --all-files` to run the linter/formatter.

```{tip}
Use ``uv run --package manager`` to run something using the dependencies of the manager.
```

### Docs

First, install [Graphviz](https://graphviz.org/download/) if you don't have `dot` installed. Then,
to edit the docs, run:

```bash
cd docs
uv run just live
```

This will start a webserver at http://127.0.0.1:8888 that will automatically rebuild
and update as you edit the docs.

To run the webserver on a different port, use

```bash
uv run just live 8080
```

## Next Steps

You're almost done! Now, we need to add some plugins that will make development easier in your IDE.
Visit [the IDE setup guide](#ide-setup).
