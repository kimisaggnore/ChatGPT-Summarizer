import openai 
import os
import fileupload.file_condenser as file_condenser
import numpy as np
import copy
from termcolor import colored
import time
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, redirect, HttpResponse
from django.conf import settings
from django.core.files.storage import FileSystemStorage

from fileupload.models import Document
from fileupload.forms import DocumentForm
import fileupload.summarizer as summarizer
import os
import json
import asyncio
from asgiref.sync import sync_to_async

# ~20,000 words.
def summarize_document(filename, prompt, foldername):
    openai.api_key = file_condenser.convert_file_to_string(os.path.join("uploads", "api_key"))
    chunked_arr = file_condenser.get_chunked_data_w_file(f"processing_files/{filename}")
    counter = 1
    chunked_arr = file_condenser.check_string_list(chunked_arr)
    if not os.path.exists(f"processing_files/{foldername}"):
        os.makedirs(f"processing_files/{foldername}")

    summarize = True
    while summarize:
        if len(chunked_arr) == 1:
            summarize = False

        final_summary = ''
        
        for txt in chunked_arr:
            messages = [
            {"role": "user", "content": txt},
            {"role": "user", "content": f"{prompt}"}
            ]
            try:
                completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                )
                chat_response = completion.choices[0].message.content
                print(f'ChatGPT: {chat_response}')
                final_summary += chat_response
                time.sleep(10)
            except:
                time.sleep(10)
        
        with open(f"processing_files/{foldername}/chatGPT_intermediate_summary_{counter}.txt", "w") as out_file:
            out_file.write(final_summary)
        counter += 1
        
        chunked_arr = file_condenser.get_chunked_data_w_arr([final_summary])
        chunked_arr = file_condenser.check_string_list(chunked_arr)
        # chunked_arr[0] = chunked_arr[0][0]


    with open(f"uploads/chatGPT_final_summary.txt", "w") as out_file:
        out_file.write(final_summary)




def print_run(path):
    filenames = os.listdir(path)

    for file in filenames:
        if file.endswith(".txt"):
            file_path = f"{path}/{file}"
            with open(file_path, 'r') as f:
                print("\n")
                print(colored(f"{file}:", "blue"))
                print(f.read())
                print("\n")

def summarize(pdf_name, prompt, foldername):
        
    file_condenser.pdf_to_text(f"uploads/{pdf_name}", "processing_files/PLACEHOLDER.txt")
    # Example usage
    file_path = 'example.txt'  # Replace with your file path
    is_valid = file_condenser.validate_file("processing_files/PLACEHOLDER.txt")

    if is_valid:
        print("The file has been validated and invalid lines have been removed.")
        summarize_document("PLACEHOLDER.txt", prompt, foldername)
    else:
        print("The file could not be opened or modified.")
    #summarize_document("PLACEHOLDER.txt", prompt, foldername)


prompt = "summarize this document with a highschool literacy level"
pdf_name = "transfusion.pdf"
foldername = "test_run_6"

#summarize(pdf_name, prompt, foldername)
#print_run("summary_files/test_run_6")

async def api_call(pdf_name, prompt, foldername):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    async_function = sync_to_async(summarize(pdf_name, prompt, foldername), thread_sensitive= False)
    loop.create_task(async_function())


