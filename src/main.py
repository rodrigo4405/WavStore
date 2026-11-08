from argparse import ArgumentParser, ArgumentTypeError
from os import getcwd
from os.path import isfile

from codec import encode, decode

ENCODE_OUTPUT = getcwd() + "/out/"
DECODE_OUTPUT = getcwd() + "/recovered/"

def file_path(path):
    if isfile(path):
        return path
    else:
        raise ArgumentTypeError(f"{path} is not a valid file")

def main():
    parser = ArgumentParser(prog="WavStore")

    options = parser.add_subparsers(dest="option")

    enc = options.add_parser("encode", help="Encodes a file to a .wav file")
    enc.add_argument("infile", type=file_path, help="The file to encode.")
    enc.add_argument("-o", "--outdir", help="The output folder where the result will be saved")

    dec = options.add_parser("decode", help="Decodes a .wav file that was encoded by WavStore.")
    dec.add_argument("infile", type=file_path, help="The file to decode.")
    dec.add_argument("-o", "--outdir", help="The output folder where the result will be saved")

    args = parser.parse_args()

    match args.option:
        case "encode": encode(args.infile, out=args.outdir or ENCODE_OUTPUT)
        case "decode": decode(args.infile, out=args.outdir or DECODE_OUTPUT)


if __name__ == "__main__":
    main()