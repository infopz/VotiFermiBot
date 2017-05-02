#!/usr/bin/python3
import botogram
from bs4 import BeautifulSoup
from base64 import b64encode, b64decode
from time import gmtime, strftime, sleep
import requests
import pickle
import traceback

from class_file import *
import apikey


# bot.api.call("sendMessage", {"chat_id": chat.id, "text": 'Testo Del messaggio', "parse_mode": "HTML", "reply_markup": '{"keyboard": [["text": "Testo"]], "one_time_keyboard": false, "resize_keyboard": true}'})

bot = botogram.create(apikey.botKey)


@bot.command('start')
def start_command(chat, message, shared):
    students = shared['user']
    user_index = shared['cUs']
    if students[user_index].password != '' and students[user_index].check_login():
        msg = 'Ciao, ' + students[user_index].nome.replace('_', '\_') + ', avevi gia inserito i tuoi dati e sono stati caricati! Inizia a usare il bot!'
        bot.api.call("sendMessage", {
            "chat_id": students[user_index].chat_id,
            "text": msg,
            "parse_mode": "Markdown",
            "reply_markup": '{"keyboard": [[{"text": "Voti per materia"}, {"text":"Voti per data"}], [{"text": "Medie"}, {"text": "Voti 1°Quad"}]], "one_time_keyboard": false, "resize_keyboard": true}'
        })
        students[user_index].statusLogin = 0
    else:
        chat.send(
            "Benvenuto " + students[
                user_index].nome.replace('_', '\_') + "\nDa ora in poi quando troverò un nuovo voto sul registro ti invierò un messaggio\n\nSe il login dovesse fallire ridai il comando /start\n\nI tuoi dati sono al sicuro! Username e Password vengono criptati appena li inserisci\n\nNel caso qualche materia non venisse abbreviata contattami\n\nBot progettato da Giovanni Casari (@infopz)")
        chat.send("Inserisci il tuo username del registro:")
        students[user_index].statusLogin = 1
    shared['user'] = students


@bot.command('load')
def load_command(chat, message, shared, bot):
    # FIXME: guarda l'user ID, mai l'username
    if message.sender.username == 'infopz':
        load_data(shared)
        students = shared['user']
        n = 0
        for student in students:
            print(f"Load {n}: {student.nome}")
            n+=1
        chat.send(f"Dati Caricati - Utenti: {len(students)}")
    else:
        chat.send("Solo @infopz e' autorizzato ad eseguire questo comando")


@bot.command('change')
def change_command(chat, message, shared, args):
    students = shared['user']
    user_index = shared['cUs']
    if not args or len(args) != 2:
        bot.api.call("sendMessage", {
            "chat_id": students[user_index].chat_id,
            "text": 'Utilizza questo comando se devi cambiare username e password memorizzati nel bot. \n`/change newUser newPassword`',
            "parse_mode": "Markdown",
            "reply_markup": '{"keyboard": [[{"text": "Voti per materia"}, {"text":"Voti per data"}], [{"text": "Medie"}, {"text": "Voti 1°Quad"}]], "one_time_keyboard": false, "resize_keyboard": true}'
        })
    else:
        msg = args[0] + 'aaaa'
        # FIXME: ti prego togli sta cosa
        us = b64encode(msg.encode('ascii')).decode('ascii')  # "cripto" il nome utente non appena viene immessa
        students[user_index].set_user(us)
        pw = b64encode(args[1].encode('ascii')).decode('ascii')  # "cripto" la password non appena viene immessa
        students[user_index].set_pass(pw)
        if students[user_index].check_login():
            bot.api.call("sendMessage", {
                "chat_id": students[user_index].chat_id, "text": 'Dati di login corretti, puoi iniziare ad usare il bot!',
                "parse_mode": "Markdown",
                "reply_markup": '{"keyboard": [[{"text": "Voti per materia"}, {"text":"Voti per data"}], [{"text": "Medie"}, {"text": "Voti 1°Quad"}]], "one_time_keyboard": false, "resize_keyboard": true}'
            })
            students[user_index].update_voti()
            students[user_index].statusLogin = 0
            log_write('CHANGE COMMAND: USER ' + students[user_index].nome, 'Cambio effettuato')
        else:
            chat.send('Dati di login non corretti')
            chat.send('Immetti il tuo username')
            students[user_index].statusLogin = 1
            log_write('CHANGE COMMAND: USER ' + students[user_index].nome, 'Dati non corretti')
    shared['user'] = students
    save_data(shared)


