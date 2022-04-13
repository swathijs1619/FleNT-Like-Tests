########################
# SHOULD BE RUN AS ROOT
########################
from nest.topology import *
from nest.experiment import *
from nest.topology.network import Network
from nest.topology.address_helper import AddressHelper

# This program emulates point to point networks that connect four hosts: `h1`
# - `h4` via two routers `r1` and `r2`. One TCP flow is configured from `h1` to
# `h3` and one UDP flow is configured from `h2` to `h4`. It is similar to
# `tcp-udp-point-to-point.py` in `examples/tcp`. The links `h1` <--> `r1`,
# `h2` <--> `r1`, and `r2` <--> `h3`, `r2` <--> `h4` are edge links. The link
# `r1` <--> `r2` is the bottleneck link with lesser bandwidth and higher
# propagation delays. This program demonstrates how to configure CHOose and
# Keep for responsive flows, CHOose and Kill for unresponsive flows (`choke`)
# queue discipline (qdisc) and obtain the relevant statistics. `choke` is
# enabled on the link from `r1` to `r2`, but not from `r2` to `r1` because
# data packets flow in one direction only (left to right) in this example.

##############################################################################
#                              Network Topology                              #
#                                                                            #
#    <- 1000mbit, 1ms ->                              <- 1000mbit, 1ms ->    #
# h1 --------------------|                          |-------------------- h5 #
#           TCP          |                          |         TCP            #
# h2                     |    <- 10mbit, 10ms ->    |                     h6 #
#                         r1 -------------------- r2                         #
# h3                     |      choke qdisc -->     |                     h7 #
#                        |                          |                        #
# h4 --------------------|                          |-------------------- h8 #
#    <- 1000mbit, 1ms ->                              <- 1000mbit, 1ms ->    #
#                                                                            #
##############################################################################

# This program runs for 200 seconds and creates a new directory called
# `choke-point-to-point(date-timestamp)_dump`. It contains a `README` that
# provides details about the sub-directories and files within this directory.
# See the plots in `netperf`, `ping` and `ss` sub-directories for this program.

# Create four hosts `h1` to `h4`, and two routers `r1` and `r2`
h1 = Node("h1")
h2 = Node("h2")
h3 = Node("h3")
h4 = Node("h4")
h5 = Node("h5")
h6 = Node("h6")
h7 = Node("h7")
h8 = Node("h8")
r1 = Router("r1")
r2 = Router("r2")

# Set the IPv4 address for the networks
n1 = Network("192.168.1.0/24")  # network consisting `h1` and `r1`
n2 = Network("192.168.2.0/24")  # network consisting `h2` and `r1`
n3 = Network("192.168.3.0/24")  # network consisting `h3` and `r1`
n4 = Network("192.168.4.0/24")  # network consisting `h4` and `r1


n5 = Network("192.168.5.0/24")  # network between two routers

n6 = Network("192.168.6.0/24")  # network consisting `r2` and `h5`
n7 = Network("192.168.7.0/24")  # network consisting `r2` and `h6`
n8 = Network("192.168.8.0/24")  # network consisting `r2` and `h7`
n9 = Network("192.168.9.0/24")  # network consisting `r2` and `h8`


# Connect `h1` and `h2` to `r1`, `r1` to `r2`, and then `r2` to `h3` and `h4`.
# `eth1` to `eth4` are the interfaces at `h1` to `h4`, respectively.
# `etr1a`, `etr1b` and `etr1c` are three interfaces at `r1` that connect it
# with `h1`, `h2` and `r2`, respectively.
# `etr2a`, `etr2b` and `etr2c` are three interfaces at `r2` that connect it
# with `r1`, `h3` and `h4`, respectively.
(eth1, etr1a) = connect(h1, r1, network=n1)
(eth2, etr1b) = connect(h2, r1, network=n2)
(eth3, etr1c) = connect(h3, r1, network=n3)
(eth4, etr1d) = connect(h4, r1, network=n4)

(etr1e, etr2a) = connect(r1, r2, network=n5)

