import sqlite3


def get_security_questions():
    con = sqlite3.connect('readrecommend.db')

    cursorObj = con.cursor()
    sql = ''' SELECT * from SECURITY'''
    cursorObj.execute(sql)
    table = cursorObj.fetchall()
    con.close()
    return table

def get_users():
    con = sqlite3.connect('readrecommend.db')

    cursorObj = con.cursor()
    sql = ''' SELECT * from USERS'''
    cursorObj.execute(sql)
    table = cursorObj.fetchall()
    con.close()
    return table



'''
Checking if the answer entered is correct!
'''
def check_answer(username, answer):
    users = get_users()
    for user in users:
        if user[1] == username:
            user_id = user[0]

    all_security = get_security_questions()


    for i in all_security:
        if i[0] == user_id:
            if i[2] == answer:
                return 1