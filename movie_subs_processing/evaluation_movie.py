 
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

total_wer = 0
total_cer = 0
total_sec = 0

bands_len = 2

ranges_tot = {}

wer = load_metric("wer")
cer = load_metric("cer")


result = open("results_movie.txt", "w") 



hug_dataset = create_hug_dataset(f"{file_transcripts}", f"{audio_directory}")
print(len(hug_dataset))

for index, batch in enumerate(hug_dataset):
    print(index)
    
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        speech_array, sampling_rate = librosa.load(f"{audio_directory}{batch['path']}", sr=16_000)
    batch["speech"] = speech_array
    batch["sentence"] = re.sub(chars_to_ignore_regex, "", batch["sentence"]).upper()

    inputs = processor(batch["speech"], sampling_rate=16_000, return_tensors="pt", padding=True)

    with torch.no_grad():
        logits = model(inputs.input_values, attention_mask=inputs.attention_mask).logits

    pred_ids = torch.argmax(logits, dim=-1)
    prediction = processor.batch_decode(pred_ids)

    prediction = re.sub(' +', ' ', prediction[0])

    print(f"PRED: {prediction.upper()}\nREF: {batch['sentence'].upper()}")

    wer_computed = wer.compute(predictions=[prediction.upper()], references=[batch["sentence"].upper()]) * 100
    cer_computed = cer.compute(predictions=[prediction.upper()], references=[batch["sentence"].upper()]) * 100

    info = torchaudio.info(f"{audio_directory}{batch['path']}")
    duration_sec = info.num_frames / info.sample_rate
    total_sec += duration_sec

    band = int(duration_sec / bands_len)

    if band not in ranges_tot:
        ranges_tot[band] = [1, wer_computed, cer_computed]
    else:
        ranges_tot[band][0] += 1
        ranges_tot[band][1] += wer_computed
        ranges_tot[band][2] += cer_computed
    
    total_wer += wer_computed
    total_cer += cer_computed

total_cer /= len(hug_dataset)
total_wer /= len(hug_dataset)

for band in ranges_tot.keys():
    mean_wer = ranges_tot[band][1] / ranges_tot[band][0]
    mean_cer = ranges_tot[band][2] / ranges_tot[band][0]
    result.write(f"[{int(band)*bands_len},{int(band)*bands_len+bands_len}) -> Count: {ranges_tot[band][0]}, Wer: {mean_wer}, Cer: {mean_cer}\n")

result.write(f"WER: {total_wer}, CER: {total_cer}\n")
result.write(f"Dataset Len: N. {len(hug_dataset)}, Sec. {total_sec}\n")


