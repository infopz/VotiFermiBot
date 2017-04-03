import time
import requests
from bs4 import BeautifulSoup
from base64 import b64encode, b64decode
from time import gmtime, strftime, sleep

import apikey

class voto:
    def __init__(self, v=0.0, m="", t="", d=""):
        self.v = v
        self.materia = m
        self.tipo = t
        self.data = d.replace('-', '/')

    def __eq__(self, other):
        return self.v == other.v and self.materia == other.materia


class utente:
    def __init__(self, chat_id=0, nome=""):
        self.chat_id = chat_id
        self.nome = nome
        self.userF = ""
        self.passF = ""
        self.voti = list()
        self.statusLogin = 0

    def setuser(self, u):
        self.userF = u

    def setpass(self, p):
        self.passF = p

    def aggiornavoti(self, shared):
        user = b64decode(self.userF).decode('ascii')
        user = user[0:-4]
        pw = b64decode(self.passF).decode('ascii')
        payload = {'ob_user': user, 'ob_password': pw}
        s = requests.Session()
        # s.post('http://www.fermi.mo.it/~loar/AssenzeVotiStudenti/elabora_PasswordStudenti.php', data=payload)
        # r = s.post('http://www.fermi.mo.it/~loar/AssenzeVotiStudenti/VotiDataOrdinati2Q.php')
        try:
            ripeti = True
            while ripeti:
                s.post('http://www.fermi.mo.it/~loar/AssenzeVotiStudenti/elabora_PasswordStudenti.php', data=payload)
                r = s.post('http://www.fermi.mo.it/~loar/AssenzeVotiStudenti/VotiDataOrdinati2Q.php')
                if len(r.text)!=11610:
                    ripeti=False
                else:
                    if shared['badReq']:
                        print("Bad Request - List Set to Empty")
                        break
                    print("Retry Request - Caronte fuck")
                    shared['badReq'] = True
                    sleep(600)
            soup = BeautifulSoup(r.text, "html.parser")
            table = soup.find("table", {"class": "TabellaVoti"})
        except Exception:
            print("Error VoteUpdate - User " + self.nome)
            return
        if table == None:
            self.voti = list()
        else:
            self.voti = list()
            for row in table.find_all('tr'):
                col = row.find_all('td')
                try:
                    if col[1].text[0].isdigit():
                        vot = voto(col[1].text, RiduciNome(col[0].text), col[3].text, col[2].text[1:6])
                        self.voti.append(vot)
                except Exception:
                    continue

    def votipermateria(self):
        user = b64decode(self.userF).decode('ascii')
        user = user[0:-4]
        pw = b64decode(self.passF).decode('ascii')
        payload = {'ob_user': user, 'ob_password': pw}
        s = requests.Session()
        s.post('http://www.fermi.mo.it/~loar/AssenzeVotiStudenti/elabora_PasswordStudenti.php', data=payload)
        r = s.post('http://www.fermi.mo.it/~loar/AssenzeVotiStudenti/VotiStudente2Q.php')
        soup = BeautifulSoup(r.text, "html.parser")
        table = soup.find("table", {"class": "TabellaVoti"})
        if table == None:
            voti = list()
        else:
            voti = list()
            for row in table.find_all('tr'):
                col = row.find_all('td')
                try:
                    if col[1].text[0].isdigit():
                        vot = voto(col[1].text, RiduciNome(col[0].text), col[3].text, col[2].text[1:6])
                        voti.append(vot)
                except Exception as e:
                    pass
        return voti

    def voti1q(self):
        user = b64decode(self.userF).decode('ascii')
        user = user[0:-4]
        pw = b64decode(self.passF).decode('ascii')
        payload = {'ob_user': user, 'ob_password': pw}
        s = requests.Session()
        s.post('http://www.fermi.mo.it/~loar/AssenzeVotiStudenti/elabora_PasswordStudenti.php', data=payload)
        r = s.post('http://www.fermi.mo.it/~loar/AssenzeVotiStudenti/VotiStudente1Q.php')
        soup = BeautifulSoup(r.text, "html.parser")
        table = soup.find("table", {"class": "TabellaVoti"})
        voti = list()
        for row in table.find_all('tr'):
            col = row.find_all('td')
            try:
                if col[1].text[0].isdigit():
                    vot = voto(col[1].text, RiduciNome(col[0].text), col[3].text, col[2].text[1:6])
                    voti.append(vot)
            except Exception:
                pass
        return voti

    def findmedie(self):
        user = b64decode(self.userF).decode('ascii')
        user = user[0:-4]
        pw = b64decode(self.passF).decode('ascii')
        payload = {'ob_user': user, 'ob_password': pw}
        s = requests.Session()
        s.post('http://www.fermi.mo.it/~loar/AssenzeVotiStudenti/elabora_PasswordStudenti.php', data=payload)
        s.post('http://www.fermi.mo.it/~loar/AssenzeVotiStudenti/VotiStudente2Q.php')
        r = s.post('http://www.fermi.mo.it/~loar/AssenzeVotiStudenti/VotiStudenteRiepilogo2Q.php')
        soup = BeautifulSoup(r.text, "html.parser")
        table = soup.find("table", {"class": "TabellaRiepilogo"})
        med = list()
        for row in table.find_all('tr'):
            col = row.find_all('td')
            try:
                scritto = str(col[22].text).strip()
                orale = str(col[25].text).strip()
                pratico = str(col[28].text).strip()
                grafico = str(col[31].text).strip()
                if scritto != "":
                    med.append(voto(scritto, col[0].text, "Scritto"))
                if orale != "":
                    med.append(voto(orale, col[0].text, "Orale"))
                if pratico != "":
                    med.append(voto(pratico, col[0].text, "Pratico"))
                if grafico != "":
                    med.append(voto(grafico, col[0].text, "Grafico"))
            except Exception as e:
                pass
        return med

    def printvoti(self, spaceformat=False):
        msg = "Ecco i tuoi Voti\n"
        mat = ''
        for i in self.voti:
            if i.materia != mat and spaceformat:
                msg += '\n'
            mat = i.materia
            msg += RiduciNome(i.materia).upper() + " - " + i.tipo + " - "+ i.data + " - *" + i.v + '*\n'
        return msg

    def checklogin(self):
        if self.userF == '' or self.passF == '':
            return False
        user = b64decode(self.userF).decode('ascii')
        user = user[0:-4]
        pw = b64decode(self.passF).decode('ascii')
        payload = {'ob_user': user, 'ob_password': pw}
        s = requests.Session()
        s.post('http://www.fermi.mo.it/~loar/AssenzeVotiStudenti/elabora_PasswordStudenti.php', data=payload)
        r = s.post('http://www.fermi.mo.it/~loar/AssenzeVotiStudenti/VotiDataOrdinati1Q.php')
        if r.text[-13:] == "doesn't exist":
            return False
        else:
            return True


