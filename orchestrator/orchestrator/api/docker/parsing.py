"""A module for parsing low-level Docker API responses."""

from collections.abc import Iterable


def parse_build_response(
    response: Iterable[dict[str, str]],
) -> tuple[list[str], bool]:
    """Attempts to stringify a Docker API response for a build operation.

    Args:
        response: The response from the Docker API.

    Returns:
        A tuple of whether the building was successful,
        and the lines of the parsed response
    """
    lines = []
    succeeded = True
    for item in response:
        if "stream" in item:
            lines.append(item["stream"])
        elif "error" in item:
            lines.append(item["error"])
            succeeded = False
        elif "status" in item:
            lines.append(item["status"])
    return (lines, succeeded)
