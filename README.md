# El còmic feliç
En aquest projecte es treballarà el disseny, 
la implementació i la consulta a una base de 
dades en MongoDB. A partir dels requisits i 
les dades que se subministraran, s’ha implementat 
un script en Python capaç de processar i inserir 
les dades en una base de dades de MongoDB. Per tal 
de demostrar que la nostra base 
de dades funciona correctament, s'ha fet un conjunt 
de proves: "joc de proves" el qual són un seguit de
queries per tal de demostrar que la base de dades està
ben estructurada i dissenyada.

# Instruccions per executar el codi

1. Clonar el repositori GitHub a un repositori local (o bé descarregar el ZIP i descomprimir-lo localment).
2. Obrir una terminal i dirigir-se al repositori local on hi ha els arxius clonats.
3. Assegurar-se que es té instal·lat: ``pandas``, ``pymongo`` i ``openpyxl``. Sinó, fer-ho utilitzant l'instal·lador ``pip``.
4. Utilitzar la comanda ``python main.py -f dades.xlsx --delete_all --bd comic_feliç
`` per tal de carregar les dades i veure les diferents queries.

El flag `delete-all` indica que s'eliminaran totes les col·leccions prèvies. <br>
El flag `bd` indica el nom de la base de dades que utilitzarem. <br>
El flag `-f` indica el nom del document Excel amb les dades.

# Estructura de les col·leccions
### Editorial
* nom ``string``
* responsable ``string``
* país ``string``
* adreça ``subdocument``: carrer ``string``, número ``int`` i població ``string``

### Col·lecció
* nom ``string``
* editor ``string`` (``_id`` de l'editorial)
* gènere ``string``
* idioma ``string``
* any d'inici ``int``
* any de finalització ``int``
* acabada ``bool``
* publicacions ``list`` of ``subdocuments``

### Publicació
* ISBN ``string``
* títol ``string``
* autor ``string``
* nombre de pàgines ``int``
* stock ``int``
* preu ``float``
* personatges ``list`` of ``documents``: nom ``string`` i tipus ``string`` de personatge
* artistes ``list`` of ``subdocuments``: ``_id`` ``string`` i contribució ``string`` de l'artista

### Artista
* nom artístic ``string``
* nom ``string``
* cognom ``string``
* data de naixement ``Date``
* país ``string``

# Fitxers que hem entregat
Els fitxers que hem entregat són els següents:
* main.py: l'script de python on hem fet la descàrrerga de les bases de dades i la l'implementació dels patronys de disseny.
* queries.py: l'script en python on estan totes les consultes fetes amb la llibreria pymongo. Hem programat un menú que t'imprimeix el resultat de les consultes a mesura que li vas demanant el nombre de l'exercici. És important demanar-ho en ordre cardinal.
* Totes les imatges són captures de pantalla de les diferentes consultes i els seus outputs fets amb SQLNoBooster.
* Dades.xlsx: el fitxer on estan emmagatzemades totes les dades que hem de descarregar
* Projecte.tex: l'informe del treball.
