# -*- coding: utf-8 -*-
"""vodSummurizer.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/11GPDyjcYrP1XXmp2KN88nuaZ0hXK2p7s
"""

!pip install pytchat #載入聊天室的工具包
!pip install git+https://github.com/pytube/pytube #影片資訊工具包

#圖表友善字體
!wget -O TaipeiSansTCBeta-Regular.ttf https://drive.google.com/uc?id=1eGAsTN1HBpJAkeVM57_C7ccp7hbgSz3_&export=download

!pip install nltk #NLP工具包

!pip install emosent-py #表情符號情緒分析工具包

!pip install -U LeXmo #情緒分析工具包

from sklearn.feature_extraction.text import TfidfVectorizer
from pytube import YouTube

import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.font_manager import fontManager

import nltk
nltk.download('punkt')
import pandas as pd
from nltk import word_tokenize
from nltk.stem.snowball import SnowballStemmer
import requests, json, re, pytchat, time
from LeXmo import LeXmo
import numpy as np
# from emosent import get_emoji_sentiment_rank

url = 'https://youtu.be/7qfhmZqXE-0'
videoToken = url[17:]

# 獲取影片標題
YouTube(url).title
# 獲取影片時長（後面在抓留言的時候，會將此時長作為進度條顯示）
videoTime = YouTube(url).length
formatVideoTime = str(videoTime//60//60)+':'+str(videoTime//60%60)+':'+str(videoTime%60)

"""## 抓取留言"""

# 抓取留言
chats = []
chat = pytchat.create(video_id=videoToken)
while chat.is_alive():
    data = chat.get()
    for ele in data.items:
        chats.append({
            'authorName': ele.author.name,
            'authorType': ele.author.type,
            'mod': ele.author.isChatModerator,
            'type': ele.type,
            'elapsedTime': ele.elapsedTime,
            'message': ele.message,
            'messageEx': ele.messageEx
        })
    print(chats[-1]['elapsedTime'],'/',formatVideoTime)
    time.sleep(3)

# 紀錄聊天室爬蟲內容
with open('drunkZatsudan.json', 'w+') as jsonFile:
    json.dump(chats, jsonFile, indent=4)

"""## 初步整理聊天室資訊"""

# 讀取聊天室爬蟲內容
with open('Zatsudan.json', 'r') as jsonFile:
    chats = json.load(jsonFile)

# 初步整理聊天室資訊
rawData = []
for ele in chats:
    sentence = []
    emoji = []
    ytEmoji = []
    for message in ele['messageEx']:
        if type(message)==str:
            sentence.append(message)
        else:
            if len(message['txt']) < 2:
                emoji.append({
                        'id': message['id'],
                        'txt': message['txt']
                })
            else:
                if message['txt'][1] != '_':
                    emoji.append({
                        'id': message['id'],
                        'txt': message['txt']
                    })
                else:
                    ytEmoji.append({
                        'id': message['id'],
                        'txt': message['txt']
                    })
    rawData.append({
        'authorName': ele['authorName'],
        'authorType': ele['authorType'],
        'mod': ele['mod'],
        'type': ele['type'],
        'elapsedTime': ele['elapsedTime'],
        'message': ele['message'],
        'messageWord': sentence,
        'emoji': emoji,
        'ytEmoji': ytEmoji
    })

# 每則整理後資訊的範例
rawData[-80]

# 整理後資訊存檔
with open('drunkZatsudan_rawData.json', 'w+') as jsonFile:
    json.dump(rawData, jsonFile, indent=4)

"""## 前處理"""

with open('/content/drive/MyDrive/大四/文字探勘/期末專案/drunkZatsudan_rawData.json', 'r') as jsonFile:
    rawData = json.load(jsonFile)

# 刪除重複字母
# target: 訊息
# limit: 遇到多少字母的時候才刪除
def singulate(target:str, limit:int):
    result = ''
    # print(sentence,end='->')
    for word in target.split():
        result += ' '
        if len(word) > 2:
            currWord = [word[0]]
            count = 0
            flag = False
            for i in range(len(word)-1):
                if word[i] == word[i+1]:
                    count += 1
                else:
                    currWord.append(word[i+1])
                    if count >= limit-1:
                        flag = True
                    count = 0
            if flag or count >= limit-1:
                result += ''.join(currWord)
                # print(''.join(currWord))
            else:
                result += word
                # print(word)
        else:
            result += word
    return result[1:]

# 針對直播的語料庫
# 將常見的縮寫解壓縮
chatCorpus = {
    'u': 'you',
    'lmao': 'laugh my ass off',
    'cuz': 'because',
    'fr': 'for real',
    'lol': 'laugh out loud',
    'af': 'as fuck',
    'irl': 'in real life',
    'ily': 'i love you',
    'brb': 'be right back',
    'bs': 'bullshit',
    'tldr': 'too long, didn\'t read',
    'tl;dr': 'too long, didn\'t read',
    'naur': 'no',
    'omg': 'oh my god',
    'wtf': 'what the fuck',
    'wth': 'what the hell',
    'tf': 'the fuck',
    'aww': 'so cute',
    'eww': 'yuck',
    'eng': 'english',
    'en': 'english',
    'jp': 'japan',
    'w/': 'with',
    'w/o': 'without',
    'tbh': 'to be honest',
    'aka': 'as known as',
    'btw': 'by the way',
    'xoxo': 'kisses and hugs',
    'bff': 'best friend forever',
    'bro': 'brother',
    'sis': 'sister',
    'grl': 'girl',
    'bt': 'but',
    'ic': 'i see',
    'afk': 'away from keyboard',
    'nm': 'never mind',
    'plz': 'please',
    'pls': 'please',
    'rip': 'rest in peace',
    'tbd': 'to be determined',
    'tyt': 'take your time',
    'ur': 'your',
    'thx': 'thanks',
    'idk': 'i don\'t know',
    'jk': 'just kidding',
    'smh': 'shake my head',
    'np': 'no problem',
    'rofl': 'rolling on the floor laughing',
    'imho': 'in my humble opinion',
    'imo': 'in my opinion',
    'etc': 'and so on',
    'gotta': 'got to',
    'gonna': 'going to',
    'wanna': 'want to',
    'woulda': 'would have',
    'sorta': 'sort of',
    'kinda': 'kind of',
    'hafta': 'have to',
    'coulda': 'could have',
    'musta': 'must have',
    'losta': 'a lot of',
    'gg': 'good game',
    'nt': 'nice try',
    'ns': 'nice shot',
    'asap': 'as soon as possible',
    'cya': 'see you',
    'wdym': 'what do you mean',
    'stfu': 'shut the fuck up',
    'tia': 'thanks in advance',
    'vs': 'versus',
    'g2g': 'got to go',
    'wc': 'water closet',
    'unseiso': 'dirty minded',
    'sus': 'suspicious',
    'sussy': 'suspicious',
    'ikz': 'let\'s go',
    'ayo': 'hey, you',
    'tskr': 'it really saves me',
    'caught in 4k': 'i got a evidence of what you\'ve done',
    'uwe': 'crying',
    'zzz': 'sleeping',
    'boomer': 'old people',
    'zoomer': 'young man',
    'kiddo': 'kid',
    'dmg': 'damage',
    'min': 'minute',
    'mins': 'minutes',
    'sec': 'second',
    'secs': 'seconds',
    'mogu': 'eating',
    'otsu': 'thank you for your work',
    'ganba': 'do your best',
    'pog': 'awesome',
    'sc': 'donation',
    'supa': 'donation',
    'ppl': 'people',
    'bbg': 'baby girl',
    'sheesh': 'damn',
    'rn': 'right now',
    'tbf': 'to be fair',
    'ikr': 'i know, right?',
    'o7': 'respect',
    'yeet': 'throw',
    'copium': 'lying to yourself',
    'forgor': 'forgot',
    'hbu': 'how about you',
    'gm': 'good morning',
    'gn': 'good night',
    'tho': 'though',
    'omfg': 'oh my fucking god',
    'gg': 'good game',
    'wb': 'welcome back',
    'thx': 'thanks',
    'va': 'voice acting',
    'daz': 'that\'s',
    'y\'all': 'you all'
}

# 解壓縮縮寫
# target: 訊息
# corpus: 解壓縮參照的語料庫
def refCorpus(target:str, corpus:dict):
    result = ''
    lowSent = target.lower()
    for word in lowSent.split():
        result += ' '
        if word in corpus.keys():
            result += corpus[word]
        else:
            result += word
    return result[1:]

for chat in rawData:
    chat['messageWord'] = ''.join(chat['messageWord'])
    chat['uniMessage'] = singulate(chat['messageWord'], 3)
    chat['unzipMessage'] = refCorpus(chat['uniMessage'], chatCorpus)

# 前處理結果
rawData[2340]

with open('drunkZatsudan_preprocess.json', 'w+') as jsonFile:
    json.dump(rawData, jsonFile, indent=4)

"""# 分析"""

# 讀取聊天室內容
with open('/content/drive/MyDrive/大四/文字探勘/期末專案/Movie_preprocess.json', 'r') as jsonFile:
    chats = json.load(jsonFile)

"""## 關鍵字"""

time_per_halfMin = {}
for message in chats:
    if int(message['elapsedTime'][-2]) > 3:
        time = message['elapsedTime'][:-3]+':30'
    else:
        time = message['elapsedTime'][:-3]+':00'
    if time not in time_per_halfMin.keys():
        time_per_halfMin[time] = [message]
        # comments_per_sec[time] = [message.lower().split('　')]
    else:
        time_per_halfMin[time].append(message)

count_per_halfMin = []
for comments in time_per_halfMin.values():
    count_per_halfMin.append(len(comments))

plt.rcParams["figure.figsize"] = [550, 20]
plt.rcParams.update({'font.size': 54})
plt.plot(list(time_per_halfMin.keys()),
         count_per_halfMin,
         linewidth=5)

fontManager.addfont('TaipeiSansTCBeta-Regular.ttf')
mpl.rc('font', family='Taipei Sans TC Beta')

plt.xticks(fontsize=18)
plt.title(YouTube(url).title, {'fontname':'Taipei Sans TC Beta'})
plt.ylabel('amount of comments (per minute)')
plt.xlabel('time')

avg = round(sum(count_per_halfMin)/len(count_per_halfMin))

over_avg = []
for time in time_per_halfMin.keys():
    if len(time_per_halfMin[time]) >= avg:
        over_avg.append(time)

print(avg, ': ',over_avg)
print('->共',len(over_avg))

setOfUniMessage = {}
setOfUnzipMessage = {}
for time in time_per_halfMin.keys():
    setOfUniMessage[time] = ' '.join(
        ele['uniMessage'] for ele in time_per_halfMin[time] if ele['uniMessage'] != '' and ele['uniMessage'] != ' ')
    setOfUnzipMessage[time] = ' '.join(
        ele['unzipMessage'] for ele in time_per_halfMin[time] if ele['unzipMessage'] != '' and ele['unzipMessage'] != ' ')

results = {}
for time in over_avg:
    ## keyword
    # initialise TfidfVectorizer
    vectoriser = TfidfVectorizer(norm = None)
    # obtain weights of each term to each document in corpus (ie, tf-idf scores)
    tf_idf_scores = vectoriser.fit_transform([setOfUniMessage[time]])
    # get vocabulary of terms
    feature_names = vectoriser.get_feature_names()
    corpus_index = [n for n in [setOfUniMessage[time]]]
    # create pandas DataFrame with tf-idf scores: Term-Document Matrix
    df_tf_idf = pd.DataFrame(tf_idf_scores.T.todense(), index = feature_names, columns = [time])
    result = df_tf_idf.to_dict()[time]

    keyword = []
    for word in result.keys():
        # if word not in stopwords.words('english') and result[word] > 10:
        #     keyword.append(word)
        if result[word] > 5:
            keyword.append(word)
    results[time] = {}
    results[time]['keyword'] = keyword

    ## emotion
    max = 0
    if setOfUnzipMessage[time] != '':
        emo = LeXmo.LeXmo(setOfUnzipMessage[time])
        emo.pop('text', None)
        count = 0
        for e in emo:
            # print(e, emo[e])
            if e != 'positive' and e != 'negative':
                if emo[e] == 0.0:
                    count += 1
                if count == 8:
                    results[time]['emotion_score'] ={}
                if emo[e] > max:
                    max = emo[e]
                    highest_emo = e
                    if emo[e] > 0.08:
                        results[time]['emotion_score'] = {e: max}
                    else:
                        results[time]['emotion_score'] = {}

    ## emoji
    count = {}
    for message in time_per_halfMin[time]:
        for emoji in message['emoji']:
            if emoji['txt'] != '':
                if emoji['txt'] in count.keys():
                    count[emoji['txt']] += 1
                else:
                    count[emoji['txt']] = 1
        for emoji in message['ytEmoji']:
            if emoji['txt'] != '':
                if emoji['txt'] in count.keys():
                    count[emoji['txt']] += 1
                else:
                    count[emoji['txt']] = 1
    results[time]['emoji'] = count

roughStopword = ['the', 'was', 'is', 'are', 'were', 'to', 'of', 'for', 'in', 'and']

for time in results.keys():
    print(time)
    for keyword in results[time]['keyword']:
        if keyword in roughStopword:
            continue
        for message in time_per_halfMin[time]:
            if keyword in message['uniMessage'].split(' '):
                print(keyword,'->', end='')
                print(message['uniMessage'])
                break
    print(results[time]['emotion_score'])
    print(results[time]['emoji'])
    print('-'*30)
