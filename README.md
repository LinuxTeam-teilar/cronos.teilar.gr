Περιγραφή
=========

Η παρούσα ιστοσελίδα δημιουργήθηκε από φοιτητές για φοιτητές (του ΤΕΙ Λάρισας
πάντα). Καθώς όλοι γνωρίζουμε, μέσα από διάφορα sites και υπηρεσίες, η
πληροφορία διασκορπίζεται και χάνεται. Από την αρχή της φοίτησής μας μας
φαινόταν εξαιρετικά δύσκολο να παρακολουθήσουμε τις ανακοινώσεις, και το
χειρότερο, να μην μπορούμε όταν κάποια ιστοσελίδα ήταν πεσμένη (και ιδιαίτερα
σε περίοδο εξεταστικής).

Η υπηρεσία Cronos δημιουργήθηκε για να καλύψει αυτό το κενό ανάμεσα από τα
sites του ΤΕΙ Λάρισας. Ο σκοπός της παρούσας υπηρεσίας είναι να προσφέρει όλες
τις ανακοινώσεις όλων των σχολών/τμημάτων/καθηγητών/ιστοσελίδων, καθώς και
βαθμολογίες, δηλώσεις, λίστα καθηγητών, αναζήτηση βιβλιοθήκης και άλλες
πληροφορίες, προσωπικές και μη, που βρίσκονται διασκορπισμένες. Ένα ακόμα πολύ
σημαντικό στοιχείο είναι ότι παρέχεται ενιαίο RSS Feed όλων αυτών των
ανακοινώσεων.

