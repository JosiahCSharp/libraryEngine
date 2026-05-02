
# Josiah's Highly Efficient Search Algorithm and Database for Libraries!
# This tool aims to add basic and advanced features for library databases.
# Things like

# * Advanced Search Queries 
#   Ex. AND, OR, AUT="", YR=####, DESC="", TITLE="", LNGE="", etc.

# * Fast Sorting for Databases
#   Ex. AVL Tree Implementations for ease of use with gigantic sets of data.

# * Import / Export / Backups
#   Ex. Export to XML, SQL, CSV, MARC21 database formats for high compatibility.

# * Database Management
#   Ex. Generating QR codes, Barcodes, Index Numbers, managing checkout, accounts, and more.

# * Secure Backend
#   Ex. Login security, HTTPS webpage backend access and API access, permission management (admin vs librarians vs users vs guest, etc.)

# * GUI interface for backend
#   Ex. Easier Management for backend users, accessibility to command line access or gui optionally.

## GUI, IMPORT/EXPORT, AND ADVANCED QUERIES are not implemented yet due to time constraints. 
## Same thing with the saving databases as files, I'm not sure how to save AVL trees as files.
## Also the login system isn't implemented even though the users have been created. 

import hashlib
import os

def hash_password(password, salt):
    #Creates a SHA-256 hash of the password combined with the salt 
    return hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000) # found this online. 

class User:
    def __init__(self, username, password, role):
        self.username = username
        self.role = role
        # Generates "salt" which basically just hides the hash with random data
        self.salt = os.urandom(32)
        # Hashes password with the salt.
        self.password_hash = hash_password(password, self.salt)

    def verify_password(self, password_attempt):
        # Hashes the attempt with the user's saved salt to see if they match
        return self.password_hash == hash_password(password_attempt, self.salt)

class Book:
    def __init__(self, title, authors, isbns, genres, **extra_data): # ** compensates for if nothing ends up being put there it will continue the code.
        self.title = title
        self.authors = authors if isinstance(authors, list) else [authors] # the isinstance allows us to have both multiple items or just one 
        self.isbns = isbns if isinstance(isbns, list) else [isbns] 
        self.genres = genres if isinstance(genres, list) else [genres]
        self.extra_data = extra_data # so we can store things like publication year, language, and more.

    def __str__(self): # so we can just print the book object itself yay!
        return f"'{self.title}' by {', '.join(self.authors)}" # Used formatter so I would'nt have to make a new variable.
 
    def get_info(self): # Formatting for books. 
        info = {
            "Title": self.title,
            "Authors": ", ".join(self.authors),
            "ISBNs": ", ".join(self.isbns),
            "Genres": ", ".join(self.genres)
        }
        info.update(self.extra_data) # Update is a built-in python function that adds extra data from the parameter we put in __init__
        return info

class AVLNode: # AVL implementation for binary search tree. 
    def __init__(self, key, book_ref): 
        self.key = key
        self.books = [book_ref] 
        self.left = None
        self.right = None
        self.height = 1

