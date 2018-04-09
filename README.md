# hate-speech-detection

This project aims to detect hate speech on twitter. The goal is to leverage user information, in addition to text, to predict if a tweet is hateful or not. The classifier is a feed forward neural network, built with Tensorflow. It will input word embeddings of the tweet's text and a feature vector with information about the user. The model architecture is fixed, and I vary the features in the user feature vector to find the best set of predictors. 

The data the model is trained on comes from https://github.com/ZeerakW/hatespeech. Many other classifiers use this data, and I hope to build one that competes with the state-of-the-art. 