(etr2b, eth5) = connect(r2, h5, network=n6)
(etr2c, eth6) = connect(r2, h6, network=n7)
(etr2d, eth7) = connect(r2, h7, network=n8)
(etr2e, eth8) = connect(r2, h8, network=n9)

# Assign IPv4 addresses to all the interfaces in the network.
AddressHelper.assign_addresses()

# Configure the parameters of `choke` qdisc.  For more details about `choke`
# in Linux, use this command on CLI: `man tc-choke`.
qdisc = "pfifo"
# choke_parameters = {
#     "limit": "100",  # set the queue capacity to 100 packets
#     "min": "5",  # set the minimum threshold to 5 packets
#     "max": "15",  # set the maximum threshold to 15 packets
# }

# Set the link attributes: `h1` and `h2` --> `r1` --> `r2` --> `h3` and `h4`
# Note: we enable `choke` queue discipline on the link from `r1` to `r2`.
eth1.set_attributes("1000mbit", "1ms")  # from `h1` to `r1`
eth2.set_attributes("1000mbit", "1ms")  # from `h2` to `r1`
eth3.set_attributes("1000mbit", "1ms")  # from `h3` to `r1`
eth4.set_attributes("1000mbit", "1ms")  # from `h4` to `r1`

etr1e.set_attributes("10mbit", "10ms", qdisc)  # from `r1` to `r2`

etr2b.set_attributes("1000mbit", "1ms")  # from `r2` to `h5`
etr2c.set_attributes("1000mbit", "1ms")  # from `r2` to `h6`
etr2d.set_attributes("1000mbit", "1ms")  # from `r2` to `h7`
etr2e.set_attributes("1000mbit", "1ms")  # from `r2` to `h8`


# Set the link attributes: `h3` and `h4` --> `r2` --> `r1` --> `h1` and `h2`
eth5.set_attributes("1000mbit", "1ms")  # from `h5` to `r2`
eth6.set_attributes("1000mbit", "1ms")  # from `h6` to `r2`
eth7.set_attributes("1000mbit", "1ms")  # from `h7` to `r2`
eth8.set_attributes("1000mbit", "1ms")  # from `h8` to `r2`


etr2a.set_attributes("10mbit", "10ms")  # from `r2` to `r1`

etr1a.set_attributes("1000mbit", "1ms")  # from `r1` to `h1`
etr1b.set_attributes("1000mbit", "1ms")  # from `r1` to `h2`
etr1c.set_attributes("1000mbit", "1ms")  # from `r1` to `h3`
etr1d.set_attributes("1000mbit", "1ms")  # from `r1` to `h4`



# Set default routes in all the hosts and routers.
h1.add_route("DEFAULT", eth1)
h2.add_route("DEFAULT", eth2)
h3.add_route("DEFAULT", eth3)
h4.add_route("DEFAULT", eth4)
h5.add_route("DEFAULT", eth5)
h6.add_route("DEFAULT", eth6)
h7.add_route("DEFAULT", eth7)
h8.add_route("DEFAULT", eth8)

r1.add_route("DEFAULT", etr1e)
r2.add_route("DEFAULT", etr2a)

# Set up an Experiment. This API takes the name of the experiment as a string.
exp = Experiment("reno_vs_cubic_vs_westwood_vs_ledbat")

# Configure one flow from `h1` to `h3` and another from `h2` to `h4`.
flow1 = Flow(h1, h5, eth5.get_address(), 0, 20, 1)
flow2 = Flow(h2, h6, eth6.get_address(), 0, 20, 1)

flow3 = Flow(h3, h7, eth7.get_address(), 0, 20, 1)
flow4 = Flow(h4, h8, eth8.get_address(), 0, 20, 1)

# Use `flow1` as a TCP flow. TCP CUBIC is default in Linux.
exp.add_tcp_flow(flow1, "reno")

exp.add_tcp_flow(flow2, "cubic")

exp.add_tcp_flow(flow3, "westwood")

exp.add_tcp_flow(flow4, "ledbat")

# The following line enables collection of stats for the qdisc installed on
# `etr1c` interface (connecting `r1` to `r2`), but it is commented because NeST
# does not support stats collection for `choke` qdisc.
# exp.require_qdisc_stats(etr1c)

# Run the experiment
exp.run()
