# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2022 NITK Surathkal

########################
# SHOULD BE RUN AS ROOT
########################

# This program emulates "TCP upload" experiment which takes AQM and number of tcp flows as input arguments
# from the users. Based on NO_TCP_FLOWS, the left and right nodes get created which are connected by two routers `r1` and `r2`. 
# Assuming left_nodes behave as clients and right_nodes as servers, this program calls the `tcp_upload` method from the `tcp_up_down.py` file
# to emulate the "TCP upload" scenario which is basically sending "NO_TCP_FLOWS" from left nodes to the corresponding right nodes.

from tcp_up_down import tcp_up
import sys

AQM = sys.argv[1]
NO_TCP_FLOWS = int(sys.argv[2])

tcp_up(NO_TCP_FLOWS, AQM)