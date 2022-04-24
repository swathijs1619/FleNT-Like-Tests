# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2022 NITK Surathkal

########################
# SHOULD BE RUN AS ROOT
########################

# This program emulates "TCP download" experiment which takes AQM and number of tcp flows as input arguments
# from the users. Based on NO_TCP_FLOWS, the right and left nodes get created which are connected by two routers `r1` and `r2`. 
# Assuming left_nodes behave as clients and right_nodes as servers, this program calls the `tcp_down` method from the `tcp_up_down.py` file
# to emulate the "TCP download" scenario which is basically sending "NO_TCP_FLOWS" from right nodes to the corresponding left nodes.

from tcp_up_down import tcp_down
import sys

AQM = sys.argv[1]
NO_TCP_FLOWS = int(sys.argv[2])

tcp_down(NO_TCP_FLOWS, AQM)