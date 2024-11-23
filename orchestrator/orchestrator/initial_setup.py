from pathlib import Path

import iptc
from pyroute2 import IPRoute, NetlinkError

from .core import settings
from .core.exceptions import NetworkingError


def run_setup():
    ip = IPRoute()
    try:
        nat_table = iptc.Table(iptc.Table.NAT)
        filter_table = iptc.Table(iptc.Table.FILTER)

        nat_chain = iptc.Chain(nat_table, "POSTROUTING")
        masquerade_rule = iptc.Rule()
        masquerade_rule.target = iptc.Target(None, "MASQUERADE")
        masquerade_rule.out_interface = settings.INTERNET_FACING_INTERFACE

        if not any(masquerade_rule == rule for rule in nat_chain.rules):
            nat_chain.insert_rule(masquerade_rule)

        forward_chain = iptc.Chain(filter_table, "FORWARD")
        forward_rule = iptc.Rule()
        forward_rule.target = iptc.Target(None, "ACCEPT")
        forward_rule.match = iptc.Match(None, "conntrack")
        forward_rule.match.conntrack.state = "RELATED,ESTABLISHED"

        if not any(forward_rule == rule for rule in forward_chain.rules):
            forward_chain.insert_rule(forward_rule)

        # Enable IP forwarding
        Path("/proc/sys/net/ipv4/ip_forward").write_text("1")

    except (NetlinkError, iptc.IPTCError) as e:
        raise NetworkingError(e) from e
    finally:
        ip.close()  # Ensure the IPRoute object is closed


if __name__ == "__main__":
    run_setup()
