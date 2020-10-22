import PyPDF2
import os
from os import listdir
from os.path import isfile, join
from io import StringIO
import pandas as pd
from collections import Counter
#import en_core_web_sm
#nlp = en_core_web_sm.load()
import spacy
nlp = spacy.load("en_core_web_sm")
from spacy.matcher import PhraseMatcher
import B as b
import matplotlib.pyplot as plt


def create_profile(obj):   #obj is tuple as (name,text) for all candidates

    text = obj[1]
    text = text.lower()
    
    #below is the csv where we have all the keywords, you can customize your own
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
    matches = matcher(doc)
    for match_id, start, end in matches:
        rule_id = nlp.vocab.strings[match_id]  # get the unicode ID, i.e. 'COLOR'
        span = doc[start : end]  # get the matched slice of the doc
        d.append((rule_id, span.text))      
    keywords = "\n".join(f'{i[0]} {i[1]} ({j})' for i,j in Counter(d).items())
    
    ## convertimg string of keywords to dataframe
    df = pd.read_csv(StringIO(keywords),names = ['Keywords_List'])
    df1 = pd.DataFrame(df.Keywords_List.str.split(' ',1).tolist(),columns = ['Subject','Keyword'])
    df2 = pd.DataFrame(df1.Keyword.str.split('(',1).tolist(),columns = ['Keyword', 'Count'])
    df3 = pd.concat([df1['Subject'],df2['Keyword'], df2['Count']], axis =1) 
    df3['Count'] = df3['Count'].apply(lambda x: x.rstrip(")"))
    
    #base = os.path.basename(file)
    #filename = os.path.splitext(base)[0]
       
    #name = filename.split('_')
    name2 = obj[0]
    ## converting str to dataframe
    name3 = pd.read_csv(StringIO(name2),names = ['Candidate Name'])
    
    dataf = pd.concat([name3['Candidate Name'], df3['Subject'], df3['Keyword'], df3['Count']], axis = 1)
    dataf['Candidate Name'].fillna(dataf['Candidate Name'].iloc[0], inplace = True)

    return(dataf)
   
    
def getGraph(candidates): # candidates is a list of tuples
    final_database=pd.DataFrame()
    i = 0 
    while i < len(candidates):
        obj = candidates[i]
        dat = create_profile(obj)
        final_database = final_database.append(dat)
        i +=1


    final_database2 = final_database['Keyword'].groupby([final_database['Candidate Name'], final_database['Subject']]).count().unstack()
    final_database2.reset_index(inplace = True)
    final_database2.fillna(0,inplace=True)
    new_data = final_database2.iloc[:,1:]
    new_data.index = final_database2['Candidate Name']

    #print("---------")
    #print(final_database2)
    #print("----------")
    final_database3 = final_database['Keyword'].groupby([final_database['Candidate Name'], final_database['Subject']]).count().unstack()


    #print("----------")
    #print(final_database3)    

    plt.rcParams.update({'font.size': 10})
    ax = new_data.plot.barh(title="Resume keywords by category", legend=False, figsize=(25,7), stacked=True)
    labels = []
    for j in new_data.columns:
        for i in new_data.index:
            label = str(j)+": " + str(new_data.loc[i][j])
            labels.append(label)
    patches = ax.patches
    for label, rect in zip(labels, patches):
        width = rect.get_width()
        if width > 0:
            x = rect.get_x()
            y = rect.get_y()
            height = rect.get_height()
            ax.text(x + width/2., y + height/2., label, ha='center', va='center')

    #return ax
    my_path = os.path.abspath(os.path.dirname(__file__)) + '/static/graph_images/'

    plot_name = 'graph.png'
    
    url = my_path + plot_name
    for filename in os.listdir('static/graph_images'):
        if filename.startswith('graph_'):  # not to remove other images
            os.remove('static/graph_images' + filename)

    #plt.savefig('/static/graph_images/'+plot_name)
    plt.savefig(url)
    return plot_name


#file = r"C:\Users\Rutuja\Desktop\New Folder\CS-IT\Rutuja.docx"
#text = b.extract_text_from_doc(file)
#name = b.extract_name(text)
#print(create_profile(name,text))
#text = text.replace("\\n", "")
#text = text.lower()
#print(text)