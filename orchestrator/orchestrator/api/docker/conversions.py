"""Module containing conversion functions for Docker API objects."""


def cpu_to_nano_cpus(cpu: float) -> float:
    """Convert a CPU value to nano CPUs.

    Docker expects the CPU value to be in nano-CPUs.
    """
    return cpu * 1e9


def convert_memory_limit(memory: int | str) -> int:
    """Converts a memory limit into its equivalent in bytes.

    Args:
        memory: String or integer representation of memory limit.

    Throws:
        ValueError: If the memory limit is not a valid string.

    Returns:
        The provided memory in bytes.
    """
    if isinstance(memory, int):
        return memory

    # MUST be sorted by longest suffix
    suffixes = [
        ("bytes", 1),
        ("KiB", 1024),
        ("MiB", 1024**2),
        ("GiB", 1024**3),
        ("KB", 1000),
        ("MB", 1000**2),
        ("GB", 1000**3),
        ("B", 1),
        ("K", 1024),
        ("M", 1024**2),
        ("G", 1024**3),
        ("b", 1),
        ("k", 1000),
        ("m", 1000**2),
        ("g", 1000**3),
    ]

    for suffix, factor in suffixes:
        if memory.endswith(suffix):
            return factor * int(memory.removesuffix(suffix).strip())

    return int(memory)
