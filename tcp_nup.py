from tcp_up_down import tcp_up
import sys

AQM = sys.argv[1]
NO_TCP_FLOWS = int(sys.argv[2])

tcp_up(NO_TCP_FLOWS, AQM)