[Περισσότερες πληροφορίες καθώς και συντελεστές της σελίδας](http://cronos.teilar.gr/about)

Ανάπτυξη
========

Ιδέες και σφάλματα
--------------------

Λίστα με ιδέες και σφάλματα βρίσκονται στον [issue tracker](https://github.com/LinuxTeam-teilar/cronos.teilar.gr/issues).
 * [Όλα τα ανοιχτά issues](https://github.com/LinuxTeam-teilar/cronos.teilar.gr/issues?direction=desc&sort=created&state=open)
 * [Bugs](https://github.com/LinuxTeam-teilar/cronos.teilar.gr/issues?direction=desc&labels=bug&page=1&sort=created&state=open)
 * [Enhancements](https://github.com/LinuxTeam-teilar/cronos.teilar.gr/issues?direction=desc&labels=enhancement&page=1&sort=created&state=open)
 * [Junior Jobs](https://github.com/LinuxTeam-teilar/cronos.teilar.gr/issues?direction=desc&labels=junior+job&page=1&sort=created&state=open)
 (Λίστα με bugs/enhancements με εύκολη επίλυση)

Επίσης, στο [wiki](https://github.com/LinuxTeam-teilar/cronos.teilar.gr/wiki)
βρίσκονται διάφορα άρθρα που αφορούν την ανάπτυξη της εφαρμογής.

Εγκατάσταση
-----------

Για Linux:

* Προαιρετικό: Δημιουργείτε μια βάση δεδομένων MySQL, εναλλακτικά το σύστημα
θα δημιουργήσει από μόνο του μια SQLite.
* `git clone git://github.com/LinuxTeam-teilar/cronos.teilar.gr`
* `cd cronos.teilar.gr`
* `pip install -r requirements.txt`
  * Πρέπει να έχετε ήδη εγκαταστήσει τα συγκεκριμένα packages από το package
  manager: `libxml2-dev` `libxslt1-dev` `mysql` `libmysqlclient-dev`
* `cp cronos/local_settings.py.sample cronos/local_settings.py`
* `$EDITOR cronos/local_settings.py`
  * Τοποθετείτε τα στοιχεία της βάσης δεδομένων σας (σε περίπτωση που έχετε
  SQLite δεν χρειάζεται να πειράξετε κάτι). Οι υπόλοιπες μεταβλητές δεν
  χρειάζεται να αλλαχθούν.
* `python manage.py syncdb`
* `bin/update_cronos.sh -p . -r -d -v`
  * Η εντολή αυτή αποθηκεύει στη βάση δεδομένων πληροφορίες και ανακοινώσεις
* `python manage.py loaddata tests/fixtures/admin_account.json`
  * Η εντολή αυτή προσθέτει ένα fake account στη βάση δεδομένων για λόγους
  testing
* `python manage.py runserver`
* Τέλος, μπορείτε να κάνετε login στο `http://localhost:8000` είτε με τα στοιχεία
που έχετε στο http://dionysos.teilar.gr, είτε με username και password: admin

Μπορούμε επίσης να σας παρέχουμε testing instance σε δικό μας server,
επικοινωνήστε μαζί μας για να κανονίσουμε τις λεπτομέρειες.

API
---

Ο cronos προσφέρει ένα CLI API, το οποίο εμφανίζει δεδομένα της βάσης
σε python variables.  
Ο cronos προσφέρει επίσης και ένα RESTful API το οποίο εμφανίζει
δεδομένα της βάσης σε JSON και XML μορφή.  
Πληροφορίες για το API θα βρείτε [εδώ](https://github.com/LinuxTeam-teilar/cronos.teilar.gr/wiki/API)  
Λόγω του RESTful API, μπορούν να γραφτούν και external applications που θα
διαχειρίζονται τις πληροφορίες του cronos, πληροφορίες [εδώ](https://github.com/LinuxTeam-teilar/cronos.teilar.gr/wiki/External-applications)

Περιγραφή του κώδικα
--------------------

* **tests**: Διάφορα unit tests. Τρέχουν με μία από τις παρακάτω εντολές:
    * `python manage.py test tests`
    * `python setup.py test`
* **cronos**: ο python/django, HTML, CSS και JS κώδικας
    * **\_\_init\_\_.py**: Περιέχει την έκδοση της εφαρμογής, καθώς και το
    Cronos object από το οποίο συνθέτονται οι πληροφορίες του φοιτητή. Το
    Cronos object μπορεί να χρησιμοποιηθεί και ως CLI API
    * **accounts**: Ότι αφορά το login και την προβολή των λογαριασμών
        * **backends.py**: Το authentication backend το οποίο εξασφαλίζει την
        αυθεντικοποίηση του λογαριασμού μέσω του http://dionysos.teilar.gr
        * **resources.py**: Το RESTful API
    * **common**: Κοινά modules/classes/functions που χρησιμοποιούνται γενικά
        * **encryption.py**: Συναρτήσεις κρυπτογράφησης/αποκρυπτογράφησης των
        κωδικών μέσω αλγορίθμου κρυπτογράφησης blowfish
    * **posts**: Ότι αφορά την προβολή των ανακοινώσεων (συμπεριλαμβανομένου
    και του cronos blog)
        * **feeds.py**: Το combined RSS feed
    * **refrigerators**: Το extension Ψυκτικά Φορτία
    * **static**: CSS, JS και αρχεία εικόνων
    * **teilar**: Εμφάνιση σελίδων σχετικών με πληροφορίες του ΤΕΙ Λάρισας
        * **management/commands**: Οι custom εντολές python manage.py $COMMAND
            * **create\_rss\_feed**: Δημιουργεί RSS feeds για τις σελίδες που
            είτε δεν παρέχουν, είτε παρέχουν αλλά δεν είναι σε καλή μορφή
            * **get\_websites**: Αποθηκεύει στη βάση τη λίστα με τα websites
            από τα οποία θα ελέγχονται για ανακοινώσεις
            * **get\_departments**: Αποθηκεύει στη βάση τα τμήματα του ΤΕΙ Λάρισας
            * **get\_teachers**: Αποθηκεύει στη βάση τους καθηγητές του ΤΕΙ Λάρισας
            * **get\_eclass\_faculties**: Αποθηκεύει στη βάση τις σχολές του
            ΤΕΙ Λάρισας όπως είναι αποθηκευμένες στο e-class.teilar.gr
            * **get\_eclass\_lessons**: Αποθηκεύει στη βάση τα μαθήματα e-class
            * **get\_rss\_feeds**: Αποθηκεύει στη βάση όλες τις ανακοινώσεις
    * **templates**: Τα HTML templates
