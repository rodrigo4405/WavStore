# WavStore

Store any file as sound. WavStore turns a file into a `.wav` made of pure tones (two tones per byte) and turns that `.wav` back into the original file.

## How it works

1. **Pack**: the file is wrapped with a small header: magic bytes `WVST`, the filename length, the data length, the filename, then the raw data.
2. **Compress**: the packed bytes are compressed with `zlib` (level 9).
3. **Split**: each byte is cut into two 4-bit halves (nibbles), each with a value from 0 to 15.
4. **Encode**: each nibble becomes a sine wave of a fixed duration, at the frequency `nibble * STEP + START`.
5. **Write**: all the tones are concatenated and saved as a mono 8-bit WAV file.

Decoding is the reverse: the WAV is cut into pieces of `DURATION` seconds, an FFT finds the strongest frequency in each piece, the frequency is mapped back to a nibble, pairs of nibbles are joined into bytes, and the bytes are decompressed and unpacked. A SHA-256 checksum is printed on both sides so you can verify the round trip.

## Requirements

- Python 3.14
- `numpy`
- `soundfile`
- `tqdm`
- `music`

```
pip install -r requirements.txt
```

## Installation

### Clone the Repository
```
git clone https://github.com/rodrigo4405/WavStore.git
cd WavStore/
```

## Usage

```
python src/main.py encode <input-file> -o [<output-dir>]
python src/main.py decode <input.wav> -o [<output-dir>]
```

The encoder writes `encoded.wav` inside the output directory. The decoder recreates the original file (with its original name) inside the output directory.

## Configuration

The constants in `src/codec.py` control the signal. The encoder and decoder must use the same values, because only the sample rate is stored in the WAV.

| Constant | Meaning | Current value |
|---|---|---|
| `N_TONES` | Number of distinct tones (4 bits per tone) | 16 |
| `START` | Frequency of nibble 0 (Hz) | 445 |
| `STEP` | Frequency gap between consecutive nibbles (Hz) | 50 |
| `DURATION` | Length of each tone (seconds) | 0.075 |
| `SAMPLE_RATE` | Samples per second, `round(2.5 * F_MAX)` | 2988 |

Files encoded with different constants will not decode correctly, so re-encode after changing any of them.

## Speed and size

Each byte takes two tones, so `2 * DURATION` seconds of audio: 1 KB of compressed data is about 2.5 minutes of sound.

The WAV size is roughly `compressed bytes * 2 * SAMPLE_RATE * DURATION` (about 448 bytes per compressed byte with the current values). 

Lowering `DURATION` makes files shorter, but the FFT resolution is `1 / DURATION` Hz, so `STEP` must stay at least that large for tones to remain distinguishable.

## Project layout

```
WavStore/
├── README.md
├── requirements.txt
├── samples/
└── src/
    ├── main.py     # command line entry point
    ├── codec.py    # pack/unpack, encode, decode
    └── utils.py    # helpers
```