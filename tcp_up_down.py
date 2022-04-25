# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2022 NITK Surathkal

########################
# SHOULD BE RUN AS ROOT
########################

from nest.topology import *
from nest.experiment import *
from nest.topology.network import Network
from nest.topology.address_helper import AddressHelper

## This program contains the methods for carrying out various "TCP upload" and "TCP download" experiments.

#################################################################################################################
#                                           Network Topology                                                    #
#                                                                                                               #
#        1000mbit, 1ms -->                                                    1000mbit, 1ms -->                 #    
#   LN1 ---------------------------                                       ----------------------- RN1           #
#       <-- 1000mbit, 1ms          \                                     /    <-- 1000mbit, 1ms                 #
#                                   \                                   /                                       #
#                                    \                                 /                                        #
#        1000mbit, 1ms -->            \        10mbit, 10ms -->       /       1000mbit, 1ms -->                 #
#   LN2 -----------------------------   r1  ---------------------  r2  -------------------------- RN2           #
#       <-- 1000mbit, 1ms             /        <-- 10mbit, 10ms       \       <-- 1000mbit, 1ms                 #
#    .                               /                                 \                           .            #
#    .                              /                                   \                          .            #
#    .                             /                                     \                         .            #
#    .                            /                                       \                        .            #
#        1000mbit, 1ms -->       /                                         \  1000mbit, 1ms -->                 #
#   LNn -------------------------                                            -------------------- RNn           #
#       <-- 1000mbit, 1ms                                                     <-- 1000mbit, 1ms                 #
#                                                                                                               #
#                                                                                                               #
#################################################################################################################

## This method performs the "TCP upload" experiment 
## i.e., sending the flows from left nodes to the right nodes 
# Assumption: left-nodes are the clients right-nodes are the servers

