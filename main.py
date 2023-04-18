#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import pandas as pd
import argparse
import os
from pymongo import MongoClient


# Lectura d'arguments
parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file', type=str, required=True, help='Nom del fitxer Excel amb les dades')
parser.add_argument('--delete_all', action='store_true', help='Eliminar tots els continguts de la col·lecció')
parser.add_argument('--bd', type=str, required=True, help='Nom de la base de dades')

args = parser.parse_args()

#Iniciem connexió amb MongoDB
conn = MongoClient(f"mongodb://localhost:27017/{args.bd}")
bd = conn['COMICS']

# Esborrar tots els continguts de la col·lecció si s'ha especificat l'argument --delete_all
if args.delete_all:
    for col in bd.list_collection_names():
        bd.get_collection(col).delete_many({})
        bd.drop_collection(col)

###############################################################################
#### Lectura dels fitxers  ####################################################
###############################################################################

# Lectura del full personatges
personatges = pd.read_excel(args.file, sheet_name='Personatges')
personatges = personatges.to_json('personatges.json', orient='records', force_ascii=False)

with open('personatges.json', 'r') as jsonfile:
    dades = json.load(jsonfile)
    dict_personatges = dict()
    # separem l'isbn en diferents camps
    for d in dades:
        if d['isbn'] in dict_personatges:
            dict_personatges[d['isbn']].append({'nom': d['nom'], 'tipus': d['tipus']})
        else:
            dict_personatges[d['isbn']] = [{'nom': d['nom'], 'tipus': d['tipus']}]
os.remove('personatges.json')

# Lectura de la fulla colleccions-publicacions
publicacions = pd.read_excel(args.file, sheet_name='Colleccions-Publicacions')
publicacions = publicacions.to_json('publicacions.json', orient='records', force_ascii=False)

# Construcció de les col·leccions
with open('publicacions.json', 'r') as jsonfile:
    dades = json.load(jsonfile)

    bd.drop_collection('publicacions')
    bd.drop_collection('coleccions')
    bd.drop_collection('editorials')
    col_pub = bd.create_collection('publicacions')
    col_edit = bd.create_collection('editorials')
    col_col = bd.create_collection('coleccions')
    exists_editorial = list()
    exists_col = list()
    colleccions = dict()

    for d in dades:
        # EDITORIAL
        if d['NomEditorial'] not in exists_editorial:
            exists_editorial.append(d['NomEditorial'])
            col_edit.insert_one({'_id': d['NomEditorial'], 'resposable': d['resposable'],
                                 'adreca': d['adreca'], 'pais': d['pais']})

        # PUBLICACIO
        llista_guionistes = (d['guionistes'].strip('[]')).split(',')
        llista_dibuixants = (d['dibuixants'].strip('[]')).split(',')
        if d['ISBN'] in dict_personatges:
            personatges = dict_personatges[d['ISBN']]
        else:
            personatges = list()
        col_pub.insert_one({'_id': d['ISBN'], 'titol': d['titol'],
                            'stock': d['stock'], 'autor': d['autor'],
                            'preu': d['preu'], 'num_pagines': d['num_pagines'],
                            'guionistes': llista_guionistes, 'dibuixants': llista_dibuixants,
                            'personatges': personatges})

        # PUBLICACIONS pertanyents a cada COLECCIO
        tupla = (d['NomEditorial'], d['NomColleccio'])
        if tupla in colleccions:
            colleccions[tupla].append(d['ISBN'])
        else:
            colleccions[tupla] = [d['ISBN']]

    # COLECCIONS
    exists_col = list()
    for d in dades:
        tupla = (d['NomEditorial'], d['NomColleccio'])
        if tupla not in exists_col:
            exists_col.append(tupla)
            list_genere = (d['genere'].strip('[]')).split(',')
            list_publicacions = colleccions[tupla]
            col_col.insert_one({'NomColleccio': d['NomColleccio'], 'NomEditorial': d['NomEditorial'],
                                'total_exemplars': d["total_exemplars"],
                                'genere': list_genere, 'idioma': d["idioma"],
                                'any_inici': d['any_inici'], 'any_fi': d['any_fi'],
                                'tancada': d['tancada'], 'exemplars': list_publicacions})

os.remove('publicacions.json')

# Lectura del full artistes
artistes = pd.read_excel(args.file, sheet_name='Artistes')
artistes = artistes.to_json('artistes.json', orient='records', force_ascii=False)

with open('artistes.json', 'r') as jsonfile:
    dades = json.load(jsonfile)

    bd.drop_collection('artistes')
    col_art = bd.create_collection('artistes')
    for d in dades:
        col_art.insert_one({'_id': d['Nom_artistic'], 'nom': d['nom'],
                            'cognoms': d['cognoms'], 'data_naix': d['data_naix'],
                            'pais': d['pais']})
os.remove('artistes.json')

conn.close()