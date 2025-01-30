import tkinter as tk
from tkinter import messagebox
from .summary import Summarization

class summaryGUI:
    def __init__(self, window):
        self.window = window
        self.window.title("DocSum")
        self.window.geometry("500x150")

        # initialize frame
        self.doc_frame = tk.Frame(self.window) # list all three document options
        # self.doc_frame.pack(fill=tk.X)
        self.doc_frame.pack(fill=tk.BOTH, expand=True)

        # Frame for bottom buttons
        self.exit_frame = tk.Frame(self.window) # generate and exit button
        self.exit_frame.pack(fill=tk.BOTH, pady=15, expand=True, side=tk.BOTTOM)

        # Frames being used in the program
        self.upload_frame = tk.Frame(self.window) # frame for uploading word or pdf
        self.content_frame = tk.Frame(self.window)
        self.success_frame = tk.Frame(self.window)
        self.decrypt_frame = tk.Frame(self.window)

        # initializing variables
        self.file_path = None
        self.incorrect_password_check = False

        self.doc_var = tk.IntVar() # variable for doc type radio buttons
        self.sum_var = tk.IntVar()
        # Doc type radio buttons
        self.doc_type_label = tk.Label(self.doc_frame, text = "Please choose a document type to summarize:")
        self.pdf_type = tk.Radiobutton(self.doc_frame, text = "PDF", value = 1, variable = self.doc_var)
        self.word_type = tk.Radiobutton(self.doc_frame, text = "Word Document", value = 2, variable = self.doc_var)
        self.article_type = tk.Radiobutton(self.doc_frame, text = "Article Url", value = 3, variable = self.doc_var)
        # Buttons at the bottom
        self.doc_button = tk.Button(self.exit_frame, text = "Select", activeforeground= "pink", highlightbackground='light sky blue', command=self.select_doc_type)
        self.exit_button = tk.Button(self.exit_frame, text="Exit", activeforeground= "pink", highlightbackground="light sky blue", command=self.window.destroy)
        self.decrypt_button = None

        self.doc_type_label.pack()
        self.pdf_type.pack()
        self.word_type.pack()
        self.article_type.pack()
        self.doc_button.pack(side=tk.LEFT, fill=tk.BOTH, padx=10, expand=True)
        self.exit_button.pack(side=tk.RIGHT, fill=tk.BOTH, padx=10, expand=True)
    def select_doc_type(self):
        if self.doc_var.get() != 0:
            if self.doc_var.get() == 1: # if user chooses pdf then prompt them to upload a pdf file
                self.doc_frame.destroy() # get rid of previous frame on the screen
                self.doc_button.destroy() # get rid of previous frame on the screen
                self.window.geometry("750x75")
                upload_button = tk.Button(self.upload_frame, text="Upload Document", command=lambda fileTypes=[("PDF files", "*.pdf")]: self.uploader(fileTypes))
                self.file_label = tk.Label(self.upload_frame, text="No file selected")
                upload_button.pack(side=tk.LEFT)
                self.file_label.pack(side=tk.LEFT, pady=5)
                self.enter_button = tk.Button(self.exit_frame, text = "Enter", activeforeground= "pink", highlightbackground='light sky blue', command=lambda file=self.file_path: self.get_content(file))
            elif self.doc_var.get() == 2: # if user chooses word doc then prompt them to upload a word file
                self.doc_frame.destroy() # get rid of previous frame on the screen
                self.doc_button.destroy() # get rid of previous frame on the screen
                self.window.geometry("750x75")
                upload_button = tk.Button(self.upload_frame, text="Upload Document", command=lambda fileTypes=[("Word documents", "*.doc *.docx")]: self.uploader(fileTypes))
                self.file_label = tk.Label(self.upload_frame, text="No file selected")
                upload_button.pack(side=tk.LEFT)
                self.file_label.pack(side=tk.LEFT, pady=5)
                self.enter_button = tk.Button(self.exit_frame, text = "Enter", activeforeground= "pink", highlightbackground='light sky blue', command=lambda file=self.file_path: self.get_content(file))
            elif self.doc_var.get() == 3: # if user chooses online articl then prompt them to enter the url
                input_label = tk.Label(self.upload_frame, text = "Please enter the URL:")
                input_entry = tk.Entry(self.upload_frame, width=50)
                self.doc_frame.destroy() # get rid of previous frame on the screen
                self.doc_button.destroy() # get rid of previous frame on the screen
                self.window.geometry("500x75")
                input_label.pack(fill=tk.X, side=tk.LEFT)
                input_entry.pack(fill=tk.X, side=tk.LEFT)
                self.enter_button = tk.Button(self.exit_frame, text = "Enter", activeforeground= "pink", highlightbackground='light sky blue', command=lambda url=input_entry: self.get_content(url))
            self.enter_button.pack(side=tk.LEFT, fill=tk.BOTH, padx=10, expand=True)
            self.upload_frame.pack(fill=tk.BOTH, side=tk.TOP, expand=True)
    def get_content(self, entry_input):
        self.sum_label = tk.Label(self.content_frame, text = "Please choose the type of summarization:")
        # radio buttons to either get an extractive or abstractive summary
        self.extract = tk.Radiobutton(self.content_frame, text = "Extractive", value = 1, variable = self.sum_var)
        self.abstract = tk.Radiobutton(self.content_frame, text = "Abstractive", value = 2, variable = self.sum_var)
        if self.doc_var.get() == 3: # get content from online url
            url = entry_input.get()
            if url:
                self.window.geometry("500x125")
                self.content_frame.pack(fill=tk.BOTH, side=tk.TOP, expand=True)
                self.upload_frame.destroy() # get rid of previous frame on the screen
                self.enter_button.destroy()
                summary = Summarization(3, url) # initialize summary object for article option
                msg, status = summary.get_url_content()
                if status == 0: # if content extracted successfully move on to summarizing
                    self.sum_label.pack()
                    self.extract.pack()
                    self.abstract.pack()
                    self.sum_button = tk.Button(self.exit_frame, text = "Summarize", activeforeground= "pink", highlightbackground='light sky blue', command=lambda summary_obj=summary: self.get_summary(summary_obj))
                    self.sum_button.pack(side=tk.LEFT, fill=tk.BOTH, padx=10, expand=True)
                    messagebox.showinfo("Content Extraction Completed", msg)
                else:
                    messagebox.showerror("Content Extraction Failed", msg)
                    self.window.destroy()
        else:
            if self.file_path:
                self.content_frame.pack(fill=tk.BOTH, side=tk.TOP, expand=True)
                self.upload_frame.destroy()
                self.enter_button.destroy()
                if self.doc_var.get() == 1:
                    summary = Summarization(1, self.file_path) # initialize summary object for pdf option
                    if summary.is_pdf_encrypted() == True: # check to see if pdf is encrypted and if so prompt the user for the password
                        self.window.geometry("750x150")
                        self.decrypt_frame.pack(fill=tk.BOTH, side=tk.TOP, expand=True)
                        decrypt_label = tk.Label(self.decrypt_frame, text = f"This PDF file is encrypted.\nPlease enter password for {self.file_path}:")
                        decrypt_entry = tk.Entry(self.decrypt_frame, width=50, show="*")
                        self.decrypt_button = tk.Button(self.exit_frame, text = "Enter", activeforeground= "pink", highlightbackground='light sky blue', command=lambda summary_obj=summary, password=decrypt_entry: self.decrypt_pdf_file(summary_obj, password))
                        decrypt_label.pack()
                        decrypt_entry.pack()
                        self.decrypt_button.pack(side=tk.LEFT, fill=tk.BOTH, padx=10, expand=True)
                    elif summary.is_pdf_encrypted() == False:
                        self.window.geometry("500x125")
                        msg, status = summary.get_pdf_content() # get content from unencrypted pdf file 
                        if status == 0:
                            self.sum_label.pack()
                            self.extract.pack()
                            self.abstract.pack()
                            self.sum_button = tk.Button(self.exit_frame, text = "Summarize", activeforeground= "pink", highlightbackground='light sky blue', command=lambda summary_obj=summary: self.get_summary(summary_obj))
                            self.sum_button.pack(side=tk.LEFT, fill=tk.BOTH, padx=10, expand=True)
                            messagebox.showinfo("Content Extraction Completed", msg)
                        else: # if content couldn't be extracted exit program as it can't be summarized
                            messagebox.showerror("Content Extraction Failed", msg)
                            self.window.destroy()
                    else:
                        error_msg = summary.is_pdf_encrypted()
                        messagebox.showerror("Could not check for encryption: ", error_msg)
                        self.window.destroy()
                elif self.doc_var.get() == 2: # get content for word doc then ask user for their preferred summary type
                    self.window.geometry("500x125")
                    summary = Summarization(2, self.file_path) # initialize summarization object for word doc option
                    msg, status = summary.get_docx_content()
                    if status == 0:
                        self.sum_label.pack()
                        self.extract.pack()
                        self.abstract.pack()
                        self.sum_button = tk.Button(self.exit_frame, text = "Summarize", activeforeground= "pink", highlightbackground='light sky blue', command=lambda summary_obj=summary: self.get_summary(summary_obj))
                        self.sum_button.pack(side=tk.LEFT, fill=tk.BOTH, padx=10, expand=True)
                        messagebox.showinfo("Content Extraction Completed", msg)
                    else: # if content couldn't be extracted exit program as it can't be summarized
                        messagebox.showerror("Content Extraction Failed", msg)
                        self.window.destroy()
    def get_summary(self, summary): # function for the summarize button
        if self.sum_var.get() != 0:
            if self.sum_var.get() == 1:
                msg, status = summary.extractive_summarize()
                if status == 0: # mark summarization as complete and let user know where the summary is located
                    self.window.geometry("750x75")
                    self.content_frame.destroy() # get rid of previous frame on the screen
                    self.sum_button.destroy() # get rid of previous frame on the screen
                    self.success_frame.pack(fill=tk.BOTH, side=tk.TOP, expand=True)
                    self.success_label = tk.Label(self.success_frame, text = msg)
                    self.success_label.pack() # add success message
                    messagebox.showinfo("Summarization Completed", msg)
                else: # if summary failed let user know and exit program
                    messagebox.showerror("Summarization Failed", msg)
                    self.window.destroy()
            elif self.sum_var.get() == 2:
                msg, status = summary.abstractive_summarize()
                if status == 0: # mark summarization as complete and let user know where the summary is located
                    self.window.geometry("750x75")
                    self.content_frame.destroy() # get rid of previous frame on the screen
                    self.sum_button.destroy() # get rid of previous frame on the screen
                    self.success_frame.pack(fill=tk.BOTH, side=tk.TOP, expand=True)
                    self.success_label = tk.Label(self.success_frame, text = msg)
                    self.success_label.pack() # add success message
                    messagebox.showinfo("Summarization Completed", msg)
                else: 
                    messagebox.showerror("Summarization Failed", msg)
                    self.window.destroy()

    def uploader(self, fileTypes): # upload function for pdf and word document option
        if fileTypes == [("PDF files", "*.pdf")]:
            fileTitle = "Please select a PDF Document"
        else:
            fileTitle = "Please select a Word Document"
        self.file_path = tk.filedialog.askopenfilename(title=fileTitle, filetypes=fileTypes)
        if self.file_path:
            self.file_label.config(text=f"Selected file: {self.file_path}")
            print("File Selected", f"File has been selected: {self.file_path}")
        else:
            self.file_label.config(text="No file selected")
            print("No File Selected", "Please select a file to upload.")
    def decrypt_pdf_file(self, summary, pass_input): # function if pdf is encrypted
        password = pass_input.get()
        if password: # once password is entered then prompt user for summary type
            if summary.decrypt_pdf(password):
                self.decrypt_frame.destroy()
                self.decrypt_button.destroy()
                msg, status = summary.get_pdf_content()
                if status == 0:
                    self.sum_label.pack()
                    self.extract.pack()
                    self.abstract.pack()
                    self.sum_button = tk.Button(self.exit_frame, text = "Summarize", activeforeground= "pink", highlightbackground='light sky blue', command=lambda summary_obj=summary: self.get_summary(summary_obj))
                    self.sum_button.pack(side=tk.LEFT, fill=tk.BOTH, padx=10, expand=True)
                    messagebox.showinfo("Content Extraction Completed", msg)
                else:
                    messagebox.showerror("Content Extraction Failed", msg)
                    self.window.destroy()
            elif not summary.decrypt_pdf(password):
                if self.incorrect_password_check == False:
                    incorrect_label = tk.Label(self.decrypt_frame, text = f"Incorrect password for {self.file_path}")
                    incorrect_label.pack()
                    self.incorrect_password_check = True
            else:
                error_msg = summary.decrypt_pdf(password)
                messagebox.showerror("Could not decrypt the pdf file: ", error_msg)
                self.window.destroy()
