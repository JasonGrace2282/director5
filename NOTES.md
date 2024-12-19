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
You will also need to create a `run.sh` in `docker/storage/sites/00/00/public/run.sh`,
with the following content

```bash
#!/bin/sh

python << EOF
import http.server as hs
import os

addr= (os.environ["HOST"], int(os.environ["PORT"]))
httpd = hs.HTTPServer(addr, hs.SimpleHTTPRequestHandler)
httpd.serve_forever()
EOF
```

Then, run the following command:
```bash
cd dev/docker
docker exec -it director_orchestrator /bin/sh
echo "<html><body>Hello World</body></html>" > /data/sites/00/00/public/index.html
```
Then go to `site-0.localhost`, and you should see a listing of all served
files. Go to `site-0.localhost/index.html` to see `Hello World`!
