#!/user/bin/env python
# -*- coding: utf-8 -*-


import re
import json
import logging
import pandas as pd
from random import choice
from datetime import datetime

import ingredientBot as iB

inSeasonDICT = json.load(open("./info/inSeason.json", encoding="utf-8")) 
IngredientRelatedDICT = json.load(open("./info/ingredient.json", encoding="utf-8"))


def checkInSeason(ingredient):
    currentMonth = datetime.now().month
    ingr_inseasonLIST = inSeasonDICT[str(currentMonth)+"月"]

    if ingredient in ingr_inseasonLIST:
        return True
    else:
        return False

def inSeason(rejectLIST):
    currentMonth = datetime.now().month
    ingr_inseasonLIST = inSeasonDICT[str(currentMonth)+"月"]
    ingr_inseason_excludeLIST = [x for x in ingr_inseasonLIST if x not in rejectLIST]

    return choice(ingr_inseason_excludeLIST)

def price(ingredient):
    table = pd.read_html("http://www.tapmc.com.taipei/")
    table[0].columns = ['品名', '品種', '上價', '中價', '下價']

    priceDICT={}
    for index,row in table[0].iterrows():
        tmp=[]
        tmp.append(row["上價"])
        tmp.append(row["中價"])
        tmp.append(row["下價"])
        name = str(row["品名"]) + "(" + str(row["品種"]) + ")"
        priceDICT[name]=tmp

    ingr_priceDICT={}
    for key in priceDICT.keys():
        if ingredient in key:
            ingr_priceDICT[key]=priceDICT[key]

    return ingr_priceDICT

def recipe(ingredient):
    if ingredient in IngredientRelatedDICT:
        return IngredientRelatedDICT[ingredient]["作法"]
    else:
        return {}
    
def taboo(ingredient):
    if ingredient in IngredientRelatedDICT:
        return IngredientRelatedDICT[ingredient]["禁忌"]
    else:
        return {}

def getLokiResult(inputSTR):
    punctuationPat = re.compile("[,\.\?:;，。？、：；\n]+")
    inputLIST = punctuationPat.sub("\n", inputSTR).split("\n")
    filterLIST = []
    resultDICT = iB.runLoki(inputLIST, filterLIST)

    return resultDICT

def model(mscDICT):
    resultDICT = getLokiResult(mscDICT["msgSTR"])
    logging.info("Loki 回傳的結果: {}".format(resultDICT))
    
    if len(resultDICT) > 0: #有找到對應的intent

        #intent = check，想確認這項食材是不是當季
        if "check" in resultDICT.keys():
            if checkInSeason(resultDICT["ingredient"]):
                mscDICT["replySTR"] = resultDICT["ingredient"] + "是當季食材沒錯！"
            else:
                mscDICT["replySTR"] = resultDICT["ingredient"] + "不是當季食材哦~"

        #intent = price，想知道這項食材的價格
        if "price" in resultDICT.keys():
            if datetime.today().weekday() == 0: #星期一休市
                mscDICT["replySTR"] = "今日休市"
            else:
                ingr_priceDICT = price(resultDICT["ingredient"])
                if len(ingr_priceDICT) > 0:
                    replySTR = ""
                    for key in ingr_priceDICT:
                        replySTR = replySTR + key + "的今日價格：{}元(上價)，{}元(中價)，{}元(下價)".format(ingr_priceDICT[key][0], ingr_priceDICT[key][1], ingr_priceDICT[key][2]) + "\n"

                    mscDICT["replySTR"] = replySTR
                else:
                    mscDICT["replySTR"] = "查不到這個品項的價錢 QAQ"
        
        #intent = inseason，想知道現在有哪些當季食材
        if "inseason" in resultDICT.keys():
            ingr_inseason = inSeason(mscDICT["rejectLIST"])
            mscDICT["ingr_inseason"] = ingr_inseason
            mscDICT["replySTR"] = ingr_inseason + "是現在的當季食材哦！"

        #intent = reject
        if "reject" in resultDICT.keys():
            if "reject_ingr" in resultDICT.keys():
                reject_ingr = resultDICT["reject_ingr"]
            else:
                reject_ingr = mscDICT["ingr_inseason"]   #如果回覆中未提到討厭甚麼食材，以上一次提供的當季食材當作討厭的食材
            mscDICT["rejectLIST"].append(reject_ingr)   #紀錄使用者reject過的食材

            #再提供另一個當季食材            
            ingr_inseason = inSeason(mscDICT["rejectLIST"])
            mscDICT["ingr_inseason"] = ingr_inseason
            mscDICT["replySTR"] = "那麼" + ingr_inseason + "如何？"

        #intent = recipe，想知道這項食材有什麼作法
        if "recipe" in resultDICT.keys():
            recipe_result = recipe(resultDICT["ingredient"])
            if len(recipe_result) > 0:
                mscDICT["replySTR"] = recipe_result
            else:
                mscDICT["replySTR"] = "查不到這種食材的作法 QAQ"

        #intent = taboo
        if "taboo" in resultDICT.keys():
            taboo_result = taboo(resultDICT["ingredient"])
            if len(taboo_result) > 0:
                mscDICT["replySTR"] = taboo_result
            else:
                mscDICT["replySTR"] = "這邊沒有記載這項食材的禁忌 QAQ"
            
    else: #沒有對應的句型
        if mscDICT["msgSTR"].lower() in ["哈囉","嗨","你好","您好","hi","hello", "早安", "午安", "晚安", "早"]:
            mscDICT["replySTR"] = "嗨嗨 o(^▽^)o"
        else:
            mscDICT["replySTR"] = "你說啥呢"
    
    return mscDICT

