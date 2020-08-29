'''
This code insterts a new user into the database this functionis to be triggered from the signup page. 
The username should be unique and returns 0 if an already existing username is inserted!

This is how to run the code: 

- enter_new_user(username='roy77', password='password123', interests='DARK, humour')

*** To check the users in database, just use get_users() function! ***

'''
import sqlite3


def get_users():
    con = sqlite3.connect('Database/readrecommend.db')
    sql = con.execute("SELECT * from USERS")
    table = sql.fetchall()
    con.close()
    return table

def enter_new_user(username, password, interests):
    
    con = sqlite3.connect('Database/readrecommend.db')
    sql = ''' INSERT INTO USERS(USERID,USERNAME,PASSWORD,INTERESTS)
                  VALUES(?,?,?, ?) ''' 
    cur = con.cursor()
    
    current_table = get_users()
    
    ## checking if the username already exists
    for user in current_table:
        if username == user[1]:
            print("USER ALREADY EXISTS!")
            return 0
    
    ## Get the new Id for the new user. 
    new_id = len(current_table) + 1    
    
    ## Insert the query. 
    cur.execute(sql, (new_id, username, password, interests.lower()))
    con.commit()
    con.close()
    return 1



'''
This function will be triggered when a new user has been made. The security questions will be stored and used if 
user ever forgets the password. 

To enter a new security question: 

run this line:
- enter_security(userid=1, question1='What is your birthplace?', answer1='Mumbai', question2='What is your pets name?', answer2='Leo')

'''

def get_security_questions():
    con = sqlite3.connect('Database/readrecommend.db')
    sql = con.execute("SELECT * from SECURITY")
    table = sql.fetchall()
    con.close()
    return table


def enter_security(username,question1, answer1):

    con = sqlite3.connect('Database/readrecommend.db')

    sql = ''' INSERT INTO SECURITY(USERNAME,QUESTION1,ANSWER1)
                  VALUES(?,?,?) ''' 

    cur = con.cursor()


    cur.execute(sql, (username,question1, answer1) )
    con.commit()
    con.close()
    return 1



