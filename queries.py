from pymongo import MongoClient
import numpy as np
import os

# Connexió amb MongoDB
Host = 'localhost'
Port = 27017
DSN = "mongodb://{}:{}".format(Host,Port)
conn = MongoClient(DSN)

# Importem la base de dades a Python
bd = conn['COMICS']

# Mostrar el menu
def mostrar_menu():
    print("=== Tria la consulta a fer ===")
    print("1. Les 5 publicacions amb major preu. Mostrar només el títol i preu.")
    print("2. Valor màxim, mínim i mitjà dels preus de les publicacions de l'editorial Juniper Books.")
    print("3. Mostrar el nom dels artistes que prticipen en més de 5 publicacions.")
    print("4. Numero de col·leccions per gènere. Mostra gènere i número total.")
    print("5. Per cada editorial, mostrar el recompte de col·leccions finalitzades i no finalitzades.")
    print("6. Mostrar les 2 col·leccions ja finalitzades amb més publicacions. Mostrar editorial i nom col·lecció.")
    print("7. Mostrar el país d’origen de l’artista o artistes que han fet més guions.")
    print("8. Mostrar les publicacions amb tots els personatges de tipus “heroe”.")
    print("9. Modificar el preu de les publicacions amb stock superior a 20 exemplars i incrementar-lo un 25%.")
    print("10. Mostrar ISBN i títol de les publicacions conjuntament amb tota la seva informació dels personatges")
    print("Escriu 'esc' per sortir del programa.")
