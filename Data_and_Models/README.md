### 1/24/17
the data in this folder is from ~28k python questions.

this is not the data I intend to use in this project!!!

I am putting the data for this project in a posgresql table called stack_exchange_db
The database is composed of two tables - question_table and answer_table.
The database is owned by the user dan-laptop

question_table is composed of (id serial, q_id integer PRIMARY KEY, word_vec varchar, score integer, view_count integer);
answer table is composed of (id serial PRIMARY KEY, a_id integer, q_id integer, word_vec varchar, score integer);
This data was downloaded running the script Download_StackOverflow.py.

Its stackoverflow questions with the tags python and numpy. There should be just under 29k questions in this set.

### 1/24/17 - 5pm.
Never mind! the data is now python questions asked during 2015. I thought 2015 because it should be enough time to rate the questions and such.
https://api.stackexchange.com/docs/questions#pagesize=100&fromdate=2015-01-01&todate=2016-01-01&order=desc&sort=creation&tagged=python&filter=default&site=stackoverflow&run=true

### 1/26/17 - 8am.
Just added a logistic regeression model (named lin_reg_model.pkl) to this folder. This model was created in the notebook Modeling/Classifying_Answers.ipynb
This model uses a bag of words input with tf-idf the objects that perform count vectorization and tfidf are also in this folder (count_vec.pkl and tfidf_tansformer.pkl)
Beware. The count vectorization transformer (unigrams and bigrams) takes awhile to load.
All these can be loaded with joblib from sklearn.externals.

### 1/27/17
I am downloading new data from the stackoverlow website (see notes.txt). The csvs Python_2015_x.csv will be all 2015 questions!!! (api was being mean before and I got as many as I could)
Never mind! Im staying with the old data! The new data does not have comments. Thank god I didn't drop the database!
I am updating the new database though. Im just going to let it slowly hit the stackoverflow system until i get all of them.

### 2/1/17
Changed the count vectorizer to just unigrams. Not much of a decrease in accuracy, but much quicker to load.

### 2/2/17
Added data (weights+vectorizer) for my RNN model.

### 2/3/17
Moved all items over 100mb ~/Insight/stackex_sum_noGit because these files are too big for github. :( Let me know if you want to use them.
