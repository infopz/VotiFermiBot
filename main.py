#!/usr/bin/python3
import botogram
from bs4 import BeautifulSoup
from base64 import b64encode, b64decode
import requests
import pickle

import apikey

#bot.api.call("sendMessage", {"chat_id": chat.id, "text": 'Testo Del messaggio', "parse_mode": "HTML", "reply_markup": '{"keyboard": [["text": "Testo"]], "one_time_keyboard": false, "resize_keyboard": true}'})

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
    self.lastV = voto()
    self.voti = list()
    self.statusLogin=0
  
  def setUser(self, u):
    self.userF = u
  
  def setPass(self, p):
    self.passF = p

  def aggiornaVoti(self, data=True, Lv=False):
    user = b64decode(self.userF).decode('ascii')
    user = user[0:-4]
    pw = b64decode(self.passF).decode('ascii')
    payload = {'ob_user': user, 'ob_password': pw}
    s = requests.Session()
    s.post('http://www.fermi.mo.it/~loar/AssenzeVotiStudenti/elabora_PasswordStudenti.php', data=payload)
    r = s.post('http://www.fermi.mo.it/~loar/AssenzeVotiStudenti/VotiDataOrdinati1Q.php')
    if not data:
      r = s.post('http://www.fermi.mo.it/~loar/AssenzeVotiStudenti/VotiStudente1Q.php')
    soup = BeautifulSoup(r.text, "html.parser")
    table = soup.find("table", {"class": "TabellaVoti"})
    self.voti=list()
    for row in table.find_all('tr'):
      col = row.find_all('td')
      try:
        if col[1].text[0].isdigit():
          vot = voto(col[1].text, RiduciNome(col[0].text), col[3].text)
          self.voti.append(vot)
      except Exception:
        continue
    if Lv: #opzione per aggiornare anche l'ultimo voto
      self.lastV = self.voti[0]

  def findMedie(self):
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
        SC=str(col[22].text).strip()
        OR=str(col[25].text).strip()
        PR=str(col[28].text).strip()
        GR=str(col[31].text).strip()
        if SC!="":
          med.append(voto(SC, col[0].text, "Scritto"))
        if OR!="":
          med.append(voto(OR, col[0].text, "Orale"))
        if PR!="":
          med.append(voto(PR, col[0].text, "Pratico"))
        if GR!="":
          med.append(voto(GR, col[0].text, "Grafico"))
      except Exception as e:
        pass
    return med

  def checkNewVote(self):
    return not (self.lastV == self.voti[0])

  def printNewVotes(self):
    msg=''
    for i in self.voti:
      if not (self.lastV == i):
        msg+=i.v+' - '+i.materia+'\n'
      else:
        break
    self.lastV = self.voti[0]
    return msg

  def printVoti(self):
    msg="Ecco i tuoi Voti\n"
    """for i in self.voti:
      sp = "    "
      sp2="  "
      if float(i.v)%1 != 0: 
        sp=" "
      if float(i.v) == 10:
        sp="  "
      if len(i.materia) == 3:
        if i.materia == 'TPS':
          pass
        else:
          sp2="     "
      elif len(i.materia) == 5:
        sp2=" "
      msg+=str(i.v)+sp+"- "+i.materia+sp2+"- "+i.tipo+"\n"""
    for i in self.voti:
      msg+=RiduciNome(i.materia).upper()+" - "+i.tipo+" - *"+i.v+'*\n'
    return msg

  def checkLogin(self):
    if self.userF == '' or self.passF == '':
      return False
    user = b64decode(self.userF).decode('ascii')
    user = user[0:-4]
    pw = b64decode(self.passF).decode('ascii')
    payload = {'ob_user': user, 'ob_password': pw}
    s = requests.Session()
    s.post('http://www.fermi.mo.it/~loar/AssenzeVotiStudenti/elabora_PasswordStudenti.php', data=payload)
    r = s.post('http://www.fermi.mo.it/~loar/AssenzeVotiStudenti/VotiDataOrdinati1Q.php')
    if r.text[-13:]=="doesn't exist":
      return False
    else:
      return True


def RiduciNome(m):
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
  elif m=='SISTEMI E RETI':
    m='Sist'
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











bot = botogram.create(apikey.botKey)

