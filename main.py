#!/usr/bin/python3
import botogram
from bs4 import BeautifulSoup
from base64 import b64encode, b64decode
from time import gmtime, strftime
import requests
import pickle

import apikey


# bot.api.call("sendMessage", {"chat_id": chat.id, "text": 'Testo Del messaggio', "parse_mode": "HTML", "reply_markup": '{"keyboard": [["text": "Testo"]], "one_time_keyboard": false, "resize_keyboard": true}'})

class voto:
    def __init__(self, v=0.0, m="", t=""):
        self.v = v
        self.materia = m
        self.tipo = t

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

    def aggiornavoti(self):
        user = b64decode(self.userF).decode('ascii')
        user = user[0:-4]
        pw = b64decode(self.passF).decode('ascii')
        payload = {'ob_user': user, 'ob_password': pw}
        s = requests.Session()
        #s.post('http://www.fermi.mo.it/~loar/AssenzeVotiStudenti/elabora_PasswordStudenti.php', data=payload)
        #r = s.post('http://www.fermi.mo.it/~loar/AssenzeVotiStudenti/VotiDataOrdinati2Q.php')
        s.post('http://www.fermi.mo.it/~loar/AssenzeVotiStudenti/elabora_PasswordStudenti.php', data=payload)
        r = s.post('http://www.fermi.mo.it/~loar/AssenzeVotiStudenti/VotiDataOrdinati2Q.php')
        soup = BeautifulSoup(r.text, "html.parser")
        table = soup.find("table", {"class": "TabellaVoti"})
        if table==None:
            self.voti = list()
        else:
            self.voti = list()
            for row in table.find_all('tr'):
                col = row.find_all('td')
                try:
                    if col[1].text[0].isdigit():
                        vot = voto(col[1].text, RiduciNome(col[0].text), col[3].text)
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
        if table==None:
            voti = list()
        else:
            voti = list()
            for row in table.find_all('tr'):
                col = row.find_all('td')
                try:
                    if col[1].text[0].isdigit():
                        vot = voto(col[1].text, RiduciNome(col[0].text), col[3].text)
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
                    vot = voto(col[1].text, RiduciNome(col[0].text), col[3].text)
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
            msg += RiduciNome(i.materia).upper() + " - " + i.tipo + " - *" + i.v + '*\n'
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


def RiduciNome(m): #per ora la lascio cosi, poi quando ho la sicurezza che siano state inserite tutte le materie usero il dict
    if m=='LINGUA INGLESE':
        m='Ing'
    elif m=='MATEMATICA':
        m='Mate'
    elif m=='LINGUA E LETTERATURA ITALIANA':
        m='Ita'
    elif m=='LINGUA  E LETTERATURA ITALIANA':
        m='Ita'
    elif m=='STORIA':
        m='Sto'
    elif m=='SCIENZE MOTORIE E SPORTIVE':
        m='Ginn'
    elif m=='TELECOMUNICAZIONI':
        m='Tele'
    elif m=='SISTEMI E RETI':
        m='Sist'
    elif m=='SISTEMI E RETI (LABORATORIO)':
        m='SisL'
    elif m=='INFORMATICA':
        m='Info'
    elif m=='INFORMATICA (LABORATORIO)':
        m='InfoL'
    elif m=='TECNOLOGIE E PROGETTAZIONE DI SISTEMI INFORMATICI E DI TELECOMUNICAZIONI':
        m='TPS' 
    elif m=='TECNOLOGIE E PROGETTAZIONE DI SISTEMI INFORMATICI  E DI TELECOMUNICAZIONI':
        m='TPS'
    elif m=='TECNOLOGIE E PROGETTAZIONE DI SISTEMI INFORMATICI E DI TELECOMUNICAZIONI (LAB)':
        m='TPSL'
    elif m=='CHIMICA ANALITICA E STRUMENTALE':
        m='Ana'
    elif m=='CHIMICA ORGANICA E BIOCHIMICA':
        m='Org'
    elif m=='TECNOLOGIE CHIMICHE INDUSTRIALI':
        m='T.C.'
    elif m=='TECNOLOGIE E PROGETTAZIONE DI SISTEMI ELETTRICI ED ELETTRONICI':
        m='TPS'
    elif m=='ELETTROTECNICA ED ELETTRONICA':
        m='Ele'
    elif m=='SISTEMI AUTOMATICI':
        m='Sist'
    elif m=='TECNOLOGIE E TECNICE DI RAPPRESENTAZIONE GRAFICA':
        m='Tec'
    elif m=='TECNOLOGIE E TECNICE DI RAPPRESENTAZIONE GRAFICA LABORATORIO':
        m='TecL'
    elif m=='GEOGRAFIA':
        m='Geo'
    elif m=='DIRITTO ED ECONOMIA':
        m='Dir'
    elif m=='SCIENZE E TECNOLOGIE APPLICATE':
        m='STA'
    elif m=='SCIENZE INTEGRATE (CHIMICA)':
        m='Chim'
    elif m=='SCIENZE INTEGRATE (FISICA)':
        m='Fis'
    elif m=='SCIENZE INTEGRATE (SCIENZE DELLA TERRA E BIOLOGIA)':
        m='Sci'
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
        numNewVote = len(b)-len(a)        
        for i in range(0, len(b)):
            if swap:
                swap=False
                ai+=1
                continue
            if not a[ai] == b[i]:
                if b[i]==a[ai+1]:
                    swap=True
                    ai+=1
                else:
                    nv.append(b[i])
                if len(nv)==numNewVote:
                    break
            else:
                ai += 1
    return nv

