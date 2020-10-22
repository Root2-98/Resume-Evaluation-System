import docx2txt
import spacy
from spacy.matcher import Matcher
import re
import pandas as pd
import spacy
from nltk.corpus import stopwords
from spacy.lang.en import English
from scoreclass import Calc_Score
import json
import textract
import PyPDF2
import Classify as clf

def extract_text_from_doc(doc_path):
    temp = docx2txt.process(doc_path)
    #temp = textract.process(doc_path)
    text = [line.replace('\t', ' ') for line in temp.split('\n') if line]
    return ' '.join(text)

def extract_text_from_pdf(file_path):
    pdfReader = PyPDF2.PdfFileReader(file_path)
    pageObj = pdfReader.getPage(0)
    data = pageObj.extractText()
    text = [line.replace('\t', ' ') for line in data.split('\n') if line]
    return ' '.join(text)
    #return text

# load pre-trained model
nlp = spacy.load('en_core_web_sm')
# initialize matcher with a vocab
matcher = Matcher(nlp.vocab)

def extract_name(resume_text):
    nlp_text = nlp(resume_text)
    
    # First name and Last name are always Proper Nouns
    pattern = [{'POS': 'PROPN'}, {'POS': 'PROPN'}]
    
    matcher.add('NAME', None, pattern)
    
    matches = matcher(nlp_text)
    
    for match_id, start, end in matches:
        span = nlp_text[start:end]
        return span.text

def extract_mobile_number(resume_text):
    phone = re.findall(re.compile(r'\(?[0-9]{3}\)?[ .-]?[0-9]{3}[ .-]?[0-9]{4}'), resume_text)
    #print(phone)
    if phone:
        for i in phone:
            number = ''.join(i)
        #num = int(number)
        #print(len(number))
        #if len(number) > 10:
            return '+' + number
        else:
            return number
        #str1 = str(phone[0])
        #return len(str1)

def extract_email(resume_text):
    resume_text = re.findall("([^@|\s]+@[^@]+\.[^@|\s]+)", resume_text)
    if resume_text:
        try:
            return resume_text[0].split()[0].strip(';')
        except IndexError:
            return None


# load pre-trained model
nlp = spacy.load('en_core_web_sm')
#chunks = nlp.noun_chunks

def extract_skills(resume_text):
    nlp_text = nlp(resume_text)

    # removing stop words and implementing word tokenization
    tokens = [token.text for token in nlp_text if not token.is_stop]
    
    # reading the csv file
    data = pd.read_csv("skills.csv") 
    
    # extract values
    skills = list(data.columns.values)
    
    skillset = []
    
    # check for one-grams (example: python)
    for token in tokens:
        if token.lower() in skills:
            skillset.append(token)
    
    # check for bi-grams and tri-grams (example: machine learning)
    for token in nlp_text.noun_chunks:
        token = token.text.lower().strip()
        if token in skills:
            skillset.append(token)
    
    return [i.capitalize() for i in set([i.lower() for i in skillset])]


back_end = ['Python', 'C', 'C++','Java','SQL','PHP']
front_end = ['Html','Css','Javascript']
Communi = ['English','Hindi','Marathi']
Hobbies = ['Sports','Drawing','Arts','Music','Dance']

def getCategory(skills):
    d_req = {'Programming Languages': [] ,'UI Designing':[],'Communication Languages':[],'Other Activities':[]}
    for i in skills:
        for j in back_end:
            if i.lower()==j.lower():
                d_req['Programming Languages'].append(i)
                
        for j in front_end:
            if i.lower()==j.lower():
                d_req['UI Designing'].append(i)
                
        for j in Communi:
            if i.lower()==j.lower():
                d_req['Communication Languages'].append(i)

        for j in Hobbies:
            if i.lower()==j.lower():
                d_req['Other Activities'].append(i)
    #print(d_req)
    return d_req

# load pre-trained model
nlp = spacy.load('en_core_web_sm')

# Grad all general stop words
STOPWORDS = set(stopwords.words('english'))

# Education Degrees
EDUCATION = [
            'BE','B.E.', 'B.E', 'BS', 'B.S','BCA','MCA','BCOM','B.COM','BSC','BSc','B.Sc','BCS','BCs','B.Cs'
            'ME', 'M.E', 'M.E.', 'MS', 'M.S', 
            'BTECH', 'B.TECH', 'M.TECH', 'MTECH', 
            'SSC', 'HSC', 'CBSE', 'ICSE', 'X', 'XII','10th','12th',
        ]

def extract_education(resume_text):
    nlp_text = nlp(resume_text)

    # Sentence Tokenizer
    nlp_text = [sent.string.strip() for sent in nlp_text.sents]

    edu = {}
    # Extract education degree
    for index, text in enumerate(nlp_text):
        for tex in text.split():
            # Replace all special symbols
            tex = re.sub(r'[?|$|.|!|,]', r'', tex)
            if tex.upper() in EDUCATION and tex not in STOPWORDS:
                edu[tex] = text + nlp_text[index + 1]

    # Extract year
    education = []
    for key in edu.keys():
        education.append(key)
        #year = re.search(re.compile(r'(((20|19)(\d{2})))'), edu[key])
        #if year:
        #    education.append((key, ''.join(year[0])))
        #else:
        #    education.append(key)
    return education


def Resume_Ranker(resume, final_skills):
    rank = 0
    scorer = Calc_Score()
    resume_skills = extract_skills(resume)
       
    with open("skills_data.json", "r") as jsonfile:
            data = json.loads(jsonfile.read())
    
    jsonfile.close()
        
        #jd = ['python', 'deep_learning','machine_learning']
        #priority_skills = [7, 4, 5]
    rank = scorer.skillscore_update(resume_skills, final_skills, data)
    return rank

def Labeler(edu,resume_text):
    label1 = clf.Classify_stage1(edu,resume_text)
    return label1

def Classifier(name,text):
    domain = clf.Classify_stage3(name,text)
    return domain


#pdfReader = PyPDF2.PdfFileReader(r"C:\Users\Rutuja\Desktop\Desktop Data\PDF Resumes\Rishabh.pdf")
#print(pdfReader.numPages)
#pageObj = pdfReader.getPage(0)
#data = pageObj.extractText()
#text = [line.replace('\t', ' ') for line in data.split('\n') if line]
#print(' '.join(text))
#print(extract_text_from_pdf(r"C:\Users\Rutuja\Desktop\Desktop Data\PDF Resumes\Rishabh.pdf"))

#data = extract_text_from_pdf(r"C:\Users\Rutuja\Desktop\New folder\CS-IT\Abhishek N.pdf")
#data = extract_text_from_doc(r"C:\Users\Rutuja\Desktop\New Folder\CS-IT\Ankita.docx")
#print(data)
#print(extract_name(data))
#name = extract_name(data)
#print(extract_mobile_number(data))
#print(extract_email(data))
#print(extract_skills(data))
#edu = extract_education(data)
#print(edu)
#print(extract_education(data))
#final_skills = ['Java','Python']
#print(Resume_Ranker(data,final_skills))

#print(clf.Classify_stage1(edu,data))
#print(clf.Classify_Stage2(data))
#print(Classifier(name,data))
