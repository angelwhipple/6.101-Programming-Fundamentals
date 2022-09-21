def backwards(sound):
    return { 'rate': sound['rate'], 'samples': sound['samples'][::-1] }
    


def mix(sound1, sound2, p):
    if sound1['rate'] != sound2['rate']:
        return None
    else:
        out = []
        if len(sound1['samples']) <= len(sound2['samples']):
            for i in range(len(sound1['samples'])):
                out.append(sound1['samples'][i]*p + sound2['samples'][i]*(1-p))
        else:
            for i in range(len(sound2['samples'])):
                out.append(sound1['samples'][i]*p + sound2['samples'][i]*(1-p))
        return { 'rate': sound1['rate'], 'samples': out }


def echo(sound, num_echoes, delay, scale):
    sample_delay, samples, x = round(delay * sound['rate']), sound['samples'], 1
    echo = [0]*(len(samples)+(num_echoes*sample_delay))
    for i in range(len(samples)):
        echo[i] = samples[i]
    for i in range(1, num_echoes+1):
        pos = i*sample_delay
        for s in samples:
            echo[pos] += (scale**x)*s
            pos += 1
        x += 1
    return { 'rate': sound['rate'], 'samples': echo }
        
            


def pan(sound):
    l, r, x, n = [], [], 0.0, len(sound['left'])
    for i in range(n):
        r.append(sound['right'][i]*(x/(n-1)))
        l.append(sound['left'][i]*(1-x/(n-1)))
        x += 1.0
    return { 'rate': sound['rate'], 'left': l, 'right': r }


def remove_vocals(sound):
    mono = []
    for i in range(len(sound['left'])):
        mono.append(sound['left'][i] - sound['right'][i])
    return { 'rate': sound['rate'], 'samples': mono }
    


# below are helper functions for converting back-and-forth between WAV files
# and our internal dictionary representation for sounds

import io
import wave
import struct


def load_wav(filename, stereo=False):
    """
    Given the filename of a WAV file, load the data from that file and return a
    Python dictionary representing that sound
    """
    f = wave.open(filename, "r")
    chan, bd, sr, count, _, _ = f.getparams()

    assert bd == 2, "only 16-bit WAV files are supported"

    out = {"rate": sr}

    if stereo:
        left = []
        right = []
        for i in range(count):
            frame = f.readframes(1)
            if chan == 2:
                left.append(struct.unpack("<h", frame[:2])[0])
                right.append(struct.unpack("<h", frame[2:])[0])
            else:
                datum = struct.unpack("<h", frame)[0]
                left.append(datum)
                right.append(datum)

        out["left"] = [i / (2**15) for i in left]
        out["right"] = [i / (2**15) for i in right]
    else:
        samples = []
        for i in range(count):
            frame = f.readframes(1)
            if chan == 2:
                left = struct.unpack("<h", frame[:2])[0]
                right = struct.unpack("<h", frame[2:])[0]
                samples.append((left + right) / 2)
            else:
                datum = struct.unpack("<h", frame)[0]
                samples.append(datum)

        out["samples"] = [i / (2**15) for i in samples]

    return out


def write_wav(sound, filename):
    """
    Given a dictionary representing a sound, and a filename, convert the given
    sound into WAV format and save it as a file with the given filename (which
    can then be opened by most audio players)
    """
    outfile = wave.open(filename, "w")

    if "samples" in sound:
        # mono file
        outfile.setparams((1, 2, sound["rate"], 0, "NONE", "not compressed"))
        out = [int(max(-1, min(1, v)) * (2**15 - 1)) for v in sound["samples"]]
    else:
        # stereo
        outfile.setparams((2, 2, sound["rate"], 0, "NONE", "not compressed"))
        out = []
        for l, r in zip(sound["left"], sound["right"]):
            l = int(max(-1, min(1, l)) * (2**15 - 1))
            r = int(max(-1, min(1, r)) * (2**15 - 1))
            out.append(l)
            out.append(r)

    outfile.writeframes(b"".join(struct.pack("<h", frame) for frame in out))
    outfile.close()


if __name__ == "__main__":
    meow = load_wav("sounds/meow.wav")
    write_wav(backwards(meow), 'meow_reversed.wav')
    
    mystery = load_wav("sounds/mystery.wav")
    write_wav(backwards(mystery), 'mystery_reversed.wav')
    
    water, synth = load_wav("sounds/water.wav"), load_wav("sounds/synth.wav")
    write_wav(mix(synth, water, 0.2), 'water_synth_mix.wav')
    
    chord = load_wav("sounds/chord.wav")
    write_wav(echo(chord, 5, 0.3, 0.6), 'chord_echo.wav')
    
    car = load_wav("sounds/car.wav", stereo = True)
    write_wav(pan(car), 'car_pan.wav')
    
    mountain = load_wav("sounds/lookout_mountain.wav", stereo = True)
    write_wav(remove_vocals(mountain), 'no_vocals.wav')
