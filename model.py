# Code for recording
import time
import numpy as np
import sounddevice as sd
fs = 44100  # Sample rate (IDK)
seconds = 10  # maximum duration of recording
threshold = 0.003  # Adjust this threshold as needed, it is good so far
wait = 4  # wait time between checking the silence
# function for recording whenever called. It stops recording whenever the max volume over the last four seconds is below a threshold, i.e. silence for four seconds. It stops if time passed 10 sec regardless, though.
# It returns a variable with the audio recorded


def recording(fs, seconds, threshold, wait):
    fs = fs  # Sample rate (IDK)
    seconds = seconds  # maximum duration of recording
    threshold = threshold  # Adjust this threshold as needed, it is good so far

    def is_silence(audio_chunk, threshold):
        return np.max(np.abs(audio_chunk)) < threshold

    myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)

    i = 0  # index for checking the silence in the my recording variable as it goes
    start = time.time()  # starting time
    t_end = time.time() + seconds  # maximum end time
    while True:   # check the silence for the maximum time of the recording
        time.sleep(wait)
        audio_chunk = myrecording[i:i + wait*int(fs / seconds)]
        if is_silence(audio_chunk, threshold) or time.time() > t_end:
            sd.stop()
            print("recording stopped", np.max(np.abs(audio_chunk)))
            break  # Stop recording when silence is detected
        print(np.max(np.abs(audio_chunk)), "still recording")
        i += wait*int(fs / seconds)
    print("length of recording", time.time()-start, "seconds")
    # testing
    # sd.play(myrecording, fs)
    # status = sd.wait()
    return myrecording
# uncomment the next line to test
# recording(fs, seconds, threshold, wait)