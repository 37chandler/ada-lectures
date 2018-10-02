# -*- coding: utf-8 -*-
"""
Created on Tue Nov 15 18:55:11 2016

Moving some of the SQL commands into functions and putting them
in a separate library.

@author: john
"""

import sqlite3
import csv

def init_db(cur) :
    cur.execute('''DROP TABLE IF EXISTS transactions''')
    cur.execute('''CREATE TABLE transactions (
        datetime TIMESTAMP,
        register_no INTEGER,
        emp_no INTEGER,
        trans_no INTEGER,
        upc INTEGER,
        description TEXT,
        trans_type TEXT,
        trans_subtype TEXT,
        trans_status TEXT,
        department INTEGER,
        quantity REAL,
        Scale INTEGER,
        cost REAL,
        unitPrice REAL,
        total REAL,
        regPrice REAL,
        altPrice REAL,
        tax INTEGER,
        taxexempt INTEGER,
        foodstamp INTEGER,
        wicable INTEGER,
        discount REAL,
        memDiscount REAL,
        discountable INTEGER,
        discounttype INTEGER,
        voided INTEGER,
        percentDiscount REAL,
        ItemQtty REAL,
        volDiscType INTEGER,
        volume INTEGER,
        VolSpecial REAL,
        mixMatch INTEGER,
        matched INTEGER,
        memType INTEGER,
        staff INTEGER,
        numflag INTEGER,
        itemstatus INTEGER,
        tenderstatus INTEGER,
        charflag TEXT,
        varflag INTEGER,
        batchHeaderID INTEGER,
        local INTEGER,
        organic INTEGER,
        display INTEGER,
        receipt INTEGER,
        card_no INTEGER,
        store INTEGER,
        branch INTEGER,
        match_id INTEGER,
        trans_id INTEGER)''')


def populate_db(db, file_handle, delimiter,limit=None):
    
    cur = db.cursor()
        
    next(file_handle,None) # for this to work here, we always need header rows.
                 # That's my standard, so it should be fine.

    for idx, row in enumerate(file_handle.readlines()) :
        row = row.strip().replace('\"','').split(delimiter)
        cur.execute('''
            INSERT INTO transactions (datetime,register_no,emp_no,
              trans_no,upc,description,trans_type,trans_subtype,
              trans_status,department,quantity,Scale,cost,unitPrice,
              total,regPrice,altPrice,tax,taxexempt,foodstamp,wicable,
              discount,memDiscount,discountable,discounttype,voided,percentDiscount,
              ItemQtty,volDiscType,volume,
              VolSpecial,mixMatch,matched,memType,staff,numflag,itemstatus,tenderstatus,
              charflag,varflag,batchHeaderID,local,organic,display,receipt,
              card_no,store,branch,match_id,trans_id)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,
            ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,
            ?,?,?,?,?,?,?,?,?,?,?,?,?)''', row)

        if limit :
            if idx >= limit :
                break
            
    db.commit()
    