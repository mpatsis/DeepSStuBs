import json

import model.AbstractModel
# from AbstractModel import *
import model.Word2VecModel
import model.FastTextModel
import model.ELMoBPEModel


# Supported models 
supported_models = ['w2v', 'FastText', 'ELMoBPE']


class ModelFactory:

    def __init__(self, config_file):
        """[summary]
        
        Arguments:
            config_file {[type]} -- [description]
        """
        assert(config_file.endswith('.json'))
        with open(config_file, 'r') as f:
            self.settings = json.load(f)
        assert(self.settings['model'] in supported_models)


    def get_model(self):
        """[summary]
        
        Raises:
            KeyError: [description]
        
        Returns:
            [type] -- [description]
        """
        model = self.settings['model']
        assert(model in supported_models)
        
        if model == 'w2v':
            return Word2VecModel(self.settings['vector_file'])
        elif model == 'FastText':
            return FastTextModel(self.settings['vector_file'])
        elif model == 'ELMoBPE':
            return ELMoBPEModel(self.settings['vector_file'])
        
