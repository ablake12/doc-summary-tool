from bs4 import BeautifulSoup
import requests

from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer

class articleHighlights():
    def __init__(self, url):
        self.url = url
        # self.file_name = ""
        self.content = ""
        self.article_title
    def get_content(self):
        response = requests.get(self.url)
        soup = BeautifulSoup(response.text, 'html.parser')
        self.article_title = soup.find('title').text
        for paragraph in soup.find_all('p'):
            self.content += paragraph.text + "\n"
        
        # with open(self.file_name, "w") as out_file:
        #     out_file.write(self.content)
    def sumy_implementation(self):
        parser = PlaintextParser.from_string(self.content, Tokenizer("english"))

        # Create an LSA summarizer
        summarizer = LsaSummarizer()

        # Generate the summary
        summary = summarizer(parser.document, sentences_count=5)  # You can adjust the number of sentences in the summary

        file_name = f"{self.article_title}_suny_summary.txt"

        with open(file_name, "w") as out_file:
            out_file.write(summary)

url = input("Please enter the url: ")
summary = articleHighlights(url)
summary.get_content()
summary.sumy_implementation