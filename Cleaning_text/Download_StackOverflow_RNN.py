# Set up StackExchange API
from StackExchange_Query import *
import stackexchange
import os

api_key = os.environ['SO_PASSWORD']

so = stackexchange.Site(stackexchange.StackOverflow, api_key)
so.be_inclusive()
so.impose_throttling = True
so.throttle_stop = False


############# build object for gathering+cleaning stackexchange data############


############## create sql table ################
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import psycopg2

dbname = 'stack_exchange_rnn_db2016'
q_tbname = 'question_table'
a_tbname = 'answer_table'
username = 'dan-laptop'

import os
password = os.environ['PGRES_PASSWORD']

engine = create_engine('postgresql://%s:%s@localhost:5432/%s'%(username,password,dbname))

## create a database (if it doesn't exist)
if not database_exists(engine.url):
    create_database(engine.url)
print(database_exists(engine.url))

## Now access sql db from python
con = None
connect_str = "dbname='%s' user='%s' host='localhost' password='%s'"%(dbname,username,password)
con = psycopg2.connect(connect_str)
cur = con.cursor() #create cursor for communicating with sql

Pass data to fill a query placeholders and let Psycopg perform
cur.execute("CREATE TABLE %s (id serial, q_id integer PRIMARY KEY, word_vec varchar, score integer, view_count integer);"%(q_tbname)) #note sure if this will work
cur.execute("CREATE TABLE %s (id serial PRIMARY KEY, a_id integer, q_id integer, word_vec varchar, score integer);"%(a_tbname)) #note sure if this will work
con.commit()

##################### Get 2015 in seconds #####################################
import datetime
import time
import pandas as pd

t_start = datetime.datetime(2016, 1, 1, 0, 0)
t_start_sec = (t_start-datetime.datetime(1970,1,1)).total_seconds()
t_end = datetime.datetime(2017, 1, 1, 0, 0)
t_end_sec = (t_end-datetime.datetime(1970,1,1)).total_seconds()

##################### Get data from stackexchange

added = 0

for i,question in enumerate(so.questions(tagged=['python'], pagesize=100, fromdate=t_start_sec, todate=t_end_sec, sort=stackexchange.Sort.Creation)):
    time.sleep(0.1) #stackoverflow hates me :(
    StackObj = acquire_SE_info(so,question,search=False)
    StackObj.model_prep=False #prep for rnn instead of bow
    StackObj.get_question_Info()
    StackObj.get_answer_Info()

    q_id = StackObj.id
    q_vect = StackObj.question_tokens
    q_vect = ','.join(q_vect)
    q_score = StackObj.score
    q_view = StackObj.view_count

    if i % 5000==0:
        print(i)
        print('i added %s questions so far!'% added)
        con.commit()

    #put question data into question table
    sql_query = 'SELECT view_count,score FROM question_table WHERE q_id = %s;'%str(q_id)
    question_df = pd.read_sql_query(sql_query,con)
    if len(question_df) > 0: continue
    added += 1

    cur.execute("INSERT INTO question_table (q_id, word_vec, score, view_count) VALUES (%s, %s, %s, %s);",(q_id, q_vect, q_score, q_view))

    new_answer_dict = StackObj.answers_dict
    for keys in new_answer_dict:
        a_id = keys
        a_dict = new_answer_dict[keys]
        a_vect = a_dict['tokens']
        a_vect = ','.join(a_vect)
        a_score = a_dict['score']
        #put answer data into answer table
        cur.execute("INSERT INTO answer_table (a_id, q_id, word_vec, score) VALUES (%s, %s, %s, %s);",(a_id, q_id, a_vect, a_score))

con.commit()
# ########## Close Connections ##############
cur.close()
con.close()
