import docx
import PyPDF2
import os
from os import listdir
from os.path import isfile, join
from io import StringIO
import pandas as pd
from collections import Counter
import spacy
from spacy.matcher import PhraseMatcher
#import B as b

Degree = ['BE','B.E.','MCA','BCA','BTech','B.Tech','B.TECH','BACHLOR OF ENGINEERING' ]
Higher_Education = ['HSC','H.S.C','12th','DSC','Deploma']
def Classify_stage1(edu,data):
    status = None
    label1 = None
    for i in edu:
        if i in Degree:
            label1 = Classify_Stage2(data)
            if label1 == 'IT':
                #print('a')
                status = 'Eligible'
                break           
    #print(status) 
    if status!='Eligible':
        #print("1")
        for i in edu:
            if i in Higher_Education:
                #print("3")
                label1 = Classify_Stage2(data)
                #print(label1)
                #print(status)
                if label1 == 'Non_IT':
                    #print('f')
                    status = 'Not Eligible'
                    break
        #print(status)                
    if status==None:
        #print("2")
        label1 = Classify_Stage2(data)
        if label1 == 'Non_IT':
            #print('c')
            status = 'Not Eligible'
        elif label1 =='IT' and (status=='Not Eligible' or status==None):
            #print('d')            
            status = 'Need Verification' 

    #print(status)    
    return status
      

