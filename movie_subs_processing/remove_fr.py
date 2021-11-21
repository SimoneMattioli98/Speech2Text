import torchvision.transforms as tf
import torch
from PIL import Image
import torch.nn as nn
import torch.nn.functional as F
import os

class CNN_model_3(nn.Module):
    def __init__(self):
        '''
        opt_fun = optimizer function (eg: torch.optim.SGD)
        lr = learning rate
        **opt_params = extra optional parameters for optimizer function (eg: weight_decay, momentum, etc...)
        '''
        super(CNN_model_3, self).__init__()

        self.net = nn.Sequential(

           # convolution layers
            nn.Conv2d(3, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),     # adding batch normalization
            nn.ReLU(),
            nn.Conv2d(64, 128, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.MaxPool2d(2, 2), # output: 128 x 32 x 32
            nn.Dropout(p=0.25), # adding dropout regularization

            nn.Conv2d(128, 256, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(),
            nn.Conv2d(256, 256, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(),
            nn.MaxPool2d(2, 2), # output: 256 x 16 x 16
            nn.Dropout(p=0.25),

            nn.Conv2d(256, 512, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(512),
            nn.ReLU(),
            nn.Conv2d(512, 512, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(512),
            nn.ReLU(),
            nn.MaxPool2d(2, 2), # output: 512 x 8 x 8
            nn.Dropout(p=0.25),

            nn.Conv2d(512, 512, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(512),
            nn.ReLU(),
            nn.Conv2d(512, 512, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(512),
            nn.ReLU(),
            nn.MaxPool2d(2, 2), # output: 512 x 4 x 4
            nn.Dropout(p=0.25),

            # flatten then go through some dense layers
            nn.Flatten(),
            nn.Linear(512*4*4, 1024),
            nn.BatchNorm1d(1024),
            nn.ReLU(),
            nn.Dropout(p=0.25),
            nn.Linear(1024, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(),
            nn.Dropout(p=0.25),
            nn.Linear(512, 5))   # output of 5 for each of our class
    def forward(self, x):
      """Perform a forward pass and return the outputs"""
      return self.net(x)  # pass through the network


model = CNN_model_3()
checkpoint = torch.load("cnn_model_trained.pt",map_location=torch.device('cpu'))
model.load_state_dict(checkpoint)

transformations = tf.Compose([tf.Resize([64,64]), tf.ToTensor()])
fold = "images/"
images = os.listdir(path=fold)
it = 0
fr = 0
threshold = 2
sentences_file = "sentences.txt"
new_sentences_file = "sentences_cleaned.txt"
sent_dict = {}
with open(sentences_file, "r") as r:
    sentences = r.read()
    sentences = sentences.split("\n")
    for sent in sentences:
        if sent != "":
            sent = sent.split(" ", maxsplit=1)
            sent_dict[sent[0]] = sent[1]



with open(new_sentences_file, "w") as w:
    for img in images:
        name = img.split(".")[0]    
        img = Image.open(f"{fold}{img}")

        img = transformations(img)

        img = img[:3]

        img = img.unsqueeze(0)

        img.shape

        with torch.no_grad():
            model.eval()
            outputs = model(img)
            pred = torch.argmax(outputs)
            print(pred)
            if pred == 0 or outputs[0][0] > threshold:
                fr += 1
                os.remove(f"audio/{name}.wav")
            else:
                w.write(f"{name} {sent_dict[name]}\n\n")
                it += 1


    

print(fr)
print(it)