@bot.command('timer')
def timer_command(chat, message, shared, bot):
    if message.sender.username == 'infopz':
        check_updates(bot, shared)
    else:
        chat.send("Solo @infopz e' autorizzato ad eseguire questo comando")


@bot.command('del')
def del_command(chat, message, shared, args):
    if message.sender.username == 'infopz':
        students = shared['user']
        if args[0].isdigit():
            user_id = int(args[0])
            print(f"User {user_id} {students[user_id].nome} deleted")
            chat.send("User "+user_id+" "+students[user_id].nome.replace('_', '\_')+" deleted")
            del students[user_id]
            shared['user'] = students
            save_data(shared)
            log_write('USER DELETED', f'User {user_id}')
        else:
            chat.send('Ehi, coglione, devi mandarmi un numero, non una stringa\nSacripante!')
    else:
        students = shared['user']
        user_index = shared['sCu']
        chat_id = students[user_index].chat_id
        bot.api.call("sendMessage", {
            "chat_id": chat_id,
            "text": "Solo @infopz e' autorizzato ad eseguire questo comando",
            "parse_mode": "Markdown",
            "reply_markup": '{"keyboard": [[{"text": "Voti per materia"}, {"text":"Voti per data"}], [{"text": "Medie"}, {"text": "Voti 1°Quad"}]], "one_time_keyboard": false, "resize_keyboard": true}'
        })


@bot.command('all')
def all_command(chat, message, shared):
    students = shared['user']
    user_index = shared['cUs']
    if message.sender.username != 'infopz':
        bot.api.call("sendMessage", {
            "chat_id": students[user_index].chat_id,
            "text": "Solo @infopz e' autorizzato ad eseguire questo comando",
            "parse_mode": "Markdown",
            "reply_markup": '{"keyboard": [[{"text": "Voti per materia"}, {"text":"Voti per data"}], [{"text": "Medie"}, {"text": "Voti 1°Quad"}]], "one_time_keyboard": false, "resize_keyboard": true}'
        })
        return
    # FIXME: se uno scrive /all@infopzbot qui muore tutto
    m = "Nuova comunicazione! \n" + message.text[5:]
    for i in students:
        try:
            bot.api.call("sendMessage", {
                "chat_id": i.chat_id,
                "text": m,
                "parse_mode": "Markdown",
                "reply_markup": '{"keyboard": [[{"text": "Voti per materia"}, {"text":"Voti per data"}], [{"text": "Medie"}, {"text": "Voti 1°Quad"}]], "one_time_keyboard": false, "resize_keyboard": true}'
            })
            print("Comunicazione inviata a " + str(i.nome))
        except Exception:
            print("Error with sending the comunication")

@bot.command('help')
def help_command(chat, message):
    m = "Ecco i comandi che puoi usare:\n" \
        "  /start - Fai partire il Bot\n" \
        "  /change - Cambia lo user e password memorizzati\n" \
        "  /help - Visualizza questo messaggio\n" \
        "\n" \
        "Per qualsiasi informazione o problema contatta @infopz"
    bot.api.call("sendMessage", {
        "chat_id": chat.chat_id,
        "text": m,
        "parse_mode": "Markdown",
        "reply_markup": '{"keyboard": [[{"text": "Voti per materia"}, {"text":"Voti per data"}], [{"text": "Medie"}, {"text": "Voti 1°Quad"}]], "one_time_keyboard": false, "resize_keyboard": true}'
    })