def sendTyping(chat_id):
    payload={
        'chat_id': chat_id,
        'action': 'typing'
        }
    a=requests.get('http://api.telegram.org/bot'+apikey.botKey+'/sendChatAction', params=payload)


bot = botogram.create(apikey.botKey)

@bot.command('start')
def startcomm(chat, message, shared):
    s = shared['user']
    scU = shared['cUs']
    if s[scU].checklogin():
        msg = 'Ciao, ' + s[scU].nome + ', avevi gia inserito i tuoi dati e sono stati caricati! Inizia a usare il bot!'
        bot.api.call("sendMessage", {
            "chat_id": s[scU].chat_id, "text": msg, "parse_mode": "Markdown",
            "reply_markup": '{"keyboard": [[{"text": "Voti per materia"}, {"text":"Voti per data"}], [{"text": "Medie"}, {"text": "Voti 1°Quad"}]], "one_time_keyboard": false, "resize_keyboard": true}'
            })
        s[scU].statusLogin = 0
    else:
        chat.send(
            "Benvenuto " + s[scU].nome + "\nDa ora in poi quando troverò un nuovo voto sul registro ti invierò un messaggio\n\nSe il login dovesse fallire ridai il comando /start\n\nI tuoi dati sono al sicuro! Username e Password vengono criptati appena li inserisci\n\nNel caso qualche materia non venisse abbreviata contattami\n\nBot progettato da Giovanni Casari (@infopz)")
        chat.send("Inserisci il tuo username del registro:")
        s[scU].statusLogin = 1
    shared['user'] = s


@bot.command('load')
def loadCommand(chat, message, shared, bot):
    if message.sender.username == 'infopz':
        loadDati(shared)
        s = shared['user']
        n=0
        for i in s:
            print("Load "+str(n)+": " + i.nome)
            n+=1
        chat.send('Dati Caricati - Utenti:'+str(n))
    else:
        chat.send("Solo @infopz e' autorizzato ad eseguire questo comando")


@bot.command('change')
def changeCommand(chat, message, shared, args):
    s = shared['user']
    scU = shared['cUs']
    if not args or len(args)!=2:
        bot.api.call("sendMessage", {
            "chat_id": s[scU].chat_id, "text": 'Utilizza questo comando se devi cambiare username e password memorizzati nel bot. \n`/change newUser newPassword`', "parse_mode": "Markdown",
            "reply_markup": '{"keyboard": [[{"text": "Voti per materia"}, {"text":"Voti per data"}], [{"text": "Medie"}, {"text": "Voti 1°Quad"}]], "one_time_keyboard": false, "resize_keyboard": true}'
            })
    else:
        msg = args[0] + 'aaaa'
        us = b64encode(msg.encode('ascii')).decode('ascii')  # cripto il nome utente non appena viene immessa
        s[scU].setuser(us)
        pw = b64encode(args[1].encode('ascii')).decode('ascii')  # cripto la password non appena viene immessa
        s[scU].setpass(pw)
        if s[scU].checklogin():
            bot.api.call("sendMessage", {
                "chat_id": s[scU].chat_id, "text": 'Dati di login corretti, puoi iniziare ad usare il bot!', "parse_mode": "Markdown",
                "reply_markup": '{"keyboard": [[{"text": "Voti per materia"}, {"text":"Voti per data"}], [{"text": "Medie"}, {"text": "Voti 1°Quad"}]], "one_time_keyboard": false, "resize_keyboard": true}'
                })
            s[scU].aggiornavoti()
            s[scU].statusLogin = 0
        else:
            chat.send('Dati di login non corretti')
            chat.send('Immetti il tuo username')
            s[scU].statusLogin = 1
    shared['user'] = s
    saveDati(shared)

