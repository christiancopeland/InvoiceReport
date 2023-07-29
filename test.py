import os
import PyPDF2
import textwrap
import re
import openai
from time import time, sleep


openai.api_key = os.environ['OPENAI_API_KEY']



def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as infile:
        return infile.read()


def save_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as outfile:
        outfile.write(content)
    return content


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
            
            

def process_invoice_pdf():
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
    save_file('profitloss.txt', output)