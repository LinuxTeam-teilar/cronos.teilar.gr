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

Ανάπτυξη
========

Ιδέες και σφάλματα
--------------------

Λίστα με ιδέες και σφάλματα βρίσκονται στον [issue tracker](https://github.com/LinuxTeam-teilar/cronos.teilar.gr/issues).

Εγκατάσταση
-----------

Για Linux:

* Δημιουργείτε μια βάση δεδομένων, κατά προτίμηση MySQL
* git clone git://github.com/LinuxTeam-teilar/cronos.teilar.gr
* cd cronos.teilar.gr
* pip install -r requirements.txt
* cp cronos/local\_settings.py.sample cronos/local\_settings.py
* $EDITOR cronos/local\_settings.py
  * Τοποθετείτε τα στοιχεία της βάσης δεδομένων σας. Οι υπόλοιπες
  μεταβλητές δεν χρειάζεται να αλλαχθούν.
* bin/update\_cronos.sh -p . -r -d -v
  * Η εντολή αυτή αποθηκεύει στη βάση δεδομένων πληροφορίες και
  ανακοινώσεις
* python manage.py loaddata tests/fixtures/admin\_account.json
  * Η εντολή αυτή προσθέτει ένα fake account στη βάση δεδομένων
  για λόγους testing
* Τέλος, μπορείτε να κάνετε login είτε με τα στοιχεία που έχετε
στο http://dionysos.teilar.gr, είτε με username και password: admin

Το script update\_cronos.sh τρέχει τις παρακάτω εντολές:
* python manage.py get\_websites
  * Αποθηκεύει στη βάση τη λίστα με τα websites από τα οποία
  θα ελέγχονται για ανακοινώσεις
* python manage.py get\_departments
  * Αποθηκεύει στη βάση τα τμήματα του ΤΕΙ Λάρισας
* python manage.py get\_teachers
  * Αποθηκεύει στη βάση τους καθηγητές του ΤΕΙ Λάρισας
* python manage.py get\_eclass\_faculties
  * Αποθηκεύει στη βάση τις σχολές του ΤΕΙ Λάρισας όπως
  είναι αποθηκευμένες στο e-class.teilar.gr
* python manage.py get\_eclass\_lessons
  * Αποθηκεύει στη βάση τα μαθήματα e-class
* python manage.py get\_rss\_feeds
  * Αποθηκεύει στη βάση όλες τις ανακοινώσεις

API
---

Ο cronos προσφέρει ένα CLI API, το οποίο εμφανίζει δεδομένα της βάσης
σε python variables.  
Ο cronos προσφέρει επίσης και ένα RESTful API το οποίο εμφανίζει
δεδομένα της βάσης σε JSON και XML μορφή.
Πληροφορίες για το API θα βρείτε [εδώ](https://github.com/LinuxTeam-teilar/cronos.teilar.gr/wiki/API)

Περιγραφή του κώδικα
--------------------

* media και static: Στους καταλόγους αυτούς μπαίνουν πληροφορίες από το web
server και δεν χρησιμοποιούνται για το development instance
* configs: Διάφορα configuration files για reference, χρησιμοποιούνται κυρίως
για το production
* test: Διάφορα unit tests. Τρέχουν με την εντολή:
  * python manage.py test tests
* cronos: ο python/django, HTML, CSS και JS κώδικας
  * \_\_init\_\_.py: Περιέχει την έκδοση της εφαρμογής, καθώς και το Cronos
  object από το οποίο συνθέτονται οι πληροφορίες του φοιτητή. Το Cronos object
  μπορεί να χρησιμοποιηθεί και ως CLI API
  * accounts: Ότι αφορά το login και την προβολή των λογαριασμών
    * backends.py: Το authentication backend το οποίο εξασφαλίζει την
    αυθεντικοποίηση του λογαριασμού μέσω του http://dionysos.teilar.gr
    * resources.py: Το RESTful API
  * common: Κοινά modules/classes/functions που χρησιμοποιούνται γενικά
    * encryption.py: Συναρτήσεις κρυπτογράφησης/αποκρυπτογράφησης των κωδικών
    μέσω αλγορίθμου blowfish
  * posts: Ότι αφορά την προβολή των ανακοινώσεων (συμπεριλαμβανομένου και
  του cronos blog)
    * feeds.py: Το combined RSS feed
  * refrigerators: Το extension Βιομηχανικά Ψυγεία
  * static: CSS, JS και αρχεία εικόνων
  * teilar: Εμφάνιση σελίδων σχετικών με πληροφορίες του ΤΕΙ Λάρισας
    * management/commands: Οι custom εντολές python manage.py $COMMAND
  * templates: Τα HTML templates

