#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul  1 13:07:34 2020

@author: pavitravobilisetty
"""

import sqlite3

def get_user_pass(username,pwd):
    con = sqlite3.connect('Database/readrecommend.db')
    sql = con.execute("SELECT count(*) from USERS where username='"+username+"' and password='"+pwd+"'")
    return sql.fetchall()[0][0]

def reset_password(username):
    con = sqlite3.connect('Database/readrecommend.db')
    sql = con.execute("SELECT * from SECURITY where username='"+username+"'")
    return sql.fetchall()

def new_pass(username,pwd):
    con = sqlite3.connect('Database/readrecommend.db')
    con.execute("UPDATE users set password='"+pwd+"' where username='"+username+"'")
    con.commit()
    con.close()