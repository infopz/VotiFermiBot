#!/usr/bin/python3
import botogram
from bs4 import BeautifulSoup
from base64 import b64encode, b64decode
import requests
import pickle

import apikey


# bot.api.call("sendMessage", {"chat_id": chat.id, "text": 'Testo Del messaggio', "parse_mode": "HTML", "reply_markup": '{"keyboard": [["text": "Testo"]], "one_time_keyboard": false, "resize_keyboard": true}'})

class Voto:
    def __init__(self, v=0.0, m="", t=""):
        self.v = v
        self.materia = m
        self.tipo = t

    def __eq__(self, other):
        return self.v == other.v and self.materia == other.materia


class Utente:
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
        s.post('http://www.fermi.mo.it/~loar/AssenzeVotiStudenti/elabora_PasswordStudenti.php', data=payload)
        r = s.post('http://www.fermi.mo.it/~loar/AssenzeVotiStudenti/VotiDataOrdinati1Q.php')
        soup = BeautifulSoup(r.text, "html.parser")
        table = soup.find("table", {"class": "TabellaVoti"})
        self.voti = list()
        for row in table.find_all('tr'):
            col = row.find_all('td')
            try:
                if col[1].text[0].isdigit():
                    vot = Voto(col[1].text, nomiridotti[col[0].text], col[3].text)
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
        r = s.post('http://www.fermi.mo.it/~loar/AssenzeVotiStudenti/VotiStudente1Q.php')
        soup = BeautifulSoup(r.text, "html.parser")
        table = soup.find("table", {"class": "TabellaVoti"})
        voti = list()
        for row in table.find_all('tr'):
            col = row.find_all('td')
            try:
                if col[1].text[0].isdigit():
                    vot = Voto(col[1].text, nomiridotti[col[0].text], col[3].text)
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
        s.post('http://www.fermi.mo.it/~loar/AssenzeVotiStudenti/VotiStudente1Q.php')
        r = s.post('http://www.fermi.mo.it/~loar/AssenzeVotiStudenti/VotiStudenteRiepilogo1Q.php')
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
                    med.append(Voto(float(scritto), col[0].text, "Scritto"))
                if orale != "":
                    med.append(Voto(float(orale), col[0].text, "Orale"))
                if pratico != "":
                    med.append(Voto(float(pratico), col[0].text, "Pratico"))
                if grafico != "":
                    med.append(Voto(float(grafico), col[0].text, "Grafico"))
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
            msg += nomiridotti[i.materia].upper() + " - " + i.tipo + " - *" + i.v + '*\n'
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


nomiridotti = {
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
}


def seeDiff(listaa, listab):  # algoritmo per cercare nuovi voti
    nuovivoti = list()
    contatore = 0
    if len(listaa) != len(listab):
        for voto in listab:
            if listaa[contatore] != voto:
                nuovivoti.append(voto)
            else:
                contatore += 1
    return nuovivoti


bot = botogram.create(apikey.botKey)


@bot.command('start')
def hellocomm(chat, message, shared):
    scU = shared['cUs']
    if scU.userF != '' and scU.passF != '':
        msg = 'Ciao, ' + scU.nome + ', avevi gia inserito i tuoi dati e sono stati caricati! Inizia a usare il bot!'
        bot.api.call("sendMessage", {
            "chat_id":      scU.chat_id, "text": msg, "parse_mode": "Markdown",
            "reply_markup": '{"keyboard": [[{"text": "Voti per materia"}],[{"text":"Voti per data"}, {"text": "Medie"}]], "one_time_keyboard": false, "resize_keyboard": true}'
            })
        scU.statusLogin = 0
    else:
        chat.send(
            "Benvenuto " + scU.nome + "\nDa ora in poi quando troverò un nuovo voto sul registro ti invierò un messaggio\n\nSe il login dovesse fallire ridai il comando /start\n\nI tuoi dati sono al sicuro! Username e Password vengono criptati appena li inserisci\n\nNel caso qualche materia non venisse abbreviata contattami\n\nBot progettato da Giovanni Casari (@infopz)")
        chat.send("Inserisci il tuo username del registro:")
        scU.statusLogin = 1
    shared['cUs'] = scU


