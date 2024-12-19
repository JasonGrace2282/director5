# Basic service

Sample input for `update-docker-service`

```py
{
  "pk": 0,
  "hosts": [
    "site-0.localhost"
  ],
  "is_served": true,
  "resource_limits": {
    "cpus": 1,
    "memory": "100MiB"
  },
  "docker": {
    "base": "python:3.12-slim"
  }
}
```
You will also need to create a `run.sh` in `docker/storage/sites/00/00/public/run.sh`
