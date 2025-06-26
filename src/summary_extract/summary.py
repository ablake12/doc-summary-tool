from bs4 import BeautifulSoup
from datetime import datetime
import docx
from http import HTTPStatus
import PyPDF2
import requests
import multiprocessing as mp
import os

import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
from transformers import BartTokenizer, BartForConditionalGeneration

from heapq import nlargest
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from string import punctuation


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
            http_code = response.status_code
            if http_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                summary_title = soup.find('title').text
                summary_title = summary_title.strip()
                self.file_name = "docs/{:<0.50}_summary.txt".format(summary_title)
                for paragraph in soup.find_all('p'):
                    text = " ".join(paragraph.text.split())
                    sentences = self.spacy_tokenizer(text) # use spacy tokenizer to split text into sentences
                    for sent in sentences:
                        self.content += sent.text + "\n"
                content_msg = f"Content extracted successfully.\nRuntime of getting the content: {datetime.now() - start_time}"
                return (content_msg, 0)
            else:
                http_msg = HTTPStatus(http_code).phrase
                error_msg = f"Error retrieving content: {http_code} error - {http_msg}"
                return (error_msg, -1)
        except Exception as error:
            error_msg = f"Error getting url content: {error}"
            return (error_msg, 1)
    def get_docx_content(self): # extracting word document content
        try: 
            start_time = datetime.now()
            doc = docx.Document(self.docx)
            for paragraph in doc.paragraphs:
                if paragraph.text.strip(): # strip white spaces
                    text = " ".join(paragraph.text.split()) # cleaning up additional white spaces
                    sentences = self.spacy_tokenizer(text) # use spacy tokenizer to split text into sentences
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
            if self.pdf_reader.is_encrypted: # check to see if user is trying to access encrypted pdf
                return True
            else:
                return False
        except Exception as error:
            error_msg = f"Error checking pdf encryption: {error}"
            return error_msg
    def decrypt_pdf(self, password): # function to return whether the password is correct or not
        try:
            if self.pdf_reader.decrypt(password): # check if password is correct
                return True
            else:
                return False # password is incorrect
        except Exception as error:
            error_msg = f"Error encrypting pdf document: {error}"
            return error_msg
    def get_pdf_content(self): # extracting content for a pdf file
        try:
            start_time = datetime.now()
            for page_num in range(len(self.pdf_reader.pages)):
                page = self.pdf_reader.pages[page_num]
                if page.extract_text().strip(): # strip white spaces
                    text = " ".join(page.extract_text().split()) # cleaning up additional white spaces
                    sentences = self.spacy_tokenizer(text) # use spacy tokenizer to split text into sentences
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
            stopwords = list(STOP_WORDS) # small words to be filtered out
            doc = self.nlp(self.content) # tokenizing the content

            word_frequencies = {} # dictionary to store word frequencies

            for word in doc: # the frequency of each word is calculated 
                if word.text.lower() not in stopwords:
                    if word.text.lower() not in punctuation:
                        if word.text not in word_frequencies.keys():
                            word_frequencies[word.text] = 1 # count word for the first time if it's not a stop word or a punctuation
                        else:
                            word_frequencies[word.text] += 1 # continue to count word that's already in the dictionary
            maximum_frequency = max(word_frequencies.values())
            for word in word_frequencies.keys():
                word_frequencies[word] = (word_frequencies[word]/maximum_frequency) # divide frequencies by the word with the highest frequency to get a frequency between 0 to 1

            # sentence scores are calculated based on word frequencies to determine most important sentences for the summary
            sent_list = [sent for sent in doc.sents] # sentences in the document
            sent_scores = {} # dictionary for the scores
            for sent in sent_list: # sentences are being scored based on the word frequencies
                for word in sent: # go through each word in sentence
                    if word.text.lower() in word_frequencies.keys(): # if the word is important then we'll get its frequency and add it to the sentence score
                        if sent not in sent_scores.keys():                            
                            sent_scores[sent]=word_frequencies[word.text.lower()] # if it's the first time adding for that particular sentence
                        else:
                            sent_scores[sent]+=word_frequencies[word.text.lower()] # if it's not the first time adding for that particular sentence
            len_tokens=int(len(sent_list)*percentage) # total amount of tokens for the summary (25% of original content)

            # Summary for the sentences with maximum score. Here, each sentence in the list is of spacy.span type
            summary = nlargest(n = len_tokens, iterable = sent_scores,key=sent_scores.get) # returns the sentences with the top score based on the maximum amount of sentences allowed
            final_summary=[word.text for word in summary] # get text attribute from the final summary

            with open(self.file_name, "w") as out_file: # write final summary to file
                for sum in final_summary:
                    out_file.write(sum)
            summary_msg = f"Extractive summary extracted to {self.file_name}"
            print(summary_msg)
            return (summary_msg, 0) # return success message and code
        except Exception as error:
            error_msg = f"Error with getting the extractive summary: {error}"
            return (error_msg, 1) # return failure message and code

    def summarize_content(self, content, temp_file): # function to summarize content using the bart model
        # start_time = datetime.now()
        max_percentage = 0.25
        max_len = round(len(content) * max_percentage) # total amount of tokens for the summary (25% of original content)
        if max_len < 56: # length constraint requires 56 as the minimum amount of tokens
            max_len = 56
            
        input_ids = self.bart_tokenizer.encode(content, return_tensors='pt') # encodes into numerical input ids
        summary_ids = self.bart_model.generate(input_ids, num_beams=4, max_length=max_len, early_stopping=True) # generates summary based on input ids, amount of beams to search for summary, max length of tokens
        summary = self.bart_tokenizer.decode(summary_ids[0], skip_special_tokens=True) # decodes back into alphabetical summary
        sentences = self.spacy_tokenizer(summary) # tokenizers to split into sentences
        summary_text = "\n".join([sent.text for sent in sentences])
        # print(f"Runtime of chunk summarization: {datetime.now() - start_time}")

        with open(temp_file, "w") as outfile:
            outfile.write(summary_text + "\n") # write to outfile
        # out_file.flush() # saves summary to file quickly in case of file closure

    def chunk_split(self, max_length):
        sentences = self.spacy_tokenizer(self.content) # use spacy tokenizer for getting sentences
        chunks = []
        current_chunk = ""

        for sent in sentences:
            if len(current_chunk) + len(sent.text) + 1 > max_length: # the current chunk length + the incoming sentence length + 1 to account for spacing between the sentences
                # if the sentences and the current chunk is more than 1024 tokens then a new chunk has to be created and the current chunk is added to the chunk list
                chunks.append(current_chunk.strip())
                current_chunk = sent.text + " "
            else:
                # the sentence gets added to the current chunk if it doesn't exceed the max length of tokens
                current_chunk += sent.text + " "

        if current_chunk: # the most recent chunk after iterating is being appended
            chunks.append(current_chunk.strip())

        return chunks
    def abstractive_summarize(self): # abstractive bart model that paraphrases the content
        try:
            chunk_size = 1024 # max tokens the model allows
            if len(self.content) > chunk_size: # if the content is more than the model allows it has to be chunked
                chunks = self.chunk_split(chunk_size) # split into chunks based on sentences
                max_cpus = min(4, mp.cpu_count()) # using the max cpus on the machine for workers
                if not os.path.exists("docs/temp"):
                    os.makedirs("docs/temp")
                print(f"Number of chunks to be summarized: {len(chunks)}")
                print(f"Number of CPUs: {max_cpus}")
                with ThreadPoolExecutor(max_workers=max_cpus) as executor: # chunks are summarized in parallel
                    retrieval_tasks = []
                    for i in range(len(chunks)):
                    # for chunk in chunks:
                        if i < 9:
                            temp_file_name = f"docs/temp/temp0{i+1}.txt"
                        else:
                            temp_file_name = f"docs/temp/temp{i+1}.txt"
                        task = executor.submit(self.summarize_content, chunks[i], temp_file_name)
                        # task = executor.submit(self.summarize_content, chunk)
                        retrieval_tasks.append(task)
                concurrent.futures.wait(retrieval_tasks) # waits for all the tasks to be completed
                with open(self.file_name, "w") as outfile:
                    # for summary in retrieval_tasks:
                    #     outfile.write(summary)
                    for file in sorted(os.listdir("docs/temp")):
                        with open(os.path.join("docs/temp", file), "r") as temp_file:
                            temp_content = temp_file.read()
                            outfile.write(temp_content)
                        os.remove(os.path.join("docs/temp", file))
                os.rmdir("docs/temp")
            else: # if the content is less than 1024 tokens it can just be summarized and written to the file
                with open(self.file_name, "w") as outfile:
                    self.summarize_content(self.content, outfile)
            summary_msg = f"Abstractive summary extracted to {self.file_name}"
            print(summary_msg)
            return (summary_msg, 0)
        except Exception as error:
            error_msg = f"Error with getting the abstractive summary: {error}"
            print(error_msg)
            return (error_msg, 1)