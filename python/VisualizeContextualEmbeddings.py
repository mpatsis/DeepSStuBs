import time
import sys
import json
import os
from os.path import join
from os import getcwd
from collections import Counter, namedtuple
import math
import numpy as np

import umap
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import seaborn as sns

import tensorflow as tf
config = tf.ConfigProto()
config.gpu_options.allow_growth = True  # dynamically grow the memory used on the GPU
# config.log_device_placement = True  # to log device placement (on which device the operation ran)

import model.ModelFactory
from model.ModelFactory import *
import model.ELMoModel
from ELMoModel import *

from gensim.models import FastText
from threading import Thread
from Util import *
from bilm import TokenBatcher


def get_tokens(filename):
    query_size = 500
    with open(filename) as json_file:
        data = json.load(json_file)
        print("Files:", len(data))
        tokens = []
        for file_tokens in data:
            if len(file_tokens) < query_size:
                tokens.append(file_tokens)
            else:
                for i in range(0, len(file_tokens), query_size):
                    tokens.append(file_tokens[i: i + query_size])
        return tokens
        # print(len(data))
        # print(data[0])
        # print(len(data))
        


if __name__ == '__main__':
    raw_code = [
        'STD:function STD:( ID:e STD:, ID:tags STD:) STD:{ ID:tags STD:. ID:should STD:. ' + 
        'ID:have STD:. ID:lengthOf STD:( LIT:1 STD:) STD:; ID:done STD:( STD:) STD:; STD:} '
        'STD:) STD:; STD:} STD:) STD:; STD:} STD:) STD:; STD:} STD:) STD:; STD:} STD:) STD:; ' +
        'STD:} STD:) STD:; STD:} STD:) STD:; STD:} STD:) STD:; STD:} STD:) STD:; STD:} STD:) ' +
        'STD:; STD:} STD:) STD:;',
        'STD:var ID:gfm STD:= ID:require STD:( LIT:github-flavored-markdown STD:) STD:;'
    ]
    tokenized_code = [sentence.split() for sentence in raw_code]
    print(tokenized_code)

    batch_size = 16
    vocab_file = 'ELMoVocab.txt'
    # Location of pretrained LM. .
    model_dir = '/disk/scratch/mpatsis/eddie/models/phog/js/elmo/emb100_hidden1024_steps20_drop0.1/'
    options_file = os.path.join(model_dir, 'query_options.json')
    weight_file = os.path.join(model_dir, 'weights/weights.hdf5')

    with tf.Session() as sess:
        elmo = ELMoModel(model_dir, vocab_file, weight_file, options_file, sess)

        # It is necessary to initialize variables once before running inference.
        sess.run(tf.global_variables_initializer())

        time_start = time.time()

        token_emb = elmo.get_embedding('STD:function')
        print(token_emb)
        print(token_emb[0].shape)
        
        token_embs = elmo.get_sequence_token_embeddings(tokenized_code)
        print(token_embs)
        print(token_embs[0].shape)

        time_end = time.time()
        print('Lasted: ', time_end - time_start)
        
        time_start = time.time()
        tokens = get_tokens('tokens/tokens_test_1561467600278.json')
        print("Sequences:", len(tokens))
        embeddings_ELMo = []
        for i in range(0, len(tokens), batch_size):
            query = tokens[i: i + batch_size]
            token_embs = elmo.get_sequence_token_embeddings(query)
            for embeddings, query_part in zip(token_embs, query):
                for t_index in range(len(query_part)):
                    embeddings_ELMo.append(embeddings[t_index])
            break
        time_end = time.time()
        print('Getting embeddings lasted: ', time_end - time_start)

        time_start = time.time()
        reducer = umap.UMAP()
        # Learn UMAP reduction on the original space
        reducer.fit(embeddings_ELMo)
        print('Learned mapping!')
        print(reducer)
        print(reducer.transform(embeddings_ELMo))
        time_end = time.time()
        print('Learning reduction mapping lasted: ', time_end - time_start)
        

        example_tokens = [[ 'STD:var', 'ID:one', 'STD:=', 'LIT:1', 'STD:;',   'ID:one', 'STD:=', 'LIT:one', 'STD:;', 'ID:one', 'STD:=', 'LIT:1.1', 'STD:;',
            'ID:one', 'STD:=',  'LIT:true', 'STD:;', 'ID:one',  'STD:=', 'LIT:null', 'STD:;' ]]
        
        example_embs = elmo.get_sequence_token_embeddings(example_tokens)[0]
        print(example_embs)
        mapped_example_embs = reducer.transform(example_embs)
        print(mapped_example_embs)
        
        # fontsize = 16
        # # Create and save plot
        # plt.figure(figsize=(20, 10))
        # # plt.scatter(mapped_example_embs[:, 0], mapped_example_embs[:, 1], c=[sns.color_palette()[1] ])
        # for e, text in zip(mapped_example_embs, example_tokens[0]):
        #     print(e[0], e[1], text)
        #     plt.text(e[0], e[1], text)
        # plt.gca().set_aspect('equal', 'datalim')
        # plt.title('UMAP projection of example code embeddings', fontsize=fontsize);
        # plt.savefig('typeExample.png')

    
        fig = plt.figure()
        fig.suptitle('bold figure suptitle', fontsize=14, fontweight='bold')

        ax = fig.add_subplot(111)
        fig.subplots_adjust(top=0.85)
        ax.set_title('axes title')

        ax.set_xlabel('xlabel')
        ax.set_ylabel('ylabel')

        for e, text in zip(mapped_example_embs, example_tokens[0]):
            ax.text(e[0], e[1], text, fontsize=12)


        # ax.text(0.95, 0.01, 'colored text in axes coords',
        #         verticalalignment='bottom', horizontalalignment='right',
        #         transform=ax.transAxes,
        #         color='green', fontsize=15)

        # ax.text(5, 6, r'an equation: $E=mc^2$', fontsize=15)


        # ax.plot([2], [1], 'o')


        ax.axis([-40, 40, -40, 40])

        plt.show()
        plt.savefig('typeExample.png')


