import os
import argparse

from console import Console


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="File Backup command line App")
    parser.add_argument(
        "-ih", "--input_handler", help="type of a handler as an input", default=Console.LOCAL_HANDLER
    )
    parser.add_argument(
        "-oh", "--output_handler", help="type of a handler as an output",
        default=Console.LOCAL_HANDLER
    )

    default_location = os.getcwd()

    parser.add_argument("-i", "--input", help="input location", default=default_location)
    parser.add_argument("-o", "--output", help="output location", required=True)
    parser.add_argument("-v", "--validation", help="use validators defined in the configs", action="store_true")

    args = parser.parse_args()

    Console(
        input_handler=args.input_handler,
        output_handler=args.output_handler,
        input_path=args.input,
        output_path=args.output,
        validation=args.validation
    ).run()
