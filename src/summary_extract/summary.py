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
    def __init__(self, doc_option, doc_input):
        if doc_option == 1:
            self.pdf = doc_input
        elif doc_option == 2:
            self.docx = doc_input
        elif doc_option == 3:
            self.url = doc_input
        self.file_name = f"docs/{datetime.now().strftime('%Y-%m-%d')}_summary.txt" # default file name
        self.content = "" # initializing content
        self.pdf_reader = None # initalizing reader
        # bart tokenizer and model for abstractive
        self.bart_tokenizer = BartTokenizer.from_pretrained('facebook/bart-large-cnn')
        self.bart_model = BartForConditionalGeneration.from_pretrained('facebook/bart-large-cnn')
        self.nlp = spacy.load("en_core_web_sm") # loading english lang model
        if not os.path.exists("docs"):
            os.mkdir("docs")
    def spacy_tokenizer(self, text): # efficient tokenizer using the library spaCy
        try:
            # Process the text using spaCy
            doc = self.nlp(text)
            return doc.sents
        except Exception as error:
            print(f"Error tokenizing summary: {error}")
    def get_url_content(self): # extracting url content
        try:
            start_time = datetime.now()
            response = requests.get(self.url)
            soup = BeautifulSoup(response.text, 'html.parser')
            summary_title = soup.find('title').text
            summary_title = summary_title.strip()
            self.file_name = "docs/{:<0.50}_summary.txt".format(summary_title)
            for paragraph in soup.find_all('p'):
                text = " ".join(paragraph.text.split())
                sentences = self.spacy_tokenizer(text)
                for sent in sentences:
                    self.content += sent.text + "\n"
            content_msg = f"Content extracted successfully.\nRuntime of getting the content: {datetime.now() - start_time}"
            return (content_msg, 0)
        except Exception as error:
            error_msg = f"Error getting url content: {error}"
            return (error_msg, 1)
    def get_docx_content(self): # extracting word document content
        try: 
            start_time = datetime.now()
            doc = docx.Document(self.docx)
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text = " ".join(paragraph.text.split())
                    sentences = self.spacy_tokenizer(text)
                    for sent in sentences:
                        self.content += sent.text + "\n"
            content_msg = f"Content extracted successfully.\nRuntime of getting the content: {datetime.now() - start_time}"
            return (content_msg, 0)
        except Exception as error:
            error_msg = f"Error getting word document content: {error}"
            return (error_msg, 1)
    def is_pdf_encrypted(self): # function that checks for an encrypted file
        try:
            self.pdf_reader = PyPDF2.PdfReader(self.pdf)
            if self.pdf_reader.is_encrypted:
                return True
            else:
                return False
        except Exception as error:
            error_msg = f"Error checking pdf encryption: {error}"
            return error_msg
    def decrypt_pdf(self, password): # function to return whether the password is correct or not
        try:
            if self.pdf_reader.decrypt(password):
                return True
            else:
                return False
        except Exception as error:
            error_msg = f"Error encrypting pdf document: {error}"
            return error_msg
    def get_pdf_content(self): # extracting content for a pdf file
        try:
            start_time = datetime.now()
            for page_num in range(len(self.pdf_reader.pages)):
                page = self.pdf_reader.pages[page_num]
                if page.extract_text().strip():
                    text = " ".join(page.extract_text().split())
                    sentences = self.spacy_tokenizer(text)
                    for sent in sentences:
                        self.content += sent.text + "\n"
            content_msg = f"Content extracted successfully.\nRuntime of getting the content: {datetime.now() - start_time}"
            return (content_msg, 0)
        except Exception as error:
            error_msg = f"Error getting pdf content: {error}"
            return (error_msg, 1)
    def extractive_summarize(self): # extractive model that creates a summary that highlights the most important parts of the content
        try:
            percentage = 0.25
            stopwords = list(STOP_WORDS)
            doc = self.nlp(self.content)

            tokens = [token.text for token in doc] # tokenizing the content
            word_frequencies = {}

            for word in doc: # the frequency of each word is calculated 
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
            for sent in sent_list: # sentences are being scored based on the word frequencies
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
            summary_msg = f"Extractive summary extracted to {self.file_name}"
            print(summary_msg)
            return (summary_msg, 0)
        except Exception as error:
            error_msg = f"Error with getting the extractive summary: {error}"
            return (error_msg, 1)
    def summarize_content(self, content, out_file): # function to summarize content using the bart model
        input_ids = self.bart_tokenizer.encode(content, return_tensors='pt')
        summary_ids = self.bart_model.generate(input_ids, num_beams=4, max_length=250, early_stopping=True)
        summary = self.bart_tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        sentences = self.spacy_tokenizer(summary)
        summary_text = "\n".join([sent.text for sent in sentences])
        out_file.write(summary_text + "\n")
        out_file.flush()
    def chunk_split(self, max_length):
        sentences = self.spacy_tokenizer(self.content)
        chunks = []
        current_chunk = ""

        for sent in sentences:
            if len(current_chunk) + len(sent.text) + 1 > max_length:
                # if the sentences and the current chunk is more than 1024 tokens then a new chunk has to be created and the current chunk is added to the chunk list
                chunks.append(current_chunk.strip())
                current_chunk = sent.text + " "
            else:
                # the sentence gets added to the current chunk if it doesn't exceed the max length of tokens
                current_chunk += sent.text + " "

        if current_chunk: # the most recent chunk is being appended
            chunks.append(current_chunk.strip())

        return chunks
    def abstractive_summarize(self): # abstractive bart model that paraphrases the content
        try:
            chunk_size = 1024 # max tokens the model allows
            if len(self.content) > chunk_size: # if the content is more than the model allows it has to be chunked
                chunks = self.chunk_split(chunk_size) # split into chunks based on sentences
                max_threads = mp.cpu_count()
                with open(self.file_name, "w") as out_file:
                    with ThreadPoolExecutor(max_workers=max_threads) as executor: # chunks are summarized in parallel
                        retrieval_tasks = []
                        for i in range(len(chunks)):
                            task = executor.submit(self.summarize_content, chunks[i], out_file)
                            retrieval_tasks.append(task)
                    concurrent.futures.wait(retrieval_tasks)
            else: # if the content is less than 1024 tokens it can just be summarized and written to the file
                with open(self.file_name, "w") as out_file:
                    self.summarize_content(self.content, out_file)
            summary_msg = f"Abstractive summary extracted to {self.file_name}"
            print(summary_msg)
            return (summary_msg, 0)
        except Exception as error:
            error_msg = f"Error with getting the abstractive summary: {error}"
            return (error_msg, 1)