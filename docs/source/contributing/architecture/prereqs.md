# Prerequisite Knowledge

Director is all about hosting sites, which requires knowledge about
how the Internet works. If you're looking for a comprehensive guide,
[this link](https://explained-from-first-principles.com/internet/) may be useful.

If you know any of the content below, feel free to skim. It's still
recommended to skim, because some applications to Director itself
will be discussed.
00

## The Life of a Request

### An overview

Let's take a look at what happens when you type in a url. For our
purposes, we can ignore a lot of what actually happens and just
think in a model where the user makes a request, and the web application
(Django, or something else) returns a response.

```{note}
If you're interested in learning more, you can research about the
[layers of the internet](https://explained-from-first-principles.com/internet/#internet-layers),
and the [different HTTP protocol versions](https://blog.cloudflare.com/http3-the-past-present-and-future/).
```

Let's imagine we have a web application running, and we're running it on
50 machines. It doesn't make sense to expose all 50 machines to everybody
on the internet. For one, that's a huge surface of attack, and two, that
might unevenly distribute the load of requests incoming.

Instead, we place something called a *load balancer* (or Proxy) in front of our machines.
Users can only access the load balancer, and none of the machines in the internal
network. The load balancer is effectively the entrypoint to the internal network.

```{graphviz} assets/request.dot
---
name: Request Graph
---
```

The load balancer does the work of evenly distributing work, some caching,
and returning responses from the internal services back to the browser.
A common software used for this is [Nginx](https://nginx.org/).

A more complete description of the flow of events is as follows:

1. The request is first received by a server running a load balancer.
   The load balancer forwards the request to a server that can handle it.
   This way no one server is overloaded with requests while another is doing nothing.
1. A WSGI (or ASGI for async programs) server receives the request. WSGI is a standard specification for Python web servers
   to communicate with web applications. It basically translates the request into a format that the web server can understand.
   and these are often referred to as "application servers" (or appservers).
1. The web server (which is something like Django or FastAPI) processes the request, and communicates with the database.
   It then sends a response back to the server.
1. The server sends the response back to the load balancer.
1. The load balancer sends the response back to your browser.
1. The browser renders the response and displays the website.

### Applying it to Director

On Director, we have to handle traffic for both https://director.tjhsst.edu, and
all of the hosted sites. To do this, we have a setup that looks like the following.

```{graphviz} assets/director-balancer.dot
```

Effectively, we pass all requests for https://director.tjhsst.edu to the Django application,
and other urls to [Traefik](https://traefik.io/traefik/), which then sends the request to
a docker image running on the appservers. We'll talk more about the last part when
we talk about the Orchestrator.

(docker-swarm)=

## Docker Swarm

Director is able to handle different dependencies per site by using Docker containers
for each site. In order to manage these containers, Director uses Docker Swarm. Before we
start, lets talk a little bit about Docker.

- A *Docker Image* is a package with all the dependencies in an application.
- A *Docker Container* is an instance of a Docker Image that has been given a CPU and RAM to run.
  These containers are portable across all systems with Docker installed.

A `Dockerfile` is a set of instructions that tells Docker how to build an image. You start by pulling `FROM`
a base image, and then you can `RUN` commands to install dependencies, `COPY` files into the container, and more.

Docker Swarm allows you to orchestrate multiple Docker containers. It does this by having two types of nodes:

- *Manager Nodes* are responsible for managing the swarm, and scheduling tasks.
- *Worker Nodes* are responsible for running the tasks. It is these nodes that run each container for each site.

It's also important to note that Manager nodes can perform tasks as well (this is how our development setup works),
but worker nodes are the main ones designated for running services.

The point of a Docker Swarm is to run *services*. A service is something that has a docker image (such as `nginx:latest`)
and an entrypoint. These services are then (semi-)evenly distributed by the manager amongst the manager/worker nodes.
This means that if one worker node goes down, the manager can just redistribute the services on that worker node.

```{admonition} Preview
Director runs each site as a service on a swarm node! We'll talk
more about this when we talk about Traefik and the Orchestrator.
```

When debugging swarm related stuff, the following commands are useful to know:

- `docker swarm init` - starts a swarm as the manager.
- `docker service ls` - lists all services on the docker swarm.
- `docker service inspect <service> --pretty` - see details about a specific service.
- `docker service update <service> <flags to update>` - update attributes about a service.
- `docker service logs <service>` - see the logs for a service.
- `docker service ps <service> --no-trunc` - see the process status on a specific service.
- `docker node ls` - see all of the manager/worker nodes on a swarm.
- `docker container ls` - see all running containers.
