#!/usr/bin/env python3
"""
Entry Point for Traning
Visual Place Recognition Pipeline

Given a yaml configuration file
Train the model using that info

"""
# Author : Theppasith N. <tutorgaming@gmail.com>
# Date : 4-Jun-2023
#####################################################################
# Imports
#####################################################################
import os
import copy
import json
import numpy as np
import PIL
import torch
import torchvision
import torch.nn as nn
import torch.nn.functional as F

import torchinfo
from torch.autograd import Variable
from torchvision.models import resnet18
from sklearn.model_selection import train_test_split
from sklearn import svm, datasets, metrics

# Visualization
%matplotlib widget
import matplotlib.pyplot as plt
from tqdm.notebook import tqdm, trange
from torch.utils.tensorboard import SummaryWriter
from dateutil import tz
from datetime import datetime

#####################################################################
# Class
#####################################################################

class Configuration(object): 
    """
    Metaclass for the configuration container
    """
    def __init__(self, config_path):
        pass


    def extract_config(self, config):
        dataset = select_dataset(config['dataset'])
        feature_extractor = select_feature_extractor(config['feature_extractor'])
        clustering = select_clustering(['clustering'])
        loss = select_loss(config['loss'])
        training = config['training']
        validation = config['validation']
        
        config_dict = {
            "dataset": dataset,
            "feature_extractor": feature_extractor,
            "clustering": clustering,
            "loss": loss,
            "training": training,
            "validation": validation,
        }

        return config_dict


class Trainer(object):
    """
    Train and Validation
    """
    def __init__(self, config_yaml_path):
        # Memorize the configuration
        self.config_path = config_yaml_path
        self.config = self.parse_config(self.config_path)

    def parse_config(self, path): 
        """
        Give the YAML Configuration file parse it into
        dictionary format 
        """
        pass



























