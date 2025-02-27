import os
import re
import subprocess
from ipaddress import ip_network
from signal import SIGTERM

from .provider import ProcessProvider, RouteProvider
from .util import get_executable


class PsProvider(ProcessProvider):
    def __init__(self):
        self.lsof = get_executable('/usr/sbin/lsof')
        self.ps = get_executable('/bin/ps')

    def pid2exe(self, pid):
        info = subprocess.check_output([self.lsof, '-p', str(pid)]).decode()
        for line in info.splitlines():
            parts = line.split()
            if parts[3] == 'txt':
                return parts[8]

    def ppid_of(self, pid=None):
        if pid is None:
            return os.getppid()
        try:
            return int(subprocess.check_output([self.ps, '-p', str(pid), '-o', 'ppid=']).decode().strip())
        except ValueError:
            return None

    def kill(self, pid, signal=SIGTERM):
        os.kill(pid, signal)


class BSDRouteProvider(RouteProvider):
    def __init__(self):
        self.route = get_executable('/sbin/route')
        self.ifconfig = get_executable('/sbin/ifconfig')

    def _route(self, *args):
        return subprocess.check_output([self.route, '-n'] + list(map(str, args))).decode()

    def _ifconfig(self, *args):
        return subprocess.check_output([self.ifconfig] + list(map(str, args))).decode()

    def add_route(self, destination, *, via=None, dev=None, src=None, mtu=None):
        args = ['add']
        if mtu is not None:
            args.extend(('-mtu', str(mtu)))
        if via is not None:
            args.extend((destination, via))
        elif dev is not None:
            args.extend(('-interface', destination, dev))
        self._route(*args)

    replace_route = add_route

    def remove_route(self, destination):
        self._route('delete', destination)

    def get_route(self, destination):
        info = self._route('get', destination)
        lines = iter(info.splitlines())
        info_d = {}
        for line in lines:
            if ':' not in line:
                break
            key, _, val = line.partition(':')
            info_d[key.strip()] = val.strip()
        keys = line.split()
        vals = next(lines).split()
        info_d.update(zip(keys, vals))
        return {
            'via': info_d['gateway'],
            'dev': info_d['interface'],
            'mtu': info_d['mtu'],
        }

    def flush_cache(self):
        pass

    _LINK_INFO_RE = re.compile(r'flags=\d<(.*?)>\smtu\s(\d+)$')

    def get_link_info(self, device):
        info = self._ifconfig(device)
        match = self._LINK_INFO_RE.search(info)
        if match:
            flags = match.group(1).split(',')
            mtu = int(match.group(2))
            return {
                'state': 'up' if 'UP' in flags else 'down',
                'mtu': mtu,
            }
        return None

    def set_link_info(self, device, state, mtu=None):
        args = [device]
        if state is not None:
            args.append(state)
        if mtu is not None:
            args.extend(('mtu', str(mtu)))
        self._ifconfig(*args)

    def add_address(self, device, address):
        if address.version == 6:
            family = 'inet6'
        else:
            family = 'inet'
        self._ifconfig(device, family, ip_network(address), address)