class AVLTree:
    def get_height(self, node):
        return node.height if node else 0

    def get_balance(self, node):
        return self.get_height(node.left) - self.get_height(node.right) if node else 0

    # I had to implement something like coordinates for the rotations to work. I had to look up most of the AVL tree implementation.
    # I also referenced from a BST implementation that I found online as well for the basic functions like insert.
    def rotate_right(self, y):
        
        # -- Actual Rotation via Swapping Variables --
        
        x = y.left # move x to right of child y
        T2 = x.right # grap child to right of x
        x.right = y # move y to right of x
        y.left = T2 # moves the children and attaches them to the left of y

        # -- Recalculate y and x height individually

        y.height = 1 + max(self.get_height(y.left), self.get_height(y.right))
        x.height = 1 + max(self.get_height(x.left), self.get_height(x.right))


        return x

    def rotate_left(self, x): # x == root from insert
        # -- Swap Variables for the Rotation --
        
        y = x.right
        T2 = y.left
        y.left = x
        x.right = T2

        # -- Recalculation of height after rotation for x,y respectively.

        x.height = 1 + max(self.get_height(x.left), self.get_height(x.right)) # Recalculates the height after rotating.
        y.height = 1 + max(self.get_height(y.left), self.get_height(y.right)) # ^ Same

        # -- Recalculate y and x height individually

        y.height = 1 + max(self.get_height(y.left), self.get_height(y.right))
        x.height = 1 + max(self.get_height(x.left), self.get_height(x.right))


        return y

    def insert(self, root, key, book_ref):
        if not root:
            return AVLNode(key, book_ref)
        
        if key == root.key:
            if book_ref not in root.books:
                root.books.append(book_ref) # adds book to node of books as part of it, if one already exists with the same key/id
            return root
        
        elif key < root.key:
            root.left = self.insert(root.left, key, book_ref) # adds new book to left

        else:
            root.right = self.insert(root.right, key, book_ref) # adds new book to right

        root.height = 1 + max(self.get_height(root.left), self.get_height(root.right)) # Recalculates height
        balance = self.get_balance(root) # Uses height to recalculate balances. 

        if balance > 1 and key < root.left.key:
            return self.rotate_right(root)
        
        if balance < -1 and key > root.right.key:
            return self.rotate_left(root)
        
        if balance > 1 and key > root.left.key:
            root.left = self.rotate_left(root.left)
            return self.rotate_right(root)
        
        if balance < -1 and key < root.right.key:
            root.right = self.rotate_right(root.right)
            return self.rotate_left(root)
        
        # Balancing functions that allow for rotations if balance is off.

        return root

    def search(self, root, key):
        if not root or root.key == key:
            return root.books if root else []
        
        if key < root.key:
            return self.search(root.left, key)
        
        return self.search(root.right, key)

