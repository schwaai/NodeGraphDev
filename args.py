import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--listen",
                    type=str,
                    default="127.0.0.1",
                    metavar="IP",
                    nargs="?",
                    const="0.0.0.0",
                    help="Specify the IP address to listen on (default: 127.0.0.1). If --listen is provided without "
                         "an argument, it defaults to 0.0.0.0. (listens on all)")
parser.add_argument("--port", type=int, default=8188, help="Set the listen port.")
args = parser.parse_args()