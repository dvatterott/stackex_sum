# Sifting the Overflow

[Sifting the Overflow](http://siftingtheoverflow.com/) is a chrome extension I built while a Data Science Fellow at Insight.
The link above directs users to a landing page where users can test Sifting the Overflow and the model underlying Sifting the Overflow
is explained.

Sifting the Overflow can be installed from the [chrome store](https://chrome.google.com/webstore/detail/sifting-the-overflow/japbeffaagcpbjilckaoigpocdgncind?hl=en-US&gl=US).

This repository contains code used for all aspects of the project.
* The folder Cleaning_text contains the code used to gather data from the Stackoverflow API using [Py-StackExchange](https://github.com/lucjon/Py-StackExchange).
* The folder Data_and_Models contains the models used in this project...well the ones that are small enough for github. Contact me if you would like the other models and data.
* The folder Modeling contains the files used to train the various models that Sifting the Overflow has used.
  * A Quick note about how Sifting the Overflow works. When on a stackoverflow question, the user presses the browser extension button,
    and the current page is sent to an aws instance. This aws instance contains a model trained to discriminate between helpful and unhelpful
    answers about the programming language python. The model reads each sentences in each answer (and comment), and predicts the helpfulness of the sentence.
    Stackoverflow then creates a version of the stackoverflow question page, but with the helpful sentences highlighted. The user is then redirected to this new page.
* Web_App contains Sifting the Overflow (the chrome extension), and the code used by my aws instance (written using Flask).