def Classify_Stage2(data):
    words= list(data.split(" ")) 
    stopwords = [':', ' ', '', ',', ';', 'and', 'of', 'is', 'was', 'to', 'the', 'at', 'in', 'were', '.', 'that', 'all', '\n', 'by', 'here', 'my']
    stopwords = ['a', 'about', 'above', 'across', 'after', 'afterwards']
    stopwords += ['again', 'against', 'all', 'almost', 'alone', 'along']
    stopwords += ['already', 'also', 'although', 'always', 'am', 'among']
    stopwords += ['amongst', 'amoungst', 'amount', 'an', 'and', 'another']
    stopwords += ['any', 'anyhow', 'anyone', 'anything', 'anyway', 'anywhere']
    stopwords += ['are', 'around', 'as', 'at', 'back', 'be', 'became']
    stopwords += ['because', 'become', 'becomes', 'becoming', 'been']
    stopwords += ['before', 'beforehand', 'behind', 'being', 'below']
    stopwords += ['beside', 'besides', 'between', 'beyond', 'bill', 'both']
    stopwords += ['bottom', 'but', 'by', 'call', 'can', 'cannot', 'cant']
    stopwords += ['co', 'computer', 'con', 'could', 'couldnt', 'cry', 'de']
    stopwords += ['describe', 'detail', 'did', 'do', 'done', 'down', 'due']
    stopwords += ['during', 'each', 'eg', 'eight', 'either', 'eleven', 'else']
    stopwords += ['elsewhere', 'empty', 'enough', 'etc', 'even', 'ever']
    stopwords += ['every', 'everyone', 'everything', 'everywhere', 'except']
    stopwords += ['few', 'fifteen', 'fifty', 'fill', 'find', 'fire', 'first']
    stopwords += ['five', 'for', 'former', 'formerly', 'forty', 'found']
    stopwords += ['four', 'from', 'front', 'full', 'further', 'get', 'give']
    stopwords += ['go', 'had', 'has', 'hasnt', 'have', 'he', 'hence', 'her']
    stopwords += ['here', 'hereafter', 'hereby', 'herein', 'hereupon', 'hers']
    stopwords += ['herself', 'him', 'himself', 'his', 'how', 'however']
    stopwords += ['hundred', 'i', 'ie', 'if', 'in', 'inc', 'indeed']
    stopwords += ['interest', 'into', 'is', 'it', 'its', 'itself', 'keep']
    stopwords += ['last', 'latter', 'latterly', 'least', 'less', 'ltd', 'made']
    stopwords += ['many', 'may', 'me', 'meanwhile', 'might', 'mill', 'mine']
    stopwords += ['more', 'moreover', 'most', 'mostly', 'move', 'much']
    stopwords += ['must', 'my', 'myself', 'name', 'namely', 'neither', 'never']
    stopwords += ['nevertheless', 'next', 'nine', 'no', 'nobody', 'none']
    stopwords += ['noone', 'nor', 'not', 'nothing', 'now', 'nowhere', 'of']
    stopwords += ['off', 'often', 'on','once', 'one', 'only', 'onto', 'or']
    stopwords += ['other', 'others', 'otherwise', 'our', 'ours', 'ourselves']
    stopwords += ['out', 'over', 'own', 'part', 'per', 'perhaps', 'please']
    stopwords += ['put', 'rather', 're', 's', 'same', 'see', 'seem', 'seemed']
    stopwords += ['seeming', 'seems', 'serious', 'several', 'she', 'should']
    stopwords += ['show', 'side', 'since', 'sincere', 'six', 'sixty', 'so']
    stopwords += ['some', 'somehow', 'someone', 'something', 'sometime']
    stopwords += ['sometimes', 'somewhere', 'still', 'such', 'system', 'take']
    stopwords += ['ten', 'than', 'that', 'the', 'their', 'them', 'themselves']
    stopwords += ['then', 'thence', 'there', 'thereafter', 'thereby']
    stopwords += ['therefore', 'therein', 'thereupon', 'these', 'they']
    stopwords += ['thick', 'thin', 'third', 'this', 'those', 'though', 'three']
    stopwords += ['three', 'through', 'throughout', 'thru', 'thus', 'to']
    stopwords += ['together', 'too', 'top', 'toward', 'towards', 'twelve']
    stopwords += ['twenty', 'two', 'un', 'under', 'until', 'up', 'upon']
    stopwords += ['us', 'very', 'via', 'was', 'we', 'well', 'were', 'what']
    stopwords += ['whatever', 'when', 'whence', 'whenever', 'where']
    stopwords += ['whereafter', 'whereas', 'whereby', 'wherein', 'whereupon']
    stopwords += ['wherever', 'whether', 'which', 'while', 'whither', 'who']
    stopwords += ['whoever', 'whole', 'whom', 'whose', 'why', 'will', 'with']
    stopwords += ['within', 'without', 'would', 'yet', 'you', 'your']
    stopwords += ['yours', 'yourself', 'yourselves']
    for word in words:
        if word in stopwords:
            words.remove(word)           
    #print(words)
    IT =[
        'Artificial',  'Intelligence' , 'blockchain' , ' Data structure' , 'Programing',
        'Java' ,'C','C++','Python','Mysql','HTML','CSS','coding','Software','Developer'
        ]
    NON_IT = ['Catia','CATIA V5R21','Solid Edge','ANSYS 16.0', 'Creo','Medical']

    candidate = None
    extracted_IT = []
    extracted_NON_IT = []

    for i in words:
        for j in IT:
            if i.lower()==j.lower():
                if i not in extracted_IT:
                    extracted_IT.append(i)
        if i not in extracted_NON_IT:
            extracted_NON_IT.append(i)             

    #print(extracted_IT)
    #print(extracted_NON_IT)        
            
    for i in words:
        if i in IT:
            candidate = "IT"
            break

    if candidate != "IT":
        for i in words:
            if i in NON_IT:
                candidate = "Non_IT" 
    #print(candidate)
    if candidate == None:
        if len(extracted_IT) > len(extracted_NON_IT):
            candidate = "IT"
        elif i in NON_IT and len(extracted_IT)<len(extracted_NON_IT):
            candidate = "Non_IT" 
        else:
            candidate = "Non_IT"

    #print("Candidate Type:",candidate)
    return candidate


nlp = spacy.load("en_core_web_sm")