def tcp_up(NO_TCP_FLOWS, AQM):

    # Creating the same number of nodes on either sides as that of the number of flows
    TOTAL_NODES_PER_SIDE = NO_TCP_FLOWS

    # Set the link attributes: `h1` --> `r1` --> `r2` --> `h2`
    # Note: we enable `pfifo` queue discipline on the link from `r1` to `r2`.
    # Default configuration of `pfifo` in Linux is used. For more details about
    # `pfifo` in Linux, use this command on CLI: `man tc-pfifo`.

    ## Creating variables to store the latencies between client-to-router and router-to-router
    client_router_latency = '1ms'
    router_router_latency = '10ms'

    ## Creating variables to store the bandwidths between client-to-router and router-to-router
    client_router_bandwidth = '1000mbit'
    router_router_bandwidth = '10mbit'

    # Assigning number of nodes on either sides of the dumbbell according to the input
    num_of_left_nodes = TOTAL_NODES_PER_SIDE
    num_of_right_nodes = TOTAL_NODES_PER_SIDE

    ###### TOPOLOGY CREATION ######

    # Creating the routers for the dumbbell topology
    left_router = Router("left-router")
    right_router = Router("right-router")

     # Lists to store all the left and right nodes
    left_nodes = []
    right_nodes = []

    # Creating all the left and right nodes
    for i in range(num_of_left_nodes):
        left_nodes.append(Node("left-node-" + str(i)))

    for i in range(num_of_right_nodes):
        right_nodes.append(Node("right-node-" + str(i)))

    print("Nodes and routers created")

    #########  Adding connections #########

    # Lists of tuples to store the interfaces connecting the router and nodes
    left_node_connections = []
    right_node_connections = []
    
    # Set the IPv4 address for the networks, and not the interfaces.
    # We will use the `AddressHelper` later to assign addresses to the interfaces.

    # This network is used for all the left-nodes and the left-router, i.e., on to the left of 'r1'
    left_network = Network("10.0.0.0/24")
    
    # This network is used for all the right-nodes and the right-router, i.e., on to the right of 'r2'
    right_network = Network("10.0.1.0/24")

    # This network is used for the connections between the two routers, i.e., between 'r1' and 'r2'
    router_network = Network("10.0.2.0/24")

    # Connecting left-nodes to the left-router under "left_network"
    for i in range(num_of_left_nodes):
        left_node_connections.append(connect(left_nodes[i], left_router, network=left_network))

    # Connecting right-nodes to the left-router under "right_network"
    for i in range(num_of_right_nodes):
        right_node_connections.append(connect(right_nodes[i], right_router, network=right_network))

    # Connecting the two routers 'r1' and 'r2' under "router_network"
    (left_router_connection, right_router_connection) = connect(left_router, right_router, network=router_network)

    # Assign IPv4 addresses to all the interfaces in the network.
    AddressHelper.assign_addresses()

    print("Connections made")

    ####### ROUTING #######

    # If any packet needs to be sent from any left-nodes, send it to left-router, 
    # i.e., Adding "default" gateways for each node
    for i in range(num_of_left_nodes):
        left_nodes[i].add_route("DEFAULT", left_node_connections[i][0])

    # If the destination address for any packet in left-router is
    # one of the left-nodes, forward the packet to that node
    for i in range(num_of_left_nodes):
        left_router.add_route(
            left_node_connections[i][0].get_address(), left_node_connections[i][1]
        )

    # If the destination address doesn't match any of the entries
    # in the left-router's iptables forward the packet to right-router
    left_router.add_route("DEFAULT", left_router_connection)

    # If any packet needs to be sent from any right nodes, send it to right-router
    # i.e., Adding "default" gateways for each node
    for i in range(num_of_right_nodes):
        right_nodes[i].add_route("DEFAULT", right_node_connections[i][0])

    # If the destination address for any packet in left-router is
    # one of the left-nodes, forward the packet to that node
    for i in range(num_of_right_nodes):
        right_router.add_route(
            right_node_connections[i][0].get_address(), right_node_connections[i][1]
        )

    # If the destination address doesn't match any of the entries
    # in the right-router's iptables forward the packet to left-router
    right_router.add_route("DEFAULT", right_router_connection)

    # Setting up the attributes of the connections between
    # the nodes on the left-side and the left-router
    for i in range(num_of_left_nodes):
        left_node_connections[i][0].set_attributes(
            client_router_bandwidth, client_router_latency
        )
        left_node_connections[i][1].set_attributes(
            client_router_bandwidth, client_router_latency
        )

    # Setting up the attributes of the connections between
    # the nodes on the right-side and the right-router
    for i in range(num_of_right_nodes):
        right_node_connections[i][0].set_attributes(
            client_router_bandwidth, client_router_latency
        )
        right_node_connections[i][1].set_attributes(
            client_router_bandwidth, client_router_latency
        )

    # Setting up the attributes of the connections between the two routers
    # Note: we enable the user given queue discipline on the link from (`r1` to `r2`) and (`r2` to `r1`)
    left_router_connection.set_attributes(router_router_bandwidth, router_router_latency, AQM)
    right_router_connection.set_attributes(router_router_bandwidth, router_router_latency, AQM)

    ######  RUN TESTS ######

    exp_name = "tcp_" + str(NO_TCP_FLOWS) + "up"

    # Set up an Experiment. This API takes the name of the experiment as a string.
    experiment = Experiment(exp_name)

    # Assuming left nodes are the clients and right nodes are the router to carry out the "upload" experiment
    # Configure flows from each `left_node` to the corresponding `right_node`. We do not use it as a TCP flow yet.
    # The `Flow` API takes in the source node, destination node, destination IP
    # address, start and stop time of the flow, and the total number of flows.
    # In this program, start time is 0 seconds, stop time is 200 seconds and the
    # number of streams is 1.

    for i in range(NO_TCP_FLOWS):
        flow = Flow(
            left_nodes[i], right_nodes[i], right_node_connections[i][0].address, 0, 200, 1
        )
        # Use TCP cubic which is the default
        experiment.add_tcp_flow(flow)

    # Request traffic control stats
    experiment.require_qdisc_stats(left_router_connection)
    experiment.require_qdisc_stats(right_router_connection)

    # Running the experiment
    experiment.run()


## This method performs the "TCP download" experiment 
## i.e., sending the flows from right nodes to the left nodes 
# Assumption: left-nodes are the clients right-nodes are the servers

