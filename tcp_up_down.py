from nest.topology import *
from nest.experiment import *
from nest.topology.network import Network
from nest.topology.address_helper import AddressHelper
import sys

def tcp_up(NO_TCP_FLOWS, AQM):
    TOTAL_NODES_PER_SIDE = NO_TCP_FLOWS

    client_router_latency = '0.5ms'
    router_router_latency = '1ms'

    client_router_bandwidth = '800mbit'
    bottleneck_bandwidth = '80mbit'

    # Assigning number of nodes on either sides of the dumbbell according to input
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

    # Add connections

    # Lists of tuples to store the interfaces connecting the router and nodes
    left_node_connections = []
    right_node_connections = []

    # A network object to auto generate addresses in the same network
    # This network is used for all the left-nodes and the left-router
    left_network = Network("10.0.0.0/24")
    
    # This network is used for all the right-nodes and the right-router
    right_network = Network("10.0.1.0/24")

    # This network is used for the connections between the two routers
    router_network = Network("10.0.2.0/24")

    # Connections of the left-nodes to the left-router
    for i in range(num_of_left_nodes):
        left_node_connections.append(connect(left_nodes[i], left_router, network=left_network))

    # Connections of the right-nodes to the right-router
    for i in range(num_of_right_nodes):
        right_node_connections.append(connect(right_nodes[i], right_router, network=right_network))

    # Connecting the two routers
    (left_router_connection, right_router_connection) = connect(left_router, right_router, network=router_network)

    # Assign IPv4 addresses to all the interfaces in the network.
    AddressHelper.assign_addresses()

    print("Connections made")

    # ###### ADDRESS ASSIGNMENT ######

    # for i in range(num_of_left_nodes):
    #     # Copying a left-node's interface and it's pair to temporary variables
    #     node_int = left_node_connections[i][0]
    #     router_int = left_node_connections[i][1]

    #     # Assigning addresses to the interfaces
    #     node_int.set_address(left_network.get_next_addr())
    #     router_int.set_address(left_network.get_next_addr())

    # for i in range(num_of_right_nodes):
    #     # Copying a right-node's interface and it's pair to temporary variables
    #     node_int = right_node_connections[i][0]
    #     router_int = right_node_connections[i][1]

    #     # Assigning addresses to the interfaces
    #     node_int.set_address(right_network.get_next_addr())
    #     router_int.set_address(right_network.get_next_addr())

    # # Assigning addresses to the connections between the two routers
    # left_router_connection.set_address(router_network.get_next_addr())
    # right_router_connection.set_address(router_network.get_next_addr())

    # print("Addresses are assigned")

    ####### ROUTING #######

    # If any packet needs to be sent from any left-nodes, send it to left-router
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

    # Setting up the attributes of the connections between
    # the two routers
    left_router_connection.set_attributes(bottleneck_bandwidth, router_router_latency, AQM)
    right_router_connection.set_attributes(bottleneck_bandwidth, router_router_latency, AQM)

    ######  RUN TESTS ######

    exp_name = "tcp_" + str(NO_TCP_FLOWS) + "up"

    experiment = Experiment(exp_name)

    # Add TCP flows from the left nodes to respective right nodes
    for i in range(NO_TCP_FLOWS):
        flow = Flow(
            left_nodes[i], right_nodes[i], right_node_connections[i][0].address, 0, 40, 1
        )
        # Use TCP reno
        experiment.add_tcp_flow(flow)

    # Request traffic control stats
    experiment.require_qdisc_stats(left_router_connection)
    experiment.require_qdisc_stats(right_router_connection)

    # Running the experiment
    experiment.run()


def tcp_down(NO_TCP_FLOWS, AQM):
    TOTAL_NODES_PER_SIDE = NO_TCP_FLOWS

    client_router_latency = '0.5ms'
    router_router_latency = '1ms'

    client_router_bandwidth = '800mbit'
    bottleneck_bandwidth = '80mbit'

    # Assigning number of nodes on either sides of the dumbbell according to input
    num_of_right_nodes = TOTAL_NODES_PER_SIDE
    num_of_left_nodes = TOTAL_NODES_PER_SIDE

    ###### TOPOLOGY CREATION ######

    # Creating the routers for the dumbbell topology
    right_router = Router("right-router")
    left_router = Router("left-router")

    # Lists to store all the right and left nodes
    right_nodes = []
    left_nodes = []

    # Creating all the right and left nodes
    for i in range(num_of_right_nodes):
        right_nodes.append(Node("right-node-" + str(i)))

    for i in range(num_of_left_nodes):
        left_nodes.append(Node("left-node-" + str(i)))

    print("Nodes and routers created")

    # Add connections

    # Lists of tuples to store the interfaces connecting the router and nodes
    right_node_connections = []
    left_node_connections = []
    
    # A network object to auto generate addresses in the same network
    # This network is used for all the left-nodes and the left-router
    left_network = Network("10.0.0.0/24")
    
    # This network is used for all the right-nodes and the right-router
    right_network = Network("10.0.1.0/24")

    # This network is used for the connections between the two routers
    router_network = Network("10.0.2.0/24")

    # Connections of the right-nodes to the right-router
    for i in range(num_of_right_nodes):
        right_node_connections.append(connect(right_nodes[i], right_router, network=left_network))

    # Connections of the left-nodes to the left-router
    for i in range(num_of_left_nodes):
        left_node_connections.append(connect(left_nodes[i], left_router, network=right_network))

    # Connecting the two routers
    (right_router_connection, left_router_connection) = connect(right_router, left_router, network=router_network)

    print("Connections made")

    # ###### ADDRESS ASSIGNMENT ######

    # for i in range(num_of_right_nodes):
    #     # Copying a right-node's interface and it's pair to temporary variables
    #     node_int = right_node_connections[i][0]
    #     router_int = right_node_connections[i][1]

    #     # Assigning addresses to the interfaces
    #     node_int.set_address(right_network.get_next_addr())
    #     router_int.set_address(right_network.get_next_addr())

    # for i in range(num_of_left_nodes):
    #     # Copying a left-node's interface and it's pair to temporary variables
    #     node_int = left_node_connections[i][0]
    #     router_int = left_node_connections[i][1]

    #     # Assigning addresses to the interfaces
    #     node_int.set_address(left_network.get_next_addr())
    #     router_int.set_address(left_network.get_next_addr())

    # # Assigning addresses to the connections between the two routers
    # right_router_connection.set_address(router_network.get_next_addr())
    # left_router_connection.set_address(router_network.get_next_addr())

    # print("Addresses are assigned")

    ####### ROUTING #######

    # If any packet needs to be sent from any right-nodes, send it to right-router
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

    # Setting up the attributes of the connections between
    # the two routers
    right_router_connection.set_attributes(bottleneck_bandwidth, router_router_latency, AQM)
    left_router_connection.set_attributes(bottleneck_bandwidth, router_router_latency, AQM)


    ######  RUN TESTS ######

    exp_name = "tcp_" + str(NO_TCP_FLOWS) + "down"

    experiment = Experiment(exp_name)

    # Add TCP flows from the right nodes to respective left nodes
    for i in range(NO_TCP_FLOWS):
        flow = Flow(
            right_nodes[i], left_nodes[i], left_node_connections[i][0].address, 0, 40, 1
        )
        # Use TCP reno
        experiment.add_tcp_flow(flow)

    # Request traffic control stats
    experiment.require_qdisc_stats(right_router_connection)
    experiment.require_qdisc_stats(left_router_connection)

    # Running the experiment
    experiment.run()