############## Set up StackExchange API ################
import stackexchange

api_key = '*****'

so = stackexchange.Site(stackexchange.StackOverflow,api_key)
so.be_inclusive()
so.impose_throttling = True
so.throttle_stop = False


############# build object for gathering+cleaning stackexchange data############
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from nltk import sent_tokenize
import re

from keras.preprocessing.text import text_to_word_sequence
# from keras.preprocessing.text import Tokenizer
# MAX_SEQUENCE_LENGTH = 1000
# MAX_NB_WORDS = 40000
# EMBEDDING_DIM = 300
# tokenizer = Tokenizer(nb_words=MAX_NB_WORDS)

p_stemmer = PorterStemmer()
#from nltk.tokenize import RegexpTokenizer
#tokenizer = RegexpTokenizer('\w+')

class acquire_SE_info:
    def __init__(self,so,q_id, search=True,sentences=False):
        if search == True:
            self.question = so.question(q_id)
            self.id = q_id
        else:
            self.question = q_id
            self.id = q_id.id

        self.question_tokens = []
        self.answers_dict = {}
        self.score = 0
        self.view_count = self.question.view_count
        self.url = self.question.link
        self.sentences = sentences

    def fetch_and_clean(self,text,model_prep=False):
        raw = BeautifulSoup(text, "lxml").get_text()
        raw = raw.lower()
        # tokens = tokenizer.tokenize(raw)
        tokens = text_to_word_sequence(raw)

        if model_prep == True:
            tokens = [word for word in tokens if not word.isdigit()]
            tokens = [word for word in tokens if word not in stopwords.words('english')]
            tokens = [p_stemmer.stem(i) for i in tokens]
        return tokens

    def sentences_tokenization(self,text):
        raw = BeautifulSoup(text, "lxml").get_text()
        raw = raw.lower()
        sentences = sent_tokenize(raw)
        return sentences

    def sentences_or_not(self,text):
        if self.sentences == False:
            output = self.fetch_and_clean(text)
        else:
            output = self.sentences_tokenization(text)
        return output

    def get_question_Info(self):
        text_source = self.question

        self.question_tokens = self.sentences_or_not(text_source.body)
        self.score = text_source.score

        return self.question_tokens

    def get_answer_Info(self):
        text_source = self.question.json

        if 'comments' in text_source.keys():
            answer_id = -1
            for text in text_source['comments']:
                answer_id += 1
                temp_dict = {}
                temp_dict['tokens'] = self.sentences_or_not(text['body'])
                temp_dict['raw'] = text['body']
                temp_dict['score'] = text['score']
                self.answers_dict[answer_id] = temp_dict
        else:
            answer_id = -1

        if 'answers' in text_source.keys():
            for text in text_source['answers']:
                answer_id += 1
                temp_dict = {}
                temp_dict['tokens'] = self.sentences_or_not(text['body'])
                temp_dict['raw'] = [text['body']]
                temp_dict['score'] = text['score']

                if 'comments' in text.keys():
                    for comments in text['comments']:
                        temp_dict['tokens'].extend(self.sentences_or_not(comments['body']))
                        temp_dict['raw'].extend(comments['body']) #was extend
                        temp_dict['score'] += comments['score']

                temp_dict['raw'] = ''.join(temp_dict['raw'])
                self.answers_dict[answer_id] = temp_dict

        return self.answers_dict

    def highlight_good_answers(self,text,good_answers):
        for good_string in good_answers:
            m = re.search('('+good_string[0]+').*('+good_string[-1]+')', text, flags=re.IGNORECASE)
            if not m: continue
            text = text.replace(m.group(0),'<span class="highlightme">'+ m.group(0) +'</span>')
        return text

    def get_comments_html(self,good_answers):
        text_source = self.question.json
        comment_list = []

        if 'comments' in text_source.keys():
            for text in text_source['comments']:
                comment_list.append(self.highlight_good_answers(text['body'],good_answers))
        return comment_list

    def get_answers_html(self,good_answers):
        text_source = self.question.json
        answer_list = []

        if 'answers' in text_source.keys():
            for text in text_source['answers']:
                temp_answer = self.highlight_good_answers(text['body'],good_answers)

                if 'comments' in text.keys():
                    for comments in text['comments']:
                        temp_answer += '<br>\n<p class="tab">'
                        temp_answer += self.highlight_good_answers(comments['body'],good_answers)
                        temp_answer += '</p>'

                answer_list.append(temp_answer)
        return answer_list


    def get_df_data(self):
        return [self.id, self.score,self.view_count,self.url]


############## create sql table ################
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import psycopg2

dbname = 'stack_exchange_rnn_db'
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

t_start = datetime.datetime(2015, 1, 1, 0, 0)
t_start_sec = (t_start-datetime.datetime(1970,1,1)).total_seconds()
t_end = datetime.datetime(2016, 1, 1, 0, 0)
t_end_sec = (t_end-datetime.datetime(1970,1,1)).total_seconds()

##################### Get data from stackexchange

added = 0

for i,question in enumerate(so.questions(tagged=['python'], pagesize=100, fromdate=t_start_sec, todate=t_end_sec)):
    time.sleep(0.1) #stackoverflow hates me :(
    StackObj = acquire_SE_info(so,question,search=False) #[python] [numpy]
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
