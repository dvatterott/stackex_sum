
<p align="center">
  <img src="/static/web_images/website_sifting.png"/>
</p>

Stackoverflow is a great resource with an amazing amount of content, which makes it extremely useful, but also makes its hard to use. This is especially true for beginners who do not know where to look for helpful and succinct answers.

Sifting the Overflow is designed specifically for helping users identify the helpful portions of answers to Stackoverflow questions about python. To collect the data used design this browser extension, I queried the [stackoverflow api](https://api.stackexchange.com/docs) using the python library [py-stackexchange](https://github.com/lucjon/Py-StackExchange). I collected every Stackoverflow question about python asked during 2015 (almost 140,000) and the associated answers (almost 500,000!).

## Data Prep and Preprocessing

I stored my data in a [postgres database](https://www.postgresql.org/), and queried the database for the data used to train my model. Over the course of this project, I tried a variety of models; the first model I trained was based on a [bag-of-words (bow)](http://scikit-learn.org/stable/tutorial/text_analytics/working_with_text_data.html#bags-of-words) representation of the data.

Preparing the data for my model involved a number of preprocessing steps such as lowering the case of all the letters, tokenizing the answers (I used the [regular expression](http://regexr.com/) '/w+'), removing [stopwords](http://nlp.stanford.edu/IR-book/html/htmledition/dropping-common-terms-stop-words-1.html), removing numbers, and [stemming](http://nlp.stanford.edu/IR-book/html/htmledition/stemming-and-lemmatization-1.html) the words. Throwing away all this information might seem a little funny, but the idea is to make this task as easy as possible for a computer. You have tons of experience with language, so you've learned that a word means basically the same thing regardless of its case (e.g., THIS SENTENCE STILL MAKES SENSE). Computers must learn *case invariance*, and by removing case, I prevent the computer from having to go through this learning experience.

The final preprocessing step was to vectorize the words, which means that I assigned a different number to each distinct word. For example, the word python might be number 8. Whenever python appears in an answer, it's replaced by the number 8. For each answer I then count the number of times each distinct word appeared in that answer (maybe now you see why I wanted to shed as many meaningless words as possible), and this vector (the number of times each possible word appeared) is how I represented each Stackoverflow answer... well not quite, I also used [tf-idf](https://lizrush.gitbooks.io/algorithms-for-webdevs-ebook/content/chapters/tf-idf.html) to penalize words that appear frequently because of the specific topic that all my text discusses (Python programming). For example, you might expect Python to appear in every answer and not be effective at discriminating between good and bad python answers.  

<p align="center">
  <img src="/static/web_images/both_problem.png"/>
</p>

I've written a lot about what features (words) I will use to predict the helpfulness of an answer, but I haven't said anything about how I will define helpful and unhelpful answers. Stackoverflow is full of answers, the majority of which (see figure above) are unhelpful. This plot is a histogram with the rating of Stackoverflow responses (upvotes-downvotes) on the x-axis, and my goal is to identify the helpful responses. Most answers receive no upvotes, but a few answers receive many. It turns out that most these highly rated answers are also highly viewed questions (see figure below). This could be because the answers are so great, or, maybe, its because Stackoverflow visitors frequently need an answer to these questions. It's hard to differentiate between these possibilities. One strategy I used to avoid this question was to treat any answer with a score of two or more as a helpful answer and any answer with a score of less than 2 as an unhelpful answer. I tried some other strategies that I am not discussing here, but please reach out to me if you're interested.

<p align="center">
  <img src="/static/web_images/Score_by_View_Slide.png"/>
</p>

## Modeling

After all this preprocessing, it was finally time to try a model. The first model I tried was a logistic regression with [l2 regularization](https://www.quora.com/Why-is-L1-regularization-better-than-L2-regularization-provided-that-all-Norms-are-equivalent). I didn't experiment much with whether l1 or l2 regularization would be better, because over-fitting this dataset was never a problem.  

<p align="center">
  <img src="/static/web_images/LogReg_Perf2.png"/>
</p>

Above I depict a [confusion matrix](https://docs.wso2.com/display/ML100/Model+Evaluation+Measures) with my model's performance. The confusion matrix demonstrates that my model is much better at identifying unhelpful responses than helpful answers. This is because the unhelpful answers are so much more common than the helpful answers. Nonetheless, the model still guesses helpful responses more often than it would by chance (20%).

<p align="center">
  <img src="/static/web_images/lg_beta_weights.png"/>
</p>

Above, I depict the beta weights of the twenty most impactful words. The greater the beta weight, the more likely an answer with that word was to be helpful. For instance, answers with the word "import" are more likely to be helpful. Most these words look like words that would appear in code (e.g., import, np, return), suggesting that people find answers with code more helpful!

I played around with more complex models that use this bow feature set, but none of the models provided dramatic improvements over the logistic regression. I decided to try a different representation of the words. Instead of using a plain bow, I decided to try embedding each word in a [word2vec](https://www.tensorflow.org/tutorials/word2vec/) type embedding. word2vec assigns each word a position in a hypothetical space, which conveys the meaning of the words. In this space, words with similar meanings are near each other and words with different meanings are far from each other. For instance, dog and cat should be closer to each other than dog and computer. By using a word2vec embedding, I save my computer some of the hardship of having to learn the meaning of words, because this [hard work was done by someone else's computer](https://www.youtube.com/watch?v=N5b4_5hvOog). I specifically used the [GloVe embedding](http://nlp.stanford.edu/projects/glove/) because it was trained on the [common crawl](http://commoncrawl.org/), which I thought would be a relatively fair representation of Stackoverflow responses. Check out this awesome [tutorial](https://blog.keras.io/using-pre-trained-word-embeddings-in-a-keras-model.html) for how to instantiate embeddings in a model.

## Recurrent Neural Net

Even with my data in the embedding matrix, my model didn't see any dramatic improvements. I next tried to see if representing the order of words would help improve my model. In all the previous models, words were represented as simply present or absent, and the order that the words appeared in did not influence whether my model thought the answer was helpful or not. This is [not true](https://www.usingenglish.com/forum/threads/159727-The-importance-of-word-order) of language generally, but if you saw a group of words, you might be able to guess what they were talking about... especially if you were an expert in the topic that the words describe. This would be much harder if you were not an expert in this topic. Because of this *expertise effect* I thought representing word order could be so useful for discriminating helpful and unhelpful answers - since when teaching someone something, the order in which topics are taught is extremely important.

[Recurrent Neural Networks](http://neuralnetworksanddeeplearning.com/chap6.html) ([here](http://colah.github.io/posts/2015-08-Understanding-LSTMs/)'s another awesome link on RNNs) are a powerful class of models that can represent the order that items occur. The next model I trained was a recurrent neural network, and this model is the one that sifting the overflow currently uses. The model consists of an embedding layer that projects to a layer of [gated recurrent units](http://www.wildml.com/2015/10/recurrent-neural-network-tutorial-part-4-implementing-a-grulstm-rnn-with-python-and-theano/), which then then feeds to the output layer.

Below, I depict the performance of my recurrent neural net. While, the model isn't perfect, it yields an increase of the precision of the model. This means that the model rarely says that unhelpful answers are helpful. Recall is still a problem (the model frequently says helpful answers are unhelpful), but the model has improved its ability to differentiate between helpful and unhelpful answers.

<p align="center">
  <img src="/static/web_images/gru_confmat.png"/>
</p>

If you liked this post, check out my [blog](http://www.danvatterott.com/blog/) where I regularly post similar content.
