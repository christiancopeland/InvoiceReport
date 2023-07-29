import pyttsx3
import speech_recognition as sr
import json
import requests 
import os
import yaml
import openai
import prettyprint as pp
import PyPDF2
import textwrap
import time
import re
from time import sleep




# Initialize the speech synthesis engine
engine = pyttsx3.init()

# Set the voice rate (speed)
engine.setProperty('rate', 150)

# Set the voice volume
engine.setProperty('volume', 0.8)

functions = [

 {
    "name": "create_folder",
    "description": "Create a folder in the given folderpath if it does not exist",
    "parameters": {
    "type": "object",
    "properties": {
      "folderpath": {
        "type": "string",
        "description": "The folderpath where the folder will be created"
      }
    }
    },
    "required": ["folderpath"]
  },
  {
    "name": "write_file",
    "description": "Create a file with the given filepath and content",
      "parameters": {
      "type": "object",
      "properties": {
        "filepath": {
          "type": "string",
          "description": "The name of the file to write"
        },
        "content": {
          "type": "string",
          "description": "The content of the file to write"
        }
      },
      "required": ["filepath", "content"]
    }
  },
  {
    "name": "delete_folder",
    "description": "Delete a folder in the given folderpath if it exists",
    "parameters": {
    "type": "object",
    "properties": {
      "folderpath": {
        "type": "string",
        "description": "The folderpath where the folder will be deleted"
      }
    }
    },
    "required": ["folderpath"]
  },
  {
    "name": "delete_file",
    "description": "Delete a file with the given file name and extension",
    "parameters": {
    "type": "object",
    "properties": {
      "file_name": {
        "type": "string",
        "description": "The name of the file to be deleted"
      },
      "extension": {
        "type": "string",
        "description": "The extension of the file to be deleted"
      }
    }
    },
    "required": ["file_name", "extension"]
  },
  {
    "name": "test_create_endpoint",
    "description": "Create a new KB article with the given text",
    "parameters": {
    "type": "object",
    "properties": {
      "text": {
        "type": "string",
        "description": "The text for the new KB article"
      }
    }
    },
    "required": ["text"]
  },
  {
    "name": "test_search_endpoint",
    "description": "Search for KB articles that match the given query",
    "parameters": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "The search query"
      }
    }
    },
    "required": ["query"]
  },
  {
    "name": "test_update_endpoint",
    "description": "Update an existing KB article with the given title and text",
    "parameters": {
    "type": "object",
    "properties": {
      "title": {
        "type": "string",
        "description": "The title of the KB article to update"
      },
      "text": {
        "type": "string",
        "description": "The new text for the KB article"
      }
    }
    },
    "required": ["title", "text"]
  }
]

def gpt3_completion(prompt, engine='gpt-3.5-turbo-16k', temp=0.1, top_p=1.0, tokens=5000, freq_pen=0.0, pres_pen=0.0, ):
    max_retry = 5
    retry = 0
    prompt = prompt.encode(encoding='ASCII',errors='ignore').decode()  # force it to fix any unicode errors
    while True:
        try:
            response = openai.Completion.create(
                engine=engine,
                prompt=prompt,
                temperature=temp,
                max_tokens=tokens,
                top_p=top_p,
                frequency_penalty=freq_pen,
                presence_penalty=pres_pen,
                )
            text = response['choices'][0]['text'].strip()
            text = re.sub('\s+', ' ', text)
            filename = '%s_gpt3.txt' % time()
            save_file('gpt3_logs/%s' % filename, prompt + '\n\n==========\n\n' + text)
            return text
        except Exception as oops:
            retry += 1
            if retry >= max_retry:
                return "GPT3 error: %s" % oops
            print('Error communicating with OpenAI:', oops)
            sleep(1)

###     file operations

