
import os
from pydub import AudioSegment
import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np



fold = "audio/"


mp3_files = os.listdir(path=fold)


for mp3_file in mp3_files:
    name = mp3_file.split(".")[0]
    src = f"{fold}{mp3_file}"
    dst = f"{fold}{name}.wav"

    sound = AudioSegment.from_mp3(src)
    sound.export(dst, format="wav")
    os.remove(src)
    