def cosultes(numero):
    os.system('cls' if os.name == 'nt' else 'clear')

    if(numero == '1'):
        print("1. Les 5 publicacions amb major preu. Mostrar només el títol i preu.\n")
        result = bd.publicacions.find({}, {'titol': 1, 'preu': 1, '_id': 0}).sort([('preu', -1)]).limit(5)
        for r in result:
            print("Títol: {}, Preu: {}".format(r['titol'], r['preu']))


    elif(numero == '2'):
        print("2. Valor màxim, mínim i mitjà dels preus de les publicacions de l'editorial Juniper Books.\n")
        result = bd.coleccions.aggregate([
            {
                '$lookup': {
                    'from': 'publicacions',
                    'localField': 'exemplars',
                    'foreignField': '_id',
                    'as': 'publicacions'
                }
            },
            {
                '$unwind': '$publicacions'
            },
            {
                '$match': {
                    'NomEditorial': 'Juniper Books'
                }
            },
            {
                '$group': {
                    '_id': '$NomEditorial',
                    'preuMax': {'$max': '$publicacions.preu'},
                    'preuMin': {'$min': '$publicacions.preu'},
                    'preuAvg': {'$avg': '$publicacions.preu'}
                }
            }
        ])

        for r in result:
            print("Editorial: {}".format(r['_id']))
            print("Preu màxim: {}".format(r['preuMax']))
            print("Preu mínim: {}".format(r['preuMin']))
            print("Preu mitjà: {}".format(np.round(r['preuAvg'],2)))

    elif (numero == '3'):
        print("3. Mostrar el nom dels artistes que prticipen en més de 5 publicacions.\n")
        result = bd.publicacions.aggregate([
            {
                '$unwind': '$dibuixants'
            },
            {
                '$group': {
                    '_id': '$dibuixants',
                    'numPub': {'$sum': 1}
                }
            },
            {
                '$match': {
                    'numPub': {'$gt': 5}
                }
            },
            {
                '$project': {
                    'numPub': 0
                }
            }
        ])

        for r in result:
            print("Nom artístic: {}".format(r['_id']))


    elif (numero == '4'):
        print("4. Numero de col·leccions per gènere. Mostra gènere i número total.\n")
        result = bd.coleccions.aggregate([
            {
                '$unwind': '$genere'
            },
            {
                '$group': {
                    '_id': '$genere',
                    'total': {'$sum': 1}
                }
            }
        ])


        for r in result:
            print("Gènere: {}, Total: {}".format(r['_id'], r['total']))

    elif (numero == '5'):
        print("5. Per cada editorial, mostrar el recompte de col·leccions finalitzades i no finalitzades.\n")
        result = bd.coleccions.aggregate([
            {
                '$group': {
                    '_id': {
                        'Editorial': '$NomEditorial',
                        'Finalitzada': '$tancada'
                    },
                    'recompte': {'$sum': 1}
                }
            }
        ])

        # Iterar sobre los resultados e imprimir el resultado
        for r in result:
            print("Editorial: {}, Finalitzada: {}, Recompte: {}".format(r['_id']['Editorial'], r['_id']['Finalitzada'],
                                                                        r['recompte']))

    elif (numero == '6'):
        print("6. Mostrar les 2 col·leccions ja finalitzades amb més publicacions. Mostrar editorial i nom col·lecció.\n")
        result = bd.coleccions.aggregate([
            {
                '$lookup': {
                    'from': 'publicacions',
                    'localField': 'exemplars',
                    'foreignField': '_id',
                    'as': 'publicacions'
                }
            },
            {
                '$match': {
                    'tancada': True
                }
            },
            {
                '$addFields': {
                    'numPublicacions': {
                        '$size': '$publicacions'
                    }
                }
            },
            {
                '$sort': {
                    'numPublicacions': -1
                }
            },
            {
                '$project': {
                    'NomEditorial': 1,
                    'NomColleccio': 1,
                    '_id': 0
                }
            },
            {
                '$limit': 2
            }
        ])

        for r in result:
            print("NomEditorial: {}, NomColleccio: {}".format(r['NomEditorial'], r['NomColleccio']))

    elif (numero == '7'):
        print("7. Mostrar el país d’origen de l’artista o artistes que han fet més guions.\n")
        pipeline = [
            {
                '$unwind': '$guionistes'  # Desfer la llista de guionistes per a poder agrupar per cada guionista
            },
            {
                '$group': {
                    '_id': '$guionistes',  # Agrupar per nom del guionista
                    'num_publications': {'$sum': 1}  # Sumar el número de publicacions per a cada guionista
                }
            },
            {
                '$sort': {'num_publications': -1}
                # Ordenar els resultats per número de publicacions en ordre descendent
            }
        ]

        result = list(bd.publicacions.aggregate(pipeline))
        nom_artista = str(result[0]['_id']).replace("[", "").replace("]", "")

        pipeline = [
            {"$match": {"_id": nom_artista}},
            {"$project": {"_id": 1, "nom": 1, "pais": 1}}
        ]

        result = bd.artistes.aggregate(pipeline)

        for r in result:
            print("Nom artístic: {}, País: {}".format(r['_id'], r['pais']))

    elif (numero == '8'):
        result = bd.publicacions.aggregate([
            {"$match": {"personatges.tipus": 'heroe'}},
            {"$project": {"ISBN":1, "titol": 1, "personatges.nom": 1}}
        ])

        for r in result:
            #print("Títol publicació: {}, Noms personatges: {}, ISBN: {}".format(r['titol'], r['personatges'], r['ISBN']))
            print("Títol: {}, Personatges: {}, ISBN: {}".format(r['titol'],r['personatges'],r['_id']))

    elif (numero == '9'):
        print("9. Modificar el preu de les publicacions amb stock superior a 20 exemplars i incrementar-lo un 25%.\n")
        filter = {'stock': {'$gt': 20}}
        update = {'$set': {'preu': {'$multiply': ['$preu', 1.25]}}}
        result = bd.publicacions.update_many(filter, update)

        print('Quantitat de documents actualitzats:', result.modified_count)

    elif (numero == '10'):
        print("10. Mostrar ISBN i títol de les publicacions conjuntament amb tota la seva informació dels personatges\n")
        result = bd.publicacions.aggregate([{'$project':{'titol':1,'personatges':1}}])

        for r in result:
            print(f"Títol: {r['titol']}, Personatges: {r['personatges']}")


    else:
        print("Opció no vàlida. Torna a intentar-ho.")

def main():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')  # fem un clear de pantalla
        mostrar_menu()  # mostrem el menu
        opcio = input("Selecciona una opció: ")

        if opcio.lower() == 'esc':
            print("Gràcies per utilitzar el programa. Fins aviat!")
            break

        cosultes(opcio)
        input("\nPrem ENTER per a continuar...")


# Iniciamos el programa llamando a la función principal
if __name__ == "__main__":
    print("* Tenir en compte que hi ha consultes que modifiquen les col·leccions i si es volen repetir algunes consultes potser no surten com en la solució")
    main()