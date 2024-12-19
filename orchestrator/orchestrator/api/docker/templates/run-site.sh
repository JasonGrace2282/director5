# This is the script used to run a site.
# We look for a run.sh file in this script to avoid
# rebuilding the docker image if it changes.

date +'DIRECTOR: Starting server at %Y-%m-%d %H:%M:%S %Z'

# This is filled in by the orchestrator
for path in $SEARCH_PATH; do
    echo "Checking $path..."
    if [ -x "$path" ]; then
        term() {
            date +'DIRECTOR: Stopping server at %Y-%m-%d %H:%M:%S %Z'
            kill "$child"
        }
        trap term TERM

        "$path" &
        child="$!"

        while ! wait; do true; done
        exec date +'DIRECTOR: Stopped server at %Y-%m-%d %H:%M:%S %Z'
    fi
done
echo 'DIRECTOR: No run.sh file found -- if it exists, make sure it is set as executable'
exec sleep infinity
