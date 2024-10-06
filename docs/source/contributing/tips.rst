###############
Tips and Tricks
###############


PostgreSQL cannot authenticate as user
--------------------------------------
Postgres is really weird, and sometimes after a
change in it's configuration it just won't authenticate.
In this case, you might also need to remove the volumes and restart::

  docker compose down -v
  docker compose up

should fix the issue. If not, you might have a problem with
the postgres configuration in Django.
