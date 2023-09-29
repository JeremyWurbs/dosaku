"""Utility methods relating to the os."""
import os


def available_cores():
    """Returns the number of cores available to the current process."""
    try:
        available_cores = len(os.sched_getaffinity(0))  # Not currently supported for Windows
        return available_cores
    except:
        return num_cores()


def num_cores():
    """Returns the number of cores visible to the OS."""
    return os.cpu_count()
