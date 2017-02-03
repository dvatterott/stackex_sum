#################### import all the libraries that ill need ###########
import pandas as pd
import numpy as np
import stackexchange

from bs4 import BeautifulSoup
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from nltk import sent_tokenize

from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.linear_model import SGDClassifier
from sklearn.externals import joblib

from keras.preprocessing.sequence import pad_sequences
from keras.preprocessing.text import text_to_word_sequence, Tokenizer
from keras.layers import Dense, Input, GRU, Embedding
from keras.models import Model
import six.moves.cPickle as cPickle

import re

############## Set up StackExchange API ################
class setup_se_api_requests:
    def __init__(self,impose_throttling=True,throttle_stop=False):
        self.api_key = '5*wCDZgONnIJ*aiaYeKjQQ(('

        so = stackexchange.Site(stackexchange.StackOverflow,self.api_key)
        so.be_inclusive()
        so.impose_throttling = impose_throttling
        so.throttle_stop = throttle_stop
        self.so = so

    def stack_exchange_query(self):
        return self.so


########## the function that i wrote for getting stack exchange info#######
p_stemmer = PorterStemmer()
tokenizer = RegexpTokenizer('\w+')
highlight_start = '<span class="highlightme">'
highlight_end = '</span>'

class acquire_SE_info:
    def __init__(self,so,q_id, search=True,sentences=False):
        if search == True:
            self.question = so.question(q_id)
            self.id = q_id
        else:
            self.question = q_id
            self.id = q_id.id

        self.question_tokens = []
        self.tags = self.question.tags
        self.answers_dict = {}
        self.score = 0
        self.view_count = self.question.view_count
        self.url = self.question.link
        self.sentences = sentences

    def fetch_and_clean(self,text,model_prep=False):
        raw = BeautifulSoup(text, "lxml").get_text()
        raw = raw.lower()

        if model_prep == False:
            tokens = text_to_word_sequence(raw)
        elif model_prep == True:
            tokens = tokenizer.tokenize(raw)
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

    def sentence_finder(self,text,good_answers,class_type):
        for tags in text.find_all("td", class_=class_type):
            for i,good_string in enumerate(good_answers):
                good_string = tokenizer.tokenize(good_string)
                search_str = ''.join(['('+x+').*' for x in good_string if len(x) > 2])
                search_str = search_str[:-2]
                new_text = ''.join([str(x) for x in tags.contents])
                m = re.search(search_str, new_text, flags=re.IGNORECASE|re.DOTALL)
                if not m: continue
                start, end = m.start(), m.end()
                print('-----------')
                print(search_str)
                print('-----------')
                print(new_text[start:end])
                tags.clear()

                replacement_text = new_text[start:end]
                pre_start = re.finditer(r'<code>|<p>',replacement_text)
                if not pre_start:
                    pass
                else:
                    for ii,start_i in enumerate(pre_start):
                        replacement_text = replacement_text[:start_i.end()+(ii*len(highlight_start))] \
                        + highlight_start + replacement_text[start_i.end()+(ii*len(highlight_start)):]
                pre_end = re.finditer(r'</code>|</p>',replacement_text)
                if not pre_end:
                    pass
                else:
                    for ii,end_i in enumerate(pre_end):
                        replacement_text = replacement_text[:end_i.start()+(ii*len(highlight_end))] \
                        + highlight_start + replacement_text[end_i.start()+(ii*len(highlight_end)):]

                temp_text = new_text[:start] + highlight_start + \
                    replacement_text + highlight_end + new_text[end:]

                tags.append(BeautifulSoup(temp_text, 'html.parser'))
                good_answers.pop(i)
        return (text,good_answers)

    def highlight_good_answers(self,text,good_answers):
        #text should be a beautiful soup object
        text, good_answers = self.sentence_finder(text,good_answers,'comment-text')
        text, good_answers = self.sentence_finder(text,good_answers,'answercell')

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

############### function for finding helpful sentences #############
class helpful_sentences:
    def __init__(self,model=None,verbose=1):
        self.model = model
        if self.model == 'Linear':
            self.lg = joblib.load('./Data_and_Models/lin_reg_model.pkl')
            self.vectorizer = joblib.load('./Data_and_Models/count_vec.pkl')
            self.tf_transformer = joblib.load('./Data_and_Models/tfidf_tansformer.pkl')
            if verbose: print('Loaded pickles')
        elif self.model == None:
            self.MAX_SEQUENCE_LENGTH = 200
            self.EMBEDDING_DIM = 300
            self.word_index_length = 374000

            embedding_layer = Embedding(self.word_index_length + 1,
                                        self.EMBEDDING_DIM,
                                        input_length=self.MAX_SEQUENCE_LENGTH,
                                        trainable=False)

            sequence_input = Input(shape=(self.MAX_SEQUENCE_LENGTH,), dtype='int32')
            embedded_sequences = embedding_layer(sequence_input)
            x = GRU(128, dropout_W=0.2, dropout_U=0.2)(embedded_sequences)
            preds = Dense(2, activation='softmax')(x)

            mymodel = Model(sequence_input, preds)
            mymodel.compile(loss='categorical_crossentropy',
                          optimizer='adam',
                          metrics=['acc'])
            mymodel.load_weights('./Data_and_Models/stackex_gru.h5')
            print('Gimme that overflow!')
            self.vectorizer = cPickle.load(open('./Data_and_Models/rnn_tokenizer.pkl', 'rb'), encoding='latin1')
            self.lg = mymodel

    def find_helpful_sentences(self,StackObj, help_threshold=-0.5,print_on=False):
        new_answer_dict = StackObj.answers_dict
        answers = []
        good_sent = []
        good_sent_text = []
        good_raw = []
        good_toks = []

        for keys in new_answer_dict:
            a_dict = new_answer_dict[keys]
            a_vect = a_dict['tokens']
            a_raw = a_dict['raw']
            just_tok = [StackObj.fetch_and_clean(x,model_prep=False) for x in a_vect]

            if self.model == 'Linear':
                tokens = [','.join(StackObj.fetch_and_clean(x, model_prep=True)) for x in a_vect]

                #transform each word vector into the count vector (bow)
                x_count = self.vectorizer.transform(tokens)
                x_tf = self.tf_transformer.transform(x_count)
                y_pred = self.lg.decision_function(x_tf)
            else:
                just_tok = [self.vectorizer.texts_to_sequences(x) for x in just_tok]
                if len(just_tok[0]) > 1:
                    temp = []
                    for items in just_tok: temp.append([x[0] for x in items if len(x)>0])
                    just_tok = temp
                else:
                    just_tok = [[x[0] for x in just_tok if len(x)>0]]

                padded_seq = pad_sequences(just_tok,maxlen=self.MAX_SEQUENCE_LENGTH)
                seq = np.array(padded_seq)
                y_pred = self.lg.predict(seq)
                y_pred = y_pred[:,1] - y_pred[:,0]

            print(y_pred)
            answers.append(y_pred)

            if len(np.where(y_pred>=help_threshold)[0])>0:
                find_good_sent = np.where(y_pred>=help_threshold)[0][0]
                good_sent.append(find_good_sent)
                good_sent_text.append(a_vect[find_good_sent])
                good_raw.append(a_raw[find_good_sent])
                good_toks.append(just_tok[find_good_sent])
                if print_on == True: print(a_vect[find_good_sent])
        answer_dict = {'prediction':answers,\
                        'good_sent_num':good_sent,\
                        'good_sent_text':good_sent_text,\
                        'good_toks': good_toks,\
                        'good_raw':good_raw}
        return answer_dict
