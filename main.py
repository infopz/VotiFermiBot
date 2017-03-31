#!/usr/bin/python3
import botogram
from bs4 import BeautifulSoup
from base64 import b64encode, b64decode
from time import gmtime, strftime, sleep
import requests
import pickle

from fileClassi import *
import apikey


# bot.api.call("sendMessage", {"chat_id": chat.id, "text": 'Testo Del messaggio', "parse_mode": "HTML", "reply_markup": '{"keyboard": [["text": "Testo"]], "one_time_keyboard": false, "resize_keyboard": true}'})

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
            "Benvenuto " + s[
                scU].nome + "\nDa ora in poi quando troverò un nuovo voto sul registro ti invierò un messaggio\n\nSe il login dovesse fallire ridai il comando /start\n\nI tuoi dati sono al sicuro! Username e Password vengono criptati appena li inserisci\n\nNel caso qualche materia non venisse abbreviata contattami\n\nBot progettato da Giovanni Casari (@infopz)")
        chat.send("Inserisci il tuo username del registro:")
        s[scU].statusLogin = 1
    shared['user'] = s


@bot.command('load')
def loadCommand(chat, message, shared, bot):
    if message.sender.username == 'infopz':
        loadDati(shared)
        s = shared['user']
        n = 0
        for i in s:
            print("Load " + str(n) + ": " + i.nome)
            n += 1
        chat.send('Dati Caricati - Utenti:' + str(n))
    else:
        chat.send("Solo @infopz e' autorizzato ad eseguire questo comando")


