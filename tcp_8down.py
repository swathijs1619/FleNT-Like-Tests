from tcp_up_down import tcp_down
import sys

NO_TCP_FLOWS = 8
AQM = sys.argv[1]

tcp_down(NO_TCP_FLOWS, AQM)