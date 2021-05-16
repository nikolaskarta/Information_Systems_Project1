# Υποχρεωτική Εργασία ΠΣ 1

Για την εργασία αυτή έχει υλοποιηθεί ένα αρχείο **app.py**, το οποίο χρησιμοποιεί την βιβλιοθήκη **PyMongo**, καθώς και τη βιβλιοθήκη του **Flask Framework**, για τη δημιουργία μιας web εφαρμογής που χρησιμοποιεί 9 **endpoints** για να προβάλλει, να επεξεργαστεί, και να δημιουργήσει documents σε μία **MongoDB** η οποία τρέχει σε ένα περιβάλλον **Docker**.


# MongoDB Container

Για την προετοιμασία της ΒΔ δημιουργήθηκε πρώτα ένα Docker container περιέχοντας μέσα μια υλοποίηση της Mongo με την εντολή

    docker run -d -p 27017:27017 --name mongodb mongo:4.0.4

Φυσικά οι θύρα που έχουμε εισάγει είναι η 27017 καθώς εκεί θέλουμε να ακούει το πρόγραμμα.
Έπειτα για την εισαγωγή του αρχείου **students.json** έπρεπε πρώτα να το αντιγράψουμε μέσα στο container. Αυτό πραγματοποιήθηκε με την εντολή 

    docker cp students.json mongodb:/students.json
Και έπειτα με την παρακάτω εντολή δημιουργήσαμε τη ΒΔ InfoSys χρησιμοποιώντας το students.json για να γεμίσουμε το **Students** collection.

    docker exec -it mongodb mongoimport --db=InfoSys --collection=Students --file=students.json

Μετά από τα παραπάνω βήματα η βάση ήταν έτοιμη για χρήση.
  
# Endpoints

Το app.py αποτελείται από 9 διαφορετικά **endpoints**, το κάθε endpoint ολοκληρώνει συγκεκριμένες λειτουργίες.

 1. **/createUser** - Δημιουργία χρήστη
 2. **/login** - Είσοδος στο σύστημα
 3. **/getStudent** - Επιστροφή πληροφοριών φοιτητή με βάσει το email
 4. **/getStudents/thirties** - Επιστροφή των φοιτητών που είναι 30 ετών
 5. **/getStudents/oldies** - Επιστροφή των φοιτητών που είναι τουλάχιστον 30
 6. **/getStudentAddress** - Επιστροφή φοιτητή εφόσον έχει δηλώσει κατοικία με βάση το email του
 7. **/deleteStudent** - Διαγραφή φοιτητή με βάση το email του
 8. **/addCourses** - Εισαγωγή μαθημάτων σε φοιτητή με βάση το email του.
 9. **/getPassedCourses** - Επιστροφή περασμένων μαθημάτων ενός φοιτητή με βάση το email του.

## Create User

Η συνάρτηση **create_user()** λαμβάνει στο body του **POST** request ένα JSON της μορφής 

```json     
{
    "usename": "some username", 
    "password": "a very secure password"
}
```
Για τον έλεγχο της ύπαρξης του **username** ήδη στην Users collection χρησιμοποίησα την εντολή

```python
users.find({"username":f"{data['username']}"}).count()
```
Έκανα αυτήν την επιλογή, καθώς κατά την αναζήτηση της ΒΔ για το username που έχουμε λάβει απο το αίτημα του χρήστη, αν έχουμε προσθέσει στο τέλος το **count()** θα λάβουμε ως αποτέλεσμα είτε το 1 (username already exists) είται το 0 (user is not registered). Αν λοιπόν το username δε βρεθεί, κάνουμε **insert** στο Users collection τα στοιχεία του, στέλνοντας τα κατάλληλα response πίσω στο χρήστη.


## Login

Αυτό το endpoint λαμβάνει **POST** αίτημα το οποίο περιέχει **JSON** με στοιχεία το username και το password, τα οποία πρέπει να έχουν δημιουργηθεί ήδη.

