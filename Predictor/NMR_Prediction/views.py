import os
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import datetime
from .apply import predict_NMR, preprocess, RBFSequence

#NN model
import sys,io,os
import pandas as pd
import numpy as np
import gzip, pickle, argparse, warnings
import pickle
import math

from tqdm import tqdm

from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit.Chem import ForwardSDMolSupplier

from itertools import islice

from nfp.preprocessing import MolAPreprocessor, GraphSequence
from .genConf import genConf

import keras
import keras.backend as K

from keras.callbacks import ModelCheckpoint, CSVLogger, LearningRateScheduler

from keras.layers import (Input, Embedding, Dense, BatchNormalization,
                                 Concatenate, Multiply, Add)

from keras.models import Model, load_model

from nfp.layers import (MessageLayer, GRUStep, Squeeze, EdgeNetwork,
                               ReduceBondToPro, ReduceBondToAtom,
                               GatherAtomToBond, ReduceAtomToPro)
from nfp.models import GraphModel
from django.views.decorators.csrf import csrf_exempt

#Load NN model
filepath = os.path.join('NMR_Prediction', 'schnet_edgeupdate', 'best_model.hdf5')
batch_size=32
atom_means = pd.Series(np.array([0,0,97.74193,0,0,0,0,0,0,0]).astype(np.float64), name='shift')
NMR_model = load_model(filepath, custom_objects={'GraphModel': GraphModel,
                                             'ReduceAtomToPro': ReduceAtomToPro,
                                             'Squeeze': Squeeze,
                                             'GatherAtomToBond': GatherAtomToBond,
                                             'ReduceBondToAtom': ReduceBondToAtom})
NMR_model.summary()

atoms = {1:'H', 6:'C', 7:'N', 8:'O', 9:'F', 15:'P', 16:'S', 17:'Cl'}

#Model check
startup_mols, startup_shift, startup_spreadShift = predict_NMR('O=C1C2=C(N=CN2C)N(C)C(N1C)=O', NMR_model)

news = [
    {
        'title': 'Hello NMR Prediction',
        'content': 'NMR real time predictor is coming',
        'date_posted': 'Feb 12, 2019',
    },
    {
        'title': 'Computational NMR',
        'content': 'How to compute Chemical Shifts',
        'date_posted': 'Feb 15, 2019',
    },
]


def home(request):
    context = {
        'news': news
    }
    return render(request, 'NMR_Prediction/home.html', context)

def about(request):
    return render(request, 'NMR_Prediction/about.html', {'title': 'About'})

def predict(request):
    return render(request, 'NMR_Prediction/predict.html')

@csrf_exempt
def NNPredict(request):
    smiles = request.POST["molsource"]
    mols, weightedPrediction, spreadShift = predict_NMR(smiles, NMR_model)

    weightedShiftTxt = ''
    for _,r in weightedPrediction.iterrows():
        weightedShiftTxt += '%s,%s;' % (int(r['atom_index']), r['Shift'])

    jsmol_command = ''
    for m in mols:
        coords = ''
        for i,a in enumerate(m.GetAtoms()):
            ixyz = m.GetConformer().GetAtomPosition(i)
            coords += "{} {} {} {}|".format(atoms[a.GetAtomicNum()], *ixyz)

        jsmol_command += "data \"model example\"|{}|testing|{}end \"model example\";show data!".format(m.GetNumAtoms(), coords)

    confShiftTxt = ''
    relative_E = ''
    group_spreadShift = spreadShift.groupby(['mol_id', 'cf_id'], sort=False)
    for _,df in group_spreadShift:
        for _,r in df.iterrows():
            confShiftTxt += "{},{};".format(int(r['atom_index']), r['predicted'])
        relative_E += "{},{}!".format(df.iloc[0]['relative_E'], df.iloc[0]['b_weight'])
        confShiftTxt += "!"

    response = JsonResponse({'jsmol_command':jsmol_command, 'weightedShiftTxt':weightedShiftTxt, 'confShiftTxt': confShiftTxt, 'relative_E': relative_E})

    return response

@csrf_exempt
def JSmol_startup(request):
    m = startup_mols[0]
    c = m.GetConformers()[0]

    coords = ''
    for i,a in enumerate(m.GetAtoms()):
        ixyz = c.GetAtomPosition(i)
        coords += "{} {} {} {}|".format(atoms[a.GetAtomicNum()], *ixyz)

    jsmol_command = "data \"model example\"|{}|testing|{}end \"model example\";show data".format(m.GetNumAtoms(), coords)

    return HttpResponse(jsmol_command)

@csrf_exempt
def Shift_startup(request):
    responseTxt = ''
    for _,r in startup_shift.iterrows():
        responseTxt += '%s,%s;' % (int(r['atom_index']), r['Shift'])

    return HttpResponse(responseTxt)
