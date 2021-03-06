import sys
import time
import datetime
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
        pSample.sort()  # Order seems to be random without this.
        ret += f" {pSample}"

    return ret

def loopStatus(hostname, port, sleep=SLEEP_DEFAULT, diff=False):
    server = mcstatus.MinecraftServer(hostname, port)

    saved_s = None
    saved_s_time = None
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

        s = None
        s_time = time.time()
        ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(s_time))

        def print_ts():
            print(f"{ts}: ", end='', flush=True)

        if not diff:
            print_ts()

        try:
            if prev_ex is not None:
                raise prev_ex
            s = statusCvn(server)
        except KeyboardInterrupt:
            if diff:
                print_ts()
            print("(Keyboard interrupt. Exiting loop.)", flush=True)
            break
        except Exception as ex:
            s = f"(Error: {ex})"

        if not diff:
            print(s, flush=True)
        else:
            if s != saved_s:
                print_ts()

                if saved_s_time is not None:
                    # (As this is a network service intended to be queried
                    # much less than once per second, try to omit the
                    # fractional seconds part of the time delta, using round().)
                    delta = datetime.timedelta(seconds=round(s_time - saved_s_time))
                    print(f"After {delta}, changed to: {s}", flush=True)
                else:
                    print(f"Changed to: {s}", flush=True)

                saved_s = s
                saved_s_time = s_time

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
    parser.add_argument(
        '--diff', default=False, action='store_true',
        help='Output only when something has changed, i.e., when there is a difference')

    # Handle command-line, including --help etc.
    args = parser.parse_args()

    # Enter loop.
    loopStatus(args.hostname, args.port, args.sleep, args.diff)

    # Indicate clean exit via exit code 0.
    # (Assume that, if the loop returns, everything is alright;
    # errors to be reported via exception handling.)
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
