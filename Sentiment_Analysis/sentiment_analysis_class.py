import torch
import torch.nn as nn
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from utils import *

class Sentiment_Analysis():

    def __init__(self, MODEL_ID, sentiments_list, pretrained=True):
        ####
        self.sents_el_en = {"χαρά": "happiness", "έκπληξη": "surprise", "λύπη": "sadness", "φόβος": "fear",
                            "θυμός": "anger", "απέχθεια": "disgust", "θετικό": "positive", "αρνητικό": "negative"}
        ###

        self.MODEL_ID = MODEL_ID

        self.pretrained = pretrained
        self.text = ""
        self.sentiments_list = sentiments_list
        self.sentiment_results = {}

        print('[INFO] Loading Sentiment-Analysis Model...')
        if self.pretrained:
            self.model = SentenceTransformer(self.MODEL_ID)

        else:
            emotion_trained_path = "new_models/emotions/"  #...path of emotion trained model
            self.emotion_model = AutoModelForSequenceClassification.from_pretrained(emotion_trained_path, num_labels=6)
            self.emotion_tokenizer = AutoTokenizer.from_pretrained(emotion_trained_path)

            sentiment_trained_path = "new_models/sentiment/"    #...path of sentiment trained model
            self.sentiment_model = AutoModelForSequenceClassification.from_pretrained(sentiment_trained_path, num_labels=2)
            self.sentiment_tokenizer = AutoTokenizer.from_pretrained(sentiment_trained_path)

    def run_sentiment_analysis(self, text, clean_text=True):

        self.text = text
        if clean_text:
            self.text = ' '.join(
                clean_doc(self.text, stop=False, unique=False, lemmatize=False, stem=False, rem_tones=False,
                          pos_tag=False))

        if self.pretrained:
            text_list = [self.text for i in range(len(self.sentiments_list))]

            embeddings1 = self.model.encode(text_list, convert_to_tensor=True)
            embeddings2 = self.model.encode(self.sentiments_list, convert_to_tensor=True)

            # Compute cosine-similarities (clone repo for util functions)
            from sentence_transformers import util

            cosine_scores = util.pytorch_cos_sim(embeddings1, embeddings2)

            # Output the pairs with their score

            for i in range(len(text_list)):
                self.sentiment_results[self.sents_el_en[self.sentiments_list[i]]] = cosine_scores[i][i].item()
               

        else:
            emotion_temp = self.emotion_tokenizer(self.text, padding=True, truncation=True, return_tensors="pt")
            sentiment_temp = self.sentiment_tokenizer(self.text, padding=True, truncation=True, return_tensors="pt")
            softmax = nn.Softmax(dim=1)
            self.emotion_model.eval()
            self.sentiment_model.eval()
            with torch.no_grad():
                emotion_logits = self.emotion_model(emotion_temp['input_ids']).logits
                emotion_norm_logits = softmax(emotion_logits).numpy().squeeze()
                for i in range(len(emotion_norm_logits)):
                    self.sentiment_results[self.sents_el_en[self.sentiments_list[i]]] = emotion_norm_logits[i].item()

                sentiment_logits = self.sentiment_model(sentiment_temp['input_ids']).logits
                sentiment_norm_logits = softmax(sentiment_logits).numpy().squeeze()
                for i in range(len(sentiment_norm_logits)):
                    self.sentiment_results[self.sents_el_en[self.sentiments_list[i + 6]]] = sentiment_norm_logits[i].item()

        return self.sentiment_results
    
