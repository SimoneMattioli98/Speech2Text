import IPython.display as ipd
import os

from torch._C import Value 
import cv2
audio_fold = "audio/"
mp3_files = os.listdir(audio_fold)

sent_dict = {}
sentences_path = "sentences.txt"
senteces_file = open(sentences_path, "r")
sentences = senteces_file.read()
sentences = sentences.split("\n")
for sent in sentences:
    if sent != "":
        sent_split = sent.split(" ", maxsplit=1)
        sent_dict[sent_split[0]] = sent_split[1]

for mp3_file in mp3_files:
    path_to_file = f"{audio_fold}{mp3_file}"
    name = mp3_file.split(".")[0]
    
    print(f"Audio file: {mp3_file}")
    print(f"Sentence\n{sent_dict[name]}")
    
    new_sent = input('Type new sent: ')
    if new_sent != "":
        sent_dict[name] = new_sent

    flag = input('Do you want to delete the audio? (y,n): ')
    if flag == "y":
        sent_dict.pop(name)
        os.remove(path_to_file)

os.remove(sentences_path)

with open(sentences_path, "w") as f:
    for key,value in sent_dict:
        f.write(f"{key} {value}\n\n")