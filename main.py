#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 21 10:19:29 2023

@author: marc
"""

import json
import pandas as pd
from openpyxl import load_workbook

from pymongo import MongoClient


# En execució remota
Host = 'localhost' 
Port = 27017

###################################### CONNEXIÓ ##############################################

DSN = "mongodb://{}:{}".format(Host,Port)

conn = MongoClient(DSN)

############################# TRANSFERÈNCIA DE DADES AMB MONGO ##############################

#Selecciona la base de dades a utilitzar --> tenda
bd = conn['COMICS']

file_path = './dades/Dades.xlsx'


###############################################################################
#### PUBLICACIONS #############################################################
###############################################################################

publicacions = pd.read_excel(file_path, sheet_name = 'Colleccions-Publicacions')

publicacions = publicacions.to_json('publicacions.json', orient='records', force_ascii=False)

with open('publicacions.json', 'r', encoding='utf-8') as jsonfile:
    dades = json.load(jsonfile)
    
    bd.drop_collection('colleccions')
    coll = bd.create_collection('colleccions')
    for d in dades:
        coll.insert_one(d)
        
###############################################################################
#### PERSONATGES ##############################################################
###############################################################################

personatges = pd.read_excel(file_path, sheet_name = 'Personatges')

personatges = personatges.to_json('personatges.json', orient='records', force_ascii=False)

with open('personatges.json', 'r', encoding='utf-8') as jsonfile:
    dades = json.load(jsonfile)
    
    bd.drop_collection('personatges')
    coll = bd.create_collection('personatges')
    for d in dades:
        coll.insert_one(d)
        
        
###############################################################################
#### ARTISTES #################################################################
###############################################################################

artistes = pd.read_excel(file_path, sheet_name = 'Artistes')

artistes = artistes.to_json('artistes.json', orient='records', force_ascii=False)

with open('artistes.json', 'r', encoding='utf-8') as jsonfile:
    dades = json.load(jsonfile)
    
    bd.drop_collection('artistes')
    coll = bd.create_collection('artistes')
    for d in dades:
        coll.insert_one(d)

conn.close()