@bot.command('vote')
def voteCommand(chat, message, shared):
    scU = shared['cUs']
    scU.aggiornavoti()
    bot.api.call("sendMessage", {
        "chat_id":      scU.chat_id, "text": scU.printvoti(), "parse_mode": "Markdown",
        "reply_markup": '{"keyboard": [[{"text": "Voti per materia"}],[{"text":"Voti per data"}, {"text": "Medie"}]], "one_time_keyboard": false, "resize_keyboard": true}'
        })
    # chat.send(s.printVoti())
    shared['cUs'] = scU
    saveDati(shared)


@bot.command('load')
def loadCommand(chat, message, shared, botc):
    if message.sender.username == 'infopz':
        loadDati(botc, shared)
        s = shared['user']
        for i in s:
            print("Load: " + i.nome)
        chat.send('Dati Caricati')
    else:
        chat.send("Solo @infopz e' autorizzato ad eseguire questo comando")


@bot.command('change')
def chanceCommand(chat, message, shared, args):
    s = shared['cUs']
    msg = args[0] + 'aaaa'
    us = b64encode(msg.encode('ascii')).decode('ascii')  # cripto il nome utente non appena viene immessa
    s.setuser(us)
    pw = b64encode(args[1].encode('ascii')).decode('ascii')  # cripto la password non appena viene immessa
    s.setpass(pw)
    if s.checklogin():
        bot.api.call("sendMessage", {
            "chat_id":      s.chat_id, "text": 'Dati di login corretti, puoi iniziare ad usare il bot!', "parse_mode": "Markdown",
            "reply_markup": '{"keyboard": [[{"text": "Voti per materia"}],[{"text":"Voti per data"}, {"text": "Medie"}]], "one_time_keyboard": false, "resize_keyboard": true}'
            })
        s.aggiornavoti()
        s.statusLogin = 0
    else:
        chat.send('Dati di login non corretti')
        chat.send('Immetti il tuo username')
        s.statusLogin = 1
    shared['cUs'] = s
    saveDati(shared)


@bot.command('timer')
def timerCommand(chat, message, shared, bot):
    if message.sender.username == 'infopz':
        vediMod(bot, shared)
    else:
        chat.send("Solo @infopz e' autorizzato ad eseguire questo comando")


def votiMateria(chat, message, shared):
    scU = shared['cUs']
    voti = scU.votipermateria()
    msg = "Ecco i tuoi Voti\n"
    mat = ''
    for i in voti:
        if i.materia != mat:
            msg += '\n'
        mat = i.materia
        msg += nomiridotti[i.materia.upper()] + " - " + i.tipo + " - *" + i.v + '*\n'
    bot.api.call("sendMessage", {
        "chat_id":      scU.chat_id, "text": msg, "parse_mode": "Markdown",
        "reply_markup": '{"keyboard": [[{"text": "Voti per materia"}],[{"text":"Voti per data"}, {"text": "Medie"}]], "one_time_keyboard": false, "resize_keyboard": true}'
        })


def medieCommand(chat, message, shared):
    scU = shared['cUs']
    m = scU.findmedie()
    msg = ""
    for i in m:
        msg += nomiridotti[i.materia[1:]] + " - " + i.tipo + " - *" + i.v + '*\n'
    bot.api.call("sendMessage", {
        "chat_id":      scU.chat_id, "text": msg, "parse_mode": "Markdown",
        "reply_markup": '{"keyboard": [[{"text": "Voti per materia"}],[{"text":"Voti per data"}, {"text": "Medie"}]], "one_time_keyboard": false, "resize_keyboard": true}'
        })


def prDataAll(s, scU):
    for i in s:
        print("n:" + i.nome + " id:" + str(i.chat_id) + " u:" + str(i.userF) + " p:" + str(i.passF) + " " + str(i.statusLogin))
    print("CU: n:" + scU.nome + " id:" + str(scU.chat_id) + " u:" + str(scU.userF) + " p:" + str(scU.passF) + " " + str(scU.statusLogin))


