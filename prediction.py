# Functions that treat event data and use vectorizers and model to perform prediction

import pandas as pd
import numpy as np
from unicodedata import normalize
import json
import re
import joblib as jb
from scipy.sparse import hstack

# NLP tools
#import nltk
#nltk.download('stopwords')
#nltk.download('punkt')
from more_itertools import unique_everseen
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import RSLPStemmer

stop_pt = stopwords.words('portuguese')

model = jb.load("model.pkl.z")
vect = dict()
vect['name'] = jb.load("vect_name.pkl.z")
vect['location'] = jb.load("vect_location.pkl.z")
vect['description'] = jb.load("vect_description.pkl.z")
vect['organizer'] = jb.load("vect_organizer.pkl.z")

# Functions to treat text
def normalize_str(string):
    string = normalize('NFKD', string).encode('ASCII','ignore').decode('ASCII')
    string = string.lower()
    string = re.sub("[^a-zA-Z0-9]"," ", string)
    string = string.strip()
    return string
    
def remove_num_str(string):
    return re.sub(r"[0-9]","", string)
    
def remove_whitespace_str(string):
    string = re.sub("\n|\t","", string)
    string = re.sub(" +"," ", string)
    string = string.strip()
    return string
    
def clean_normalize_numbers_whitespace(string, numbers=False):
    if string != '':
        string = normalize_str(string)
        if numbers:
            string = remove_num_str(string)
        string = remove_whitespace_str(string)
    return string

def nlp_treatment(text_feats, stem=False):
    
    processed = dict()
    
    for key, value in text_feats.items():
        if value != '':
            string_list = word_tokenize(value)
            string_list = [w for w in string_list if w not in stop_pt]
            string_list = list(unique_everseen(string_list))
            if stem:
                stemmer = RSLPStemmer()
                string_list = [stemmer.stem(w) for w in string_list]
            value = " ".join(string_list)
        processed[key] = value
        
    return processed
    
def compute_features(event_data):
    name = clean_normalize_numbers_whitespace(event_data['name'], numbers=True)
    location = clean_normalize_numbers_whitespace(event_data['location'], numbers=True)
    description = clean_normalize_numbers_whitespace(event_data['description'])
    organizer = clean_normalize_numbers_whitespace(event_data['organizer'])
    
    if event_data['platform'] == 'eventbrite':
        # Remove useless words
        location = re.sub('ver mapa','', location)
        description = re.sub('(sobre este evento)|(about this event)|(a propos de cet evenement)|(acerca deste evento)|(acerca de este evento)', '', description)
        organizer = re.sub('(por )|(by )','', organizer)
    
    text_feats_raw = dict()
    text_feats_raw['name'] = name
    text_feats_raw['location'] = location
    text_feats_raw['description'] = description
    text_feats_raw['organizer'] = organizer
    
    text_feats = nlp_treatment(text_feats_raw)
    
    X = pd.DataFrame()
    for key, value in text_feats.items():
        # Use adequate vectorizer for each feature
        string = vect[key].transform([value])
        X = hstack([X, string])
    
    return X

def compute_prediction(event_data):
    features = compute_features(event_data)

    if features is None:
        return 0

    pred = model.predict_proba(features)[0][1]
    return pred