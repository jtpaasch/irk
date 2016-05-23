# -*- coding: utf-8 -*-

"""Exceptions the application can raise."""


class ConnectionBroken(Exception):
    """Raise when the connection is broken."""
    pass


class CouldNotConnect(Exception):
    """Raise when you cannot connect over a socket."""
    pass


class SendFailed(Exception):
    """Raise when sending data over a socket fails."""
    pass
