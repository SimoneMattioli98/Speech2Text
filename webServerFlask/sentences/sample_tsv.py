import csv
from datetime import datetime
from os.path import join
from os import listdir

folder = "tsv"
file_used = "tot_files_used.txt"
distination_file_name = "sentences.txt"

colum_text_name = "sentence"
colum_text_index = 0

already_sampled = []

with open(file_used, "r") as f:
    already_sampled = f.read().split('\n')

only_tsv = [f for f in listdir(folder) if join(folder, f).endswith(".tsv") and f not in already_sampled]

with open(file_used, "a") as f:
    for tsv_name in only_tsv: f.write(tsv_name+'\n')

with open(distination_file_name, "a") as f_txt:
    
    for tsv in only_tsv:

        with open(join(folder, tsv), 'r') as f_tsv:
            
            read_tsv = csv.reader(f_tsv, delimiter="\t")
            for index, row in enumerate(read_tsv):
                if index == 0 : colum_text_index = row.index(colum_text_name)
                else:
                    sentence = row[colum_text_index]
                    now = datetime.now()
                    now = now.strftime("%d%m%Y%H%M%S%f")
                    f_txt.write(f"{now} {sentence}\n")

            
