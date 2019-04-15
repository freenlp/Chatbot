import data_load as dl
import torch
import numpy as np
from lstm import Seq2seq

class QaEngine:
    def __init__(self):
        # 词汇表
        vo_file = 'qa/ai.vocab.txt'
        self.sentence_len = 80
        self.vo_size = 400
        self.batch_size = 1

        self.hidden_size = 256
        self.embedding_length = 100
        self.data_layer = dl.PredictionData(vo_file, self.sentence_len)
        self.model = Seq2seq(self.batch_size, self.hidden_size, self.vo_size, self.embedding_length)
        self.model.load_state_dict(torch.load('qa/params.pkl'))

        if torch.cuda.is_available():
            self.model.cuda()
        self.model.eval()

    def prediction(self, question):
        eos_id = self.data_layer.get_eos_id()
        encoder_input, decoder_input = self.data_layer.get_ids_by_words(question)
        encoder_input = encoder_input.unsqueeze(0)
        if torch.cuda.is_available():
            encoder_input = encoder_input.cuda()
            decoder_input = decoder_input.cuda()

        output, hidden = self.model.encoder(encoder_input, self.batch_size, None)
        decoder_hidden = hidden
        decoder_input = decoder_input.unsqueeze(0)
        answer = ""
        for di in range(self.sentence_len):
            decoder_output, decoder_hidden = self.model.decoder(
                decoder_input, decoder_hidden)
            id = torch.argmax(decoder_output.squeeze()).item()
            if id == eos_id:
                break
            word = self.data_layer.get_word_by_id(id)
            answer += word
            decoder_input = torch.LongTensor(np.array([id], dtype=np.int64)).unsqueeze(0)
            if torch.cuda.is_available():
                decoder_input = decoder_input.cuda()
        return answer

if __name__ == "__main__":

    question = "什么是ai"
    qa = QaEngine()
    answer = qa.prediction(question)
    print(answer)


