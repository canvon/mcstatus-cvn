import sys
import time
import argparse

import mcstatus

SLEEP_DEFAULT = 3*60  # 3 minutes

def statusCvn(server):
    status = server.status()
    players = status.players
    pOnline = players.online
    pMax = players.max
    ret = f"Players {pOnline}/{pMax}"

    sample = players.sample
    if sample is not None:
        pSample = list(map(lambda p: p.name, sample))
        ret += f" {pSample}"

    return ret

def loopStatus(hostname, port, sleep=SLEEP_DEFAULT):
    server = mcstatus.MinecraftServer(hostname, port)

    first = True
    while True:
        prev_ex = None
        if first:
            first = False
        else:
            try:
                time.sleep(sleep)
            except KeyboardInterrupt as ex:
                prev_ex = ex

        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        s = None
        print(f"{ts}: ", end='', flush=True)
        try:
            if prev_ex is not None:
                raise prev_ex
            s = statusCvn(server)
        except KeyboardInterrupt:
            print("(Keyboard interrupt. Exiting loop.)", flush=True)
            break
        except Exception as ex:
            print(f"(Error: {ex})", flush=True)
            continue
        print(s, flush=True)

def main(argv):
    if not isinstance(argv, list):
        raise TypeError(f"List of command-line arguments argv needs to be (derived from) type list, but got type {type(argv).__name__!r}")
    if not len(argv) >= 1:
        raise ValueError(f"List of command-line arguments argv needs to at least contain the script name")

    # Prepare command-line arguments parser.
    parser = argparse.ArgumentParser(
        description="Minecraft status script which wraps Dinnerbone's mcstatus to loop over only the data of interest to canvon")
    parser.add_argument(
        'hostname', metavar='HOSTNAME', type=str,
        help='Hostname of the Minecraft server to query in a loop')
    parser.add_argument(
        'port', metavar='PORT', type=int,
        help='Port number of Minecraft server')
    parser.add_argument(
        '--sleep', metavar='SLEEP_SECONDS', default=SLEEP_DEFAULT, type=int,
        help='Seconds to sleep between each iteration of the loop')

    # Handle command-line, including --help etc.
    args = parser.parse_args()

    # Enter loop.
    loopStatus(args.hostname, args.port, args.sleep)

    # Indicate clean exit via exit code 0.
    # (Assume that, if the loop returns, everything is alright;
    # errors to be reported via exception handling.)
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
