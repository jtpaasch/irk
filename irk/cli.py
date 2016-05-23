# -*- coding: utf-8 -*-

"""The CLI for the package."""

import logging
import sys

from . import ircclient


TEXT_BOLD = '\033[01m'
TEXT_DIM = '\033[02m'
TEXT_OK = '\033[92m'
TEXT_WARNING = '\033[93m'
TEXT_ERROR = '\033[91m'
TEXT_RESET = '\033[0m'

STDOUT_MESSAGE_FORMAT = '%(message)s'
STDOUT_DATE_FORMAT = '%m/%d/%Y %I:%M:%S %p'

STDERR_MESSAGE_FORMAT = '%(message)s'
STDERR_DATE_FORMAT = '%m/%d/%Y %I:%M:%S %p'

VERBOSE_MESSAGE_FORMAT = '%(message)s'
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
    output = text
    if is_verbose:
        if sys.stderr.isatty():
            output = format_for_tty(text, [TEXT_DIM])
        verbose_log.info(output)


def usage():
    """Print the usage for the command."""
    echo("Usage: python " + str(__file__) + " [Options] [Arguments]")
    echo("")
    echo("  A dumb little IRC client.")
    echo("")
    echo("Options:")
    echo("  -h --help     Display this help.")
    echo("  -v --verbose  Show verbose logging details.")
    echo("")
    echo("Arguments:")
    echo("  HOST[:PORT]   The IRC server to connect to.")
    echo("                Defaults to port 6667.")
    echo("")
    echo("Example:")
    echo("  irk irc.freenode.net")


def main(host, port, is_verbose=False):
    """This starts the main program loop.

    Args:

        is_verbose
            True if you want to write to the verbose log. False if not.

    """
    log("Executing main()...", is_verbose)
    try:
        ircclient.start(host, port, 
            echo, error, lambda x: log(x, is_verbose))

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

    # What are the HOST and PORT arguments?
    host = None
    port = 6667

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

            # The first argument should be HOST.
            if not host:
                host = arg

            # We don't recognize any other arguments.
            else:
                error("Unrecognized argument: " + str(arg))
                sys.exit(1)

        arg_index += 1

    # Make sure the HOST argument was provided.
    log("The user provided this value for HOST: " + str(host), is_verbose)
    if not host:
        error("Missing required argument: HOST.")
        sys.exit(1)

    host_pieces = host.split(":")
    if len(host_pieces) == 2:
        host = host_pieces[0]
        port = host_pieces[1]

    # Start the program.
    main(host, port, is_verbose)


if __name__ == "__main__":
    """In case the user executes the script directly."""
    entrypoint()