def vote_command(chat, message, shared):
    students = shared['user']
    user_index = shared['cUs']
    set_typing(students[user_index].chat_id)
    try:
        students[user_index].update_voti(shared)
        if shared['badReq']:
            bot.api.call("sendMessage", {
                "chat_id": students[user_index].chat_id,
                "text": "Scusa se ci ho messo tanto ma il server del registro e' impallato",
                "parse_mode": "Markdown",
                "reply_markup": '{"keyboard": [[{"text": "Voti per materia"}, {"text":"Voti per data"}], [{"text": "Medie"}, {"text": "Voti 1°Quad"}]], "one_time_keyboard": false, "resize_keyboard": true}'
            })
        if len(students[user_index].voti) == 0:
            msg = 'Non hai ancora nessun voto nel secondo quadrimestre'
        else:
            msg = students[user_index].voti_string()
        bot.api.call("sendMessage", {
            "chat_id": students[user_index].chat_id,
            "text": msg,
            "parse_mode": "Markdown",
            "reply_markup": '{"keyboard": [[{"text": "Voti per materia"}, {"text":"Voti per data"}], [{"text": "Medie"}, {"text": "Voti 1°Quad"}]], "one_time_keyboard": false, "resize_keyboard": true}'
        })
    except Exception as e:
        bot.api.call("sendMessage", {
            "chat_id": students[user_index].chat_id,
            "text": "Errore nel login\n"
                    "Dai il comando /start e riprova\n"
                    "Nel caso il problema si dovesse ripresentare contatta @infopz",
            "parse_mode": "Markdown",
            "reply_markup": '{"keyboard": [[{"text": "Voti per materia"}, {"text":"Voti per data"}], [{"text": "Medie"}, {"text": "Voti 1°Quad"}]], "one_time_keyboard": false, "resize_keyboard": true}'
        })
        print(f"Error voteCommand - User {students[user_index].nome} {e}")
        log_write(f"VOTE COMMAND: USER: {students[user_index].nome}", traceback.format_exc())
    shared['user'] = students
    save_data(shared)


def voti_materia(chat, message, shared):
    students = shared['user']
    user_index = shared['cUs']
    set_typing(students[user_index].chat_id)
    try:
        voti = students[user_index].voti_per_materia()
        if len(voti) == 0:
            msg = 'Non hai ancora nessun voto nel secondo quadrimestre'
        else:
            msg = "Ecco i tuoi Voti\n"
            mat = ''
            for i in voti:
                if i.materia != mat:
                    msg += '\n'
                mat = i.materia
                msg += shorten_name(i.materia.upper()) + " - " + i.tipo + " - " + i.data + " - *" + i.voto + '*\n'
        bot.api.call("sendMessage", {
            "chat_id": students[user_index].chat_id, "text": msg, "parse_mode": "Markdown",
            "reply_markup": '{"keyboard": [[{"text": "Voti per materia"}, {"text":"Voti per data"}], [{"text": "Medie"}, {"text": "Voti 1°Quad"}]], "one_time_keyboard": false, "resize_keyboard": true}'
        })
    except Exception as e:
        bot.api.call("sendMessage", {
            "chat_id": students[user_index].chat_id,
            "text": "Errore nel login\nDai il comando /start e riprova\nNel caso il problema si dovesse ripresentare contatta @infopz",
            "parse_mode": "Markdown",
            "reply_markup": '{"keyboard": [[{"text": "Voti per materia"}, {"text":"Voti per data"}], [{"text": "Medie"}, {"text": "Voti 1°Quad"}]], "one_time_keyboard": false, "resize_keyboard": true}'
        })
        print(f"Error voteCommand - User {students[user_index].nome} -")
        log_write(f"MATERIE COMMAND: USER: {students[user_index].nome}", traceback.format_exc())


def medie_command(chat, message, shared):
    students = shared['user']
    user_index = shared['cUs']
    set_typing(students[user_index].chat_id)
    try:
        m = students[user_index].find_averages()
        msg = str()
        if len(m) == 0:
            msg = "Non hai ancora nessun voto nel secondo quadrimestre"
        else:
            for i in m:
                msg += shorten_name(i.materia[1:]) + " - " + i.tipo + " - *" + i.voto + '*\n'
        bot.api.call("sendMessage", {
            "chat_id": students[user_index].chat_id,
            "text": msg,
            "parse_mode": "Markdown",
            "reply_markup": '{"keyboard": [[{"text": "Voti per materia"}, {"text":"Voti per data"}], [{"text": "Medie"}, {"text": "Voti 1°Quad"}]], "one_time_keyboard": false, "resize_keyboard": true}'
        })
    except Exception as e:
        bot.api.call("sendMessage", {
            "chat_id": students[user_index].chat_id,
            "text": "Errore nel login\nDai il comando /start e riprova\nNel caso il problema si dovesse ripresentare contatta @infopz",
            "parse_mode": "Markdown",
            "reply_markup": '{"keyboard": [[{"text": "Voti per materia"}, {"text":"Voti per data"}], [{"text": "Medie"}, {"text": "Voti 1°Quad"}]], "one_time_keyboard": false, "resize_keyboard": true}'
        })
        print(f"Error voteCommand - User {students[user_index].nome} - {e}")
        log_write(f"MEDIE COMMAND: USER: {students[user_index].nome}", traceback.format_exc())


