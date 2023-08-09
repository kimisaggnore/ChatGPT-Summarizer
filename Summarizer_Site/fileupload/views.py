from django.shortcuts import render, redirect, HttpResponseRedirect, HttpResponse
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.files.base import ContentFile
from django.http import JsonResponse
from fileupload.models import Document
from fileupload.forms import DocumentForm
import fileupload.summarizer as summarizer
import os
from termcolor import colored
import fileupload.file_condenser as file_condenser
from asgiref.sync import sync_to_async
import asyncio
import fileupload.summarizer_async as summarizer_async
from django.views import View
from django.views.decorators.http import require_GET
from django.urls import reverse
import time


def home(request):
    try:
        documents = Document.objects.all()
        return render(request, 'fileupload/home.html', { 'documents': documents })
    except Exception as e:
        print(f"An error occurred: {e}")
        return render(request, 'fileupload/exception_page.html')


def simple_upload(request):
    # if request.POST.get('form_id') == "return_to_login":
    #     return render(request, 'fileupload/login.html')
    try:
        if request.method == 'POST' and len(request.FILES) != 0:
            with open(f"processing_files/progress_file.txt", 'w') as file:
                file.write("no")
            myfile = request.FILES['myfile']
            request.session["summary_length"] = request.POST.get("summaryLength")
            request.session["detail_level"] = request.POST.get("detailLevel")
            request.session["literacy_level"] = request.POST.get("languages")
            request.session["tone"] = request.POST.get("Tone")
            request.session["form"] = request.POST.get("format")
            request.session["AdditionalInformation"] = request.POST.get("AdditionalInformation")
            request.session["enabled"] = True
            request.session["filename"] = myfile.name
            with open(f"processing_files/ACTIVATED.txt", 'r') as file:
                txt = file.read()
            with open(f"processing_files/ACTIVATED.txt", 'w') as file:
                if txt != "0":
                    file.write(str(1))
            fs = FileSystemStorage()
            filename = fs.save(myfile.name, myfile)
            add_info_tokens = file_condenser.count_tokens_in_string(request.session["AdditionalInformation"])
            uploaded_file_url_2 = fs.url(f"chatGPT_final_summary.pdf")
            if add_info_tokens < 100:
                return render(request, 'fileupload/success_page.html', {'show_form': True, "show_message": False})
            else:
                return render(request, 'fileupload/simple_upload.html', {"exceed_limit": True})
            
            # return render(request, 'fileupload/simple_upload.html', {
            #     'uploaded_file_url': uploaded_file_url_2
            # }) 
        return render(request, 'fileupload/simple_upload.html', {"exceed_limit": False})
    except Exception as e:
        print(f"An error occurred: {e}")
        return render(request, 'fileupload/exception_page.html')

def success_page(request):
    try:
        return redirect('link_page')
    except Exception as e:
        print(f"An error occurred: {e}")
        return render(request, 'fileupload/exception_page.html')
    
def waiting_page(request):
    try: 
        print("original")
        time.sleep(5)
        return render(request, 'fileupload/waiting_page.html', {"activate_script": True})
    except Exception as e:
        print(f"An error occurred: {e}")
        return render(request, 'fileupload/exception_page.html')

def run_iteration(request):
    try:
        print("redirected")
        time.sleep(5)
        #return render(request, 'fileupload/waiting_page.html', {"activate_script": True})
        return redirect("waiting_page")
    except Exception as e:
        print(f"An error occurred: {e}")
        return render(request, 'fileupload/exception_page.html')
    
def model_form_upload(request):
    try:
        if request.method == 'POST':
            form = DocumentForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                return redirect('home')
        else:
            form = DocumentForm()
        return render(request, 'fileupload/model_form_upload.html', {
            'form': form
        })
    except Exception as e:
        print(f"An error occurred: {e}")
        return render(request, 'fileupload/exception_page.html')
    
def login(request):
    try:
        if 'api_key' in request.POST:
            key = ContentFile(request.POST["api_key"])
            fs = FileSystemStorage()
            if os.path.exists(os.path.join("uploads", "api_key")):
                os.remove(os.path.join("uploads", "api_key"))
            filename = fs.save("api_key", key)
            return render(request, 'fileupload/simple_upload.html')

        if os.path.exists(os.path.join("uploads", "api_key")):
            key = file_condenser.convert_file_to_string(os.path.join("uploads", "api_key"))
            return render(request, 'fileupload/login.html', {"api_key" : key})
        else:
            return render(request, 'fileupload/login.html')
    except Exception as e:
        print(f"An error occurred: {e}")
        return render(request, 'fileupload/exception_page.html')
    
