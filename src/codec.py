import music
import soundfile as sf
import zlib, struct
from hashlib import sha256
from pathlib import Path
import numpy as np
from tqdm import tqdm

from utils import file_size

N_TONES = 16
CHUNK = 250
START = 450
STEP = 50
DURATION = 0.075
F_MAX = START + (N_TONES - 1) * STEP
SAMPLE_RATE = round(2.5 * F_MAX)

MAGIC = b"WVST"

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
        raise ValueError("This file wasn't encoded by WavStore")

    cursor = 9
    name_len, data_len = struct.unpack(">BI", blob[4:cursor])
    name = blob[cursor:cursor+name_len].decode()
    cursor += name_len
    data = blob[cursor:cursor+data_len]

    if len(data) != data_len:
        raise ValueError("Couldn't retrieve the full data.")
    return name, data

def checksum(bytes):
    return sha256(bytes).hexdigest()

def compareSha256(path1, path2):
    checksum1 = checksum(Path(path1).read_bytes())
    checksum2 = checksum(Path(path2).read_bytes())

    return checksum1 == checksum2

def decode(path, out):
    samples, sample_rate = music.read_audio(path, return_sample_rate=True)
    n_samples = round(sample_rate * DURATION)
    values = []

    for start in range(0, len(samples)-n_samples+1, n_samples):
        piece = samples[start:start+n_samples]
        freq = piece_to_freq(piece, sample_rate)
        values.append(freq_to_byte(freq))

    packed = bytes((values[i] << 4) | values[i+1] for i in range(0,len(values)-1, 2)) 
    try:
        result = zlib.decompress(packed)
        name, data = unpack(result)
    except (ValueError, zlib.error) as e:
        print(e)
        return

    Path(out).mkdir(exist_ok=True)
    fpath = Path(out, Path(name).name)
    fpath.write_bytes(data)

    print(f"Recovered file can be found at {fpath.absolute()}  \n(sha256 checksum): {checksum(data)}")

def encode(path, name, out):
    data = zlib.compress(pack(Path(path)), level=9)
    
    samples = []
    for byte in data:
        samples.append(byte_to_freq(byte >> 4))
        samples.append(byte_to_freq(byte & 0x0F))

    Path(out).mkdir(exist_ok=True)
    fpath = Path(out, name.rstrip(".wav") + ".wav")

    print("\nEncoding your file. Please wait...")
    with sf.SoundFile(fpath, "w", samplerate=SAMPLE_RATE, channels=1, subtype="PCM_U8") as f:
        for start in tqdm(range(0, len(samples), CHUNK), bar_format="{l_bar}{bar} {n_fmt}/{total_fmt} [{elapsed}<{remaining}]"):
            notes = [music.note(sample, duration=DURATION, sample_rate=SAMPLE_RATE) for sample in samples[start:start+CHUNK]]
            f.write(music.horizontal_stack(*notes))

    print(f"\nOutput can be found at: {fpath.absolute()} [{file_size(fpath)}] \n(sha256 checksum): {checksum(Path(path).read_bytes())}")
