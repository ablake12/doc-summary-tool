from bs4 import BeautifulSoup
import requests

# import warnings
# from urllib3.exceptions import RequestsDependencyWarning

# # Suppress RequestsDependencyWarning
# warnings.filterwarnings("ignore", category=RequestsDependencyWarning)

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize

# from sumy.parsers.plaintext import PlaintextParser
# from sumy.nlp.tokenizers import Tokenizer
# from sumy.summarizers.lsa import LsaSummarizer
# from gensim.summarization import summarize
from summarizer import Summarizer
from transformers import T5Tokenizer, T5ForConditionalGeneration

from pysummarization.nlpbase.auto_abstractor import AutoAbstractor
from pysummarization.tokenizabledoc.simple_tokenizer import SimpleTokenizer
from pysummarization.abstractabledoc.top_n_rank_abstractor import TopNRankAbstractor

class articleHighlights:
    def __init__(self, url):
        self.url = url
        # self.file_name = ""
        self.content = ""
        self.article_title = ""
    def get_content(self):
        try:
            response = requests.get(self.url)
        except Exception as error:
            print(f"{error}")
        soup = BeautifulSoup(response.text, 'html.parser')
        self.article_title = soup.find('title').text
        for paragraph in soup.find_all('p'):
            self.content += paragraph.text + "\n"
    # def sumy_implementation(self):
    #     parser = PlaintextParser.from_string(self.content, Tokenizer("english"))

    #     # Create an LSA summarizer
    #     summarizer = LsaSummarizer()

    #     # Generate the summary
    #     summary = summarizer(parser.document, sentences_count=5)  # You can adjust the number of sentences in the summary
    #     # print(summary)
    #     # print(f"type: {type(summary[0])}")
    #     file_name = f"{self.article_title}_suny_summary.txt"

    #     with open(file_name, "w") as out_file:
    #         for sentence in summary:
    #             # print(type(sentence))
    #             out_file.write(f"{sentence}\n")
    def bert_implementation(self):
        summarizer = Summarizer()

        # Generate the summary
        summary = summarizer(self.content, min_length=50, max_length=150)  # You can adjust the min_length and max_length parameters

        file_name = f"{self.article_title}_bert_summary.txt"

        with open(file_name, "w") as out_file:
            out_file.write(f"{summary}\n")
    def tFive_implementation(self):
        # Load pre-trained T5 model and tokenizer
        model_name = "t5-small"
        tokenizer = T5Tokenizer.from_pretrained(model_name)
        model = T5ForConditionalGeneration.from_pretrained(model_name)

        # Tokenize and summarize the input text using T5
        inputs = tokenizer.encode("summarize: " + self.content, return_tensors="pt", max_length=1024, truncation=True)
        summary_ids = model.generate(inputs, max_length=150, min_length=50, length_penalty=2.0, num_beams=4, early_stopping=True)

        # Decode and output the summary
        summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)

        file_name = f"{self.article_title}_t5_summary.txt"

        with open(file_name, "w") as out_file:
            out_file.write(f"{summary}\n")
    # def gensim_implemenation(self):
    #     # Generate the summary using TextRank algorithm
    #     summary = summarize(self.content, ratio=0.3)  # You can adjust the ratio parameter based on the summary length you desire
    #     file_name = f"{self.article_title}_gensim_summary.txt"

    #     with open(file_name, "w") as out_file:
    #         out_file.write(f"{summary}\n")
    def nltk_implementation(self):
        stopWords = set(stopwords.words("english")) 
        words = word_tokenize(self.content)
        freqTable = dict()
        for word in words: 
            word = word.lower() 
            if word in stopWords: 
                continue
            if word in freqTable: 
                freqTable[word] += 1
            else: 
                freqTable[word] = 1
        sentences = sent_tokenize(self.content) 
        sentenceValue = dict()
        for sentence in sentences: 
            for word, freq in freqTable.items(): 
                if word in sentence.lower(): 
                    if sentence in sentenceValue: 
                        sentenceValue[sentence] += freq 
                    else: 
                        sentenceValue[sentence] = freq
        sumValues = 0
        for sentence in sentenceValue:
            sumValues += sentenceValue[sentence] 
        
        # Average value of a sentence from the original text 
        
        average = int(sumValues / len(sentenceValue)) 
        
        # Storing sentences into our summary. 
        summary = '' 
        for sentence in sentences: 
            if (sentence in sentenceValue) and (sentenceValue[sentence] > (1.2 * average)): 
                summary += " " + sentence 
        # print(summary)
        file_name = f"{self.article_title}_nltk_summary.txt"

        with open(file_name, "w") as out_file:
            out_file.write(f"{summary}\n")
    def pysum_implementation(self):
        # document = "Natural language generation (NLG) is the natural language processing task of generating natural language from a machine representation system such as a knowledge base or a logical form. Psycholinguists prefer the term language production when such formal representations are interpreted as models for mental representations."
        # Object of automatic summarization.
        auto_abstractor = AutoAbstractor()
        # Set tokenizer.
        auto_abstractor.tokenizable_doc = SimpleTokenizer()
        # Set delimiter for making a list of sentence.
        auto_abstractor.delimiter_list = [".", "\n"]
        # Object of abstracting and filtering document.
        abstractable_doc = TopNRankAbstractor()
        # Summarize document.
        result_dict = auto_abstractor.summarize(self.content, abstractable_doc)
        file_name = f"{self.article_title}_nltk_summary.txt"

        with open(file_name, "w") as out_file:
            for sentence in result_dict["summarize_result"]:
                out_file.write(f"{sentence}\n")
    def spacy_implementation(self):
        print() #go to medium article
url = input("Please enter the url: ")
summary = articleHighlights(url)
summary.get_content()
summary.gensim_implementation()