def RiduciNome(m):  # per ora la lascio cosi, poi quando ho la sicurezza che siano state inserite tutte le materie usero il dict
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


"""nomiridotti = {
    'LINGUA INGLESE': 'Ing',
    'MATEMATICA': 'Mate',
    'LINGUA E LETTERATURA ITALIANA': 'Ita',
    'LINGUA  E LETTERATURA ITALIANA': 'Ita',
    'STORIA': 'Sto',
    'SCIENZE MOTORIE E SPORTIVE': 'Ginn',
    'SISTEMI E RETI': 'Sist',
    'INFORMATICA': 'Info',
    'INFORMATICA (LABORATORIO)': 'InfoL',
    'TECNOLOGIE E PROGETTAZIONE DI SISTEMI INFORMATICI E DI TELECOMUNICAZIONI': 'TPS',
    'TECNOLOGIE E PROGETTAZIONE DI SISTEMI INFORMATICI  E DI TELECOMUNICAZIONI': 'TPS',
    'TECNOLOGIE E PROGETTAZIONE DI SISTEMI INFORMATICI E DI TELECOMUNICAZIONI (LAB)': 'TPSL',
    'CHIMICA ANALITICA E STRUMENTALE': 'Ana',
    'CHIMICA ORGANICA E BIOCHIMICA': 'Org',
    'TECNOLOGIE CHIMICHE INDUSTRIALI': 'T.C.',
    'TECNOLOGIE E PROGETTAZIONE DI SISTEMI ELETTRICI ED ELETTRONICI': 'TPS',
    'ELETTROTECNICA ED ELETTRONICA': 'Ele',
    'SISTEMI AUTOMATICI': 'Sist',
    'TECNOLOGIE E TECNICE DI RAPPRESENTAZIONE GRAFICA': 'Tec',
    'TECNOLOGIE E TECNICE DI RAPPRESENTAZIONE GRAFICA LABORATORIO': 'TecL',
    'GEOGRAFIA': 'Geo',
    'DIRITTO ED ECONOMIA': 'Dir',
    'SCIENZE E TECNOLOGIE APPLICATE': 'STA',
    'SCIENZE INTEGRATE (CHIMICA)': 'Chim',
    'SCIENZE INTEGRATE (FISICA)': 'Fis',
    'SCIENZE INTEGRATE (SCIENZE DELLA TERRA E BIOLOGIA)': 'Sci'
}"""


def seeDiff(a, b):  # algoritmo per cercare nuovi voti
    nv = list()
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
                    nv.append(b[i])
                if len(nv) == numNewVote:
                    break
            else:
                ai += 1
    return nv


def sendTyping(chat_id):
    payload = {
        'chat_id': chat_id,
        'action': 'typing'
    }
    a = requests.get('http://api.telegram.org/bot' + apikey.botKey + '/sendChatAction', params=payload)
