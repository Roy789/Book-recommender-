import sqlite3
import os
import math
'''
function that can be used to view the books!!
'''

path = os.getcwd()+'/Database/readrecommend.db'

def get_books():
    con = sqlite3.connect(path)

    cursorObj = con.cursor()
    sql = ''' SELECT * from BOOKS'''
    cursorObj.execute(sql)
    table = cursorObj.fetchall()
    con.close()
    return table

books = get_books()

## Add a collection in the book database:
def add_book_to_collections(user_id, collection_id, book_id, read,name, location = path):
    con = sqlite3.connect(location)
    sql = ''' INSERT INTO COLLECTIONS(USERID,COLLECTIONID,BOOKID,READ,NAME)
                  VALUES(?,?,?,?,?) '''
    cur = con.cursor()
    cur.execute(sql, (user_id, collection_id, book_id, read,name))
    con.commit()
    con.close()
    
# Update when a user reads a book
def update_read(user_id, book_id, read,name, location = path)   :
    con = sqlite3.connect(location)
    sql = ''' UPDATE COLLECTIONS SET READ = ?
                  WHERE USERID = ? 
                  AND 
                  BOOKID = ? 
                  AND 
                  NAME = ?'''
    cur = con.cursor()
    cur.execute(sql, (read, user_id, book_id, name))
    con.commit()
    con.close()

# Add a new collection
def add_collection(user_id):
    con = sqlite3.connect(path)
    sql = ''' INSERT INTO COLLECTIONS(USERID,COLLECTIONID,BOOKID,READ,NAME)
                  VALUES(?,?,?,?,?) '''
    cur = con.cursor()
    cur.execute(sql, (user_id, 1, -1, 0,'Default'))
    con.commit()
    con.close()


## Removing a collection!! 
def remove_collection(collection_name, user_id,  location=path):
    con = sqlite3.connect(location)
    cur = con.cursor()
    
    sql_update_query = """DELETE from COLLECTIONS where NAME = ? AND USERID = ?"""
    
    cur.execute(sql_update_query, (collection_name,user_id,  ))
    
    con.commit()
    
    con.close()
 
# Removing book from a specific collection for a user
def remove_book(collection_name, user_id,book_id):
    con = sqlite3.connect(path)
    cur = con.cursor()
    
    sql_update_query = """DELETE from COLLECTIONS where NAME = ? AND USERID = ? AND BOOKID = ?"""
    
    cur.execute(sql_update_query, (collection_name,user_id,book_id,  ))
    
    con.commit()
    
    con.close()

# Get the specific book details by book id
def get_book_by_id(book_id):
    con = sqlite3.connect(path)
    
    cursorObj = con.cursor()
    sql = "SELECT * from BOOKS where BOOKID="+str(book_id)
    cursorObj.execute(sql)
    table = cursorObj.fetchall()
    con.close()
    return table
    
# Get all the authors from the db    
def get_authors():
    books = get_books()
    authors = []
    for i in books:
        lister = [j.strip() for j in i[2].split(',')]
        authors +=  lister
    return list(set(authors))

# Get all the users from the db
def get_users():
    con = sqlite3.connect(path)
    cursorObj = con.cursor()
    sql = ''' SELECT * from USERS'''
    cursorObj.execute(sql)
    table = cursorObj.fetchall()
    con.close()
    return table

# Get user details based on the username
def get_user_by_name(username):
    con = sqlite3.connect(path)
    cursorObj = con.cursor()
    sql = "SELECT * from USERS WHERE USERNAME='"+username+"'"
    cursorObj.execute(sql)
    table = cursorObj.fetchall()
    con.close()
    return table


def search_books(genre,author,ratings, books = books):
    return_books = []
    if len(ratings) == 0:
        ratings.append(0)

    for book in books:

        ## If every option is selected!
        if len(author) >= 1 and len(genre) >= 1:
            if any(ext in book[8] for ext in genre) and any(ext in book[2] for ext in author) and book[3] > min(ratings):
                return_books.append(book)

        ## If the author list is empty 
        elif len(author) == 0 and len(genre) != 0:
            if any(ext in book[8] for ext in genre) and book[3] > min(ratings):
                return_books.append(book)

        ## If the genre list is empty!
        elif len(genre) == 0 and len(author) != 0:
            if any(ext in book[2] for ext in author) and book[3] > min(ratings):
                return_books.append(book)        

        ## If no option is selected
        else:
            if book[3] >= min(ratings):
                return_books.append(book)

    return return_books

# Get all the collections for a particular user
def get_collections(user_id):
    con = sqlite3.connect(path)

    cursorObj = con.cursor()
    sql = "SELECT DISTINCT * from COLLECTIONS WHERE USERID = '" + str(user_id) + "'"
    cursorObj.execute(sql)
    table = cursorObj.fetchall()
    con.close()
    return table

# Get the unique collection names for a user
def get_unique_collection(user_id):
    con = sqlite3.connect(path)

    cursorObj = con.cursor()
    sql = "SELECT DISTINCT NAME from COLLECTIONS WHERE USERID = '" + str(user_id) + "'"
    cursorObj.execute(sql)
    table = cursorObj.fetchall()
    con.close()
    return table

# Adds a new user review into the review table
def add_review(user_id,book_id,review,rating):
    con = sqlite3.connect(path)

    cursorObj = con.cursor()
    sql = ''' INSERT INTO REVIEWS(USERID,BOOKID,REVIEWS,RATINGS)
                  VALUES(?,?,?,?) '''
    cursorObj.execute(sql, (user_id, book_id,review,rating))
    con.commit()
    con.close()  

# Gets all the reviews for a particular book along with username
def get_reviews(book_id):
    con = sqlite3.connect(path)

    cursorObj = con.cursor()
    sql = "SELECT DISTINCT REVIEWS, RATINGS, USERNAME from REVIEWS R INNER JOIN USERS U ON R.USERID=U.USERID \
        WHERE BOOKID = '"+ str(book_id)+ "'"
    cursorObj.execute(sql)
    table = cursorObj.fetchall()
    
    con.close()
    return table

# Update interests of the user on account page
def update_interests(user_id, interests):
    con = sqlite3.connect(path)
    sql = ''' UPDATE USERS SET INTERESTS = ?
                  WHERE USERID = ? 
                  '''
    cur = con.cursor()
    cur.execute(sql, (interests,user_id,))
    con.commit()
    con.close()

# Method to set the progress bar for a particular user based on the number of books read
def get_read_collections(user_id,collection_name):
    con = sqlite3.connect(path)

    cursorObj = con.cursor()
    sql = "SELECT DISTINCT BOOKID, MAX(READ) from COLLECTIONS WHERE USERID = '" + str(user_id) + "' AND NAME='"+collection_name+"' GROUP BY BOOKID"
    cursorObj.execute(sql)
    table = cursorObj.fetchall()
    con.close()
    read = 0
    unread = 0
    for i in table:
        if i[1]== 1:
            read+=1
        else:
            unread+=1
    print(table)
    try:
        percent = math.floor(read*100/(read + unread))
    except:
        return 0

    return percent