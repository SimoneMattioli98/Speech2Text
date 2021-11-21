from transformers import (
            Wav2Vec2ForCTC,
            Wav2Vec2Processor,
        )

class Wav2Vec2():

    def __init__(self, model, processor):

        #initialize the model 
        self.model = Wav2Vec2ForCTC.from_pretrained(model)
        self.processor = Wav2Vec2Processor.from_pretrained(processor)