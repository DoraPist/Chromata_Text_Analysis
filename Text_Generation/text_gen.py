import requests
from requests.auth import HTTPBasicAuth

def text_gen(text):
    
    basic = HTTPBasicAuth('evan', 'mklab')
    if text == 'gikna':
        r = requests.get(".../gikna", auth=basic)   # add IP before /gikna

    elif text == 'karsilamas':
        r = requests.get(".../karsilamas", auth=basic)   # add IP before /karsilamas

    elif text == 'baidouska':
        r = requests.get(".../baidouska", auth=basic)   #  # add IP before /baidouska

    else:
        generated_text = """Δεν υπάρχουν πληροφορίες για αυτόν τον χορό. Εσαγωγή ένός απο 'gikna', 'karsilamas', 'baidouska'. """

        return generated_text
    
    for i in range(len(r.json()['table'])):
        info = r.json()['table'][i]['predicate']['value'].split('/')[-1]
        if info == 'danceType':
            dance_type = r.json()['table'][i]['object']['value']
        elif info == 'danceGenre':
            dance_genre = r.json()['table'][i]['object']['value']
        elif info == 'kineticUnit':
            kinetic_unit = r.json()['table'][i]['object']['value']
        elif info == 'danceFormation':
            dance_formation = r.json()['table'][i]['object']['value']
        elif info == 'handMovement':
            hand_movement = r.json()['table'][i]['object']['value']
        elif info == 'attire':
            attire = r.json()['table'][i]['object']['value']

    generated_text = "Το είδος του χορού που εντοπίστηκε ειναι " + dance_type + ". Το γένος του χορού είναι " + dance_genre+ ". Η μορφή κινητικής ενότητας είναι " + kinetic_unit + ", το σχήμα του χορού είναι " + dance_formation + " και η κίνηση των χεριών είναι " + hand_movement + ". Το ένδυμα των χορευτών ειναι " + attire + "."

    return generated_text

    