Με παρόμοιο τρόπο όπως και στο προηγούμενο endpoint (χρήση του **count()**), ελέγχουμε αν τα στοιχεία υπάρχουν στη ΒΔ και αν αντιστοιχούν οι κωδικοί. Αν τα στοχεία που έχουμε λάβει είναι σωστά, καλούμε τη συνάρτηση **create_session()** με παράμετρο το username που έχουμε ελέγξει προηγουμένως. Η συνάρτηση επιστρέφει το **uuid** το οποίο μετά εμφανίζεται στο χρήστη ώστε να το χρησιμοποιήσει στα endpoints που ακολουθούν (status 200). Αν η επαλήθευση του χρήστη αποτύχει εμφανίζεται το κατάλληλο μήνυμα αποτυχίας με status 400.

## Get Student
Το endpoint αυτό λαμβάνει αίτημα **GET** το οποίο περιέχει **JSON** με στοιχεία το email του φοιτητή. Ταυτόχρονα, διαβάζει το **authorization** header του αιτήματος, το οποίο χρησιμοποιείται για την επαλήθευση του session, με τη χρήση του **is_session_valid**. Αν το uuid που χρησιμοποιήθηκε στα headers δεν αντιστοιχεί στα ενεργά uuid που υπάρχουν εκείνη τη στιγμή, το endpoint τερματίζει με το μήνυμα "Not authorized", και το status 401. Αν όμως χρησιμοποιηθεί σωστό UUID, εκτελούμε την εντολή find_one στο Students collection και αποθηκεύουμε το αποτέλεσμα της εντολής στη μεταβλητή **studentcursor**. Για να αποφύγω τα λάθη κατά την προβολή των αποτελεσμάτων της εντολής λόγω μη σειριοποιήσιμων στοιχείων των MongoDB documents, χρησιμοποίησα τη συνάρτηση **json_util.dumps()** της βιβλιοθήκης bson. Στη συνέχεια έκανα **loads** το αποτέλεσμα της συνάρτησης αυτής στο student dictionary. Στη συνέχεια γίνεται έλεγχος αν το **student** περιέχει πληροφορίες ή οχι, καθώς αν το student είναι κενό, αυτό σημαίνει ότι δεν βρέθηκε κανένας φοιτητής με αυτο το email. Στην περίπτωση αυτή εμφανίζεται το μήνυμα "Student not found" με status 400. Αν όμως το student δεν είναι κενό, εμφανίζεται στο χρήστη μαζί με status 200.

## Get Students Thirty

Με τον ίδιο τρόπο όπως πριν, υλοποιούμε την αυθεντικοποίηση του χρήστη, και με την εντολή **find()** στο Students collection, βρίσκουμε όλους τους φοιτητές με έτος γέννησης ίσο με 1991. Τα αποτελέσματα αποθηκεύονται στο **thirtiescursor** και στη συνέχεια αποθηκεύονται στο Students μετά την μετατροπή τους. Αν το Students είναι άδειο, δεν βρέθηκαν φοιτητές και το endpoint τερματίζει με τα κατάλληλα μηνύματα. Αν δεν είναι άδειο τότε βρέθηκαν φοιτητές, και τα δεδομένα τους εμφανίζονται.

## Get Students Oldies

Για αυτό το endpoint ακολούθησα τα ίδια βήματα με το παραπάνω, με τη διαφορά όμως ότι κατα την αναζήτηση των φοιτητών χρησιμοποίησα την εντολή:
```python
    oldiescursor = students.find({"yearOfBirth": {'$lte' : 1991}})
```
Στην εντολή αυτή χρησιμοποιήθηκε ο operator **$lte** για να βρούμε τους φοιτητές που είναι τουλάχιστον 30.

## Get Student Address
Όπως προηγουμένως, το endpoint λαμβάνει αίτημα **GET** με **JSON** στο body που περιέχει email, και UUID στο authorization header. Για να βρούμε αν ο φοιτητής του οποίου το email λάβαμε έχει δηλωμένει διεύθυνση, εκτελείται η εντολή
```python
students.find_one({"email" : f"{data['email']}", "address": {"$exists": 1}})
```
Η παραπάνω εντολή ψαχνει dοcuments που έχουν το ίδιο email με αυτό που λάβαμε στο Body του αιτήματος, και ταυτόχρονα περιέχουν address field.

