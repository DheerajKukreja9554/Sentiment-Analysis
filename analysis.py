import pandas as pd
import nltk
from nltk import sent_tokenize,WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

import requests
from bs4 import BeautifulSoup


# ### making list of positive and negative words using link given in problem statement

word_dict=pd.read_csv('files/master dictionary/LoughranMcDonald_MasterDictionary_2020.csv')

positive_words=list(word_dict.Word[word_dict.Positive>0])
positive_words=[word.lower() for word in positive_words]

negative_words=list(word_dict.Word[word_dict.Negative>0])
negative_words=[word.lower() for word in negative_words]

# ### making List of stop words using link given in problem statement

text=''
file_names=['StopWords_Auditor','StopWords_Currencies','StopWords_DatesandNumbers','StopWords_Generic','StopWords_GenericLong','StopWords_Geographic','StopWords_Names']
for file_name in file_names:
    with open(f'files/stop_words/{file_name}.txt','r') as file:
        text+=file.read()
stop_words=list(text.replace('|','').split())
# stop_words2=stopwords.words('english')
# stop_words2
# making stop words list from the link given in objective file


# ### reading input

input_data=pd.read_excel('files/Input.xlsx')

# ### extracting text files from articles and saving them with their respective id names in articles folder
def extract_text(url_id,url):
    page=requests.get(url, headers={"User-Agent": "XY"}) 
    data=page.content
    soup=BeautifulSoup(data,'html.parser')
    article_title = soup.find('title').text.strip()
    article_content=soup.find("div",attrs={'class':"td-post-content"}).text.strip()
    with open(f"articles/{url_id}.txt",'w', encoding="utf-8") as f:
        f.write(article_title+'\n')
        f.write(article_content)

input_data.apply(lambda row: extract_text(row['URL_ID'],row['URL']),axis=1)

# ### function to preprocess text, i.e, break text into sentences and words and then removing stop words from text and lowercasing it

def preprocess_text(text:str):
    sentences=sent_tokenize(text)
    tokens=word_tokenize(text)
    lemma=WordNetLemmatizer()
    punctuations=['?','!',',','.']
    words=[lemma.lemmatize(word.lower()) for word in tokens if word.isalpha() and word not in stop_words and word not in punctuations]
    return sentences,tokens,words

# ### to count positive and negative score of a text 

def score(words):
    pos_score=0
    neg_score=0
    for word in words:
        if word in positive_words:
            pos_score+=1
        if word in negative_words:
            neg_score-=1
    neg_score*=-1
    return pos_score,neg_score

# ### to count complex words
def count_syllables(word:str):
    vowels='aeiou'
    endings=['es','ed']
    syllables=0
    for i in word:
        if i in vowels:
            syllables+=1
    for end in endings:
        if word.endswith(end):
            syllables-=1
            break
    if word.endswith('le'):
        syllables+=1
    return syllables
def count_complex_words(words):
    complex_word_counts=0
    total_syllables=0
    for word in words:
        if count_syllables(word)>2:
            complex_word_counts+=1
        total_syllables+=1
    return complex_word_counts,total_syllables

# ### to count personal prononuns 

def count_pronouns(words):
    pronouns=['i','we','us','ours','my','I','We','Us','Ours','My']
    pronoun_count=0
    for word in words:
        if word in pronouns:
            pronoun_count+=1
    return pronoun_count

# ### total number of characters in a text 

def count_characters(words):
    character_count=0
    for word in words:
        character_count+=len(word)
        
    return character_count

# ### analyse the text for respective variables

def analyse_text(url_id):
    with open(f'articles/{url_id}.txt','r',encoding='utf8') as file:
        text=file.read().lower()
    sentences,words,cleaned_words=preprocess_text(text)
    pos_score,neg_score=score(cleaned_words)
    
    polarity=round((pos_score-neg_score)/((pos_score+neg_score)+0.000001),6)
    
    subjectivity=round((pos_score+neg_score)/(len(cleaned_words)+0.000001),6)
    
    average_sentence_length=round(len(words)/len(sentences))
    
    complex_word_counts, syllable_count =count_complex_words(words)
    
    complex_words_percentage=round(complex_word_counts*100/len(words),ndigits=6)
    
    fog_index=round(.4*(average_sentence_length+complex_words_percentage),ndigits=6)
    
    clean_word_count=len(cleaned_words)
    
    syllable_per_word= round(syllable_count/len(words))
    
    pronoun_count=count_pronouns(words)
    
    character_count=count_characters(words)
    
    average_word_length=round(character_count/len(words))
    
    return pos_score,neg_score,polarity,subjectivity,average_sentence_length,complex_words_percentage,fog_index,average_sentence_length,complex_word_counts,clean_word_count,syllable_per_word,pronoun_count,average_word_length

# making list of all new columns to be added
new=['POSITIVE SCORE', 'NEGATIVE SCORE', 'POLARITY SCORE','SUBJECTIVITY SCORE', 'AVG SENTENCE LENGTH','PERCENTAGE OF COMPLEX WORDS', 'FOG INDEX','AVG NUMBER OF WORDS PER SENTENCE', 'COMPLEX WORD COUNT', 'WORD COUNT','SYLLABLE PER WORD', 'PERSONAL PRONOUNS', 'AVG WORD LENGTH']

# output dataframe for storing output
output_data=input_data

#making dataframe of all new columns to be added for analysed test
new_data=pd.DataFrame(list(input_data.apply(lambda row: analyse_text(row['URL_ID']),axis=1)),columns=new)

# joining output and new data
output_data=output_data.join(new_data)

print(output_data)

output_data.to_excel(f'files/output.xlsx')