def save_yaml(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as file:
        yaml.dump(data, file, allow_unicode=True)
        
def process_invoice_pdf(file_path):
    files = os.listdir('pdfs/')
    print(files)
    output = ''
    for file in files:
        print(file)
        pdffileobj = open('pdfs/%s' % file, 'rb')
        pdfreader = PyPDF2.PdfReader(pdffileobj)
        x = len(pdfreader.pages)
        paper = ''
        for i in list(range(0,x)):
            pageobj = pdfreader.pages[i]
            text = pageobj.extract_text()
            paper = paper + '\n' + text
        #print(paper)
        #exit()
        chunks = textwrap.wrap(paper, 6000)
        result = ''
        for chunk in chunks:
            prompt = open_file('prompt_summary.txt').replace('<<PAPER>>', chunk)
            summary = gpt3_completion(prompt)
            result = result + ' ' + summary
        print(result)
        output = output + '\n\n%s: %s' % (file, result)
    save_file('literature_review.txt', output)
    




def open_yaml(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        data = yaml.load(file, Loader=yaml.FullLoader)
    return data



def save_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as outfile:
        outfile.write(content)
    return content
    



def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as infile:
        return infile.read()


###     create and delete folders and files

def create_folder(folderpath):
    if not os.path.exists(folderpath):
        #mkdirs creates a leaf directory and all intermediate ones, may lead to lots of folders
        os.makedirs(folderpath)
        print("Folder created: ", folderpath)
    else:
        print("Folder already exists: ", folderpath)
        
        
def delete_folder(folderpath):
    if os.path.exists(folderpath):
        os.rmdir(folderpath)
        print("Folder deleted: ", folderpath)
    else:
        print("Folder does not exist: ", folderpath)
        
def create_file(file_name, extension):
    file_path = f"{file_name}.{extension}"
    try:
        with open(file_path, 'w') as file:
            pass  # The file is created and immediately closed
        print(f"File '{file_path}' created successfully.")
    except IOError:
        print(f"An error occurred while creating the file '{file_path}'.")

def delete_file(file_name, extension):
    file_path = f"{file_name}.{extension}"
    try:
        os.remove(file_path)
        print(f"File '{file_path}' deleted successfully.")
    except IOError:
        print(f"An error occurred while deleting the file '{file_path}'.")

        
###     kb functions

def test_create_endpoint(text):
    # text = input("Enter the text for the new KB article: ")
    payload = {"input": text}
    response = requests.post("", json=payload)
    print('\n\n\n', response.json())
    response = response.json()
    return response



def test_search_endpoint(query):
    # query = input("Enter the search query: ")
    payload = {"query": query}
    response = requests.post("", json=payload)
    print('\n\n\n')
    pp(response.json())
    response = response.json()
    return response



def test_update_endpoint(title, text):
    # title = input("Enter the title of the KB article to update: ")
    # text = input("Enter the new text for the KB article: ")
    payload = {"title": title, "input": text}
    response = requests.post("", json=payload)
    print('\n\n\n', response.json())
    response = response.json()
    return response

def function_call(function_name, arguments):
   
    if function_name == "":
       # query = eval(arguments).get("query")
        return test_search_endpoint(**arguments)
    elif function_name == "":
       # text = eval(arguments).get("text")
        return test_create_endpoint(**arguments)
    elif function_name == "":
        #title = eval(arguments).get("title")
        #text = eval(arguments).get("text")
        return test_update_endpoint(**arguments)
    elif function_name == "write_file":
        #filename = eval(arguments).get("file_name")
        #extension = eval(arguments).get("extension")
        return save_file(**arguments)
    elif function_name == "delete_file":
       # filename = eval(arguments).get("file_name")
        #extension = eval(arguments).get("extension")
        return delete_file(**arguments)
    elif function_name == "create_folder":
        #folderpath = eval(arguments).get("folderpath")
        return create_folder(**arguments)
    elif function_name == "delete_folder":
        #folderpath = eval(arguments).get("folderpath")
        return delete_folder(**arguments)
    else:
        print("Function not found")
        
def multi_line_input():
    print('\n\n\nType END to save and exit.\n[MULTI] USER:\n')
    lines = []
    while True:
        line = input()
        if line == "END":
            break
        lines.append(line)
    return "\n".join(lines)
        
def check_scratch(user_message):
  # check if scratchpad updated, continue
    if 'SCRATCHPAD' in user_message:
        user_message = multi_line_input()
        save_file('scratchpad.txt', user_message.strip('END').strip())
        print('\n\n#####      Scratchpad updated!')
            
  # empty submission, probably on accident
    if user_message == '':
        print('You said nothing.')
        return


# Function to read the AI response out loud
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Chatbot function
def chatbot(conversation, model="gpt-3.5-turbo-0613", temperature=0, functions=functions):
    max_retry = 7
    retry = 0
    while True:
        system_message = open_file('system_message.txt').replace('<<CODE>>', open_file('scratchpad.txt'))
        conversation.append({'role': 'system', 'content': system_message})
        response = openai.ChatCompletion.create(model=model, messages=conversation, temperature=temperature, functions=functions)
        bot_message = response['choices'][0]['message']
        speak(bot_message)
        

        if "function_call" in bot_message:
            function_to_call = bot_message["function_call"]
            function_name = function_to_call["name"]
            arguments = json.loads(function_to_call["arguments"])
            function_response = function_call(function_name, arguments)
            conversation.append({
                "role": "function",
                "name": function_name,
                "content": json.dumps(function_response)
            })
        else:
            user_message = input("\n\nGPT: " + bot_message["content"] + "\n\nYou: ")
            conversation.append({
                "role": "user",
                "content": user_message
            })
        
            
        return bot_message["content"], response['usage']['total_tokens']
            

# Main loop
def main():
    openai.api_key = open_file('key_openai.txt').strip()
    ALL_MESSAGES = list()
    print('\n\n****** IMPORTANT: ******\n\nType SCRATCHPAD to enter multi line input mode to update scratchpad. Type END to save and exit.')
    while True:
        user_message = input('\n\n\n[NORMAL] USER:\n\n')
        check_scratch(user_message)
        system_message = open_file('system_message.txt').replace('<<CODE>>', open_file('scratchpad.txt'))
        conversation = list()
        conversation.append({'role': 'user', 'content': user_message})
        conversation.append({'role': 'system', 'content': system_message})
        response, tokens = chatbot(conversation)
        
        
        
        if tokens < 7000:
            conversation.pop(1)

if __name__ == "__main__":
    main()
    
    
    
    
    
 
# import streamlit as st
# import os
# from PyPDF2 import PdfFileReader

# # Function to process the invoice PDF
# def process_invoice_pdf(file_path):
#     # Read the PDF file
#     with open(file_path, 'rb') as file:
#         pdf = PdfFileReader(file)
#         num_pages = pdf.getNumPages()

#         # Extract text from each page
#         text = ""
#         for page_num in range(num_pages):
#             page = pdf.getPage(page_num)
#             text += page.extractText()

#         # Process the extracted text (e.g., extract invoice number, total amount, etc.)
#         # Add your processing logic here

#         return text

# # Main function to run the Streamlit app
# def main():
#     st.title("Invoice PDF Processing")

#     # File upload
#     uploaded_file = st.file_uploader("Upload an invoice PDF", type="pdf")

#     if uploaded_file is not None:
#         # Save the uploaded file to a temporary location
#         temp_path = os.path.join(os.getcwd(), "temp.pdf")
#         with open(temp_path, 'wb') as file:
#             file.write(uploaded_file.getvalue())

#         # Process the invoice PDF
#         text = process_invoice_pdf(temp_path)

#         # Display the extracted text
#         st.subheader("Extracted Text")
#         st.text(text)

#         # Delete the temporary file
#         os.remove(temp_path)

# # Run the app
# if __name__ == "__main__":
#     main()
