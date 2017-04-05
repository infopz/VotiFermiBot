import requests
from bs4 import BeautifulSoup
from base64 import b64encode, b64decode
from time import gmtime, strftime, sleep
import traceback

import apikey

class Voto:
    def __init__(self, voto=0.0, materia="", tipo="", data=""):
        self.voto = voto
        self.materia = materia
        self.tipo = tipo
        self.data = data.replace('-', '/')

    def __eq__(self, other):
        return self.voto == other.voto and self.materia == other.materia

    def __repr__(self):
        return f"Voto(voto={self.voto}, materia={self.materia}, tipo={self.tipo}, data={self.data})"

    def __str__(self):
        return f"{self.materia} - {self.tipo} - {self.data} - *{self.voto}*"

class Utente:
    def __init__(self, chat_id=0, nome=""):
        self.chat_id = chat_id
        self.nome = nome
        self.username = str()  # (Steffo: perchè aggiungi aaaa alla fine di ogni username?)
        self.password = str()
        self.voti = list()
        self.statusLogin = 0

    def __repr__(self):
        return f"<Utente {self.nome} con id {self.chat_id}>"

    def set_user(self, u):
        self.username = u

    def set_pass(self, p):
        self.password = p

    def update_voti(self, shared):
        decoded_username = b64decode(self.username).decode('ascii')[0:-4]
        decoded_password = b64decode(self.password).decode('ascii')
        payload = {
            'ob_user': decoded_username,
            'ob_password': decoded_password
        }
        session = requests.Session()
        shared['badReq'] = False
        try:
            while True:
                session.post('http://www.fermi.mo.it/~loar/AssenzeVotiStudenti/elabora_PasswordStudenti.php', data=payload)
                response = session.post('http://www.fermi.mo.it/~loar/AssenzeVotiStudenti/VotiDataOrdinati2Q.php')
                if len(response.text) != 11610:
                    break
                else:
                    if shared['badReq']:
                        print("Bad Response - Caronte Fuck Two Times")
                        log_write('CARONTE FUCK TWO: USER ' + self.nome + '\n' + response.text[-100:])
                        break
                    print("Retry Request - Caronte fuck")
                    log_write('CARONTE FUCK ONCE: USER ' + self.nome + '\n' + response.text[-100:])
                    shared['badReq'] = True
                    sleep(60)
            soup = BeautifulSoup(response.text, "html.parser")
            table = soup.find("table", {"class": "TabellaVoti"})
        except Exception:
            print("Error VoteUpdate - User " + self.nome)
            log_write('Error AggiornaVoti: USER ' + self.nome + '\n' + traceback.format_exc())
            return
        if table is None:
            self.voti = list()
        else:
            self.voti = list()
            for row in table.find_all('tr'):
                col = row.find_all('td')
                try:
                    if col[1].text[0].isdigit():
                        vot = Voto(col[1].text, shorten_name(col[0].text), col[3].text, col[2].text[1:6])
                        self.voti.append(vot)
                except Exception:
                    continue

    def voti_per_materia(self):
        decoded_username = b64decode(self.username).decode('ascii')[0:-4]
        decoded_password = b64decode(self.password).decode('ascii')
        payload = {
            'ob_user': decoded_username,
            'ob_password': decoded_password
        }
        session = requests.Session()
        session.post('http://www.fermi.mo.it/~loar/AssenzeVotiStudenti/elabora_PasswordStudenti.php', data=payload)
        response = session.post('http://www.fermi.mo.it/~loar/AssenzeVotiStudenti/VotiStudente2Q.php')
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table", {"class": "TabellaVoti"})
        if table is None:
            voti = list()
        else:
            voti = list()
            for row in table.find_all('tr'):
                col = row.find_all('td')
                try:
                    if col[1].text[0].isdigit():
                        vot = Voto(col[1].text, shorten_name(col[0].text), col[3].text, col[2].text[1:6])
                        voti.append(vot)
                except Exception:
                    pass
        return voti

    def voti_primo_quadrimestre(self):
        decoded_username = b64decode(self.username).decode('ascii')
        decoded_username = decoded_username[0:-4]
        decoded_password = b64decode(self.password).decode('ascii')
        payload = {
            'ob_user': decoded_username,
            'ob_password': decoded_password
        }
        session = requests.Session()
        session.post('http://www.fermi.mo.it/~loar/AssenzeVotiStudenti/elabora_PasswordStudenti.php', data=payload)
        response = session.post('http://www.fermi.mo.it/~loar/AssenzeVotiStudenti/VotiStudente1Q.php')
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table", {"class": "TabellaVoti"})
        voti = list()
        for row in table.find_all('tr'):
            col = row.find_all('td')
            try:
                if col[1].text[0].isdigit():
                    vot = Voto(col[1].text, shorten_name(col[0].text), col[3].text, col[2].text[1:6])
                    voti.append(vot)
            except Exception:
                pass
        return voti

    def find_averages(self):
        decoded_username = b64decode(self.username).decode('ascii')
        decoded_username = decoded_username[0:-4]
        decoded_password = b64decode(self.password).decode('ascii')
        payload = {
            'ob_user': decoded_username,
            'ob_password': decoded_password
        }
        session = requests.Session()
        session.post('http://www.fermi.mo.it/~loar/AssenzeVotiStudenti/elabora_PasswordStudenti.php', data=payload)
        session.post('http://www.fermi.mo.it/~loar/AssenzeVotiStudenti/VotiStudente2Q.php')
        response = session.post('http://www.fermi.mo.it/~loar/AssenzeVotiStudenti/VotiStudenteRiepilogo2Q.php')
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table", {"class": "TabellaRiepilogo"})
        medie = list()
        for row in table.find_all('tr'):
            col = row.find_all('td')
            try:
                scritto = str(col[22].text).strip()
                orale = str(col[25].text).strip()
                pratico = str(col[28].text).strip()
                grafico = str(col[31].text).strip()
                if scritto:
                    medie.append(Voto(scritto, col[0].text, "Scritto"))
                if orale:
                    medie.append(Voto(orale, col[0].text, "Orale"))
                if pratico:
                    medie.append(Voto(pratico, col[0].text, "Pratico"))
                if grafico:
                    medie.append(Voto(grafico, col[0].text, "Grafico"))
            except Exception:
                pass
        return medie

    def voti_string(self, space_format=False):
        msg = "Ecco i tuoi Voti\n"
        materia = ''
        # TODO: questo funziona solo se i voti sono ordinati per materia...
        for voto in self.voti:
            if voto.materia != materia and space_format:
                msg += '\n'
            materia = voto.materia
            msg += f"{voto}\n"
        return msg

    def check_login(self):
        if self.username == '' or self.password == '':
            return False
        decoded_username = b64decode(self.username).decode('ascii')[0:-4]
        decoded_password = b64decode(self.password).decode('ascii')
        payload = {
            'ob_user': decoded_username,
            'ob_password': decoded_password
        }
        session = requests.Session()
        session.post('http://www.fermi.mo.it/~loar/AssenzeVotiStudenti/elabora_PasswordStudenti.php', data=payload)
        response = session.post('http://www.fermi.mo.it/~loar/AssenzeVotiStudenti/VotiDataOrdinati1Q.php')
        return response.text[-13:] != "doesn't exist"


