def _check_regex():
    """Checks if regex is installed and returns it as a module.

    Returns:
        module: regex module.
    """
    try:
        import regex

        return regex
    except ImportError:
        raise ImportError(
            '"regex" is not installed. Please install "regex" -> "pip install regex"'
        )

def _check_jsbeautifier():
    """Checks if jsbeautifier is installed and returns it as a module.

    Returns:
        module: jsbeautifier module.
    """
    try:
        from jsbeautifier import beautify, default_options

        return beautify, default_options
    except ImportError:
        raise ImportError(
            '"jsbeautifier" is not installed. Please install "jsbeautifier" -> "pip install jsbeautifier"'
        )