def Classify_stage3(name2,text):
    
    text = text.lower()
    
    keyword_dict = pd.read_csv('CalssifierSkillsNew.csv',encoding= 'unicode_escape')
   
    java_words = [nlp(text) for text in keyword_dict['Java Developer'].dropna(axis = 0)]
    python_words = [nlp(text) for text in keyword_dict['Python Developer'].dropna(axis = 0)]
    DL_words = [nlp(text) for text in keyword_dict['Deep learning'].dropna(axis = 0)]
    ML_words = [nlp(text) for text in keyword_dict['Machine Learning'].dropna(axis = 0)]
    UI_words = [nlp(text) for text in keyword_dict['UI Designing'].dropna(axis = 0)]
    AI_words = [nlp(text) for text in keyword_dict['Artificial Intelligence'].dropna(axis = 0)]
    Blockchain_words = [nlp(text) for text in keyword_dict['Blockchain'].dropna(axis = 0)]
    Android_words = [nlp(text) for text in keyword_dict['Android Developer'].dropna(axis = 0)]
    Tester_words = [nlp(text) for text in keyword_dict['Software Tester'].dropna(axis = 0)]
    Architect_words = [nlp(text) for text in keyword_dict['Software Architect'].dropna(axis = 0)]
    Cloud_words = [nlp(text) for text in keyword_dict['Cloud administrator'].dropna(axis = 0)]
   
    matcher = PhraseMatcher(nlp.vocab)
    matcher.add('Java', None, *java_words)
    matcher.add('Python', None, *python_words)
    matcher.add('DL', None, *DL_words)
    matcher.add('ML', None, *ML_words)
    matcher.add('UIDevloper', None, *UI_words)
    matcher.add('AI', None, *AI_words)
    matcher.add('Blockchain', None, *Blockchain_words)
    matcher.add('Android', None, *Android_words)
    matcher.add('Tester', None, *Tester_words)
    matcher.add('Architect', None, *Architect_words)
    matcher.add('cloud', None, *Cloud_words)
   
    doc = nlp(text)
   
    d = []  
    a= []
    unique_list = []
    final_unique_list = []
    matches = matcher(doc)
    for match_id, start, end in matches:
        rule_id = nlp.vocab.strings[match_id]  # get the unicode ID, i.e. 'COLOR'
        span = doc[start : end]# get the matched slice of the doc
        d.append((rule_id, span.text))
        a.append((span.text))
        
    keywords = "\n".join(f'{i[0]} {i[1]} ({j})' for i,j in Counter(d).items())
    
    ## convertimg string of keywords to dataframe
    df = pd.read_csv(StringIO(keywords),names = ['Keywords_List'])
    df1 = pd.DataFrame(df.Keywords_List.str.split(' ',1).tolist(),columns = ['Subject','Keyword'])
    df2 = pd.DataFrame(df1.Keyword.str.split('(',1).tolist(),columns = ['Keyword', 'Count'])
    df3 = pd.concat([df1['Subject'],df2['Keyword'], df2['Count']], axis =1)
    df3['Count'] = df3['Count'].apply(lambda x: x.rstrip(")"))
   
    name2 = name2.lower()

    ## converting str to dataframe
    name3 = pd.read_csv(StringIO(name2),names = ['Candidate Name'])
    dataf = pd.concat([name3['Candidate Name'], df3['Subject'], df3['Keyword'], df3['Count']], axis = 1)
    dataf['Candidate Name'].fillna(dataf['Candidate Name'].iloc[0], inplace = True)
    #print(d)
    #print(dataf)
   
    final_database=pd.DataFrame()
    final_database = final_database.append(dataf)
    #print(final_database)

    final_database2 = final_database['Keyword'].groupby([final_database['Candidate Name'], final_database['Subject']]).count().unstack()
    final_database2.reset_index(inplace = True)
    final_database2.fillna(0,inplace=True)
    new_data = final_database2.iloc[:,1:]
    new_data.index = final_database2['Candidate Name']


    final_database3 = final_database['Keyword'].groupby([final_database['Candidate Name'], final_database['Subject']]).count().unstack()
    final_database3.max(axis=1, skipna=None, level=None, numeric_only=None)
    final_database3['Prefered Subject'] = final_database3.idxmax(axis=1)
    #print(final_database3)


    final_database3.reset_index(inplace=True)
    final_database3.set_index('Candidate Name', inplace =True)
    indexes = list(final_database3.index.values)

    #print(indexes)
    for i in indexes:
        domain = False
        count_matched_skills = 0
        a = final_database3.at[i,'Prefered Subject']

    return a
