### Models

* Classifying_Answers.ipynb is the code used to create a bow representation and train a logistic regression on this representation.
  I tried some more complex models using this bow representation, but the models did not perform much better than the logistic regression.

* Classifying_Answers_RNN.ipynb is the code I wrote to set up my net before throwing it on aws.
* Classifying_Answers_RNN_aws.ipynb is the code used to train my recurrent neural net. This model was trained on an aws instance with a gpu.
* Classifying_Answers_Distributions is some code where I visualize various parts of my data (how view count and answer score are distributed)
* data_from_sackex.py is a script I used to create some of the plots in my first insight presentations. visualizing scores and viewcounts again
* Interpreting Model_trainingset.ipynb uses LIME to visualize what words my model uses to discriminate between helpful and unhelpful answers
* Interpreting Model is the same as above but just looking at one stack overflow question.
* Load RNN is a script where I made sure I could load the RNN I trained on aws on my current computer
* Visualizing Important Words is code where I plot the words found by Interpreting Model_trainingset
* What_answers_model_likes.py is code that looks at what answers tend to have helpful answers (2016 data)
* What_answers_model_likes_plots plots the data from above