@bot.command('start')
def hellocomm(chat, message, shared):
  scU=shared['cUs']
  if scU.userF!='' and scU.passF!='':
    msg='Ciao, '+scU.nome+', avevi gia inserito i tuoi dati e sono stati caricati! Inizia a usare il bot!'
    bot.api.call("sendMessage", {"chat_id": scU.chat_id, "text": msg, "parse_mode": "Markdown", "reply_markup": '{"keyboard": [[{"text": "Voti per materia"}],[{"text":"Voti per data"}, {"text": "Medie"}]], "one_time_keyboard": false, "resize_keyboard": true}'})
    scU.statusLogin=0
  else:
    chat.send("Benvenuto "+scU.nome+"\nNel caso troverò un nuovo voto sul registro ti invierò un messaggio\n\nNel caso il login fallisse ridai il comando /start\n\nI tuoi dati sono al sicuro! Username e Password vengono criptati appena li inserisci\n\nNel caso qualche materia non venisse abbreviata contattatemi\n\nBot progettato da Giovanni Casari (@infopz)")
    chat.send("Inserisci il tuo username del registro:")
    scU.statusLogin = 1
  shared['cUs']=scU

@bot.command('vote')
def voteCommand(chat, message, shared):
  scU=shared['cUs']
  scU.aggiornaVoti(True, True)
  bot.api.call("sendMessage", {"chat_id": scU.chat_id, "text": scU.printVoti(), "parse_mode": "Markdown", "reply_markup": '{"keyboard": [[{"text": "Voti per materia"}],[{"text":"Voti per data"}, {"text": "Medie"}]], "one_time_keyboard": false, "resize_keyboard": true}'})
  #chat.send(s.printVoti())
  shared['cUs']=scU
  saveDati(shared)

@bot.command('load')
def loadCommand(chat, message, shared):
  if message.sender.username=='infopz':
    loadDati(shared)
    s=shared['user']
    for i in s:
      print("Load: "+i.nome)
    chat.send('Dati Caricati')
  else:
    chat.send("Solo @infopz e' autorizzato ad eseguire questo comando")

@bot.command('change')
def chanceCommand(chat, message, shared, args):
  s=shared['cUs']
  msg = args[0]+'aaaa'
  us=b64encode(msg.encode('ascii')).decode('ascii')#cripto il nome utente non appena viene immessa
  s.setUser(us)
  pw=b64encode(args[1].encode('ascii')).decode('ascii')#cripto la password non appena viene immessa
  s.setPass(pw)
  if s.checkLogin():
    bot.api.call("sendMessage", {"chat_id": s.chat_id, "text": 'Dati di login corretti, puoi iniziare ad usare il bot!', "parse_mode": "Markdown", "reply_markup": '{"keyboard": [[{"text": "Voti per materia"}],[{"text":"Voti per data"}, {"text": "Medie"}]], "one_time_keyboard": false, "resize_keyboard": true}'})
    s.aggiornaVoti(True, True)
    s.statusLogin=0
  else:
    chat.send('Dati di login non corretti')
    chat.send('Immetti il tuo username')
    s.statusLogin=1
  shared['cUs']=s

def votiMateria(chat, message, shared):
  scU=shared['cUs']
  scU.aggiornaVoti(False, False)
  msg=scU.printVoti()
  bot.api.call("sendMessage", {"chat_id": scU.chat_id, "text": msg, "parse_mode": "Markdown", "reply_markup": '{"keyboard": [[{"text": "Voti per materia"}],[{"text":"Voti per data"}, {"text": "Medie"}]], "one_time_keyboard": false, "resize_keyboard": true}'})

def medieCommand(chat, message, shared):
  scU=shared['cUs']
  m=scU.findMedie()
  msg=""
  for i in m:
    msg+=RiduciNome(i.materia[1:])+" - "+i.tipo+" "+i.v+'\n'
  bot.api.call("sendMessage", {"chat_id": scU.chat_id, "text": msg, "parse_mode": "Markdown", "reply_markup": '{"keyboard": [[{"text": "Voti per materia"}],[{"text":"Voti per data"}, {"text": "Medie"}]], "one_time_keyboard": false, "resize_keyboard": true}'})