Αν βρεθεί φοιτητής, συναρμολογούμε το student dictionary με τον παρακάτω τρόπο:
```python
 student = {

    "name" : addressdict['name'],
    "street": addressdict['address'][0]['street'],
    "postcode": addressdict['address'][0]['postcode']

}
```
Όπου **addressdict** είναι το αποτέλεσμα της εντολής find_one() αφού αυτο γίνει σειριοποιήσιμο.
Τέλος, οι πληροφορίες επιστρέφουν στο χρήστη με τη μορφή που έχει ζητηθεί και το endpoint ολοκληρώνει. Αν δε βρεθεί φοιτητής τότε εμφανίζονται στο χρήστη τα κατάλληλα μηνύματα και το endpoint ολοκληρώνει.
## Delete User
Το endpoint αυτό λαμβάνει αίτημα **DELETE** με body περιέχοντας ένα **JSON** με μοναδικό πεδίο το email, και authorization header με το uuid. Πραγματοποιώ αναζήτηση στη ΒΔ για το φοιτητή του οποίου έχουμε λάβει το email, και σειριοποιώ το αποτέλεσμα στο **deldict**. Αν αυτό είναι άδειο, δε βρέθηκε φοιτητής και το endpoint τερματίζεται με τα κατάλληλα μηνύματα. Αν δεν είναι άδειο, τότε με την εντολή
```python
students.delete_one({"email" : f"{data['email']}"})
```
Διαγράφεται το document του φοιτητή από τη συλλογή Students. Έπειτα φτιάχνουμε το μήνυμα **msg** χρησιμοποιώντας το πεδίο "name" από την αναζήτηση της οποίας το αποτέλεσμα είχε αποθηκευτεί στο dictionary **deldict**
```python
msg = deldict['name'] + "was deleted."
return Response(msg, status=200, mimetype='application/json')
```

## Add Courses

Το endpoint αυτό λαμβάνει αίτημα **PATCH** με email, courses sto body και uuid στο authorization header. Αποθήκευσα στο **courses** τα στοιχεία οπού έστειλε ο χρήστης και κατασκευάζω ένα query για να κάνω το γράψιμο της εντολής **update_one** λιγότερο μπερδεμένη.
```python
query = {"email": f"{data['email']}"}
newvalues = { "$set": { "courses": f"{courses}" } }
```
Αν βρεθεί τελικα φοιτητής με το email που μας έχει δοθεί, εκτελούμε την εντολή update_one με τα παραπάνω στοιχεία και εμφανίζουμε τα κατάλληλα μηνύματα.
```python
if (students.find({"email" : f"{data['email']}"}).count()==1):
    students.update_one(query, newvalues)
    return Response("Courses added succesfully", status=200, mimetype='application/json')
```

## Get Passed Courses
Σε αυτό το endpoint λαμβάνεται αίτημα **GET** με authorization header και JSON sto body που περιέχει ένα email. Αν το email αντοιστοιχεί σε φοιτητή και το document του φοιτητή περιέχει πεδίο courses, φτιάχνουμε το list dictionary **student** στο οποίο εισάγουμε τα courses του φοιτητή.
```python
student = coursesdict['courses']
```
Τέλος εμφάνίζουμε το students στο χρήστη με status 200. Αν δεν βρεθεί document με το αντίστοιχο email, ή ο συγκεκριμένος φοιτητής δεν έχει περασμένα μαθήματα, το endpoint ολοκληρώνει με το κατάλληλο μήνυμα και status 400.

# Σημειωση
**Σε κάθε endpoint έχει υλοποιηθεί ο έλεγχος του UUID. Αν ο χρήστης δεν είναι αυθεντικοποιημένος, ολα τα endpoint τερματίζουν με το μήνυμα "Not authorized" και το status 401.**
