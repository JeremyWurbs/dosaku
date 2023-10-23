"""Utility methods relating to cleaning and handling code."""


def clean_code(code: str) -> str:
    """Cleans the given python code.

    It is anticipated that the code being given has been generated from an AI and, as such, may contain markdown (e.g.
    ```python) or other non-delimited comments explaining the code. This method attempts to strip out all non-python
    extraneous components and return only python code.

    Args:
        code: The input code string to clean.

    Returns:
        The cleaned code. If no ```python block is detected the original code will be returned. If multiple ```python
        blocks are found, only the first will be returned.
    """
    if len(code.split('```python\n')) == 1:  # no ```python block was found
        return code
    else:
        return code.split('```python\n')[-1].split('```')[0]
