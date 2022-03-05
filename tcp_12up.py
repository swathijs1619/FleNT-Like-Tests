from tcp_up_down import tcp_up
import sys

NO_TCP_FLOWS = 12
AQM = sys.argv[1]

tcp_up(NO_TCP_FLOWS, AQM)