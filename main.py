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
    
    bd.drop_collection('publicacions')
    pub = bd.create_collection('publicacions')
    
    for d in dades:
        pub.insert_one(d)
        
        
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
        
###############################################################################
#### PATRONS DE DISSENY #######################################################
###############################################################################


bd.publicacions.aggregate([
   {"$project" : {"NomEditorial" : 1, 
                  "responsable" : 1, 
                  "adreca" : 1, 
                  "pais" : 1}},
   {"$out" : "editorial"}])

    
bd.publicacions.aggregate([
    {"$project" : {"NomColleccio" : 1, 
                   "total_exemplars" : 1, 
                   "genere" : 1, 
                   "idioma" : 1, 
                   "any_inici" : 1, 
                   "any_fi" : 1, 
                   "tancada" : 1, 
                   "NomEditorial" : 1}},
    {"$out" : "colleccio"}])


bd.publicacions.aggregate([
    {"$project" : {"ISBN" : 1,
                   "titol" : 1, 
                   "stock" : 1, 
                   "autor" : 1, 
                   "preu" : 1, 
                   "num_pagines": 1,
                   "NomColleccio" : 1, 
                   "guionistes" : 1, 
                   "dibuixants" : 1
        }},
    {"$out" : "publicacions"}])

pipeline = [
    {
        "$lookup":
        {
            "from": "personatges",
            "localField": "ISBN",
            "foreignField": "isbn",
            "as": "personatges"
        }
    },
    {
        "$project":
        {
            "_id": 0,
            "ISBN": 1,
            "title": 1,
            "author": 1,
            "publisher": 1,
            "personatges.name": 1,
            "personatges.gender": 1,
            "personatges.age": 1
        }
    }
]




conn.close()