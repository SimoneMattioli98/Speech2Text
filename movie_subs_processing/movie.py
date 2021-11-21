import re
from pydub import AudioSegment
from num2words import num2words

def h_2_ml(value):
    hours = value.lstrip('0')
    if hours != '':
        return int(hours) * 60 * 60 * 1000
    return 0

def m_2_ml(value):
    mins = value.lstrip('0')
    if mins != '':
        return int(mins) * 60 * 1000
    return 0

def s_2_ml(value):
    secs = value.lstrip('0')
    if secs != '':
        return int(secs) * 1000
    return 0

#unpack the subtitles file
with open("lisoladellerose.srt", 
            encoding = "ISO-8859-1") as sub_file:
    sub_file = sub_file.read()

#all the operations below are based on the file format

'''
each scene is mapped as a number and in the file has this format

id
h:m:s,ml --> h:m:s,ml
<tag> subtitle <tag>
.
.
.
there could be more than one

'''

#divide the scenes
split_file = sub_file.split("\n\n")

#remove empty strings
split_file = list(filter(None, split_file))

#save in a dictionary each scene with the respective time and subtitles
sub_dict = {}
base_dict = {"start" : None, "end": None, "sub": None}
for split in split_file :
    content = split.split("\n", maxsplit=2)
    id = content[0]
    #remove html tags from subtitles
    subtitle = re.sub('<.*?>', '', content[2])
    #replace newline with spaces
    subtitle = subtitle.replace("\n", " ")
    #remove words btw opening squares
    subtitle = re.sub('\[.*?\]', '', subtitle)

    if subtitle.isupper():
        subtitle = ''

    #skipp if the subtitle is empty
    if subtitle == '':
        continue

    new_subtitle = ""
    for word in subtitle.split(" "):
        word = word.replace(".","")
        if(word.isnumeric()):
            word = num2words(int(word), lang='it')
        new_subtitle += word + " " 

    #remove arrow btw start and end
    start_end = content[1].replace(" --> ", " ")
    #replace , with :
    start_end = start_end.replace(",", ":")
    #split start and end
    start_end = start_end.split(" ")
    start = start_end[0].split(":")
    end = start_end[1].split(":")

    #string to millisecond
    start = h_2_ml(start[0]) + m_2_ml(start[1]) + s_2_ml(start[2]) + int(start[3])
    end = h_2_ml(end[0]) + m_2_ml(end[1]) + s_2_ml(end[2]) + int(end[3]) 

    base_dict = {"start" : start, "end": end, "sub": subtitle}

    sub_dict[id] = base_dict

sound = AudioSegment.from_mp3("lisoladellerose.mp3")
flag = False
start = 0
end = 0
millis = 8_000 #milliseconds
sent = ""
sentences = open("sentences.txt", "w")
for key, value in sub_dict.items():
    if not flag:
        start = value['start']
        flag = True
    end = value['end']
    sent += " " + value['sub']

    if end - start >= millis:
        slice = sound[start:end]
        slice.export(f'audio/{key}.mp3', format='mp3')
        flag = False
        sentences.write(f'{key} {sent}\n\n')
        sent = ""
        


