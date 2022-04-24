# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2022 NITK Surathkal

########################
# SHOULD BE RUN AS ROOT
########################

# This program emulates "TCP upload" experiment which takes AQM as input argument from the users. 
# But the NO_TCP_FLOWS is set to `6` denoting there is going to be 6 tcp flows from the leftnodes to the corresponding rightnodes,
# which is in accordance with its experiment name "tcp_6up". 
# the left and right nodes get created which are connected by two routers `r1` and `r2`. 
# Assuming left_nodes behave as clients and right_nodes as servers, this program calls the `tcp_up` method from the `tcp_up_down.py` file
# to emulate the "TCP upload" scenario with `6` tcp flows.

from tcp_up_down import tcp_up
import sys

NO_TCP_FLOWS = 6
AQM = sys.argv[1]

tcp_up(NO_TCP_FLOWS, AQM)