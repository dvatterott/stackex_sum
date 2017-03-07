## Opening
  * Hi, my name is Dan Vatterott
  * Today, I am presenting my product, Sifting the Overflow which was designed to help people learning to program to better use the website stackoverflow.com.
## Demo
  * To introduce my product, I am going to do a quick demo. This is Stackoverflow, its a place where users can ask programming quesitons and other users will answer those questions
  * For example this user asked how to tell if a variable is a number or not.
  * Other users can answer the question, the answers are rated, and the best answers are presented first.
  * This is a great product, but the number and length of answers can be overwhelming. Sifting the Overflow is a browser extension designed to help users direct their attention to the most helpful part of answers.
  * I've already installed the browser extension here, so you can see the associated icon in the upper right hand corner. The extension is available for free on the chrome store.
  * When on a stackoverflow question, I can now click the browser extension button, and the page will be rendered with the most helpful parts of answers highlighted.
  * Sifting the overflow selects the first part of the first answer and the second part of the second answer. Lending face validity and and showing the practicality of item
## Pipeline
  * To constrain this problem, I focused on python questions. I Downloaded 150k python questions from 2015 and the associated 500k answers. Only used answers with at least 50 views.
  * Stored in a postgres database
  * I then trained a recurrent neural net to predict whether an answer would be helpful or not. I won't say more about this model now, but please ask me about it later if you're interested.

## Classification vs Regression
  * I decided to treat this as a classification problem and defined helpful answers as all answers with a score of two or more and unhelpful answers as answers with a score of less than two, which left me with 20% of answers rated as helpful.
  * I treated this problem as a classification problem because I wanted my model to learn what makes an answer helpful or not rather than what makes an answer more or less helpful. While this is a subtle difference, a classification approach better mirrors my goal of training a model that can learn the sub-components of helpful answers. I'm happy to talk about this more later if you have questions.

## Classifier Performance
  * The recurrent neural net succesfully discrimates between helpful and unhelpful answers.
  * See the AUC and the confusion matrix... so the model has succesfully learned the components of helpful answers.
  * ...Indicating that my model learned the language features that distinguish helpful and unhelpful responses

## What is the model learning!?
  * At the lowest level, these features are individual words. In an attempt to find what words tend to be associated with helpful and unhelpful answers, I used the library lime, which I am happy to talk more about later.
  * This analysis is ongoing, but so far it has found that words with a positive sentiment and code are predictive of helpful answers while plain language such as hi is predictive of an unhelpful answer. 

## Translating model into product
  * When you use siftingtheoverflow. Text from each answer is sent to my model, and the model outputs its predicted helpfulness of each sentence.
  * The key to Sifting the Overflow is that it selects the subunits, sentences, of answers that are the most helpful.
  * These helpful sentences are then highlighted.

## About me
  * I received my phd in psychology from the University of Iowa and more recently did a postdoc in cognitive neuroscience at Columbia.
  * I studied how we choose where to direct our attention, which involves trying to infer what someone is thinking from poor data such as button presses and looking behavior. I look forward to applying as a data scientist.


----------------
## Why not score relative to views
  * my ultimate goal is not to perfectly predict the score of an answer. its to simply find the components of helpful answers. So I dumbed down the answer to maximize the probability of success given this goal.
