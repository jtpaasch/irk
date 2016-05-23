# -*- coding: utf-8 -*-

"""Connects, sends, receives, and disconnects to/from a socket."""

import socket
import threading

from . import exceptions


def connect(host, port, vlog):
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
    thread_should_stop.set()
    vlog("Shutting down socket.")
    sock.shutdown(1)
    vlog("Waiting for thread to terminate.")
    thread.join()
    vlog("Closing socket.")
    sock.close()


def send(sock, data, vlog):
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
        vlog("Sent: " + str(part_to_send.decode("utf-8")))
        total_chars_sent += chars_sent
    vlog("Finished sending: " + str(data))
    return sock


def receive(sock, thread_should_stop, output_handler, vlog):
    chunk_size = 1024
    buffer = ""

    while not thread_should_stop.isSet():
        vlog("Checking for data sent over the socket...")

        data = sock.recv(chunk_size)
        data_utf8 = data.decode("utf-8")
        vlog("Received: " + data_utf8)

        # Split the data on the lines.
        buffer += data_utf8
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


def start(sock, input_handler, output_handler, vlog):
    thread_should_stop = threading.Event()
    args = (sock, thread_should_stop, output_handler, vlog)
    thread = threading.Thread(target=receive, args=args)
    thread.start()

    should_continue = True

    try:
        while should_continue:
            entered_data = input()
            entered_data = entered_data.strip()

            if entered_data:
                vlog("STDIN: " + str(entered_data))
                should_continue = input_handler(entered_data)

    except (KeyboardInterrupt, SystemExit):
        vlog("")
        vlog("Caught exit signal...")
        disconnect(sock, thread, thread_should_stop, vlog)
        vlog("Raising exit signal again...")
        raise

    vlog("All finished.") 
    disconnect(sock, thread, thread_should_stop, vlog)
    vlog("Goodbye.")
