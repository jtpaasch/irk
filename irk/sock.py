# -*- coding: utf-8 -*-

"""Socket wrapper."""

import os
import socket
import sys


def exit_clean(sock, error):
    error("Closing socket.")
    sock.close()
    sys.exit()


def connect(address, echo, emphasize, warning, error, vlog):
    try:
        sock = socket.create_connection(address)
    except socket.error as socket_error:
        error("Socket not created: " + str(socket_error))
        error("Could not connect to: " + str(address[0]) 
            + ":" + str(address[1]))
        sys.exit()
    emphasize("Connected to " + str(address[0]) + ":" + str(address[1]))
    return sock


def send(sock, data, echo, emphasize, warning, error, vlog):
    data = data.encode()
    total_chars = len(data)
    total_chars_sent = 0
    while total_chars_sent < total_chars:
        part_to_send = data[total_chars_sent:]
        try:
            chars_sent = sock.send(part_to_send)
        except socket.error as socket_error:
            error("Send failed: " + str(socket_error))
            warning("Sent: " + str(data[:total_chars_sent]))
            exit_clean(sock)
        if chars_sent == 0:
            error("Socket connection broken.")
            warning("Sent: " + str(data[:total_chars_sent]))
            exit_clean(sock)
        total_chars_sent += chars_sent
    return sock


def receive(sock, echo, emphasize, warning, error, vlog):

    chunk_size = 1024
    buffer = ""
    continue_reading = True

    while continue_reading:

        # Pull out a chunk of data.
        bytes_read = sock.recv(chunk_size)
        buffer += bytes_read.decode("utf-8")

        # Get all the lines.
        lines_read = buffer.split("\n")

        # Put the last line back on the buffer.
        # It might be incomplete.
        buffer = lines_read.pop()

        for line in lines_read:

            # Strip off anything at the end of the line
            # (including an "\r", which some IRC servers add on).
            line = line.rstrip()

            # Break the line up at the spaces.
            words_in_line = line.split()

            # If the first word is "PING", we need to PONG back
            # the token.
            if words_in_line[0] == "PING":
                msg = "PONG %s\r\n" % words_in_line[1]
                send(sock, msg, echo, emphasize, warning, error, vlog)

            # Otherwise, we have a line we can use.
            else:
                echo(line)


def start(echo, emphasize, warning, error, vlog):

    address = ("irc.freenode.net", 6667)

    sock = connect(address, echo, emphasize, warning, error, vlog)

    msg = "PASS to-wong-foo" + os.linesep
    send(sock, msg, echo, emphasize, warning, error, vlog)

    msg = "NICK jt2222" + os.linesep
    send(sock, msg, echo, emphasize, warning, error, vlog)

    msg = "USER paul 8 * : Paul Muttonchops" + os.linesep
    send(sock, msg, echo, emphasize, warning, error, vlog)

    msg = "JOIN #bitcoin-otc" + os.linesep
    send(sock, msg, echo, emphasize, warning, error, vlog)

    try:
        receive(sock, echo, emphasize, warning, error, vlog)
    except:
        echo("")
        msg = "QUIT :gotta go" + os.linesep
        send(sock, msg, echo, emphasize, warning, error, vlog)
        echo("Closing connection...")
        sock.close()
        raise

    echo("")
    msg = "QUIT :out" + os.linesep
    send(sock, msg, echo, emphasize, warning, error, vlog)
    echo("Closing connection...")
    sock.close()