@bot.command('timer')
def timerCommand(chat, message, shared, bot):
    if message.sender.username == 'infopz':
        vediMod(bot, shared)
    else:
        chat.send("Solo @infopz e' autorizzato ad eseguire questo comando")

@bot.command('del')
def delCommand(chat, message, shared, args):
    if message.sender.username=='infopz':
        s=shared['user']
        i=int(args[0])
        print("User "+str(i)+" "+s[i].nome+" deleted")
        chat.send("User "+str(i)+" "+s[i].nome+" deleted")
        del s[i]
        shared['user']=s
        saveDati(shared)
    else:
        bot.api.call("sendMessage", {
            "chat_id": shared['user'[shared['scu']]].chat_id, "text": "Solo @infopz e' autorizzato ad eseguire questo comando", "parse_mode": "Markdown",
            "reply_markup": '{"keyboard": [[{"text": "Voti per materia"}, {"text":"Voti per data"}], [{"text": "Medie"}, {"text": "Voti 1°Quad"}]], "one_time_keyboard": false, "resize_keyboard": true}'
            })


@bot.command('all')
def allCommand(chat, message, shared):
    s = shared['user']
    scU = shared['cUs']
    if message.sender.username!='infopz':
        bot.api.call("sendMessage", {
            "chat_id": s[scU].chat_id,
            "text": "Solo @infopz e' autorizzato ad eseguire questo comando", "parse_mode": "Markdown",
            "reply_markup": '{"keyboard": [[{"text": "Voti per materia"}, {"text":"Voti per data"}], [{"text": "Medie"}, {"text": "Voti 1°Quad"}]], "one_time_keyboard": false, "resize_keyboard": true}'
        })
        return
    m = "Nuova comunicazione! \n"+message.text[5:]
    for i in s:
        bot.api.call("sendMessage", {
            "chat_id": i.chat_id,
            "text": m, "parse_mode": "Markdown",
            "reply_markup": '{"keyboard": [[{"text": "Voti per materia"}, {"text":"Voti per data"}], [{"text": "Medie"}, {"text": "Voti 1°Quad"}]], "one_time_keyboard": false, "resize_keyboard": true}'
        })
        try:
        	print("Comunicazione inviata a "+str(i.nome))
        except Exception:
        	print("Error with sending the comunication")

def voteCommand(chat, message, shared):
    s = shared['user']
    scU = shared['cUs']
    sendTyping(s[scU].chat_id)
    try:
        s[scU].aggiornavoti()
        msg=''
        if len(s[scU].voti)==0:
            msg='Non hai ancora nessun voto nel secondo quadrimestre'
        else:
            msg=s[scU].printvoti()
        bot.api.call("sendMessage", {
            "chat_id": s[scU].chat_id, "text": msg, "parse_mode": "Markdown",
            "reply_markup": '{"keyboard": [[{"text": "Voti per materia"}, {"text":"Voti per data"}], [{"text": "Medie"}, {"text": "Voti 1°Quad"}]], "one_time_keyboard": false, "resize_keyboard": true}'
            })
    except Exception as e:
        bot.api.call("sendMessage", {
            "chat_id": s[scU].chat_id, "text": "Errore nel login\nDai il comando /start e riprova\nNel caso il problema si dovesse ripresentare contatta @infopz", "parse_mode": "Markdown",
            "reply_markup": '{"keyboard": [[{"text": "Voti per materia"}, {"text":"Voti per data"}], [{"text": "Medie"}, {"text": "Voti 1°Quad"}]], "one_time_keyboard": false, "resize_keyboard": true}'
            })
        print("Error voteCommand - User "+s[scU].nome+" - "+str(e))
    shared['user'] = s
    saveDati(shared)

