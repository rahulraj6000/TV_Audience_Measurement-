from porcupine import Porcupine
import os
import struct
import sys
import pyaudio
import time
import soundfile
import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), './binding/python'))

# hello_benji_linux.ppn not for commercial use
keyword_file_path = os.path.join(
    os.path.dirname(__file__), './hi_barc_linux.ppn')
machine = 'x86_64'
library_path = os.path.join(os.path.dirname(
    __file__), './lib/linux/%s/libpv_porcupine.so' % machine)
model_file_path = os.path.join(os.path.dirname(
    __file__), './lib/common/porcupine_params.pv')
output_path = os.path.join(os.path.dirname(__file__), './recorded.wav')
sensitivity = 0.5
sample_rate = 0


def trigger_detect():
    porcupine = None
    pa = None
    audio_stream = None
    record = []
    done = 0
    try:
        porcupine = Porcupine(
            library_path, model_file_path, keyword_file_path, sensitivity)
        pa = pyaudio.PyAudio()
        global sample_rate
        sample_rate = porcupine.sample_rate
        audio_stream = pa.open(
            rate=porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=porcupine.frame_length,
            input_device_index=None)
        start = time.time()
        while True:
            #print("While True")
            end = time.time()
            if (end-start) < 2:
                pcm = audio_stream.read(porcupine.frame_length)
                pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
                result = porcupine.process(pcm)
                record.append(pcm)
                if result:
                    print('Starting BARC')
                    done = 1
            else:
                print("Entering")
                if done == 1:
                    recorded_audio = np.concatenate(
                        record, axis=0).astype(np.int16)
                    soundfile.write(output_path, recorded_audio,
                                    samplerate=sample_rate, subtype='PCM_16')
                    done = 0
                    ##
                record = []
                start = time.time()

    except KeyboardInterrupt:
        print('stopping ...')
    finally:
        if porcupine is not None:
            porcupine.delete()
        if audio_stream is not None:
            audio_stream.close()
        if pa is not None:
            pa.terminate()


if __name__ == '__main__':
    recorded = trigger_detect()