def start1(chat, message, shared):
    s = shared['cUs']
    msg = message.text + 'aaaa'
    us = b64encode(msg.encode('ascii')).decode('ascii')  # TODO: pls no
    s.setuser(us)
    s.statusLogin = 2
    shared['cUs'] = s
    chat.send('Ora inserisci la password')


def start2(chat, message, shared):
    s = shared['cUs']
    pw = b64encode(message.text.encode('ascii')).decode('ascii')  # TODO: pls no anche qui
    s.setpass(pw)
    if s.checklogin():
        bot.api.call("sendMessage", {
            "chat_id":      s.chat_id, "text": 'Dati di login corretti, puoi iniziare ad usare il bot!', "parse_mode": "Markdown",
            "reply_markup": '{"keyboard": [[{"text": "Voti per materia"}],[{"text":"Voti per data"}, {"text": "Medie"}]], "one_time_keyboard": false, "resize_keyboard": true}'
            })
        s.aggiornavoti()
        s.statusLogin = 0
    else:
        chat.send('Dati di login non corretti')
        chat.send('Immetti il tuo username')
        s.statusLogin = 1
    shared['cUs'] = s
    saveDati(shared)


def saveDati(shared):
    s = shared['user']
    scU = shared['cUs']
    n = -1
    for i in s:
        n += 1
        if scU.chat_id == i.chat_id:
            break
    if n != -1:
        s[n] = scU
    f = open('user.txt', 'wb')
    pickle.dump(s, f)
    f.close()
    shared['user'] = s
    shared['cUs'] = scU


def loadDati(bot, shared):
    s = shared['user']
    scU = shared['cUs']
    f = open('user.txt', 'rb')
    s = pickle.load(f)
    shared['cUs'] = scU
    shared['user'] = s
    shared['load'] = True


@bot.timer(900)
def vediMod(bot, shared):
    print('Timer')
    utenti = shared['user']
    scU = shared['cUs']
    if not shared['firstTimer']:
        for i in range(0, len(utenti)):
            if utenti[i].chat_id == scU.chat_id:
                utenti[i] = scU
                break
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
            pass
    shared['user'] = utenti
    if not shared['firstTimer']:
        scU.aggiornavoti()
    shared['cUs'] = scU
    if not shared['firstTimer']:
        saveDati(shared)
    shared['firstTimer'] = False


@bot.before_processing
def processM(chat, message, shared):
    print("Message from: @" + message.sender.first_name)
    s = shared['user']
    scU = shared['cUs']
    if chat.id != scU.chat_id and not shared['load']:
        # salvataggio vecchio currentUser
        n = -1
        for i in s:
            n += 1
            if scU.chat_id == i.chat_id:
                break
        try:
            if n != -1:
                s[n] = scU
        except Exception:
            pass
        # inserimento nuovo current user
        newUser = True
        for i in s:
            if chat.id == i.chat_id:
                scU = i
                newUser = False
                break
        if newUser:
            nU = Utente(chat.id, message.sender.first_name)
            print('NewUser: ' + nU.nome)
            s.append(nU)
            scU = nU
    elif shared['load']:
        for i in s:
            if i.chat_id == scU.chat_id:
                scU = i
                break
        shared['load'] = False
    shared['user'] = s
    shared['cUs'] = scU
    if scU.statusLogin == 1:
        start1(chat, message, shared)
    elif scU.statusLogin == 2:
        start2(chat, message, shared)
    elif message.text == 'Voti per materia':
        votiMateria(chat, message, shared)
    elif message.text == 'Voti per data':
        voteCommand(chat, message, shared)
    elif message.text == 'Medie':
        medieCommand(chat, message, shared)


@bot.prepare_memory
def prepare_memory(shared):
    shared['firstTimer'] = True
    shared['cUs'] = Utente()
    shared['user'] = list()
    shared['load'] = False


if __name__ == "__main__":
    bot.run()