def shorten_name(m):
    # per ora la lascio cosi, poi quando ho la sicurezza che siano state inserite tutte le materie usero il dict
    # (Steffo: my eyes! they burn!)
    if m == 'LINGUA INGLESE':
        m = 'Ing'
    elif m == 'MATEMATICA':
        m = 'Mate'
    elif m == 'LINGUA E LETTERATURA ITALIANA':
        m = 'Ita'
    elif m == 'LINGUA  E LETTERATURA ITALIANA':
        m = 'Ita'
    elif m == 'STORIA':
        m = 'Sto'
    elif m == 'SCIENZE MOTORIE E SPORTIVE':
        m = 'Ginn'
    elif m == 'TELECOMUNICAZIONI':
        m = 'Tele'
    elif m == 'SISTEMI E RETI':
        m = 'Sist'
    elif m == 'SISTEMI E RETI (LABORATORIO)':
        m = 'SisL'
    elif m == 'INFORMATICA':
        m = 'Info'
    elif m == 'INFORMATICA (LABORATORIO)':
        m = 'InfoL'
    elif m == 'TECNOLOGIE E PROGETTAZIONE DI SISTEMI INFORMATICI E DI TELECOMUNICAZIONI':
        m = 'TPS'
    elif m == 'TECNOLOGIE E PROGETTAZIONE DI SISTEMI INFORMATICI  E DI TELECOMUNICAZIONI':
        m = 'TPS'
    elif m == 'TECNOLOGIE E PROGETTAZIONE DI SISTEMI INFORMATICI E DI TELECOMUNICAZIONI (LAB)':
        m = 'TPSL'
    elif m == 'CHIMICA ANALITICA E STRUMENTALE':
        m = 'Ana'
    elif m == 'CHIMICA ORGANICA E BIOCHIMICA':
        m = 'Org'
    elif m == 'TECNOLOGIE CHIMICHE INDUSTRIALI':
        m = 'T.C.'
    elif m == 'TECNOLOGIE E PROGETTAZIONE DI SISTEMI ELETTRICI ED ELETTRONICI':
        m = 'TPS'
    elif m == 'ELETTROTECNICA ED ELETTRONICA':
        m = 'Ele'
    elif m == 'SISTEMI AUTOMATICI':
        m = 'Sist'
    elif m == 'TECNOLOGIE E TECNICE DI RAPPRESENTAZIONE GRAFICA':
        m = 'Tec'
    elif m == 'TECNOLOGIE E TECNICE DI RAPPRESENTAZIONE GRAFICA LABORATORIO':
        m = 'TecL'
    elif m == 'GEOGRAFIA':
        m = 'Geo'
    elif m == 'DIRITTO ED ECONOMIA':
        m = 'Dir'
    elif m == 'SCIENZE E TECNOLOGIE APPLICATE':
        m = 'STA'
    elif m == 'SCIENZE INTEGRATE (CHIMICA)':
        m = 'Chim'
    elif m == 'SCIENZE INTEGRATE (FISICA)':
        m = 'Fis'
    elif m == 'SCIENZE INTEGRATE (SCIENZE DELLA TERRA E BIOLOGIA)':
        m = 'Sci'
    return m

