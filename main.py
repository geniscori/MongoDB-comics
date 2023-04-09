import pandas as pd
import argparse
from pymongo import MongoClient

# Definir els arguments
parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file', type=str, required=True, help='Nom del fitxer Excel amb les dades')
parser.add_argument('--delete_all', action='store_true', help='Eliminar tots els continguts de la col·lecció')
parser.add_argument('--bd', type=str, required=True, help='Nom de la base de dades')

args = parser.parse_args()

# Llegir el fitxer Excel
try:
    df = pd.read_excel(args.file)
except FileNotFoundError:
    raise FileNotFoundError("El nom del fitxer no s'ha introduït correctament")

# Eliminar les files duplicades
df.drop_duplicates(inplace=True)

# Connectar amb la base de dades MongoDB
conn = MongoClient(f"mongodb://localhost:27017/{args.bd}")
db = conn['comic-happy']

# Esborrar tots els continguts de la col·lecció si s'ha especificat l'argument --delete_all
if args.delete_all:
    for col in db.list_collection_names():
        db.get_collection(col).delete_many({})
        db.drop_collection(col)

# Aquí podem crear les nostres colections
'''
Hem de crear les diferents collections
'''

if not(len(db.list_collection_names())):
    print("No s'ha creat cap col·lecció")
else:
    print(f"S'han creat les següents col·leccions {db.list_collection_names()}")



'''
Fer les diferents queries
'''



# Tancar la connexió amb la base de dades MongoDB
conn.close()
