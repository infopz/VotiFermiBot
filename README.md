# VotiFermiBot
A bot for all Enrico Fermi's students

Un ringraziamento speciale a Lorenzo Balugani e a Stefano Pigozzi che hanno aiutato alla scrittura di questo codice e anche a tutti gli improvvisati beta-tester miei compagni di classe.

## Funzioni
Ogni 2 ore (il tempo verra' cambiato in periodo di scrutini) il bot controlla la presenza di nuovo voti, nel caso ne trovasse uno, invia un messaggio contenente i dati del nuovo voto.
Inoltre permette la visualizzazione dei propri voti ordinati per materia o per data, e volendo permette anche la visualizzazione delle medie delle varie materie divise in scritto, orale e pratico.

## Comandi
Il bot e' programmato per rispondere ad altri comandi oltre ai messaggi utilizzabili dalla tastiera personalizzata:

* `/change newUsername newPassword` Permette di cambiare il proprio username e password nel caso venissero modificati
* `/load` Carica i dati presenti nel file `user.txt` sostituendo quelli presenti nel programma
* `/timer` Chiama la funzione di ricerca dei nuovi voti, indipendetemente dal tempo trascorso dall'ultima ricerca

I comandi `/load` e `/timer` possono essere chiamati solamente dal proprietario del programma


Un ringraziamento a Pietro Albini per la creazione di Botogram su cui si basa questo bot (https://botogram.pietroalbini.org/)
