import music
import zlib, struct
from hashlib import sha256
from pathlib import Path
import numpy as np

START = 100
STEP = 5
DURATION = 0.2

MAGIC = b"PERF"

def byte_to_freq(byte):
    return byte * STEP + START

def freq_to_byte(freq):
    return round((freq-START) / STEP)

def piece_to_freq(piece, sample_rate):
    strengths = np.abs(np.fft.rfft(piece))
    freqs = np.fft.rfftfreq(len(piece), 1/sample_rate)
    best = np.argmax(strengths)

    return freqs[best]

def pack(path):
    data = path.read_bytes()
    filename = path.name.encode()
    header = MAGIC + struct.pack(">BI", len(filename), len(data)) + filename
    return header + data

def unpack(blob):
    if blob[:len(MAGIC)] != MAGIC:
        return ValueError("Yo this aint right")

    cursor = 9
    name_len, data_len = struct.unpack(">BI", blob[4:cursor])
    name = blob[cursor:cursor+name_len].decode()
    cursor += name_len
    data = blob[cursor:cursor+data_len]

    if len(data) != data_len:
        raise ValueError("Couldn't retrieve the full data.")
    return name, data

def bytes_to_samples(data):
    data = zlib.compress(data)

    samples = []
    for byte in data:
        samples.append(byte_to_freq(byte))
    return samples

def generate_audio(samples, path):
    notes = [music.note(sample, duration=DURATION) for sample in samples]
    music.write_wav_mono(music.horizontal_stack(*notes), path, sample_rate=44100)

def checksum(bytes):
    return sha256(bytes).hexdigest()

def decode(path, out):
    samples, sample_rate = music.read_audio(path, return_sample_rate=True)
    n_samples = round(sample_rate * DURATION)
    values = []

    for start in range(0, len(samples), n_samples):
        piece = samples[start:start+n_samples]
        freq = float(piece_to_freq(piece, sample_rate))
        values.append(freq_to_byte(freq))

    result = zlib.decompress(bytes(values))
    try:
        name, data = unpack(result)
    except ValueError as e:
        print(e)
        return

    Path(out).mkdir(exist_ok=True)
    Path(out, Path(name).name).write_bytes(data)

    print(f"Recovered file can be found at {out+name}  \n(checksum): {checksum(data)}")

def encode(path, out):
    samples = bytes_to_samples(pack(Path(path)))

    Path(out).mkdir(exist_ok=True)
    fpath = Path(out, "encoded.wav")
    generate_audio(samples, fpath)
    print(f"Output can be found at: {out + fpath.name} \n(checksum): {checksum(fpath.read_bytes())}")
