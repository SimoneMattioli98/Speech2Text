from datetime import datetime
from os import listdir
from os.path import join

folder = "txt"
file_used = "tot_files_used.txt"
distination_file_name = "sentences.txt"

already_sampled = []

with open(file_used, "r") as f:
    already_sampled = f.read().split('\n')

only_txt = [f for f in listdir(folder) if join(folder, f).endswith(".txt") and f not in already_sampled]

with open(file_used, "a") as f:
    for txt_name in only_txt: f.write(txt_name+'\n')

with open(distination_file_name, 'a') as f_dest:

    for txt in only_txt:

        with open(join(folder, txt), "r") as f_txt:
            for row in f_txt:
                now = datetime.now()
                now = now.strftime("%d%m%Y%H%M%S%f")
                f_dest.write(f"{now} {row}")