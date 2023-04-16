#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import pandas as pd
import argparse
import os

from pymongo import MongoClient

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file', type=str, required=True, help='Nom del fitxer Excel amb les dades')
parser.add_argument('--delete_all', action='store_true', help='Eliminar tots els continguts de la col·lecció')
parser.add_argument('--bd', type=str, required=True, help='Nom de la base de dades')

args = parser.parse_args()

conn = MongoClient(f"mongodb://localhost:27017/{args.bd}")
bd = conn['COMICS']

# Esborrar tots els continguts de la col·lecció si s'ha especificat l'argument --delete_all
if args.delete_all:
    for col in bd.list_collection_names():
        bd.get_collection(col).delete_many({})
        bd.drop_collection(col)

###############################################################################
#### PUBLICACIONS #############################################################
###############################################################################

publicacions = pd.read_excel(args.file, sheet_name='Colleccions-Publicacions')

publicacions = publicacions.to_json('publicacions.json', orient='records', force_ascii=False)

with open('publicacions.json', 'r', encoding='utf-8') as jsonfile:
    dades = json.load(jsonfile)

    bd.drop_collection('publicacions')
    pub = bd.create_collection('publicacions')

    for d in dades:
        pub.insert_one(d)

os.remove('publicacions.json')
###############################################################################
#### PERSONATGES ##############################################################
###############################################################################

personatges = pd.read_excel(args.file, sheet_name='Personatges')

personatges = personatges.to_json('personatges.json', orient='records', force_ascii=False)

with open('personatges.json', 'r', encoding='utf-8') as jsonfile:
    dades = json.load(jsonfile)

    bd.drop_collection('personatges')
    coll = bd.create_collection('personatges')
    for d in dades:
        coll.insert_one(d)
os.remove('personatges.json')
###############################################################################
#### ARTISTES #################################################################
###############################################################################

artistes = pd.read_excel(args.file, sheet_name='Artistes')

artistes = artistes.to_json('artistes.json', orient='records', force_ascii=False)

with open('artistes.json', 'r', encoding='utf-8') as jsonfile:
    dades = json.load(jsonfile)

    bd.drop_collection('artistes')
    coll = bd.create_collection('artistes')
    for d in dades:
        coll.insert_one(d)
os.remove('artistes.json')
###############################################################################
#### PATRONS DE DISSENY #######################################################
###############################################################################


bd.publicacions.aggregate([
    {"$project": {"NomEditorial": 1,
                  "responsable": 1,
                  "adreca": 1,
                  "pais": 1}},
    {"$out": "editorial"}])

bd.publicacions.aggregate([
    {"$project": {"NomColleccio": 1,
                  "total_exemplars": 1,
                  "genere": 1,
                  "idioma": 1,
                  "any_inici": 1,
                  "any_fi": 1,
                  "tancada": 1,
                  "NomEditorial": 1}},
    {"$out": "colleccio"}])

bd.publicacions.aggregate([
    {"$project": {"ISBN": 1,
                  "titol": 1,
                  "stock": 1,
                  "autor": 1,
                  "preu": 1,
                  "num_pagines": 1,
                  "NomColleccio": 1,
                  "guionistes": 1,
                  "dibuixants": 1,
                  }},
    {"$out": "publicacions"}])

pipeline = [
    {
        "$lookup":
        {
            "from": "personatges",
            "localField": "ISBN",
            "foreignField": "isbn",
            "as": "personatges"
        }
    }
]
result = bd.publicacions.aggregate(pipeline)

for doc in result:
    isbn = doc['ISBN']
    personatges = doc['personatges']
    bd.publicacions.update_one(
        {'ISBN': isbn},
        {'$set': {'personatges': personatges}}
    )
"""
# Comprovació que la coll està ben feta
resulta = bd.publicacions.find()
for i in resulta:
    print(i)
"""
conn.close()