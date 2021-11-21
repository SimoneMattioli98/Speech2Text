import re
from os.path import isfile, join
from os import listdir, walk
from datasets import Dataset, load_dataset, load_metric, concatenate_datasets
import torchaudio
import librosa
import numpy as np
from transformers import Wav2Vec2Processor
from transformers import Wav2Vec2ForCTC
import torch 
import random
import pandas as pd
import warnings
import os
from statistics import stdev, mean
import time

main_folder = "audio_voices/"

file_transcripts = f"sentences.txt"

audio_directory = f"audio/"

CHARS_TO_IGNORE = [",", "?", "¿", ".", "!", "¡", ";", ";", ":", '""', "%", '"', "?", "?", "·", "?", "~", "?",
                   "?", "?", "?", "?", "«", "»", "„", "“", "”", "?", "?", "‘", "’", "«", "»", "(", ")", "[", "]",
                   "{", "}", "=", "`", "_", "+", "<", ">", "…", "–", "°", "´", "?", "‹", "›", "©", "®", "—", "?", "?",
                   "?", "?", "?", "?", "~", "?", ",", "{", "}", "(", ")", "[", "]", "?", "?", "?", "?",
                   "?", "?", "?", "?", "?", "?", "?", ":", "!", "?", "?", "?", "/", "\\", "º", "-", "^", "?", "ˆ"]

chars_to_ignore_regex = f"[{re.escape(''.join(CHARS_TO_IGNORE))}]"

def remove_special_characters(sentence):
    sentence = re.sub(chars_to_ignore_regex, "", sentence).strip().upper() + " "
    return sentence

def create_hug_dataset(file_txt, directory):
    list_mp3 = []
    labels_dict = {}
    list_mp3 = listdir(directory)
    with open(file_txt, 'r') as f: 
        content = f.read()
        sentences = content.split(sep="\n")

    for sent in sentences:
        if(sent != ''):
            sent = re.sub(' +', ' ', sent)
            sent = sent.split(" ", maxsplit=1)
            labels_dict[sent[0]] = sent[1]

    audio_dict = {mp3.split("/")[-1].split(".")[0]: mp3 for mp3 in list_mp3}

    print("#### Removing special characters from labels mlls")

    labels_dict = {k: remove_special_characters(v) for k, v in labels_dict.items()}
    print(len(labels_dict))
    dict_dataset = {'path': [], 'sentence': []}

    

    for k, v in labels_dict.items():
        if k != "":
        
            dict_dataset['sentence'].append(v)
            dict_dataset['path'].append(audio_dict[k])
            

    tot_len = len(dict_dataset["path"])
    print(f"N DATA TEST: {tot_len}")

    return Dataset.from_dict(dict_dataset)

DEVICE = "cuda"

processor = Wav2Vec2Processor.from_pretrained("jonatasgrosman/wav2vec2-large-xlsr-53-italian")

model = Wav2Vec2ForCTC.from_pretrained("jonatasgrosman/wav2vec2-large-xlsr-53-italian")

start = time.time()

total_wer = 0
total_cer = 0
total_len = 0
total_sec = 0

bands_len = 2

standard_dev_audio = []
standard_dev_sec = []

ranges = {}
ranges_tot = {}

wer = load_metric("wer")
cer = load_metric("cer")

speakers = [ name for name in os.listdir(main_folder) if os.path.isdir(os.path.join(main_folder, name)) ]
print(len(speakers))

result = open("results_webinar.txt", "w") 

for speaker in speakers:

    print(speaker)
    path_to_speaker = f"{main_folder}{speaker}/"
    path_to_audio_dir = f"{path_to_speaker}{audio_directory}"
    hug_dataset = create_hug_dataset(f"{path_to_speaker}{file_transcripts}", f"{path_to_audio_dir}")
    total_len += len(hug_dataset)
    standard_dev_audio.append(len(hug_dataset))
    ranges[speaker] = {}

    
    for index, batch in enumerate(hug_dataset):
        print(index)
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            speech_array, sampling_rate = librosa.load(f"{path_to_audio_dir}{batch['path']}", sr=16_000)
        batch["speech"] = speech_array
        batch["sentence"] = re.sub(chars_to_ignore_regex, "", batch["sentence"]).upper()

        inputs = processor(batch["speech"], sampling_rate=16_000, return_tensors="pt", padding=True)

        with torch.no_grad():
            logits = model(inputs.input_values, attention_mask=inputs.attention_mask).logits

        pred_ids = torch.argmax(logits, dim=-1)
        prediction = processor.batch_decode(pred_ids)

        prediction = re.sub(' +', ' ', prediction[0])

        #print(f"PRED: {prediction.upper()}\nREF: {batch['sentence'].upper()}")

        wer_computed = wer.compute(predictions=[prediction.upper()], references=[batch["sentence"].upper()]) * 100
        cer_computed = cer.compute(predictions=[prediction.upper()], references=[batch["sentence"].upper()]) * 100

        info = torchaudio.info(f"{path_to_audio_dir}{batch['path']}")
        duration_sec = info.num_frames / info.sample_rate
        standard_dev_sec.append(duration_sec)
        total_sec += duration_sec

        band = int(duration_sec / bands_len)

        if band not in ranges[speaker]:
            ranges[speaker][band] = [1, wer_computed, cer_computed]
        else:
            ranges[speaker][band][0] += 1
            ranges[speaker][band][1] += wer_computed
            ranges[speaker][band][2] += cer_computed

        if band not in ranges_tot:
            ranges_tot[band] = [1, wer_computed, cer_computed]
        else:
            ranges_tot[band][0] += 1
            ranges_tot[band][1] += wer_computed
            ranges_tot[band][2] += cer_computed
        
        total_wer += wer_computed
        total_cer += cer_computed

total_cer /= total_len
total_wer /= total_len

end = time.time()

for speaker in sorted(ranges.keys()):
    result.write(f"{speaker}\n")
    for band in sorted(ranges[speaker].keys()):
        mean_wer = ranges[speaker][band][1] / ranges[speaker][band][0]
        mean_cer = ranges[speaker][band][2] / ranges[speaker][band][0]
        result.write(f"\t[{int(band)*bands_len},{int(band)*bands_len+bands_len}) -> Count: {ranges[speaker][band][0]}, Wer: {round(mean_wer, 2)}, Cer: {round(mean_cer, 2)}\n")

result.write(f"\nTotal Dataset\n")
for band in ranges_tot.keys():
    mean_wer = ranges_tot[band][1] / ranges_tot[band][0]
    mean_cer = ranges_tot[band][2] / ranges_tot[band][0]
    result.write(f"\t[{int(band)*bands_len},{int(band)*bands_len+bands_len}) -> Count: {ranges_tot[band][0]}, Wer: {round(mean_wer, 2)}, Cer: {round(mean_cer, 2)}\n")

n_audio_mean = mean(standard_dev_audio)
sec_mean = mean(standard_dev_sec)

standard_dev_sec = stdev(standard_dev_sec)
standard_dev_audio = stdev(standard_dev_audio)


result.write(f"WER: {round(total_wer)}, CER: {round(total_cer)}\n")
result.write(f"Dataset Len: N. {total_len}, Sec. {total_sec}, N° Audio Mean: {round(n_audio_mean, 2)}, Stdev N° Audio: {round(standard_dev_audio, 2)}, Sec. Mean: {round(sec_mean, 2)}, Stdev Sec.: {round(standard_dev_sec, 2)}\n")
result.write(f"Time elapsed: {round(end - start, 2)}\n")

