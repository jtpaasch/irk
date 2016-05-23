# -*- coding: utf-8 -*-

"""Connects, sends, receives, and disconnects to/from a socket."""

import socket

from . import exceptions


def connect(host, port, vlog):
    """Connect to a socket.

    Args:

        host
            The host to connect to.

        port
            The port to use.

        vlog
            A verbose logger to pass messages to.

    Raises:

        CouldNotConnect
            If it could not connect.

    Returns
        An open socket connected to the server.

    """
    address = (host, port)
    vlog("About to connect to " + str(host) + ":" + str(port))
    try:
        sock = socket.create_connection(address)
    except socket.error as error:
        msg = "Could not connect. Error: " + str(error)
        vlog(msg)
        raise exceptions.CouldNotConnect(msg)
    vlog("Connected successfully to " + str(host) + ":" + str(port))
    return sock


def disconnect(sock, thread, thread_should_stop, vlog):
    """Disconnect from a socket listening on a separate thread.

    Args:

        sock
            The socket you want to disconnect.

        thread
            The thread that's listening to the socket.

        thread_should_stop
            A threading ``Event`` that can be flagged/cleared.

        vlog
            A verbose logger to pass messages to.

    """
    thread_should_stop.set()
    vlog("Shutting down socket.")
    sock.shutdown(1)
    vlog("Waiting for thread to terminate.")
    thread.join()
    vlog("Closing socket.")
    sock.close()


def send(sock, data, vlog):
    """Send data over the socket to the server.

    Args:

        sock
            An open socket to send data over.

        data
            The data to send.

        vlog
            A verbose logger to pass messages to.

    """
    bytes_of_data = data.encode()
    total_chars = len(bytes_of_data)
    total_chars_sent = 0
    vlog("About to send: " + str(data))
    while total_chars_sent < total_chars:
        part_to_send = bytes_of_data[total_chars_sent:]
        try:
            chars_sent = sock.send(part_to_send)
        except socket.error as error:
            msg = "Send failed: " + str(error)
            vlog(msg)
            raise exceptions.SendFailed(msg)
        if chars_sent == 0:
            msg = "Socket connection broken."
            vlog(msg)
            raise exceptions.ConnectionBroken(msg)
        vlog("Sent: " + str(part_to_send.decode("ascii", "ignore")))
        total_chars_sent += chars_sent
    vlog("Finished sending: " + str(data))


def receive(sock, thread_should_stop, output_handler, vlog):
    """Listen for data sent over a socket.

    Args:

        sock
            The socket to listen on.

        thread_should_stop
            A threading ``Event`` that can be flagged/cleared.

        output_handler
            A logger to pass output to.

        vlog
            A verbose logger to pass messages to.

    """
    chunk_size = 1024
    buffer = ""

    while not thread_should_stop.isSet():
        vlog("Checking for data sent over the socket...")

        data = sock.recv(chunk_size)
        data_ascii = data.decode("ascii", "ignore")
        vlog("Received: " + data_ascii)

        # Split the data on the lines.
        buffer += data_ascii
        lines_in_buffer = buffer.split("\n")

        # The last line might be half a line.
        # Start the buffer again with just that part.
        buffer = lines_in_buffer.pop()

        # Git rid of any "\r" chars at the end of lines.
        cleaned_lines = [x.rstrip() for x in lines_in_buffer]

        for line in cleaned_lines:

            output_handler(line)

            # If the server has PINGed us, we need to PONG back,
            # or else it will sever our connection.
            words = line.split()
            if (words[0] == "PING"):
                msg = "PONG " + " ".join(words[1:]) + "\r\n"
                vlog(msg)
                send(sock, msg, vlog)

        vlog("Done reading chunks of " + str(chunk_size) + " bytes...")

    vlog("Done receiving data over the socket.")
