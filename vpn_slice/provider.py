from abc import ABCMeta, abstractmethod


class ProcessProvider(metaclass=ABCMeta):
    @abstractmethod
    def pid2exe(self, pid):
        """Get the path to the executable running as a given PID."""

    @abstractmethod
    def ppid_of(self, pid=None):
        """Get the PID of the parent of the process with the given PID,
        or of the current process if None."""

    @abstractmethod
    def kill(self, pid):
        """Kill the process with the given PID."""


class RouteProvider(metaclass=ABCMeta):
    @abstractmethod
    def add_route(self, destination, *, via=None, dev=None, src=None, mtu=None):
        """Add a route to a destination.

        You must specify a device or gateway saying where to route to.
        If both are specified, they must agree.

        Implementations may fail if a route that already exists is
        added again.

        """

    @abstractmethod
    def replace_route(self, destination, *, via=None, dev=None, src=None, mtu=None):
        """Add or replace a route to a destination.

        You must specify a device or gateway saying where to route to.
        If both are specified, they must agree.

        Implementations should not fail if a route that already exists
        is added again.

        """

    @abstractmethod
    def remove_route(self, destination):
        """Remove a route to a destination."""

    @abstractmethod
    def get_route(self, destination):
        """Return the gateway to a destination.

        Return a dict with these keys containing the information,
        or None if it is unavailable:

        * via
        * dev
        * src
        * mtu

        """

    @abstractmethod
    def flush_cache(self):
        """Flush the routing cache (if necessary)."""

    @abstractmethod
    def get_link_info(self, device):
        """Get the MTU and state for a device.

        Return a dict with these keys containing the information,
        or None if it is unavailable:

        * mtu
        * state

        """

    @abstractmethod
    def set_link_info(self, device, state, mtu=None):
        """Set the MTU and state of a device."""

    @abstractmethod
    def add_address(self, device, address):
        """Add an address to an interface."""


class FirewallProvider(metaclass=ABCMeta):
    @abstractmethod
    def configure_firewall(self, device):
        """Configure the firewall to prevent inbound traffic on the device."""

    @abstractmethod
    def deconfigure_firewall(self, device):
        """Remove the firewall configuration for a device."""


class DNSProvider(metaclass=ABCMeta):
    @abstractmethod
    def lookup_host(self, hostname, dns_servers, *, bind_address=None, search_domains=()):
        """Look up the address of a host."""


class HostsProvider(metaclass=ABCMeta):
    @abstractmethod
    def write_hosts(self, host_map, name):
        """Write information to the hosts file.

        Lines include a tag so we can identify which lines to remove.
        The tag is derived from the name.

        host_map maps IP addresses to host names, like the hosts file expects.

        """

class TunnelPrepProvider:
    def prepare_tunnel(self):
        """Prepare operating system to create tunnel devices.

        Base class behavior is to do nothing.

        """
