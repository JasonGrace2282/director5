# Orchestrator

The Orchestrator is a [FastAPI](https://fastapi.tiangolo.com/) service that
manages docker containers, swarm services, and in general access
to the site directories.

## Hosting Sites

As mentioned in the [section about docker swarm](project:#docker-swarm), Director hosts sites as
services on a docker swarm.

We then use a program called [Traefik](https://traefik.io/traefik/) to route
traffic into the service. Traefik works by configuring a set of labels
on the service that tell it how to route traffic into the container.

For example, the following labels

- `` traefik.http.routers.my-site.rule=Host(`hi.example.com`) ``
- `traefik.http.routers.my-site.service=my-site-service`
- `traefik.http.services.my-site-service.loadbalancer.server.port=80`

creates a Traefik router called `my-site`. This redirects requests from
`hi.example.com` into port 80 of `my-site` service.

Traefik discovers the different swarm services by being connected to the same
overlay network as the services. This means that Traefik is also being run
on the docker swarm itself.

### Dynamic Sites

For a dynamic site, hosting it is relatively simple. The following actions
happen on site deployment:

- Choose a docker base image (either the default, or a custom one for the site)
- Start a service on the docker swarm (with the name `site_{site_id:04d}` - e.g. site_0001)
  running the base image with an entrypoint that runs the `run.sh` file.
- Give the service labels so that traefik can route requests into the service.

Additionally, there are bind mounts for things like `/site` to ensure data persistence.
Whenever a user wants to open a terminal, they can access the same docker image
used in deployment.

### Static Sites

The steps for static site deployments include:

- Start a service using the `nginx:latest` docker image
- Give the service labels so that traefik can route requests into the service.

There is significantly less configurability with static sites (by design).
Additionally, if a user wants to open a web terminal, they *do NOT* get access
to the `nginx:latest` container, but rather a default base image or a customized
base image for the site.
