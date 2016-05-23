# -*- coding: utf-8 -*-

"""Starts an IRC client."""

import sys

from . import exceptions
from . import ircsocket


LINESEP = "\r\n"


def login(host, port, vlog):
    sock = ircsocket.connect(host, port, vlog)

    msg = "PASS to-wong-foo" + LINESEP
    vlog(msg)
    ircsocket.send(sock, msg, vlog)

    msg = "NICK jt2222" + LINESEP
    vlog(msg)
    ircsocket.send(sock, msg, vlog)

    msg = "USER paul 8 * : Paul Muttonchops" + LINESEP
    vlog(msg)
    ircsocket.send(sock, msg, vlog)

    return sock


def parse_input(sock, data, vlog):
    words = data.split()

    cmd = words[0]
    cmd = cmd.upper()

    msg = cmd + " " + " ".join(words[1:]) + LINESEP
    vlog("SENDING: " + msg)
    ircsocket.send(sock, msg, vlog)

    return cmd != "QUIT"


def parse_output(data, echo):
    echo(data)


def start(host, port, echo, error, vlog):

    try:
        sock = login(host, port, vlog)
    except exceptions.CouldNotConnect as login_error:
        error(str(login_error))
        sys.exit()

    # TO DO: catch SendFailed and ConnectionBroken.
    # Be sure to close connections first though.
    # For that, you need the thread and the thread_should_stop event.
    ircsocket.start(sock, 
        lambda x: parse_input(sock, x, vlog), 
        lambda x: parse_output(x, echo), 
        vlog)

    echo("Goodbye.")
