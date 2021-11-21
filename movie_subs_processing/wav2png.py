import os
import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np

fold = "audio/"
dst_dir = "images"
if not os.path.exists(dst_dir):
    os.mkdir(dst_dir)
wav_files = os.listdir(fold)
n_fft = 2048
hop_length = 512
n_mels = 64
f_min = 20
f_max = 8000
sample_rate = 16000
for wav_file in wav_files:
    name = wav_file.split(".")[0]

    clip, sample_rate = librosa.load(path=f"{fold}{wav_file}")
    duration = len(clip)

    # clip = clip[16000:16000+60000] if duration >= 76000 else clip[:60000]
    # initialize our plot for the melspectrogram
    
    fig = plt.figure(figsize=[0.75,0.75])
    ax = fig.add_subplot(111)
    ax.axes.get_xaxis().set_visible(False)
    ax.axes.get_yaxis().set_visible(False)
    ax.set_frame_on(False)

    # create the melspectrogram as a plot
    mel_spec = librosa.feature.melspectrogram(clip, n_fft=n_fft, hop_length=hop_length, n_mels = n_mels,
                                    sr=sample_rate, power=1.0, fmin=f_min, fmax=f_max)
    librosa.display.specshow(librosa.amplitude_to_db(mel_spec, ref=np.max), fmax=f_max, sr=sample_rate)

    # extract the speaker from filename and rename with autoincrement key

    filename  = f"{dst_dir}/{name}.png"

    # save the output image
    plt.savefig(filename, dpi=400, bbox_inches='tight',pad_inches=0)
    fig.clear()
    plt.close(fig)