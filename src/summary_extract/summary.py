from bs4 import BeautifulSoup
import requests
import PyPDF2
import docx
import multiprocessing as mp
from datetime import datetime
import os

import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
from transformers import BartTokenizer, BartForConditionalGeneration

import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from string import punctuation
from heapq import nlargest

class Summarization:
    def __init__(self, doc_option):
        if doc_option == 1:
            # self.pdf = "data/offer_letter.pdf"
            self.pdf = "/Users/alanzablake/Downloads/s41347-020-00134-x.pdf"
        elif doc_option == 2:
            self.docx = "data/final_paper.docx"
        elif doc_option == 3:
            self.url = input("Please enter the url: ")
        self.file_name = f"docs/{datetime.now().strftime('%Y-%m-%d')}_summary.txt" # default file name
        self.content = ""
        self.bart_tokenizer = BartTokenizer.from_pretrained('facebook/bart-large-cnn')
        self.bart_model = BartForConditionalGeneration.from_pretrained('facebook/bart-large-cnn')
        self.nlp = spacy.load("en_core_web_sm")
        if not os.path.exists("docs"):
            os.mkdir("docs")
    def spacy_tokenizer(self, text):
        try:
            # Process the text using spaCy
            doc = self.nlp(text)
            return doc.sents
        except Exception as error:
            print(f"Error tokenizing summary: {error}")
    def get_url_content(self):
        try:
            start_time = datetime.now()
            response = requests.get(self.url)
        except Exception as error:
            print(f"Error retrieving url: {error}")
        try:
            soup = BeautifulSoup(response.text, 'html.parser')
            summary_title = soup.find('title').text
            summary_title = summary_title.strip()
            self.file_name = "docs/{:<0.50}_summary.txt".format(summary_title)
            for paragraph in soup.find_all('p'):
                text = " ".join(paragraph.text.split())
                sentences = self.spacy_tokenizer(text)
                for sent in sentences:
                    self.content += sent.text + "\n"
            print("Content extracted successfully.")
            print(f"Runtime of getting the content: {datetime.now() - start_time}")
        except Exception as error:
            print(f"Error getting url content: {error}")
            os._exit(1)
    def get_docx_content(self):
        try: 
            start_time = datetime.now()
            doc = docx.Document(self.docx)
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text = " ".join(paragraph.text.split())
                    sentences = self.spacy_tokenizer(text)
                    for sent in sentences:
                        self.content += sent.text + "\n"
            print("Content extracted successfully.")
            print(f"Runtime of getting the content: {datetime.now() - start_time}")
        except Exception as error:
            print(f"Error getting word document content: {error}")
            os._exit(1)

    def get_pdf_content(self):
        try:
            start_time = datetime.now()
            with open(self.pdf, "rb") as file:
                reader = PyPDF2.PdfReader(file)
                if reader.is_encrypted:
                    password = input("File is encrypted. Please enter a password: ")
                    if reader.decrypt(password):
                        for page_num in range(len(reader.pages)):
                            page = reader.pages[page_num]
                            if page.extract_text().strip():
                                text = " ".join(page.extract_text().split())
                                sentences = self.spacy_tokenizer(text)
                                for sent in sentences:
                                    self.content += sent.text + "\n"
                    else:
                        print("Incorrect password. Unable to decrypt file.")
                else:
                    for page_num in range(len(reader.pages)):
                        page = reader.pages[page_num]
                        self.content += page.extract_text()
            print("Content extracted successfully.")
            print(f"Runtime of getting the content: {datetime.now() - start_time}")
        except Exception as error:
            print(f"Error getting pdf content: {error}")
            os._exit(1)
    def extractive_summarize(self):
        try:
            percentage = 0.25
            stopwords = list(STOP_WORDS)
            doc = self.nlp(self.content)

            tokens = [token.text for token in doc]
            word_frequencies = {}

            for word in doc:
                if word.text.lower() not in stopwords:
                    if word.text.lower() not in punctuation:
                        if word.text not in word_frequencies.keys():
                            word_frequencies[word.text] = 1
                        else:
                            word_frequencies[word.text] += 1
            maximum_frequency = max(word_frequencies.values())
            for word in word_frequencies.keys():
                word_frequencies[word] = (word_frequencies[word]/maximum_frequency)

            sent_list = [sent for sent in doc.sents]
            sent_scores = {}
            for sent in sent_list:
                for word in sent:
                    if word.text.lower() in word_frequencies.keys():
                        if sent not in sent_scores.keys():                            
                            sent_scores[sent]=word_frequencies[word.text.lower()]
                        else:
                            sent_scores[sent]+=word_frequencies[word.text.lower()]
            len_tokens=int(len(sent_list)*percentage)
            # Summary for the sentences with maximum score. Here, each sentence in the list is of spacy.span type
            summary = nlargest(n = len_tokens, iterable = sent_scores,key=sent_scores.get)
            final_summary=[word.text for word in summary]
            with open(self.file_name, "w") as out_file:
                for sum in final_summary:
                    out_file.write(sum)
            print(f"Extractive summary extracted to {self.file_name}")
        except Exception as error:
            print(f"Error with getting the extractive summary: {error}")
            os._exit(1)
    def summarize_content(self, content, out_file):
        try:
            input_ids = self.bart_tokenizer.encode(content, return_tensors='pt')
            summary_ids = self.bart_model.generate(input_ids, num_beams=4, max_length=250, early_stopping=True)
            summary = self.bart_tokenizer.decode(summary_ids[0], skip_special_tokens=True)
            sentences = self.spacy_tokenizer(summary)
            summary_text = "\n".join([sent.text for sent in sentences])
            out_file.write(summary_text + "\n")
            out_file.flush()
        except Exception as error:
            print(f"Error getting summarizing content: {error}")
    def chunk_split(self, max_length=1024):
        sentences = self.spacy_tokenizer(self.content)
        chunks = []
        current_chunk = ""

        for sent in sentences:
            if len(current_chunk) + len(sent.text) + 1 > max_length:
                chunks.append(current_chunk.strip())
                current_chunk = sent.text + " "
            else:
                current_chunk += sent.text + " "

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks
    def abstractive_summarize(self):
        try:
            chunk_size = 1024 # max tokens the model allows
            if len(self.content) > chunk_size:
                chunks = self.chunk_split(chunk_size)
                max_threads = mp.cpu_count()
                with open(self.file_name, "w") as out_file:
                    with ThreadPoolExecutor(max_workers=max_threads) as executor:
                        retrieval_tasks = []
                        for i in range(len(chunks)):
                            task = executor.submit(self.summarize_content, chunks[i], out_file)
                            retrieval_tasks.append(task)
                    concurrent.futures.wait(retrieval_tasks)
            else:
                with open(self.file_name, "w") as out_file:
                    self.summarize_content(self.content, out_file)
            print(f"Abstractive summary extracted to {self.file_name}")
        except Exception as error:
            print(f"Error with getting the abstractive summary: {error}")
            os._exit(1)