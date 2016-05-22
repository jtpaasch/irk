#!/usr/bin/env python

"""A template for a long running python script.

To execute it from the command line, run it normally, like this::

    python <THIS-SCRIPT>.py --opt1 --opt2 ARG1 ARG2 ...

If you execute it from the command line, the python interpeter will
execute the ``if __name__ == "__main__"`` block at the end of the
file. That block will parse the command line arguments, then
execute the ``main()`` function.

If you import this file into some other python script, you need to
invoke the ``main()`` function yourself.

Note:
    If the --verbose/is_verbose flag is on, this program will
    report anything sent to the ``log()`` function to STDERR. 
    It's a good idea to report everything the program does
    via the ``log()`` function, for debugging.

"""

import logging
import os
import subprocess
import sys
import time


TEXT_BOLD = '\033[01m'
TEXT_OK = '\033[92m'
TEXT_WARNING = '\033[93m'
TEXT_ERROR = '\033[91m'
TEXT_RESET = '\033[0m'

STDOUT_MESSAGE_FORMAT = '%(message)s'
STDOUT_DATE_FORMAT = '%m/%d/%Y %I:%M:%S %p'

STDERR_MESSAGE_FORMAT = '%(message)s'
STDERR_DATE_FORMAT = '%m/%d/%Y %I:%M:%S %p'

VERBOSE_MESSAGE_FORMAT = '%(asctime)s - ' + \
    '%(name)s - ' + \
    '%(levelname)s - ' + \
    '%(message)s'
VERBOSE_DATE_FORMAT = '%m/%d/%Y %I:%M:%S %p'

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_formatter = logging.Formatter(
    STDOUT_MESSAGE_FORMAT, 
    datefmt=STDOUT_DATE_FORMAT)
stdout_handler.setFormatter(stdout_formatter)

stdout_log = logging.getLogger("stdout-log")
stdout_log.addHandler(stdout_handler)
stdout_log.setLevel(logging.DEBUG)

stderr_handler = logging.StreamHandler(sys.stderr)
stderr_formatter = logging.Formatter(
    STDERR_MESSAGE_FORMAT,
    datefmt=STDERR_DATE_FORMAT)
stderr_handler.setFormatter(stderr_formatter)

stderr_log = logging.getLogger("stderr-log")
stderr_log.addHandler(stderr_handler)
stderr_log.setLevel(logging.DEBUG)

verbose_handler = logging.StreamHandler(sys.stderr)
verbose_formatter = logging.Formatter(
    VERBOSE_MESSAGE_FORMAT,
    datefmt=VERBOSE_DATE_FORMAT)
verbose_handler.setFormatter(verbose_formatter)

verbose_log = logging.getLogger("verbose-log")
verbose_log.addHandler(verbose_handler)
verbose_log.setLevel(logging.DEBUG)


def format_for_tty(text, formats):
    """Format text for output to a TTY."""
    pre = "".join(formats) if formats else ""
    post = TEXT_RESET if formats else ""
    return pre + text + post


def echo(text):
    """Safely echo output to STDOUT."""
    stdout_log.info(text)


def emphasize(text):
    """Safely echo error to STDERR."""
    output = text
    if sys.stderr.isatty():
        output = format_for_tty(text, [TEXT_BOLD])
    stdout_log.info(output)


def warning(text):
    """Safely echo a warning to STDERR."""
    output = text
    if sys.stderr.isatty():
        output = format_for_tty(text, [TEXT_WARNING, TEXT_BOLD])
    stderr_log.warning(output)


def error(text):
    """Safely echo an error to STDERR."""
    output = text
    if sys.stderr.isatty():
        output = format_for_tty(text, [TEXT_ERROR, TEXT_BOLD])
    stderr_log.error(output)


def log(text, is_verbose):
    """Safely echo to the verbose log."""
    if is_verbose:
        verbose_log.info(text)


def usage():
    """Print the usage for the command."""
    echo("Usage: python " + str(__file__) + " [Options] [Arguments]")
    echo("")
    echo("  A description of what the program does goes here.")
    echo("")
    echo("")
    echo("Options:")
    echo("  -h --help     Display this help.")
    echo("  -v --verbose  Show verbose logging details.")
    echo("")
    echo("Arguments:")
    echo("  FOO           Something something something.")
    echo("")
    echo("Example:")
    echo("  python " + str(__file__) + " --verbose bar")


def irk(is_verbose):
    from .. import sock
    sock.start(echo, emphasize, warning, error, lambda x: log(x, is_verbose))


def main(foo, wait=30, is_verbose=False):
    """This starts the main program loop.

    Args:

        foo
            Some argument.

        wait
            How long to sleep for each iteration.

        is_verbose
            True if you want to write to the verbose log. False if not.

    """
    log("Executing main()...", is_verbose)
    try:
        irk(is_verbose)
        while True:
            log("Waking up...", is_verbose)

            # Do what you need to do.
            log("Nothing to do...", is_verbose)

            log("Sleeping " + str(wait) + " seconds...", is_verbose)
            time.sleep(wait)
            
    # Trap exits so we can handle them.
    except KeyboardInterrupt:
        echo("")
        warning("You killed the process. Goodbye.")
        log("User killed the process. Goodbye.", is_verbose)
    except SystemExit:
        error("The system exited the process. Goodbye.")
        log("System exited the process. Goodbye.", is_verbose)


def entrypoint():
    """Parses arguments from the command line and starts the program."""
    # Are we showing verbose logging details?
    is_verbose = False

    # What is the default sleep time for each execution loop?
    wait = 1

    # What is the FOO argument?
    foo = None

    # Parse the command line arguments.
    args = sys.argv
    arg_index = 1
    num_args = len(args)
    while arg_index < num_args:
        arg = args[arg_index]

        # The --help option.
        if arg in ["-h", "--help"]:
            usage()
            sys.exit(1)

        # The --verbose option.
        elif arg in ["-v", "--verbose"]:
            is_verbose = True

        # Any other options (it start with a dash) are unrecognized.
        elif arg.startswith("-"):
            error("Unrecognized option: " + str(arg))
            sys.exit(1)

        # Anything else must be an argument.
        else:

            # The first argument should be FOO.
            if not foo:
                foo = arg

            # We don't recognize any other arguments.
            else:
                error("Unrecognized argument: " + str(arg))
                sys.exit(1)

        arg_index += 1

    # Make sure the FOO argument was provided.
    log("The user provided this value for FOO: " + str(foo), is_verbose)
    if not foo:
        error("Missing required argument: FOO.")
        sys.exit(1)

    # Start the program.
    main(foo, wait, is_verbose)


if __name__ == "__main__":
    """In case the user executes the script directly."""
    entrypoint()
