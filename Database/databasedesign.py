import sqlite3
import os

'''
Making the user table where all the users will be stored, the fields of
the table are:
1) USERID:  	A unique id which will be assigned to ever user. 
2) USERNAME:	A User selected name, which will be displayed in their profile
3) PASSWORD: 	A User selected password.
4) Interests: 	Interests of the user, will be mentioned by the users when the sign up. 
'''

path = os.getcwd()+'/readrecommend.db'


def make_user_table():

	conn = sqlite3.connect(path)
	try:
	    conn.execute('''CREATE TABLE IF NOT EXISTS USERS
	             (
	             USERID              INT PRIMARY KEY     NOT NULL,
	             USERNAME            TEXT                NOT NULL,
	             PASSWORD            TEXT                NOT NULL,
	             INTERESTS           TEXT                        					 
	             );''')
	    print("USERS table created successfully!")
	except Exception as e:
	    print(e, "USERS table could not be created!")
	    pass

	conn.commit()
	conn.close()


'''
Making the security table which will store the security questions for the user
i.e. if the user forgets their password then the security question can 
help them recover their password!
This table has the following columns: 
1) USERID:  	A unique id which will be assigned to ever user. 
2) Question1:	The first security question of the user. 
3) Answer1: 	The answer to the first question.
4) Question2: 	The Second security question of the user. 
5) Answer2:		The answer to the Second question.
'''


def make_security_table():
	conn = sqlite3.connect(path)
	try:
	    conn.execute('''CREATE TABLE IF NOT EXISTS SECURITY
	             (
	             USERNAME            TEXT PRIMARY KEY     NOT NULL,
	             QUESTION1           TEXT                NOT NULL,
	             ANSWER1             TEXT                NOT NULL
                 );''')
	    print("SECURITY table created successfully")
	except Exception as e:
	    print(e,"SECURITY table could not be created!")

	conn.commit()    
	conn.close()


'''
Making the collections table for the user. Which will be used to store
the books for every collection for every user.
This table will have the following columns:
1) USERID:  	 A unique id which will be assigned to ever user.
2) COLLECTIONID: The Collection id for the user, the main collection would be with the id 0
3) BOOKID: 		 The ID for the book.
4) Read: 		 If the book was Read!
5) NameL		 Name of the collection!
'''


def make_collections_table():
	conn = sqlite3.connect(path)
	try:
	    conn.execute('''CREATE TABLE IF NOT EXISTS COLLECTIONS
	             (
	             USERID                 INT                 NOT NULL,
	             COLLECTIONID           INT                 NOT NULL,
	             BOOKID                 INT            ,
			     READ		    		INT				,
			     NAME		    		TEXT			
	             );''')
	    print("COLLECTIONS table created successfully")
	except Exception as e:
		print(e,"COLLECTIONS table could not be created!")
		pass

	
	conn.commit()
	conn.close()


"""
Making a table to store all the books in our database. 
The table books will have the following columns: 
1) BOOKID:		 	A Unique id for every book.
2) BOOKNAME:	 	The name of the book. 
3) AUTHOR:		  	Author of the book. 
4) AVERAGERATING:	Average rating as given by the users of readrecommend.
5) ISBN:			The ISBN of the book.
6) LANGUAGE:		The language in which the book was written. 
7) PUBLICATIONDATE: The date of the book publication.
8) PUBLISHER:		The publishing company of the book. 	
"""


def make_books_table():
    conn = sqlite3.connect(path)
    try:
	    conn.execute('''CREATE TABLE IF NOT EXISTS BOOKS
	             (
	             BOOKID                 INT PRIMARY KEY     NOT NULL,
	             BOOKNAME               TEXT                NOT NULL,
	             AUTHOR                 TEXT                NOT NULL,
	             AVERAGERATING          FLOAT                       ,
	             ISBN                   TEXT                        ,
	             LANGUAGE               TEXT                        ,	           
	             PUBLICATIONDATE        TEXT                        ,
		     	 URL		    		TEXT	            		,
		     	 GENRE					TEXT						,
	             PUBLISHER              TEXT                       ,
                 NUMBER_REVIEWS         INT
	         );''')
	    print("BOOKS table created successfully")

    except Exception as e:
        print(e,"BOOKS table could not be created!")
    
    conn.commit()
    conn.close()


"""
Making the reviews table in our database which will store the reviews provided by 
our users.
The table will have the following columns: 
1) USERID: The id of the user that provided the review.
2) BOOKID: The id of the book that the review belongs to. 
3) REVIEWS: Content of the review. 
"""


def make_reviews_table():
	conn = sqlite3.connect(path)
	try:
	    conn.execute('''CREATE TABLE IF NOT EXISTS REVIEWS
	             (
	             USERID                  INT                 NOT NULL,
	             BOOKID                  INT                 NOT NULL,
	             REVIEWS                 TEXT                NOT NULL,
                 RATINGS                 INT                 NOT NULL
	             );''')
	    print("REVIEWS table created successfully")
	except Exception as e:
	    print(e,"REVIEWS table could not be created!")

	conn.commit()
	conn.close()


"""
Making the ratings table for the database. This will store the ratings
provided by the user. 
The table will have the following columns: 
1) USERID:  The id of the user that provided the rating.
2) BOOKID:  The id of the book that the rating belongs to. 
3) RATINGS: Ratings out of 5.  
"""


def make_ratings_table():
	conn = sqlite3.connect(path)
	try:
	    conn.execute('''CREATE TABLE IF NOT EXISTS RATING
	             (
	             USERID                  INT                 NOT NULL,
	             BOOKID                  INT                 NOT NULL,
	             RATINGS                 INT                 NOT NULL
	             );''')
	    print("RATINGS table created successfully")
	except Exception as e:
	    print(e,"RATINGS table could not be created!")
	
	conn.commit()
	conn.close()


if __name__ == '__main__':
	make_user_table()
	make_security_table()
	make_collections_table()
	make_books_table()
	make_reviews_table()
	make_ratings_table()

	## FIlling all the books.
