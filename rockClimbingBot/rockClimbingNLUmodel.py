from rockClimbing import runLoki
import json
import logging
import pandas as pd
import re

gymsInfo = pd.read_csv('data/climbingGym.csv', encoding = 'utf-8')
defaultResponse = json.load(open("data/defaultResponse.json",encoding="utf-8"))

def getLokiResult(inputSTR):
    punctuationPat = re.compile("[,\.\?:;，。？、：；\n]+")
    inputLIST = punctuationPat.sub("\n", inputSTR).split("\n")
    filterLIST = []
    #if "規則" in inputSTR or "規定" in inputSTR:
        #lokiRst = LokiResult(inputLIST, filterLIST)
        #resultDICT = Loki_rules.getResult(key, lokiRst.getUtterance(index, resultIndex), lokiRst.getArgs(index, resultIndex), resultDICT)
    #else:
    resultDICT = runLoki(inputLIST, filterLIST)
    logging.debug("Loki Result => {}".format(resultDICT))
    return resultDICT

def NLUmodel(mscDICT):
    print('mscDICT["msgSTR"]==',mscDICT["msgSTR"])
    resultDICT = getLokiResult(mscDICT["msgSTR"])
    logging.info("\nLoki 處理結果如下: {}\n".format(resultDICT))

    if len(resultDICT) > 0: #放找得到對應intent
        if "規則" in mscDICT["msgSTR"] or "規定" in mscDICT["msgSTR"]:
            if "reply_rules" in resultDICT.keys():
                mscDICT["replySTR"] = resultDICT["reply_rules"]
            print("\n---rules---\n")
        elif "錢" in mscDICT["msgSTR"] or "多少" in mscDICT["msgSTR"]:
            if "reply_gym_price" in resultDICT.keys():
                mscDICT["replySTR"] = resultDICT["reply_gym_price"]
            print("\n---price---\n")
        elif "幾時" in mscDICT["msgSTR"] or "幾點" in mscDICT["msgSTR"] or "何時" in mscDICT["msgSTR"] or "開" in mscDICT["msgSTR"] or "關" in mscDICT["msgSTR"]:
            if "reply_gym_time" in resultDICT.keys():
                mscDICT["replySTR"] = resultDICT["reply_gym_time"]
            print("\n---time---\n")
        elif "位置" in mscDICT["msgSTR"] or "地址" in mscDICT["msgSTR"] or "電話" in mscDICT["msgSTR"]  or "資訊" in mscDICT["msgSTR"] or "聯絡" in mscDICT["msgSTR"]:
            if "reply_gym_location" in resultDICT.keys():
                mscDICT["replySTR"] = resultDICT["reply_gym_location"]
            print("\n---location---\n")
        elif "買" in mscDICT["msgSTR"] or "租" in mscDICT["msgSTR"]:
            if "reply_equipment_whereGet" in resultDICT.keys():
                mscDICT["replySTR"] = resultDICT["reply_equipment_whereGet"] 
            print("\n---equipment where get---\n")
        else:
            if "reply_gym_distance" in resultDICT.keys():
                mscDICT["replySTR"] = resultDICT["reply_gym_distance"]  
    
            if "reply_whatIs" in resultDICT.keys():
                mscDICT["replySTR"] = resultDICT["reply_whatIs"]
        
            if "reply_gym_price" in resultDICT.keys():
                mscDICT["replySTR"] = resultDICT["reply_gym_price"]
    
            if "reply_gym_time" in resultDICT.keys():
                mscDICT["replySTR"] = resultDICT["reply_gym_time"]
            
            if "reply_person_location" in resultDICT.keys():
                mscDICT["replySTR"] = resultDICT["reply_person_location"]
                resultDICT["_distance_intent"] = 0
        
            if "reply_chat" in resultDICT.keys():
                mscDICT["replySTR"] = resultDICT["reply_chat"]
        
            if "reply_gym_name" in resultDICT.keys():
                if resultDICT["_person_loc"] == "": #若有地點資訊，可以回答的問題：附近岩館
                    mscDICT["replySTR"] = "請問您在哪裡呢？可以給我一個地址或縣市嗎？"
                else:
                    mscDICT["replySTR"] = resultDICT["reply_gym_name"]
                    
            if "reply_gym_location" in resultDICT.keys():
                if resultDICT["_gym_name"] == "":
                    mscDICT["replySTR"] = "請問想問哪間岩館呢？"
                else:
                    mscDICT["replySTR"] = resultDICT["reply_gym_location"]            
        
            if "reply_gym_howMany" in resultDICT.keys():
                mscDICT["replySTR"] = resultDICT["reply_gym_howMany"]
        
            if "reply_gym_yesNo" in resultDICT.keys():
                mscDICT["replySTR"] = resultDICT["reply_gym_yesNo"]
        
            if "reply_equipment_list" in resultDICT.keys():
                mscDICT["replySTR"] = resultDICT["reply_equipment_list"]
        
            if "reply_equipment_price" in resultDICT.keys():
                mscDICT["replySTR"] = resultDICT["reply_equipment_price"]
        
            if "reply_equipment_yesNo" in resultDICT.keys():
                mscDICT["replySTR"] = resultDICT["reply_equipment_yesNo"]
        
            if "reply_rocks" in resultDICT.keys():
                mscDICT["replySTR"] = resultDICT["reply_rocks"]
        
            if "reply_rules" in resultDICT.keys():
                mscDICT["replySTR"] = resultDICT["reply_rules"]
                
            if "reply_equipment_whereGet" in resultDICT.keys():
                mscDICT["replySTR"] = resultDICT["reply_equipment_whereGet"] 
    
    else: #沒有對應intent
        mscDICT["replySTR"] = "不太明白你的意思欸"

    return mscDICT