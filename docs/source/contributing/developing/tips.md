# Tips and Tricks

## PostgreSQL cannot authenticate as user

There is a chance that there is another application running that is
using the same volume that we use for Director. Try giving the volume
of the other application a non-conflicting name.