def votiMateria(chat, message, shared):
    s = shared['user']
    scU = shared['cUs']
    sendTyping(s[scU].chat_id)
    try:
        msg=''
        voti = s[scU].votipermateria()
        if len(voti)==0:
            msg='Non hai ancora nessun voto nel secondo quadrimestre'
        else:
            msg = "Ecco i tuoi Voti\n"
            mat = ''
            for i in voti:
                if i.materia != mat:
                    msg += '\n'
                mat = i.materia
                msg += RiduciNome(i.materia.upper()) + " - " + i.tipo + " - *" + i.v + '*\n'
        bot.api.call("sendMessage", {
            "chat_id": s[scU].chat_id, "text": msg, "parse_mode": "Markdown",
            "reply_markup": '{"keyboard": [[{"text": "Voti per materia"}, {"text":"Voti per data"}], [{"text": "Medie"}, {"text": "Voti 1°Quad"}]], "one_time_keyboard": false, "resize_keyboard": true}'
                })
    except Exception as e:
        bot.api.call("sendMessage", {
            "chat_id": s[scU].chat_id, "text": "Errore nel login\nDai il comando /start e riprova\nNel caso il problema si dovesse ripresentare contatta @infopz", "parse_mode": "Markdown",
            "reply_markup": '{"keyboard": [[{"text": "Voti per materia"}, {"text":"Voti per data"}], [{"text": "Medie"}, {"text": "Voti 1°Quad"}]], "one_time_keyboard": false, "resize_keyboard": true}'
            })
        print("Error voteCommand - User "+s[scU].nome+" -")

def medieCommand(chat, message, shared):
    s = shared['user']
    scU = shared['cUs']
    sendTyping(s[scU].chat_id)
    try:
        m = s[scU].findmedie()
        msg = ""
        if len(m)==0:
            msg="Non hai ancora nessun voto nel secondo quadrimestre"
        else:
            for i in m:
                msg += RiduciNome(i.materia[1:]) + " - " + i.tipo + " - *" + i.v + '*\n'
        bot.api.call("sendMessage", {
            "chat_id": s[scU].chat_id, "text": msg, "parse_mode": "Markdown",
            "reply_markup": '{"keyboard": [[{"text": "Voti per materia"}, {"text":"Voti per data"}], [{"text": "Medie"}, {"text": "Voti 1°Quad"}]], "one_time_keyboard": false, "resize_keyboard": true}'
            })
    except Exception as e:
        bot.api.call("sendMessage", {
            "chat_id": s[scU].chat_id, "text": "Errore nel login\nDai il comando /start e riprova\nNel caso il problema si dovesse ripresentare contatta @infopz", "parse_mode": "Markdown",
            "reply_markup": '{"keyboard": [[{"text": "Voti per materia"}, {"text":"Voti per data"}], [{"text": "Medie"}, {"text": "Voti 1°Quad"}]], "one_time_keyboard": false, "resize_keyboard": true}'
            })
        print("Error voteCommand - User "+s[scU].nome+" - "+str(e))

def voti1q(chat, message, shared):
    s=shared['user']
    scU = shared['cUs']
    try:
        sendTyping(s[scU].chat_id)
        voti = s[scU].voti1q()
        msg = "Ecco i tuoi voti del primo quadrimestre\n"
        mat = ''
        for i in voti:
            if i.materia != mat:
                msg += '\n'
            mat = i.materia
            msg += RiduciNome(i.materia.upper()) + " - " + i.tipo + " - *" + i.v + '*\n'
        bot.api.call("sendMessage", {
            "chat_id": s[scU].chat_id, "text": msg, "parse_mode": "Markdown",
            "reply_markup": '{"keyboard": [[{"text": "Voti per materia"}, {"text":"Voti per data"}], [{"text": "Medie"}, {"text": "Voti 1°Quad"}]], "one_time_keyboard": false, "resize_keyboard": true}'
            })
    except Exception as e:
        bot.api.call("sendMessage", {
            "chat_id": s[scU].chat_id, "text": "Errore nel login\nDai il comando /start e riprova\nNel caso il problema si dovesse ripresentare contatta @infopz", "parse_mode": "Markdown",
            "reply_markup": '{"keyboard": [[{"text": "Voti per materia"}, {"text":"Voti per data"}], [{"text": "Medie"}, {"text": "Voti 1°Quad"}]], "one_time_keyboard": false, "resize_keyboard": true}'
            })
        print("Error voteCommand - User "+s[scU].nome+" - "+str(e))

