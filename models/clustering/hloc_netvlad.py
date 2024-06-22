#!/usr/bin/env python3
"""
NetVLAD Layer Implementation
From the Hierachical Localization (HLoc) Repo
"""
#####################################################################
# Imports
#####################################################################
import logging
from pathlib import Path

import numpy as np

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.nn.parameter import Parameter
from scipy.io import loadmat

#####################################################################
# Class
#####################################################################

class HLOCNetVLAD(nn.Module):
    def __init__(
        self,
        input_dim:int = 512,        # Input Vector Dimension
        num_clusters:int = 64,                 # Cluster Count
        score_bias:bool = False,    # Bias for the Score
        intranorm:bool = True,      # Intra Group Normalization
        whiten:bool = True          # Whiten the Output
    ):
        super().__init__()
        # Score Projection
        self.conv = nn.Conv1d(
            input_dim,
            num_clusters,
            kernel_size=1,
            bias=score_bias
        )
        self.centers = nn.Parameter(
            torch.empty([input_dim, num_clusters])
        )
        nn.init.xavier_uniform_(self.centers)

        self.register_parameter("centers", self.centers)

        # Configuration
        self.whiten = whiten
        self.intranorm = intranorm
        self.output_dim = input_dim * num_clusters

        # Initialize
        # Load MATLAB Weights
        checkpoint_path = "datasets/Pitts30K_struct.mat"
        mat = loadmat(
            checkpoint_path,
            struct_as_record=False,
            squeeze_me=True
        )
        self.assign_matlab_weights(mat)

    def assign_matlab_weights(self, mat_weight):
        """
        Assign MATLAB weights to the corresponding layers
        """
        # Score Weight
        score_w = mat_weight["net"].layers[30].weights[0] # D x K
        score_w = torch.tensor(score_w).float()
        score_w = score_w.permute([1,0])
        score_w = score_w.unsqueeze(-1)
        self.conv.weight = nn.Parameter(score_w)

        # Center Weight
        center_w = -mat_weight["net"].layers[30].weights[1]
        center_w = torch.tensor(center_w).float()
        self.centers = nn.Parameter(center_w)

        print("[NetVLAD] Weights Imported")


    def forward(self, x):
        """
        Forward pass

        Args:
            x (Tensor[BxWxHxD]): Tensor output from the backbone layer
        """
        # if input is batch - remember the batch size
        if len(x.size()) >= 4:
            batch_size = x.size(0)
            img_desc_channel = x.size(1)
        else:
            batch_size = 1
            img_desc_channel = x.size(0)

        # Transform input map (BxDxWxH) to a vector x (BxDxN)
        # Flattened_input (x)
        flattened_input = x.view(batch_size, img_desc_channel, -1)
        # Score Projection (s)
        scores = self.conv(flattened_input)
        # Softmax Layer output (a) (e^s / sum(e^s))
        softmax_output = F.softmax(scores, dim=1)

        # VLAD Core Calculation
        # V(j,k) : J is Dimension of the descriptor, K is the cluster
        # V(j,k) = sum( (x(j) - c(k)) * a(k) )
        diff = x.unsqueeze(2) - self.centers.unsqueeze(0).unsqueeze(-1)

        desc = (softmax_output.unsqueeze(1) * diff).sum(dim=-1)

        if self.intranorm:
            # From the official MATLAB implementation.
            desc = F.normalize(desc, dim=1)

        desc = desc.view(batch_size, -1)
        desc = F.normalize(desc, dim=1)

        if self.whiten:
            desc = self.whiten(desc)
            desc = F.normalize(desc, dim=1) # Final L2 Normalization

        return desc


