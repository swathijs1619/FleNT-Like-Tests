from tcp_up_down import tcp_down
import sys

AQM = sys.argv[1]
NO_TCP_FLOWS = int(sys.argv[2])

tcp_down(NO_TCP_FLOWS, AQM)