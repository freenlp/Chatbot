import torch
import numpy as np


def read_vocab(vocab_dir):
    """读取词汇表"""
    with open(vocab_dir, 'r') as fp:
        words = [_.strip() for _ in fp.readlines()]
    word_to_id = dict(zip(words, range(len(words))))
    return words, word_to_id

class PredictionData():

    def __init__(self, vocab_file, sen_len):
        self.words, self.word_to_id = read_vocab(vocab_file)
        self.SOS = self.word_to_id['<SOS>']
        self.EOS = self.word_to_id['<EOS>']
        self.vocab_file = vocab_file
        self.sen_len = sen_len

    def crop_pad(self, content):
        if len(content) > self.sen_len:
            content = content[0:self.sen_len]
            # content[-1] = self.EOS
            return content, self.sen_len
        else:
            pad_start = len(content)
            tmp_zero = [self.EOS]       # * (self.sen_len - len(content))
            content.extend(tmp_zero)
            return content, pad_start

    def get_ids_by_words(self, words):
        encoder_data_id = [self.word_to_id[x] for x in words if x in self.word_to_id]
        decoder_data_id = [self.SOS]

        encoder_data_id, pad_start = self.crop_pad(encoder_data_id)

        encoder_data_id = torch.LongTensor(np.array(encoder_data_id, dtype=np.int64))
        decoder_data_id = torch.LongTensor(np.array(decoder_data_id, dtype=np.int64))

        return encoder_data_id, decoder_data_id


    def get_sos_id(self):
        return self.SOS

    def get_eos_id(self):
        return self.EOS

    def get_word_by_id(self, id):
        return str(self.words[id])