# nomiridotti = {
#     'LINGUA INGLESE': 'Ing',
#     'MATEMATICA': 'Mate',
#     'LINGUA E LETTERATURA ITALIANA': 'Ita',
#     'LINGUA  E LETTERATURA ITALIANA': 'Ita',
#     'STORIA': 'Sto',
#     'SCIENZE MOTORIE E SPORTIVE': 'Ginn',
#     'SISTEMI E RETI': 'Sist',
#     'INFORMATICA': 'Info',
#     'INFORMATICA (LABORATORIO)': 'InfoL',
#     'TECNOLOGIE E PROGETTAZIONE DI SISTEMI INFORMATICI E DI TELECOMUNICAZIONI': 'TPS',
#     'TECNOLOGIE E PROGETTAZIONE DI SISTEMI INFORMATICI  E DI TELECOMUNICAZIONI': 'TPS',
#     'TECNOLOGIE E PROGETTAZIONE DI SISTEMI INFORMATICI E DI TELECOMUNICAZIONI (LAB)': 'TPSL',
#     'CHIMICA ANALITICA E STRUMENTALE': 'Ana',
#     'CHIMICA ORGANICA E BIOCHIMICA': 'Org',
#     'TECNOLOGIE CHIMICHE INDUSTRIALI': 'T.C.',
#     'TECNOLOGIE E PROGETTAZIONE DI SISTEMI ELETTRICI ED ELETTRONICI': 'TPS',
#     'ELETTROTECNICA ED ELETTRONICA': 'Ele',
#     'SISTEMI AUTOMATICI': 'Sist',
#     'TECNOLOGIE E TECNICE DI RAPPRESENTAZIONE GRAFICA': 'Tec',
#     'TECNOLOGIE E TECNICE DI RAPPRESENTAZIONE GRAFICA LABORATORIO': 'TecL',
#     'GEOGRAFIA': 'Geo',
#     'DIRITTO ED ECONOMIA': 'Dir',
#     'SCIENZE E TECNOLOGIE APPLICATE': 'STA',
#     'SCIENZE INTEGRATE (CHIMICA)': 'Chim',
#     'SCIENZE INTEGRATE (FISICA)': 'Fis',
#     'SCIENZE INTEGRATE (SCIENZE DELLA TERRA E BIOLOGIA)': 'Sci'
# }


def voti_diff(a: list, b: list):  # algoritmo per cercare nuovi voti
    # (Steffo: non ho capito, commenta pls!)
    nuova = list()
    ai = 0
    swap = False
    if len(a) == 0:
        return b
    if len(a) != len(b):
        numNewVote = len(b) - len(a)
        for i in range(0, len(b)):
            if swap:
                swap = False
                ai += 1
                continue
            if not a[ai] == b[i]:
                if b[i] == a[ai + 1]:
                    swap = True
                    ai += 1
                else:
                    nuova.append(b[i])
                if len(nuova) == numNewVote:
                    break
            else:
                ai += 1
    return nuova


def set_typing(chat_id):
    payload = {
        'chat_id': chat_id,
        'action': 'typing'
    }
    requests.get('http://api.telegram.org/bot' + apikey.botKey + '/sendChatAction', params=payload)


def log_write(ty, e=''):
    t = str(strftime("%d-%H:%M:%S", gmtime()))
    m = ''
    if e == '':
        m = t+'    '+ty+'\n'
    else:
        m = t+'    '+ty+'\n'+e+'\n'
    with open('log.txt', 'a') as f:
        f.write(m)