@bot.command('change')
def changeCommand(chat, message, shared, args):
    s = shared['user']
    scU = shared['cUs']
    if not args or len(args) != 2:
        bot.api.call("sendMessage", {
            "chat_id": s[scU].chat_id,
            "text": 'Utilizza questo comando se devi cambiare username e password memorizzati nel bot. \n`/change newUser newPassword`',
            "parse_mode": "Markdown",
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
                "chat_id": s[scU].chat_id, "text": 'Dati di login corretti, puoi iniziare ad usare il bot!',
                "parse_mode": "Markdown",
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
    if message.sender.username == 'infopz':
        s = shared['user']
        i = int(args[0])
        print("User " + str(i) + " " + s[i].nome + " deleted")
        chat.send("User " + str(i) + " " + s[i].nome + " deleted")
        del s[i]
        shared['user'] = s
        saveDati(shared)
    else:
        s = shared['user']
        scu = shared['sCu']
        cID = s[scu].chat_id
        bot.api.call("sendMessage", {
            "chat_id": cID,
            "text": "Solo @infopz e' autorizzato ad eseguire questo comando", "parse_mode": "Markdown",
            "reply_markup": '{"keyboard": [[{"text": "Voti per materia"}, {"text":"Voti per data"}], [{"text": "Medie"}, {"text": "Voti 1°Quad"}]], "one_time_keyboard": false, "resize_keyboard": true}'
        })


@bot.command('all')
def allCommand(chat, message, shared):
    s = shared['user']
    scU = shared['cUs']
    if message.sender.username != 'infopz':
        bot.api.call("sendMessage", {
            "chat_id": s[scU].chat_id,
            "text": "Solo @infopz e' autorizzato ad eseguire questo comando", "parse_mode": "Markdown",
            "reply_markup": '{"keyboard": [[{"text": "Voti per materia"}, {"text":"Voti per data"}], [{"text": "Medie"}, {"text": "Voti 1°Quad"}]], "one_time_keyboard": false, "resize_keyboard": true}'
        })
        return
    m = "Nuova comunicazione! \n" + message.text[5:]
    for i in s:
        try:
            bot.api.call("sendMessage", {
                "chat_id": i.chat_id,
                "text": m, "parse_mode": "Markdown",
                "reply_markup": '{"keyboard": [[{"text": "Voti per materia"}, {"text":"Voti per data"}], [{"text": "Medie"}, {"text": "Voti 1°Quad"}]], "one_time_keyboard": false, "resize_keyboard": true}'
            })
            print("Comunicazione inviata a " + str(i.nome))
        except Exception:
            print("Error with sending the comunication")


def voteCommand(chat, message, shared):
    s = shared['user']
    scU = shared['cUs']
    sendTyping(s[scU].chat_id)
    try:
        s[scU].aggiornavoti()
        msg = ''
        if len(s[scU].voti) == 0:
            msg = 'Non hai ancora nessun voto nel secondo quadrimestre'
        else:
            msg = s[scU].printvoti()
        bot.api.call("sendMessage", {
            "chat_id": s[scU].chat_id, "text": msg, "parse_mode": "Markdown",
            "reply_markup": '{"keyboard": [[{"text": "Voti per materia"}, {"text":"Voti per data"}], [{"text": "Medie"}, {"text": "Voti 1°Quad"}]], "one_time_keyboard": false, "resize_keyboard": true}'
        })
    except Exception as e:
        bot.api.call("sendMessage", {
            "chat_id": s[scU].chat_id,
            "text": "Errore nel login\nDai il comando /start e riprova\nNel caso il problema si dovesse ripresentare contatta @infopz",
            "parse_mode": "Markdown",
            "reply_markup": '{"keyboard": [[{"text": "Voti per materia"}, {"text":"Voti per data"}], [{"text": "Medie"}, {"text": "Voti 1°Quad"}]], "one_time_keyboard": false, "resize_keyboard": true}'
        })
        print("Error voteCommand - User " + s[scU].nome + " - " + str(e))
    shared['user'] = s
    saveDati(shared)


def votiMateria(chat, message, shared):
    s = shared['user']
    scU = shared['cUs']
    sendTyping(s[scU].chat_id)
    try:
        msg = ''
        voti = s[scU].votipermateria()
        if len(voti) == 0:
            msg = 'Non hai ancora nessun voto nel secondo quadrimestre'
        else:
            msg = "Ecco i tuoi Voti\n"
            mat = ''
            for i in voti:
                if i.materia != mat:
                    msg += '\n'
                mat = i.materia
                msg += RiduciNome(i.materia.upper()) + " - " + i.tipo + " - "+ i.data +" - *" + i.v + '*\n'
        bot.api.call("sendMessage", {
            "chat_id": s[scU].chat_id, "text": msg, "parse_mode": "Markdown",
            "reply_markup": '{"keyboard": [[{"text": "Voti per materia"}, {"text":"Voti per data"}], [{"text": "Medie"}, {"text": "Voti 1°Quad"}]], "one_time_keyboard": false, "resize_keyboard": true}'
        })
    except Exception as e:
        bot.api.call("sendMessage", {
            "chat_id": s[scU].chat_id,
            "text": "Errore nel login\nDai il comando /start e riprova\nNel caso il problema si dovesse ripresentare contatta @infopz",
            "parse_mode": "Markdown",
            "reply_markup": '{"keyboard": [[{"text": "Voti per materia"}, {"text":"Voti per data"}], [{"text": "Medie"}, {"text": "Voti 1°Quad"}]], "one_time_keyboard": false, "resize_keyboard": true}'
        })
        print("Error voteCommand - User " + s[scU].nome + " -")


def medieCommand(chat, message, shared):
    s = shared['user']
    scU = shared['cUs']
    sendTyping(s[scU].chat_id)
    try:
        m = s[scU].findmedie()
        msg = ""
        if len(m) == 0:
            msg = "Non hai ancora nessun voto nel secondo quadrimestre"
        else:
            for i in m:
                msg += RiduciNome(i.materia[1:]) + " - " + i.tipo + " - *" + i.v + '*\n'
        bot.api.call("sendMessage", {
            "chat_id": s[scU].chat_id, "text": msg, "parse_mode": "Markdown",
            "reply_markup": '{"keyboard": [[{"text": "Voti per materia"}, {"text":"Voti per data"}], [{"text": "Medie"}, {"text": "Voti 1°Quad"}]], "one_time_keyboard": false, "resize_keyboard": true}'
        })
    except Exception as e:
        bot.api.call("sendMessage", {
            "chat_id": s[scU].chat_id,
            "text": "Errore nel login\nDai il comando /start e riprova\nNel caso il problema si dovesse ripresentare contatta @infopz",
            "parse_mode": "Markdown",
            "reply_markup": '{"keyboard": [[{"text": "Voti per materia"}, {"text":"Voti per data"}], [{"text": "Medie"}, {"text": "Voti 1°Quad"}]], "one_time_keyboard": false, "resize_keyboard": true}'
        })
        print("Error voteCommand - User " + s[scU].nome + " - " + str(e))


def voti1q(chat, message, shared):
    s = shared['user']
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
            msg += RiduciNome(i.materia.upper()) + " - " + i.tipo + " - " + i.data + " - *" + i.v + '*\n'
        bot.api.call("sendMessage", {
            "chat_id": s[scU].chat_id, "text": msg, "parse_mode": "Markdown",
            "reply_markup": '{"keyboard": [[{"text": "Voti per materia"}, {"text":"Voti per data"}], [{"text": "Medie"}, {"text": "Voti 1°Quad"}]], "one_time_keyboard": false, "resize_keyboard": true}'
        })
    except Exception as e:
        bot.api.call("sendMessage", {
            "chat_id": s[scU].chat_id,
            "text": "Errore nel login\nDai il comando /start e riprova\nNel caso il problema si dovesse ripresentare contatta @infopz",
            "parse_mode": "Markdown",
            "reply_markup": '{"keyboard": [[{"text": "Voti per materia"}, {"text":"Voti per data"}], [{"text": "Medie"}, {"text": "Voti 1°Quad"}]], "one_time_keyboard": false, "resize_keyboard": true}'
        })
        print("Error voteCommand - User " + s[scU].nome + " - " + str(e))


def prDataAll(s):
    for i in s:
        print("n:" + i.nome + " id:" + str(i.chat_id) + " u:" + str(i.userF) + " p:" + str(i.passF) + " " + str(
            i.statusLogin))


def start1(chat, message, shared):
    s = shared['user']
    scU = shared['cUs']
    msg = message.text + 'aaaa'
    if msg.isalnum():
        us = b64encode(msg.encode('ascii')).decode('ascii')
        s[scU].setuser(us)
        s[scU].statusLogin = 2
        shared['user'] = s
        chat.send('Ora inserisci la password')
    else:
        chat.send('Username non valido, riprova')


def start2(chat, message, shared):
    s = shared['user']
    scU = shared['cUs']
    if message.text.isprintable():
        pw = b64encode(message.text.encode('ascii')).decode('ascii')
        s[scU].setpass(pw)
        if s[scU].checklogin():
            bot.api.call("sendMessage", {
                "chat_id": s[scU].chat_id, "text": 'Dati di login corretti, puoi iniziare ad usare il bot!',
                "parse_mode": "Markdown",
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
    else:
        chat.send('Password non valida, riprova')


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
    h = int(strftime("%H", gmtime())) + 1
    if h >= 22 or h <= 7:
        print("NOTime "+str(h))
        return
    else:
        print("Time " + str(h))
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
            print("Error NewVoti - User " + str(i.nome))
        sleep(17)
    shared['user'] = utenti
    if not shared['firstTimer']:
        saveDati(shared)
    shared['firstTimer'] = False

@bot.timer(5)
def resetControlNumber(shared):
    shared['maxMess']=0


@bot.before_processing
def bef_proc(chat, message, shared):
    nom = ''
    if message.sender.username != None:
        nom = message.sender.username
    else:
        nom = message.sender.first_name
    print("Message from: " + nom)
    s = shared['user']
    scU = shared['cUs']
    shared['maxMess']+=1
    if shared['maxMess']>4:
        print('Error - Too Much Message')
        return
    if message.text != '/load':
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
                scU = len(s) - 1
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
        elif message.text == 'Voti 1°Quad':
            voti1q(chat, message, shared)


@bot.prepare_memory
def prepare_memory(shared):
    shared['firstTimer'] = True
    shared['cUs'] = 0
    shared['user'] = list()
    shared['maxMess'] = 0


if __name__ == "__main__":
    bot.run()
