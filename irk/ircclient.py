# -*- coding: utf-8 -*-

"""Starts an IRC client."""

import sys
import threading

from . import exceptions
from . import ircsocket


LINESEP = "\r\n"
"""IRC likes a \r\n, though most accept a \n."""


def connect_to_irc(host, port, vlog):
    """Connect to an IRC server.

    Args:

        host
            The host to connect to.

        port
            The port to use.

        vlog
            A verbose logger to pass messages to.

    Return:
        An open socket connected to the server, or the
        program exits if it cannot connect.

    """
    try:
        sock = ircsocket.connect(host, port, vlog)
    except exceptions.CouldNotConnect as connect_error:
        error(str(connect_error))
        sys.exit()
    return sock


def login(sock, vlog):
    """Login to an IRC server.

    Args:

        sock
            An open socket to login over.

        vlog
            A verbose logger to pass messages to.

    """
    msg = "PASS to-wong-foo" + LINESEP
    vlog(msg)
    ircsocket.send(sock, msg, vlog)

    msg = "NICK jt2222" + LINESEP
    vlog(msg)
    ircsocket.send(sock, msg, vlog)

    msg = "USER paul 8 * : Paul Muttonchops" + LINESEP
    vlog(msg)
    ircsocket.send(sock, msg, vlog)


def parse_input(sock, data, vlog):
    """Convert input into IRC commands and send them to the server.

    Args:

        sock
            An open socket to login over.

        data
            The data entered by the user.

        vlog
            A verbose logger to pass messages to.

    Return:
        True if its okay to continue; False if not.

    """
    words = data.split()

    cmd = words[0]
    cmd = cmd.upper()

    msg = cmd + " " + " ".join(words[1:]) + LINESEP
    vlog("SENDING: " + msg)
    ircsocket.send(sock, msg, vlog)

    return cmd != "QUIT"


def parse_output(data, echo):
    """Parse output received from the server.

    Args:

        data
            Data received from the server.

        echo
            A logger to pass the parsed data to.

    """
    # Break up the data into words.
    words = data.split()

    # If there's a prefix, the first word starts with a colon
    prefix = None
    if words[0].startswith(":"):
        prefix = words[0][1:]
        words.pop(0)

    # The command is the next word.
    command = None
    if words:
        command = words[0]
        words.pop(0)

    # The params are everything up to the next colon.
    params = []
    is_param = True
    while is_param:
        if words and not words[0].startswith(":"):
            params.append(words[0])
            words.pop(0)
        else:
            is_param = False

    # The tail is the rest.
    tail = []
    if words:
        tail.extend(words)

    output = command + " " + " ".join(tail)

    # echo(output)
    echo(data)


def start(host, port, echo, error, vlog):
    """Start an IRC client.

    Args:

        host
            The host to connect to.

        port
            The port to use.

        echo
            A logger to pass output messages to.

        error
            A logger to pass error messages to.

        vlog
            A verbose logger to pass messages to.

    """
    sock = connect_to_irc(host, port, vlog)
    login(sock, vlog)

    # Start listening on the socket in a separate thread.
    thread_should_stop = threading.Event()
    args = (sock, thread_should_stop, lambda x: parse_output(x, echo), vlog)
    thread = threading.Thread(target=ircsocket.receive, args=args)
    thread.start()

    # Listen for input from the user in this thread.
    keep_alive = True
    try:
        while keep_alive:
            raw_entered_data = input()
            entered_data = raw_entered_data.strip()

            if entered_data:
                vlog("STDIN: " + str(entered_data))
                keep_alive = parse_input(sock, entered_data, vlog)

    # If the user exits, or the system exits, disconnect first.
    except (KeyboardInterrupt, SystemExit):
        vlog("")
        vlog("Caught exit signal...")
        ircsocket.disconnect(sock, thread, thread_should_stop, vlog)
        vlog("Re-raising exit signal...")
        raise

    # Disconnect before stopping.
    vlog("")
    vlog("Nothing left to do.")
    ircsocket.disconnect(sock, thread, thread_should_stop, vlog)
    echo("Goodbye.")