def voti_primo_quadrimestre(chat, message, shared):
    students = shared['user']
    user_index = shared['cUs']
    try:
        set_typing(students[user_index].chat_id)
        voti = students[user_index].voti_primo_quadrimestre()
        msg = "Ecco i tuoi voti del primo quadrimestre\n"
        materia = ''
        for voto in voti:
            if voto.materia != materia:
                msg += '\n'
            materia = voto.materia
            msg += f"{shorten_name(voto.materia.upper())} - {voto.tipo} - {voto.data} - *{voto.voto}*\n"
        bot.api.call("sendMessage", {
            "chat_id": students[user_index].chat_id,
            "text": msg,
            "parse_mode": "Markdown",
            "reply_markup": '{"keyboard": [[{"text": "Voti per materia"}, {"text":"Voti per data"}], [{"text": "Medie"}, {"text": "Voti 1°Quad"}]], "one_time_keyboard": false, "resize_keyboard": true}'
        })
    except Exception as e:
        bot.api.call("sendMessage", {
            "chat_id": students[user_index].chat_id,
            "text": "Errore nel login\n"
                    "Dai il comando /start e riprova\n"
                    "Nel caso il problema si dovesse ripresentare contatta @infopz",
            "parse_mode": "Markdown",
            "reply_markup": '{"keyboard": [[{"text": "Voti per materia"}, {"text":"Voti per data"}], [{"text": "Medie"}, {"text": "Voti 1°Quad"}]], "one_time_keyboard": false, "resize_keyboard": true}'
        })
        print(f"Error voteCommand - User {students[user_index].nome} - {e}")
        log_write(f"1 QUAD COMMAND: USER: {students[user_index].nome}", traceback.format_exc())


def start1(chat, message, shared):
    students = shared['user']
    user_index = shared['cUs']
    msg = message.text + 'aaaa'
    if msg.isalnum():
        # FIXME: pls
        username = b64encode(msg.encode('ascii')).decode('ascii')
        students[user_index].set_user(username)
        students[user_index].statusLogin = 2
        shared['user'] = students
        chat.send('Ora inserisci la password')
        log_write('START1: USER ' + students[user_index].nome)
    else:
        chat.send('Username non valido, riprova')


def start2(chat, message, shared):
    students = shared['user']
    user_index = shared['cUs']
    if message.text.isprintable():
        # FIXME: dai
        password = b64encode(message.text.encode('ascii')).decode('ascii')
        students[user_index].set_pass(password)
        if students[user_index].check_login():
            bot.api.call("sendMessage", {
                "chat_id": students[user_index].chat_id, "text": 'Dati di login corretti, puoi iniziare ad usare il bot!',
                "parse_mode": "Markdown",
                "reply_markup": '{"keyboard": [[{"text": "Voti per materia"}, {"text":"Voti per data"}], [{"text": "Medie"}, {"text": "Voti 1°Quad"}]], "one_time_keyboard": false, "resize_keyboard": true}'
            })
            students[user_index].update_voti(shared)
            students[user_index].statusLogin = 0
        else:
            chat.send('Dati di login non corretti')
            chat.send('Immetti il tuo username')
            students[user_index].statusLogin = 1
        shared['user'] = students
        save_data(shared)
    else:
        chat.send('Password non valida, riprova')


def save_data(shared):
    s = shared['user']
    f = open('user.txt', 'wb')
    pickle.dump(s, f)
    f.close()
    shared['user'] = s


def load_data(shared):
    s = shared['user']
    f = open('user.txt', 'rb')
    s = pickle.load(f)
    shared['user'] = s
    print("LoadDati")


