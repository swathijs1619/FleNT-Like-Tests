# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2022 NITK Surathkal

########################
# SHOULD BE RUN AS ROOT
########################

# This program emulates "TCP download" experiment which takes AQM as input argument from the users. 
# But the NO_TCP_FLOWS is set to `2` denoting there is going to be two tcp flows from the rightnodes to the corresponding leftnodes,
# which is in accordance with its experiment name "tcp_2down". 
# the left and right nodes get created which are connected by two routers `r1` and `r2`. 
# Assuming left_nodes behave as clients and right_nodes as servers, this program calls the `tcp_down` method from the `tcp_up_down.py` file
# to emulate the "TCP download" scenario with `2` tcp flows.

from tcp_up_down import tcp_down
import sys

NO_TCP_FLOWS = 2
AQM = sys.argv[1]

tcp_down(NO_TCP_FLOWS, AQM)