def prDataAll(s):
    for i in s:
        print("n:" + i.nome + " id:" + str(i.chat_id) + " u:" + str(i.userF) + " p:" + str(i.passF) + " " + str(i.statusLogin))


def start1(chat, message, shared):
    s = shared['user']
    scU = shared['cUs']
    msg = message.text + 'aaaa'
    us = b64encode(msg.encode('ascii')).decode('ascii')
    s[scU].setuser(us)
    s[scU].statusLogin = 2
    shared['user'] = s
    chat.send('Ora inserisci la password')


def start2(chat, message, shared):
    s = shared['user']
    scU = shared['cUs']
    pw = b64encode(message.text.encode('ascii')).decode('ascii')
    s[scU].setpass(pw)
    if s[scU].checklogin():
        bot.api.call("sendMessage", {
            "chat_id": s[scU].chat_id, "text": 'Dati di login corretti, puoi iniziare ad usare il bot!', "parse_mode": "Markdown",
            "reply_markup": '{"keyboard": [[{"text": "Voti per materia"}, {"text":"Voti per data"}], [{"text": "Medie"}, {"text": "Voti 1°Quad"}]], "one_time_keyboard": false, "resize_keyboard": true}'
            })
        s[scU].aggiornavoti()
        s[scU].statusLogin = 0
    else:
        chat.send('Dati di login non corretti')
        chat.send('Immetti il tuo username')
        s[scU].statusLogin = 1
    shared['user'] = s
    saveDati(shared)


def saveDati(shared):
    s = shared['user']
    f = open('user.txt', 'wb')
    pickle.dump(s, f)
    f.close()
    shared['user'] = s


def loadDati(shared):
    s = shared['user']
    f = open('user.txt', 'rb')
    s = pickle.load(f)
    shared['user'] = s


@bot.timer(7200)
def vediMod(bot, shared):
    h = int(strftime("%H", gmtime()))+1
    print(str(h))
    if h>=22 or h<=7:
        return
    print("Timer "+str(h))
    utenti = shared['user']
    for i in range(0, len(utenti)):
        votivecchi = list()
        try:
            votivecchi = utenti[i].voti
            utenti[i].aggiornavoti()
            nuovivoti = seeDiff(votivecchi, utenti[i].voti)
            if len(nuovivoti) > 0:
                print('NewVotesFound ' + utenti[i].nome)
                msg = "Ehi, " + utenti[i].nome + ", hai dei nuovi voti sul registro:\n"
                for voto in nuovivoti:
                    msg += "Hai preso *" + voto.v + '* in ' + voto.materia + " " + voto.tipo + '\n'
                bot.chat(utenti[i].chat_id).send(msg)
        except Exception as e:
            print("Error NewVoti - User "+str(i)+": "+str(e))
    shared['user'] = utenti
    if not shared['firstTimer']:
        saveDati(shared)
    shared['firstTimer'] = False


@bot.before_processing
def bef_proc(chat, message, shared):
    nom=''
    if message.sender.username!=None:
        nom=message.sender.username
    else:
        nom=message.sender.first_name
    print("Message from: " + nom)
    s = shared['user']
    scU = shared['cUs']
    if message.text!='/load':
        if chat.id != s[scU].chat_id:
            # inserimento nuovo current user
            newUser = True
            for i in range(0, len(s)):
                if chat.id == s[i].chat_id:
                    scU = i
                    newUser = False
                    break
            if newUser:
                nU = utente(chat.id, nom)
                print('NewUser: ' + nU.nome)
                s.append(nU)
                scU = len(s)-1
        shared['user'] = s
        shared['cUs'] = scU
        if s[scU].statusLogin == 1:
            start1(chat, message, shared)
        elif s[scU].statusLogin == 2:
            start2(chat, message, shared)
        elif message.text == 'Voti per materia':
            votiMateria(chat, message, shared)
        elif message.text == 'Voti per data':
            voteCommand(chat, message, shared)
        elif message.text == 'Medie':
            medieCommand(chat, message, shared)
        elif message.text=='Voti 1°Quad':
            voti1q(chat, message, shared)
    

@bot.prepare_memory
def prepare_memory(shared):
    shared['firstTimer'] = True
    shared['cUs'] = 0
    shared['user'] = list()


if __name__ == "__main__":
    bot.run()
