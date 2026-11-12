from argparse import ArgumentParser, ArgumentTypeError
from os import getcwd
from os.path import isfile

from codec import encode, decode, compareSha256

ENCODE_OUTPUT = getcwd() + "/out/"
DECODE_OUTPUT = getcwd() + "/recovered/"
DEFAULT_NAME = "encoded"

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
    enc.add_argument("--name", default=DEFAULT_NAME, help="Output WAV filename (default: encoded.wav)")

    dec = options.add_parser("decode", help="Decodes a .wav file that was encoded by WavStore.")
    dec.add_argument("infile", type=file_path, help="The file to decode.")
    dec.add_argument("-o", "--outdir", help="The output folder where the result will be saved")

    com = options.add_parser("compare", help="Compares the SHA-256 checksums of two files.")
    com.add_argument("file1", type=file_path)
    com.add_argument("file2", type=file_path)

    args = parser.parse_args()

    match args.option:
        case "encode":  encode(args.infile, out=args.outdir or ENCODE_OUTPUT, name=args.name or DEFAULT_NAME)
        case "decode":  decode(args.infile, out=args.outdir or DECODE_OUTPUT)
        case "compare": print({"The files match!" if compareSha256(args.file1, args.file2) else "The files don't match!"})
        case _:         parser.print_usage()


if __name__ == "__main__":
    main()