def file_updates(request):
    try:
        file_path = "uploads/chatGPT_final_summary.txt"  # Adjust the directory path as per your requirement
        filenames = os.listdir("uploads")
        file_exists = False
        for file in filenames:
            print(file)
            if file == "chatGPT_final_summary.txt":
                file_exists = True

        if file_exists:
            print("file exists")
            file_condenser.text_to_pdf("uploads/chatGPT_final_summary.txt", "uploads/chatGPT_final_summary.pdf")
            fs = FileSystemStorage()
            uploaded_file_url_2 = fs.url(f"chatGPT_final_summary.pdf")
            
            context = {
            'files': [uploaded_file_url_2]
            }
            return render(request, 'fileupload/file_updates.html', context)
        else:
            print("file not exists")
            context = {
            'files': []
            }
            return render(request, 'fileupload/file_updates.html', context)
    except Exception as e:
        print(f"An error occurred: {e}")
        return render(request, 'fileupload/exception_page.html')
    
def link_page(request):
    try:
        with open(f"processing_files/progress_file.txt", 'w') as file:
            file.write("preprocessing")
        # if request.POST.get('form_id') == "upload_new_file":
        #     print("here")
        #     if os.path.exists(os.path.join("uploads", "chatGPT_final_summary.txt")):
        #         os.remove(os.path.join("uploads", "chatGPT_final_summary.txt"))
            #render(request, 'fileupload/simple_upload.html', {"exceed_limit": False})
            # return redirect('simple_upload')
            #return render(request, 'fileupload/simple_upload.html')
        
        if not os.path.exists(os.path.join("uploads", "chatGPT_final_summary.txt")):
            summary_length = request.session["summary_length"]
            detail_level = request.session["detail_level"]
            literacy_level = request.session["literacy_level"]
            tone = request.session["tone"]
            form = request.session["form"]
            filename = request.session["filename"]
            Additional_Information = request.session["AdditionalInformation"]
            prompt = f"summarize this document with a {detail_level} level of detail and a {literacy_level} literacy level. Do this in a {form} format with a {tone} tone with the given text. {Additional_Information}"
            #within {summary_length} words and
            print(colored("PROMPT: ", "blue") + prompt)
            pdf_name = filename
            foldername = "test_run_6"
            ###SYNC
            #summarizer.summarize(pdf_name, prompt, foldername)
            ###ASYNC
            valid = summarizer_async.validate(pdf_name)
            with open(f"processing_files/ACTIVATED.txt", 'r') as file:
                val = file.read()
            if valid and val == "1":
                with open(f"processing_files/ACTIVATED.txt", 'w') as file:
                    file.write(str(0))

                loop = asyncio.new_event_loop()
                task = loop.create_task(summarizer_async.summarize_document("PLACEHOLDER.txt", prompt, foldername, loop, summary_length))
                loop.run_until_complete(task)

                with open(f"processing_files/status_file.txt", 'r') as file:
                    status = file.read()
                
                with open(f"processing_files/ACTIVATED.txt", 'w') as file:
                    file.write(str(1))
                # print("entered")
                if status != "bad":
                    return redirect("link_page")
                else:
                    with open(f"processing_files/progress_file.txt", 'w') as file:
                        file.write("no")
                    return render(request, 'fileupload/error_page.html')

            return render(request, 'fileupload/success_page.html', {'show_form': True, "show_message": False})
        else:
            file_condenser.text_to_pdf("uploads/chatGPT_final_summary.txt", "uploads/summarized_file/chatGPT_final_summary.pdf")
            print("converted")
            fs = FileSystemStorage()
            uploaded_file_url_2 = fs.url(f"/summarized_file/chatGPT_final_summary.pdf")
            return render(request, 'fileupload/link_page.html', {'uploaded_file_url': uploaded_file_url_2})
    except Exception as e:
        print(f"An error occurred: {e}")
        return render(request, 'fileupload/exception_page.html')
        
def fetch_progress(request):
    try:
        if os.path.exists(f"processing_files/progress_file.txt") and os.path.exists(f"processing_files/progress_file_2.txt"):
            with open(f"processing_files/progress_file.txt", 'r') as file:
                content = file.read()

            with open(f"processing_files/progress_file_2.txt", 'r') as file:
                content_2 = file.read()

            return JsonResponse({'progress': content, 'progress_2': content_2})
        
        if os.path.exists(f"processing_files/progress_file.txt"):
            with open(f"processing_files/progress_file.txt", 'r') as file:
                content = file.read()

            return JsonResponse({'progress': content})
        else:
            return JsonResponse({'progress': "no"})
    except Exception as e:
        print(f"An error occurred: {e}")
        return render(request, 'fileupload/exception_page.html')
        
def return_to_upload(request):
    try:
        if os.path.exists(os.path.join("uploads", "chatGPT_final_summary.txt")):
            os.remove(os.path.join("uploads", "chatGPT_final_summary.txt"))
        if os.path.exists(os.path.join("uploads", "summarized_file/chatGPT_final_summary.pdf")):
            os.remove(os.path.join("uploads", "summarized_file/chatGPT_final_summary.pdf"))
        return redirect("simple_upload")
    except Exception as e:
        print(f"An error occurred: {e}")
        return render(request, 'fileupload/exception_page.html')
