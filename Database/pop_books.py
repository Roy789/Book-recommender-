import sqlite3
import pandas as pd
import os

path = os.getcwd()+'/readrecommend.db'

'''
function that can be used to view the books!!
'''
def get_books():
    con = sqlite3.connect('path')

    cursorObj = con.cursor()
    sql = ''' SELECT * from BOOKS'''
    cursorObj.execute(sql)
    table = cursorObj.fetchall()
    con.close()
    return table


'''
Cleaning the genre column of the csv file!
'''
def join_genre(x):
    string = ''
    for i in eval(x).keys():
        string += i
        string += ', '
    return string


'''
This function reads the csv file and adds the books into our database!
'''
def fill_books():
    
    data = pd.read_csv("final_book_data.csv")
    con = sqlite3.connect(path)

    for ind,row in data.iterrows():
        


        sql = ''' INSERT INTO BOOKS(BOOKID,BOOKNAME,AUTHOR,AVERAGERATING,ISBN, LANGUAGE, PUBLICATIONDATE, URL,GENRE,  PUBLISHER, NUMBER_REVIEWS)
                  VALUES(?,?,?,?,?,?,?,?,?,?,?) '''
        cur = con.cursor()
        
        cur.execute(sql, (row["best_book_id"], row['title'], row['authors'], float(row['average_rating']), str(row['isbn']), str(row['language_code']), str(row['original_publication_year_x']), str(row['image_url']), str(join_genre(row['genres'])), '', row['ratings_count_x']))
    
    
    con.commit()
        

    con.close()
    print("Books filled!")
    return 1

if __name__ == '__main__':
    fill_books()