class Library:
    def __init__(self, name="Database"):
        self.name = name
        self.all_books = [] 
        self.loginPromptAssist = ""
        
        # Different Indexes for searching quickly!
        self.idx_isbn = None
        self.idx_title = None
        self.idx_author = None
        self.idx_genres = {} 
        self.engine = AVLTree()

        # User Database Dictionary (Username -> User Object)
        self.users = {} # Creates users dictionary to store accounts
        
        # Create a default Admin account on startup
        self._force_add_user("admin", "admin123", "Admin")

    def __str__(self):
        y = ""
        for i in self.all_books:
            x  = Book.get_info(i) # x is a Dictionary
            if y == "": # if y empty just set as string of dict x
                y = str(x)
            else: # else concatenate str(x) to y under a new line.
                y = y+"\n"+str(x)
        return y
    
    def reset_password(self, username, authority):

        if authority.role == "Admin" and self.users[username].role != "Admin":
            NewPass = "123456"
            self.users[username].password_hash = hash_password(NewPass, self.salt)
            print('reset ' + self.users[username] + "'s password to 123456")

        elif authority.role == "Librarian" and (self.users[username].role != "Admin" and self.users[username].role != "Librarian"):
            NewPass = "123456"
            self.users[username].password_hash = hash_password(NewPass, self.salt)
        
        elif authority.role == "Librarian" and username[username] == authority:
            NewPass = input("Please type your new password: ")
            self.users[username].password_hash = hash_password(NewPass, self.salt)

        elif authority.role == "User" and username[username] == authority:
            NewPass = input("Please type your new password: ")
            self.users[username].password_hash = hash_password(NewPass, self.salt)

        else:
            print("NOTICE: Admin cannot reset own password, but can reset Librarian password.\nLibrarian can reset user and guest passwords.\nUsers can reset their own passwords.\n Passwords are stored securely.")
            print("Insufficient Permissions or Error has occurred.\nPlease contact your administrator for more information")


    def _force_add_user(self, username, password, role):
        #Bypasses permissions to create initial accounts.
        self.users[username] = User(username, password, role)

    def get_loginPromptAssist(self, **help):
        if help.upper() == "YES" or "TRUE" or "1":
            print("This tool allows you to set your custom prompt including USERNAME guidlines\nPhone Number and more for users to login! It will be printed at login attempt.")
        return self.loginPromptAssist
    
    def set_loginPromptAssist(self, prompt = "", **help):
        if help.upper() == "YES" or "TRUE" or "1":
            print("This tool allows you to set your custom prompt including USERNAME guidlines\nPhone Number and more for users to login! It will be printed at login attempt.")
            print("Administrators can access this command via the backend! Must be written using standard python syntax for strings!")
        self.loginPromptAssist = prompt
        return self.loginPromptAssist

    def authenticate(self, username, password):
        #Checks credentials and returns the User object if valid 
        user = self.users.get(username)
        if user and user.verify_password(password):
            return user
        return None

    def add_user(self, current_user, new_username, password, role):
        #Adds a user based on permissions 
        if current_user.role not in ["Admin", "Librarian"]:
            return False, "Permission Denied: Only Admins and Librarians can create accounts."
        
        if current_user.role == "Librarian" and role in ["Admin", "Librarian"]:
            return False, "Permission Denied: Librarians can only create User or Guest accounts."

        if new_username in self.users:
            return False, "Username already exists."

        self.users[new_username] = User(new_username, password, role)
        return True, f"Account '{new_username}' created successfully."

    def remove_user(self, current_user, target_username):
        # Removes a user based on hirearchy
        target_user = self.users.get(target_username)
        
        if not target_user:
            return False, "User not found."
        
        if target_user.role == "Admin":
            return False, "Permission Denied: Admin accounts can only be removed by editing database files directly."

        if current_user.role == "Admin":
            # Admin can remove anyone (except other Admins, handled above)
            del self.users[target_username]
            return True, f"User '{target_username}' removed."
            
        elif current_user.role == "Librarian":
            # Librarian can only remove Users and Guests
            if target_user.role in ["User", "Guest"]:
                del self.users[target_username]
                return True, f"User '{target_username}' removed."
            else:
                return False, "Permission Denied: Librarians can only remove User and Guest accounts."
        else:
            return False, "Permission Denied: You do not have removal privileges."

    def add_book(self, title, authors, isbns, genres, **extra_data):
        new_book = Book(title, authors, isbns, genres, **extra_data)
        self.all_books.append(new_book)
        
        # Insertions to add new books in avl tree.
        self.idx_title = self.engine.insert(self.idx_title, title, new_book)

        for author in new_book.authors:
            self.idx_author = self.engine.insert(self.idx_author, author, new_book)

        for isbn in new_book.isbns:
            self.idx_isbn = self.engine.insert(self.idx_isbn, isbn, new_book)

        for genre in new_book.genres:
            if genre not in self.idx_genres:
                self.idx_genres[genre] = None

            self.idx_genres[genre] = self.engine.insert(self.idx_genres[genre], title, new_book)
    def batch_add_book(self, books = None, formatType = "dict", formatassist = False):
        if formatassist == True:
            print("Format can go as follows")
            print("dict:\n")
            print('{{"Title": "NameOfBook", "Author":"NameOfAuthor", "ISBN":"NUMBERS", "Genre":"NameOfGenre", "Extra":"InfoSuchAsLoans"},\n {another book},\n {"Title":["Title1","Title2"], etc.}}')
            print('Dict is useful for when you need extra info not previously named')
            print("lst:\n")
            print('["Title", "Author", "ISBN", "Genre"]')
            print("List is faster than dict for typing out your imports since keys aren't necessary. But extra info won't have context.")
            print("List is good when you need subinfo for trees or you have commas in the names of items!")
            print("str:\n")
            print('"Title, Author, ISBN, Genre"')
            print("Easiest to use format but has lots of limitations. No commas in names, still subinfo ['T1','T2', etc.]")
            # It is easier to put limitations on options so that one option may be more desirable than the other, rather than to make them all desirable. IMO. Also less work for me. Yay!
        if formatType=="dict":
            for i in books:
                if isinstance(i, dict):
                    for x in i:
                        if x.upper() == "TITLE":
                            title = i[x]
                        elif x.upper() == "AUTHOR":
                            author = i[x]
                        elif x.upper() == "ISBN":
                            isbn = i[x]
                        elif x.upper() == "GENRE":
                            genre = i[x]
                        else: 
                            extra = ""
                            extra += i[x]
                    self.add_book(title, author, isbn, genre, extra)

                else:
                    if x.upper() == "TITLE":
                        title = i[x]
                    if x.upper() == "AUTHOR":
                        author = i[x]
                    if x.upper() == "ISBN":
                        isbn = i[x]
                    if x.upper() == "GENRE":
                        genre = i[x]
                    else: 
                        extra += i[x]
                    self.add_book(title, author, isbn, genre, extra)

        elif formatType=="lst":
            for i in books:
                if isinstance(i, list):
                    n=0
                    for x in i:
                        if n == 0:
                            title = x
                            n+=1
                        elif n==1:
                            author = x
                            n+=1
                        elif n==2:
                            isbn = x
                            n+=1
                        elif n==3:
                            genre = x
                            n=0
                    self.add_book(title, author, isbn, genre)
                else:
                    n=0
                    for x in i:
                        if n==0:
                            title = x
                            print(title)
                            n+=1
                        elif n==1:
                            author = x
                            print(author)
                            n+=1
                        elif n==2:
                            isbn = x
                            n+=1
                        elif n==3:
                            genre = x
                    self.add_book(title, author, isbn, genre)

        elif formatType=="str":
            books = books.split(',')
            n = 0
            for x in len(books)/4:
                if n == 0:
                    title = x
                    n+=1
                elif n==1:
                    author = x
                    n+=1
                elif n==2:
                    isbn = x
                    n+=1
                elif n==3:
                    genre = x
                    n=0
            self.add_book(title, author, isbn, genre)
        
        

    def userHandler(self, user):
        if user.role == "Admin":
            z=0
            if z==0:
                print("Admin Login Successful.")
                z+=1

            x = input("Type H for help or type the command you would like to run: ")
            if x.upper() == "H":
                print("List of Commands:\n")
                print("Reset Password: resetPassword")
                print("Remove User: removeUser")
                print("Add Book: addBook")
                print("Batch Add Books: batchAddBook ")
                print("Set Login Prompt Assist: setLoginPrompt")
                print("Search by Title: searchTitle")
                print("Search by Author: searchAuthor")
                input("\nPress any key to continue")
                self.userHandler(user)

            elif x == "resetPassword":
                y = input("username: ")
                self.reset_password(y, user)

            elif x == "removeUser":
                y = input("username: ")
                self.remove_user(user, y)

            elif x == "addBook":
                y = input('book data "title","author","isbn","genre" format: \n')
                y = y.split(',')
                n=0
                for i in y:
                    if n == 0:
                        title = i
                        n+=1
                    elif n==1:
                        author = i
                        n+=1
                    elif n==2:
                        isbn = i
                        n+=1
                    elif n==3:
                        genre = i
                        n=0
                self.add_book(title, author, isbn, genre)

        elif user.role == "Librarian":
            print("Librarian Login Successful.")
            x = input("Type H for help or type the command you would like to run: ")
            if x.upper() == "H":
                print("List of Commands:\n")
                print("Reset Password: resetPassword user")
                print("Remove User: removeUser user")
                print("Add Book: addBook book")
                print("Batch Add Books: batchAddBook ")
                print("Search by Title: searchTitle bookTitle")
                print("Search by Author: searchAuthor authorName")
                input("\nPress any key to continue")
                self.userHandler(user)

        elif user.role == "User" or "Guest":
            print(user.role+" Login Successful.")
            x = input("Type H for help or type the command you would like to run: ")
            if x.upper() == "H":
                print("List of Commands:\n")
                print("Reset Password: resetPassword")
                print("Search by Title: searchTitle bookTitle")
                print("Search by Author: searchAuthor authorName")
                input("\nPress any key to continue")
                self.userHandler(user)

    def login(self, username = "", password = ""):
        print("Welcome to the login terminal!\nIf you have an account please login now,\notherwise contact your librarian/admin!")
        if username == "":
            x = input("\ncaseMatters!\nUSERNAME: ")
        else:
            x = username
        if password == "":
            y = input("Password: ")
        else:
            y = password
        a = self.authenticate(x,y)
        if x != None:
            self.userHandler(self.users[x])
        else:
            print("Login failed, please try again or contact your administrator/librarian!")


    def search_by_title(self, title):
        return self.engine.search(self.idx_title, title)
    
    def search_by_author(self, author):
        return self.engine.search(self.idx_author, author)

def main():
    db = Library("Central Database")

    db.add_book("Dune", "Frank Herbert", ["9780441172719", 
    "9780593099322"], "Sci-Fi")
    db.add_book("1984", "George Orwell", "9780452284234", "Dystopian")
    db.add_book("Animal Farm", "George Orwell", "533", "Satire")
    db.batch_add_book([["Harry Potter and The Sorceror's Stone", "J.K. Rowling","978-1338878929",["Fantasy", "Adventure", "Mystery"]]],"lst", False)
    db._force_add_user("Josiah","123","Admin")
    db.login("Josiah","123")
    print(db)
    


if __name__ == "__main__":
    main()