@bot.timer(7200) #FIXME la lista copiata
def check_updates(bot, shared):
    hour = int(strftime("%H", gmtime())) + 1
    if hour >= 20 or hour <= 5:
        print(f"NO Time {hour}")
        return
    print("Time " + str(hour))
    students = shared['user']
    if shared['reverseTimer']: # reverso la lista cosi caronte non mi risponde sempre su quei 5 utenti
        students.reverse()
    log_write(f"Timer Start {str(shared['reverseTimer'])}")
    number_badRes = 0
    for i, student in enumerate(students):
        try:
            old_voti = student.voti
            student.update_voti(shared)
            if shared['badReq']:
                number_badRes += 1
                continue
            new_voti = voti_diff(old_voti, student.voti)
            if len(new_voti) > 0:
                print(f"NewVotesFound {student.nome} {len(new_voti)}")
                msg = "Ehi, "+student.nome.replace('_', '\_')+", hai dei nuovi voti sul registro:\n"
                for voto in new_voti:
                    msg += f"Hai preso *{voto.voto}* in {voto.materia} {voto.tipo}\n"
                bot.chat(student.chat_id).send(msg)
        except Exception as e:
            print(f"Error NewVoti - User {student.nome} {e}")
            log_write('TIMER ERROR: USER ' + student.nome, traceback.format_exc())
        if i % 5 == 4: # per non sovraccaricare il server
            sleep(30)
        sleep(2)
    if number_badRes != 0:
        bot.chat(20403805).send(f'Salve Smilzo, {str(number_badRes)} Bad Response da caronte')
    if shared['reverseTimer']:
        students.reverse()
    shared['reverseTimer'] = not shared['reverseTimer']
    shared['user'] = students
    if not shared['firstTimer']:
        save_data(shared)
    log_write("Timer End")
    shared['firstTimer'] = False

@bot.timer(300)
def reset_blocked(shared):
    b = shared['lock']
    if b:
        print(f'User {str(b)} Unlocked')
    b = list()
    shared['lock'] = b

@bot.timer(5)
def reset_control_number(shared):
    shared['maxMess']=0


@bot.before_processing
def before_processing(chat, message, shared):
    b = shared['lock']
    if chat.id in b:
        return True
    if message.sender.username is not None:
        name = message.sender.username
    else:
        name = message.sender.first_name
    print("Message from: " + name)
    students = shared['user']
    user_index = shared['cUs']
    shared['maxMess'] += 1
    if shared['maxMess'] > 4:
        chat.send('Hai mandato troppi messaggi, sei stato bloccato per un po di tempo')
        b = shared['lock']
        b.append(chat.id)
        shared['lock'] = b
        print(f'Too Many Messages - User {name} Blocked')
        shared['maxMess'] = 0
        return True
    if message.text != '/load':
        if chat.id != students[user_index].chat_id:
            for student in range(0, len(students)):
                if chat.id == students[student].chat_id:
                    user_index = student
                    break
            else: # inserimento nuovo current user
                new_user = Utente(chat.id, name)
                print('NewUser: ' + new_user.nome)
                students.append(new_user)
                user_index = len(students) - 1
                log_write('NEW USER ' + new_user.nome)
                if message.text != '/start': #nuovo user che scrive un messaggio alla cazzo, lo rimanda a start
                    start_command(chat, message, shared)
        shared['user'] = students
        shared['cUs'] = user_index
        if students[user_index].statusLogin == 1:
            start1(chat, message, shared)
        elif students[user_index].statusLogin == 2:
            start2(chat, message, shared)
        elif message.text == 'Voti per materia':
            voti_materia(chat, message, shared)
        elif message.text == 'Voti per data':
            vote_command(chat, message, shared)
        elif message.text == 'Medie':
            medie_command(chat, message, shared)
        elif message.text == 'Voti 1°Quad':
            voti_primo_quadrimestre(chat, message, shared)


@bot.prepare_memory
def prepare_memory(shared):
    shared['firstTimer'] = True
    shared['cUs'] = 0
    shared['user'] = list()
    shared['maxMess'] = 0
    shared['badReq'] = list()
    shared['lock'] = list()
    shared['reverseTimer'] = False


if __name__ == "__main__":
    bot.run()
