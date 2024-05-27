# document-summary-tool

## Prerequisites
Python 3.6+
## Usage
1. Open terminal and run the program in the current working directory
2. Run the requirements.txt
```bash
pip3 install -r requirements.txt
```
3. Download the model
```bash
python3 -m spacy download en_core_web_sm
```
4. Run the program
```bash
python3 src/main.py
```
## Adapted From
@article{DBLP:journals/corr/abs-1910-13461,
  author    = {Mike Lewis and
               Yinhan Liu and
               Naman Goyal and
               Marjan Ghazvininejad and
               Abdelrahman Mohamed and
               Omer Levy and
               Veselin Stoyanov and
               Luke Zettlemoyer},
  title     = {{BART:} Denoising Sequence-to-Sequence Pre-training for Natural Language
               Generation, Translation, and Comprehension},
  journal   = {CoRR},
  volume    = {abs/1910.13461},
  year      = {2019},
  url       = {http://arxiv.org/abs/1910.13461},
  eprinttype = {arXiv},
  eprint    = {1910.13461},
  timestamp = {Thu, 31 Oct 2019 14:02:26 +0100},
  biburl    = {https://dblp.org/rec/journals/corr/abs-1910-13461.bib},
  bibsource = {dblp computer science bibliography, https://dblp.org}
}
## Notes
* Explain the difference between extractive and abstractive summaries
* Based on the document type, recommend what summaries may work best (extractive: word docs or long pdfs (10+ pages), abstractive: online articles and shorter pdfs (a few pages))
* Put disclaimer about the text summary not being perfect and all of that