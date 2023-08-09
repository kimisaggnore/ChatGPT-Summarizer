from transformers import GPT2TokenizerFast
import os
import math
from nltk.tokenize import sent_tokenize
import numpy as np
import copy
import PyPDF2
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit
import asyncio
from asgiref.sync import sync_to_async
# import nltk
# nltk.download('punkt')


def remove_empty_lines(filename):
    result = ""
    with open(f"./{filename}", "r+", encoding= "utf8") as file:
        for line in file:
            if not line.isspace():
                result += line

        file.seek(0)
        file.write(result)

def count_num_words_in_file(filename):
    number_of_words = 0

    with open(f"./{filename}",'r', encoding = "utf8") as file:
        data = file.read()
        lines = data.split()
        number_of_words += len(lines)

    return number_of_words

def count_total_file_tokens(filename):
    with open(f"./{filename}",'r', encoding = "utf8") as file:
        data = file.read()
        tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
        number_of_tokens = len(tokenizer(data)['input_ids'])

    return number_of_tokens

def count_tokens_in_string(str):
    tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
    number_of_tokens = len(tokenizer(str)['input_ids'])
    return number_of_tokens


def split_by_claim(filename_read, filename_write):
    with open(f"./{filename_read}",'r', encoding = "utf8") as file:
        data = file.read()
        lines = data.split('[')

    with open(f"./{filename_write}",'w', encoding = "utf8") as file2:
        for line in lines:
            file2.write(line + "[")


def allocate_chunks(arr_of_lines, token_budget):
    chunked_text = []
    tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
    cur_spent = 0
    cur_chunk = ''
    segmented_chunk = False
    for line in arr_of_lines:
        num_line_tokens = len(tokenizer(line)['input_ids'])
        cur_spent += num_line_tokens
        if cur_spent < token_budget:
            cur_chunk += line
        else:
            if cur_chunk != '':
                chunked_text.append(cur_chunk)
            if num_line_tokens > token_budget:
                rechunked = sent_tokenize(line)
                cur_chunk = allocate_chunks(rechunked, token_budget)
                for chunk in cur_chunk:
                    chunked_text.append(chunk)
                segmented_chunk = True
            else:
                cur_chunk = line
                cur_spent = num_line_tokens
                segmented_chunk = False
    if not segmented_chunk:
        chunked_text.append(cur_chunk)

    return chunked_text

def get_arr_of_lines(filename):
    with open(f"./{filename}",'r+', encoding = "utf8") as file:
        data = file.read()
        lines = data.split('[')
        ret_data = []
        for line in lines:
            line = "[" + line
            ret_data.append(line)

    return ret_data

def verify_chunked_text(arr_of_chunked, token_budget):
    tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
    total_tokens = 0
    for chunked in arr_of_chunked:
        num_tokens = len(tokenizer(chunked)['input_ids'])
        total_tokens += num_tokens
        #kprint(num_tokens)
        if num_tokens > token_budget:
            return False
    print(f"total_tokens_of_chunked_text: {total_tokens}")
    return True

def get_chunked_data_w_file(filename):
    lines = get_arr_of_lines(filename)
    chunked = allocate_chunks(lines, 2048)
    correctly_chunked = verify_chunked_text(chunked, 2048)
    print(f"Is properly chunked?: {correctly_chunked}")
    if correctly_chunked:
        return chunked
    else:
        return None

def get_chunked_data_w_arr(arr):
    chunked = allocate_chunks(arr, 2048)
    correctly_chunked = verify_chunked_text(chunked, 2048)
    print(f"Is properly chunked?: {correctly_chunked}")
    if correctly_chunked:
        return chunked
    else:
        return None


def clean_data():
    remove_empty_lines("centrifuge_system_full.txt")
    print(count_num_words_in_file("centrifuge_system_full.txt"))
    total_original_file_tokens = count_total_file_tokens("centrifuge_system_full.txt")
    print(f"total_original_file_tokens {total_original_file_tokens}")
    split_by_claim("centrifuge_system_full.txt", "centrifuge_system_full_claim_split.txt")

def encode_valid_utf(filename_in, filename_out):
    result = ""
    with open(filename_in, "r+", encoding = "utf8") as file:
        for line in file:
            line = line.strip()
            line = bytes(line, 'utf-8').decode('utf-8', 'ignore')
            result += line

    with open(filename_out, "w") as file:
        file.write(result)

    return result

def pdf_to_text(filename_in, filename_out):
    pdffileobj=open(filename_in,'rb')
    pdfreader=PyPDF2.PdfReader(pdffileobj)
    num_pages = len(pdfreader.pages)
    with open(filename_out, "w", encoding = "utf8") as file:
        for i in range(0, num_pages):
            pageobj=pdfreader.pages[i]
            line=pageobj.extract_text()
            line = line.strip()
            line = bytes(line, 'utf-8').decode('utf-8', 'ignore')
            file.write(line)

def text_to_pdf(filename_in, filename_out):
    pdf = canvas.Canvas(filename_out, pagesize=letter)
    pdf.setFont("Helvetica", 12)
    with open(filename_in, 'r') as file:
        lines = file.readlines()
    page_width, page_height = letter
    left_margin = 50
    right_margin = page_width - left_margin
    text_width = right_margin - left_margin
    y = page_height - 50  # Initial y position
    for line in lines:
        words = line.strip().split()
        lines = simpleSplit(' '.join(words), 'Helvetica', 12, text_width)
        for wrapped_line in lines:
            pdf.drawString(left_margin, y, wrapped_line)
            y -= 16  # Adjust line spacing (modify as needed)
            if y <= 50:
                pdf.showPage()
                y = page_height - 50
    pdf.save()


def validate_line(line):
    try:
        _ = str(line)  # Attempt to convert line to a string
        return True
    except UnicodeDecodeError:
        return False

def validate_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        with open(file_path, 'w', encoding='utf-8') as file:
            valid_lines = [line for line in lines if validate_line(line)]
            file.writelines(valid_lines)
            return True
    except IOError:
        print(f"Error: Could not open file '{file_path}'")
        return False

def check_string_list(lst):
    count = 0
    for item in lst:
        if not isinstance(item, str):
            lst.remove(item)
            #print(item)
    return lst

def convert_file_to_string(filepath):
    with open(filepath, 'r') as file:
        file_content = file.read()
        return file_content