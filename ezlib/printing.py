def print_succ(*args, **kwargs):
    """
    Prints a success message prefixed with '[+]', behaves like print.
    """
    print("[+]", *args, **kwargs)


def print_fail(*args, **kwargs):
    """
    Prints a failure message prefixed with '[-]', behaves like print.
    """
    print("[-]", *args, **kwargs)


def print_status(*args, **kwargs):
    """
    Prints a status message prefixed with '[*]', behaves like print.
    """
    print("[*]", *args, **kwargs)
