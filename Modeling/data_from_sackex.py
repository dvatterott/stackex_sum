import stackexchange, os, time
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

api_key = os.environ['SO_PASSWORD']

so = stackexchange.Site(stackexchange.StackOverflow,api_key)
so.be_inclusive()
so.impose_throttling = True
so.throttle_stop = False

control_var = 'question_answer'

#############Question Scores#################
if control_var == 'question':
    count = 0
    samples = 5000
    scores = []
    for question in so.questions(tagged=['python','numpy'], pagesize=10):
       # print(question)
        assert 'python' in question.tags

        scores.append(question.score)
        count +=1
        if count % 500 == 0: print(count)
        if count == samples:break

    plt.Figure()
    sns.distplot(scores,kde=False)
    plt.show()

##########Answer Scores####################
if control_var == 'answer':
    count = 0
    samples = 5000
    answer_scores = []
    q_object = so.questions(tagged=['python','numpy'], pagesize=10)
    for question in q_object:
       # print(question)
        assert 'python' in question.tags

        if question.json['answer_count'] > 0:
            for answers in question.json['answers']:
                answer_scores.append(answers['score'])
                count +=1
                if count % 500 == 0: print(count)
                if count == samples:break
        if count == samples:break

    plt.Figure()
    sns.distplot(answer_scores,kde=False)
    plt.show()

    # sns.set_context("poster")
    # plt.Figure() #765 with two
    # sns.distplot(answer_scores,bins=40,kde=False, hist_kws={"range":(-10,30)}, norm_hist=True)
    # plt.xlim((-10,30))
    # plt.show()

##########Question by Answer Scores####################

if control_var == 'question_answer':
    count = 0
    samples =10000
    answer_scores = []
    scores = []
    for question in so.questions(tagged=['python','numpy'], pagesize=100):
        time.sleep(0.1) #stackoverflow hates me :(
        assert 'python' in question.tags

        if question.json['answer_count'] > 0:
            scores.append(question.view_count)
            count +=1

            temp_answer = -1000
            for answers in question.json['answers']:
                    if answers['score'] > temp_answer:
                        temp_answer = answers['score']

            answer_scores.append(temp_answer)

            if count % 500 == 0: print(count)
            if count == samples:break


    import numpy as np
    df = pd.DataFrame(scores,columns=['View Counts'])
    df['Answer Scores'] = answer_scores
    g = sns.jointplot("View Counts", "Answer Scores", data=df, kind="reg")
    plt.show()

    from sklearn.linear_model import LinearRegression
    lr = LinearRegression()
    lr.fit(df['View Counts'].values.reshape(-1,1),df['Answer Scores'].values.reshape(-1,1))
    lr.intercept_
    residual = df['Answer Scores'].values.reshape(-1,1) - lr.predict(df['View Counts'].values.reshape(-1,1)) + lr.intercept_
    from sklearn.externals import joblib
    joblib.dump(lr, 'view_count_model.pkl',protocol=2)
    #lr = joblib.load('view_count_model.pkl')
