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

async def call_openai_api(api_key, index, txt, prompt):
    try:
        openai.api_key = api_key
        #messages = prompt + txt
        #print(messages)
        messages = [{"role": "system", "content": "You are a summarizer. I will give you text to summarize. I want you to summarize text as if the text is a part of a longer summary." + prompt}, {"role": "user", "content": txt}]
        response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages = messages)
        return index, response.choices[0].message.content
        #return index, response.choices[0]['text']
    except Exception as e:
        print(f"Error: {e}")
        return index, ""
    
async def summarize_document(filename, prompt, foldername, loop, summary_length):
    openai.api_key = file_condenser.convert_file_to_string(os.path.join("uploads", "api_key"))
    openai_api_key_1 = file_condenser.convert_file_to_string(os.path.join("uploads", "api_key"))
    chunked_arr = file_condenser.get_chunked_data_w_file(f"processing_files/{filename}")
    summarize = True
    counter = 1
    chunked_arr = file_condenser.check_string_list(chunked_arr)

    if len(chunked_arr) == 1 and chunked_arr[0] == "[":
        with open(f"processing_files/status_file.txt", 'w') as file:
            file.write("bad")
        return False

    if not os.path.exists(f"processing_files/{foldername}"):
        os.makedirs(f"processing_files/{foldername}")

    time.sleep(2)
    with open(f"processing_files/progress_file.txt", 'w') as file:
        file.write("postprocessing")
    time.sleep(2)
    # with open(f"processing_files/progress_file.txt", 'w') as file:
    #     file.write(str(len(chunked_arr)))
    last_run = False
    while summarize:
        print(len(chunked_arr))
        with open(f"processing_files/progress_file.txt", 'w') as file:
            file.write(str(len(chunked_arr)))
        #print(file_condenser.check_string_list(chunked_arr))

        final_summary = ''
        
        num_chunks = len(chunked_arr)
        counter = 0
        max_RPM = 5
        max_TPM = 90000
        to_continue = True
        while to_continue:
            api_key_prompt_pairs = []
            for _ in range(0, max_RPM):
                if counter == num_chunks:
                    to_continue = False
                    break
                else:
                    api_key_prompt_pairs.append([openai_api_key_1, 0, chunked_arr[counter], prompt])
                    counter += 1
            if len(api_key_prompt_pairs) != 0:

                start_time = time.time()
                if not last_run:
                    tasks = [loop.create_task(call_openai_api(api_key, index, txt, prompt)) for api_key, index, txt, prompt in api_key_prompt_pairs]
                else:
                    #print("pre")
                    summarize = False
                    upper_bound = int(summary_length) + 100
                    api_key_prompt_pairs[0][3] = prompt + f"Make this summary between {summary_length} and {upper_bound} words. Also say the summary length at the end."
                    print("last run")
                    print(api_key_prompt_pairs[0][3])
                    tasks = [loop.create_task(call_openai_api(api_key, index, txt, prompt)) for api_key, index, txt, prompt in api_key_prompt_pairs]
                
                print(len(tasks))

                with open(f"processing_files/progress_file_2.txt", 'w') as file:
                    file.write(str(counter))

                results = await asyncio.gather(*tasks)
                remaining_time = 30 - (time.time() - start_time)
                if remaining_time >= 0 and len(chunked_arr) != 1:
                    print(f"sleeping for: {remaining_time}")
                    time.sleep(remaining_time)

                sorted_results = sorted(results, key=lambda x: x[0])
                for _, result in sorted_results:
                    final_summary += result
                    print(result)
                num_words = len(final_summary.split())
                print(num_words)
                if num_words < int(summary_length):
                    print("summary already short")
                    summarize = False
                    break
            else:
                to_continue = False


        with open(f"processing_files/progress_file.txt", 'w') as file:
            file.write(str(len(chunked_arr)))


        with open(f"processing_files/{foldername}/chatGPT_intermediate_summary_{counter}.txt", "w", encoding = 'utf-8') as out_file:
            #final_summary = "hello"
            print("hello")
            final_summary = final_summary.encode('utf-8', errors= 'ignore').decode('utf-8', errors = 'ignore')
            print("passed")
            out_file.write(final_summary)
            print("written")
        counter += 1
        
        chunked_arr = file_condenser.get_chunked_data_w_arr([final_summary])
        chunked_arr = file_condenser.check_string_list(chunked_arr)
        # chunked_arr[0] = chunked_arr[0][0]
        if len(chunked_arr) == 1:
            last_run = True
            #summarize = False

    with open(f"uploads/chatGPT_final_summary.txt", "w", encoding='utf-8') as out_file:
        out_file.write(final_summary)
    
    with open(f"processing_files/progress_file.txt", 'w') as file:
        file.write(str(len(chunked_arr)))
    
    with open(f"processing_files/progress_file_2.txt", 'w') as file:
        file.write(str(counter))
    
    with open(f"processing_files/status_file.txt", 'w') as file:
        file.write("good")
    return True

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


def validate(pdf_name):
        
    file_condenser.pdf_to_text(f"uploads/{pdf_name}", "processing_files/PLACEHOLDER.txt")
    is_valid = file_condenser.validate_file("processing_files/PLACEHOLDER.txt")

    if is_valid:
        print("The file has been validated and invalid lines have been removed.")
        return True
        #await summarize_document("PLACEHOLDER.txt", prompt, foldername, loop)
    else:
        print("The file could not be opened or modified.")
        return False
    #summarize_document("PLACEHOLDER.txt", prompt, foldername)


prompt = "summarize this document with a highschool literacy level"
pdf_name = "transfusion.pdf"
foldername = "test_run_6"

#summarize(pdf_name, prompt, foldername)
#print_run("summary_files/test_run_6")

# async def api_call(pdf_name, prompt, foldername):
#     loop = asyncio.new_event_loop()
#     asyncio.set_event_loop(loop)
#     async_function = sync_to_async(summarize(pdf_name, prompt, foldername), thread_sensitive= False)
#     loop.create_task(async_function())