def prDataAll(s, scU):
  for i in s:
    print("n:"+i.nome+" id:"+str(i.chat_id)+" u:"+str(i.userF)+" p:"+str(i.passF)+" "+str(i.statusLogin))
  print("CU: n:"+scU.nome+" id:"+str(scU.chat_id)+" u:"+str(scU.userF)+" p:"+str(scU.passF)+" "+str(scU.statusLogin))

def start1(chat, message, shared):
  s=shared['cUs']
  msg = message.text+'aaaa'
  us=b64encode(msg.encode('ascii')).decode('ascii')#cripto il nome utente non appena viene immessa
  s.setUser(us)
  s.statusLogin=2
  shared['cUs']=s
  chat.send('Ora inserisci la password')

def start2(chat, message, shared):
  s=shared['cUs']
  pw=b64encode(message.text.encode('ascii')).decode('ascii')#cripto la password non appena viene immessa
  s.setPass(pw)
  if s.checkLogin():
    bot.api.call("sendMessage", {"chat_id": s.chat_id, "text": 'Dati di login corretti, puoi iniziare ad usare il bot!', "parse_mode": "Markdown", "reply_markup": '{"keyboard": [[{"text": "Voti per materia"}],[{"text":"Voti per data"}, {"text": "Medie"}]], "one_time_keyboard": false, "resize_keyboard": true}'})
    s.aggiornaVoti(True, True)
    s.statusLogin=0
  else:
    chat.send('Dati di login non corretti')
    chat.send('Immetti il tuo username')
    s.statusLogin=1
  shared['cUs']=s
  

def saveDati(shared):
  s=shared['user']
  scU = shared['cUs']
  n=-1
  for i in s:
    n+=1
    if scU.chat_id == i.chat_id:
      break
  if n!=-1:
    s[n]=scU
  f=open('user.txt', 'wb')
  pickle.dump(s, f)
  f.close()
  shared['user']=s
  shared['cUs']=scU

def loadDati(shared):
  s=shared['user']
  scU=shared['cUs']
  f=open('user.txt', 'rb')
  s=pickle.load(f)
  shared['cUs']=scU
  shared['user']=s
  shared['load']=True

@bot.timer(300)
def vediMod(bot, shared):
  print('Timer')
  s = shared['user']
  for i in range(0, len(s)):
    try:
      s[i].aggiornaVoti(Lv=False)
      if s[i].checkNewVote():
        print('NewVotesFound '+s[i].nome)
        nv="Ehi, "+s[i].nome+", hai dei nuovi voti sul registro:\n"+s[i].printNewVotes()
        bot.chat(s[i].chat_id).send(nv)
        s[i].aggiornaVoti(LV=True)
    except Exception as e:
        pass
  shared['user']=s
  if not shared['firstTimer']:
    saveDati(shared)
  shared['firstTimer']=False

@bot.before_processing
def processM(chat, message, shared):
  print("@"+message.sender.username)
  s=shared['user']
  scU = shared['cUs']
  if chat.id != scU.chat_id and not shared['load']:
    #salvataggio vecchio currentUser
    n=-1
    for i in s:
      n+=1
      if scU.chat_id == i.chat_id:
        break
    try:
      if n!=-1:
        s[n]=scU
    except Exception:
      pass
    #inserimento nuovo current user
    newUser=True
    for i in s:
      if chat.id == i.chat_id:
        scU=i
        newUser=False
        break
    if newUser:
      nU=utente(chat.id, message.sender.first_name)
      print('NewUser: '+nU.nome)
      scU=nU
  elif shared['load']:
    for i in s:
      if i.chat_id == scU.chat_id:
        scU = i
        break
    shared['load']=False
  shared['user']=s
  shared['cUs']=scU
  if scU.statusLogin==1:
    start1(chat, message, shared)
  elif scU.statusLogin==2:
    start2(chat, message, shared)
  elif message.text=='Voti per materia':
    votiMateria(chat, message, shared)
  elif message.text=='Voti per data':
    voteCommand(chat, message, shared)
  elif message.text=='Medie':
    medieCommand(chat, message, shared)


@bot.prepare_memory
def prepare_memory(shared):
    shared['firstTimer']=True
    shared['cUs']=utente();
    shared['user']=list()
    shared['load']=False

if __name__ == "__main__":
  bot.run()

