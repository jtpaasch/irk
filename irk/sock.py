# -*- coding: utf-8 -*-

"""Socket wrapper."""

import socket
import string
import sys
import threading


LINESEP = "\r\n"


def exit_cleanly(sock, thread, thread_should_stop,
                 echo, emphasize, warning, error, vlog):
    thread_should_stop.set()
    vlog("Shutting down socket...")
    sock.shutdown(1)
    vlog("Waiting for thread to terminate...")
    thread.join()
    vlog("Closing socket...")
    sock.close()


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
        vlog("Sent: " + str(part_to_send.decode("utf-8")))
        total_chars_sent += chars_sent
    return sock


def receive(thread_should_stop, sock, echo, emphasize, warning, error, vlog):

    chunk_size = 1024
    buffer = ""

    while not thread_should_stop.isSet():
        vlog("Checking for new data...")

        data = sock.recv(chunk_size)
        data_utf8 = data.decode("utf-8")
        vlog("RECV: " + data_utf8)

        buffer += data_utf8
        lines_in_buffer = buffer.split("\n")

        buffer = lines_in_buffer.pop()

        cleaned_lines = [x.rstrip() for x in lines_in_buffer]

        for line in cleaned_lines:

            echo(line)

            words = line.split()
            if (words[0] == "PING"):
                msg = "PONG " + " ".join(words[1:]) + "\r\n"
                vlog(msg)
                send(sock, msg, echo, emphasize, warning, error, vlog)

        vlog("Done with recv...")

    vlog("Done receiving...")


def login(address, echo, emphasize, warning, error, vlog):

    sock = connect(address, echo, emphasize, warning, error, vlog)

    msg = "PASS to-wong-foo" + LINESEP
    vlog(msg)
    send(sock, msg, echo, emphasize, warning, error, vlog)

    msg = "NICK jt2222" + LINESEP
    vlog(msg)
    send(sock, msg, echo, emphasize, warning, error, vlog)

    msg = "USER paul 8 * : Paul Muttonchops" + LINESEP
    vlog(msg)
    send(sock, msg, echo, emphasize, warning, error, vlog)

    return sock


def start(echo, emphasize, warning, error, vlog):

    address = ("irc.freenode.net", 6667)
    channel = ""

    sock = login(address, echo, emphasize, warning, error, vlog)

    thread_should_stop = threading.Event()
    args = (thread_should_stop, sock, echo, emphasize, warning, error, vlog)
    thread = threading.Thread(target=receive, args=args)

    thread.start()

    try:
        while True:

            entered_data = input()
            entered_data = entered_data.strip()

            if entered_data:
                vlog("STDIN: " + str(entered_data))
                parts = entered_data.split()

                cmd = parts[0]
                cmd = cmd.upper()

                msg = cmd + " " + " ".join(parts[1:]) + LINESEP
                vlog("SENDING: " + msg)
                send(sock, msg, echo, emphasize, warning, error, vlog)

                if cmd == "QUIT":
                    break

    except (KeyboardInterrupt, SystemExit):
        vlog("Caught exit signal...")
        exit_cleanly(sock, thread, thread_should_stop,
                     echo, emphasize, warning, error, vlog)
        vlog("Raising exit signal again...")
        raise

    vlog("No exceptions raised: waiting for thread to terminate...")
    exit_cleanly(sock, thread, thread_should_stop,
                 echo, emphasize, warning, error, vlog)
    echo("Goodbye.")