def tcp_down(NO_TCP_FLOWS, AQM):
    
    # Creating the same number of nodes on either sides as that of the number of flows
    TOTAL_NODES_PER_SIDE = NO_TCP_FLOWS

    # Set the link attributes: `h1` --> `r1` --> `r2` --> `h2`
    # Note: we enable `pfifo` queue discipline on the link from `r1` to `r2`.
    # Default configuration of `pfifo` in Linux is used. For more details about
    # `pfifo` in Linux, use this command on CLI: `man tc-pfifo`.

    ## Creating variables to store the latencies between client-to-router and router-to-router
    client_router_latency = '1ms'
    router_router_latency = '10ms'

    ## Creating variables to store the bandwidths between client-to-router and router-to-router
    client_router_bandwidth = '1000mbit'
    router_router_bandwidth = '10mbit'

    # Assigning number of nodes on either sides of the dumbbell according to the input
    num_of_left_nodes = TOTAL_NODES_PER_SIDE
    num_of_right_nodes = TOTAL_NODES_PER_SIDE

    ###### TOPOLOGY CREATION ######

    # Creating the routers for the dumbbell topology
    left_router = Router("left-router")
    right_router = Router("right-router")

     # Lists to store all the left and right nodes
    left_nodes = []
    right_nodes = []

    # Creating all the left and right nodes
    for i in range(num_of_left_nodes):
        left_nodes.append(Node("left-node-" + str(i)))

    for i in range(num_of_right_nodes):
        right_nodes.append(Node("right-node-" + str(i)))

    print("Nodes and routers created")

    #########  Adding connections #########

    # Lists of tuples to store the interfaces connecting the router and nodes
    left_node_connections = []
    right_node_connections = []
    
    # Set the IPv4 address for the networks, and not the interfaces.
    # We will use the `AddressHelper` later to assign addresses to the interfaces.

    # This network is used for all the left-nodes and the left-router, i.e., on to the left of 'r1'
    left_network = Network("10.0.0.0/24")
    
    # This network is used for all the right-nodes and the right-router, i.e., on to the right of 'r2'
    right_network = Network("10.0.1.0/24")

    # This network is used for the connections between the two routers, i.e., between 'r1' and 'r2'
    router_network = Network("10.0.2.0/24")

    # Connecting left-nodes to the left-router under "left_network"
    for i in range(num_of_left_nodes):
        left_node_connections.append(connect(left_nodes[i], left_router, network=left_network))

    # Connecting right-nodes to the left-router under "right_network"
    for i in range(num_of_right_nodes):
        right_node_connections.append(connect(right_nodes[i], right_router, network=right_network))

    # Connecting the two routers 'r1' and 'r2' under "router_network"
    (left_router_connection, right_router_connection) = connect(left_router, right_router, network=router_network)

    # Assign IPv4 addresses to all the interfaces in the network.
    AddressHelper.assign_addresses()

    print("Connections made")

    ####### ROUTING #######

    # If any packet needs to be sent from any right-nodes, send it to right-router
    # i.e., Adding "default" gateways for each node
    for i in range(num_of_right_nodes):
        right_nodes[i].add_route("DEFAULT", right_node_connections[i][0])

    # If the destination address for any packet in right-router is
    # one of the right-nodes, forward the packet to that node
    for i in range(num_of_right_nodes):
        right_router.add_route(
            right_node_connections[i][0].get_address(), right_node_connections[i][1]
        )

    # If the destination address doesn't match any of the entries
    # in the right-router's iptables forward the packet to left-router
    right_router.add_route("DEFAULT", right_router_connection)

    # If any packet needs to be sent from any left nodes, send it to left-router
    # i.e., Adding "default" gateways for each node
    for i in range(num_of_left_nodes):
        left_nodes[i].add_route("DEFAULT", left_node_connections[i][0])

    # If the destination address for any packet in right-router is
    # one of the right-nodes, forward the packet to that node
    for i in range(num_of_left_nodes):
        left_router.add_route(
            left_node_connections[i][0].get_address(), left_node_connections[i][1]
        )

    # If the destination address doesn't match any of the entries
    # in the left-router's iptables forward the packet to right-router
    left_router.add_route("DEFAULT", left_router_connection)

    # Setting up the attributes of the connections between
    # the nodes on the right-side and the right-router
    for i in range(num_of_right_nodes):
        right_node_connections[i][0].set_attributes(
            client_router_bandwidth, client_router_latency
        )
        right_node_connections[i][1].set_attributes(
            client_router_bandwidth, client_router_latency
        )

    # Setting up the attributes of the connections between
    # the nodes on the left-side and the left-router
    for i in range(num_of_left_nodes):
        left_node_connections[i][0].set_attributes(
            client_router_bandwidth, client_router_latency
        )
        left_node_connections[i][1].set_attributes(
            client_router_bandwidth, client_router_latency
        )

    # Setting up the attributes of the connections between the two routers
    # Note: we enable the user given queue discipline on the link from (`r1` to `r2`) and (`r2` to `r1`)
    right_router_connection.set_attributes(router_router_bandwidth, router_router_latency, AQM)
    left_router_connection.set_attributes(router_router_bandwidth, router_router_latency, AQM)


    ######  RUN TESTS ######

    exp_name = "tcp_" + str(NO_TCP_FLOWS) + "down"

    # Set up an Experiment. This API takes the name of the experiment as a string.
    experiment = Experiment(exp_name)

    # Assuming left nodes are the clients and right nodes are the router to carry out the "download" experiment
    # Configure flows from each `right_node` to the corresponding `left_node`. We do not use it as a TCP flow yet.
    # The `Flow` API takes in the source node, destination node, destination IP
    # address, start and stop time of the flow, and the total number of flows.
    # In this program, start time is 0 seconds, stop time is 200 seconds and the
    # number of streams is 1.
    for i in range(NO_TCP_FLOWS):
        flow = Flow(
            right_nodes[i], left_nodes[i], left_node_connections[i][0].address, 0, 200, 1
        )
        # Use TCP cubic which is the default
        experiment.add_tcp_flow(flow)

    # Request traffic control stats
    experiment.require_qdisc_stats(right_router_connection)
    experiment.require_qdisc_stats(left_router_connection)

    # Running the experiment
    experiment.run()