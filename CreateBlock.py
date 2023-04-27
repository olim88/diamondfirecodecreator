#create codeblocks
from ast import List, Str
import fileHandling
import json
#base vars
file = "dfcode.json"
fileHandling.CodeTools.loadFileData(file)
codeTools = fileHandling.CodeTools.LoadTools()


#block functions
def GroupBlocks(blocks: List):
    return ({"blocks":blocks})

def CreateBracket(state:Str): # open or closed
    block = {"id": "bracket", "direct": "", "type": "norm"}
    block["direct"] = state
    return block

def CreateBlock(blockType:str,actionType:Str = None,items: List = None,data: Str = None,NOT:bool = False,subAction:Str = None,target = None):#the block type is the type of block e.g. IF PLAYER, action type is used when the block has diffrent options like PLAYER LEFT CLICK or PLAYER RIGHT CLICK, the items are the things to go in the chest, and the data is used in things like functions where it has a name or calls a function with that name,NOT is for if statements if thay are not if
    block = {"id": "block", "block": "", "args": {}}#base layout for the block   
    block["block"] = fileHandling.CodeTools.GetCodeBlockByName(blockType)["identifier"]#the final block needs identifier not name but code is given name
    if actionType != None:#the action of the block e.g. send message
        block["action"] = actionType
    if target != None:
        block["target"] = target
    if subAction != None:#the second action of the block e.g. while player near
        block["subAction"] = subAction
    if items != None:#the items inside the blocks chest
        block["args"] = {"items":items}    
    elif actionType != None:
        if subAction != None:
            actionType= subAction
        try:
            if GetBaseActionItem(actionType) != []:
                block["args"] = {"items":[GetBaseActionItem(actionType)]}
            else:
                block["args"] = {"items":[]} 
            
        except:
           block["args"] = {"items":[]} 
    else:              
        block["args"] = {"items":[]} 
    if NOT == True:
        block["inverted"] = "NOT"
    if data != None:#the function name 
        block["data"] =data      
    return block

#item functions
def GetValueItem(value,idType:str,slot:int = 0): #num, txt, how the variable can be used,slot in chest
    if idType == "num":
        item = {"item":{"id":idType,"data":{"name":float(value)}},"slot":slot} 
    else:
        item = {"item":{"id":idType,"data":{"name":value}},"slot":slot}    
    return item
    
def GetValueVarItem(name,scope="",slot = 0): #scope is unsaved,saved($),local(~)
    scopes = {"":"unsaved","$":"saved","~":"local"}
    item = {"item":{"id":"var","data":{"name":name,"scope":scopes[scope]}},"slot":slot} 
    return item 

def GetLocationValueItem(x,y=0,z=0,pitch=0,yaw=0,slot = 0): 
    if y == None:
        y = 0
    if z == None:
        z = 0
    if pitch == None:
        pitch = 0
    if yaw == None:
        yaw = 0
    item = {"item":{"id":"loc","data":{"isBlock":False,"loc":{"x":float(x),"y":float(y),"z":float(z),"pitch":float(pitch),"yaw":float(yaw)}}},"slot":slot}    
    return item

def GetSoundItem(sound,pitch=1,volume=1,slot = 0):
    if pitch == None:
        pitch = 1
    if volume == None:
        volume = 1
    item = {"item":{"id":"snd","data":{"sound":sound.replace("\"",""),"pitch":float(pitch),"vol":float(volume)}},"slot":slot} 
    return item

def GetPotionItem(potType,duration="60",ampifcation="1",slot = 0):
    if duration == None:
        duration = "60"
    if ampifcation == None:
        ampifcation = "1"
    item = {"item":{"id":"pot","data":{"pot":potType.replace("\"",""),"dur":duration,"amp":ampifcation}},"slot":slot} 
    return item

def GetGValueItem(type,target="default",slot = 0):
    if target == None:
        target = "default"
    item = {"item":{"id":"g_val","data":{"type":type.replace("\"",""),"target":target.replace("\"","")}},"slot":slot}    
    return item

def GetVecotorItem(x,y=0,z=0,slot=0):
    if y == None:
        y =0
    if z == None:
        z = 0
    item = {'item': {'id': 'vec', 'data': {'x': float(x), 'y':float(y), 'z': float(z)}}, 'slot': slot}
    return item

def getParticalItem(name,amount=1,horizontal=0,vertical=0,data={},slot = 0):
    if amount == None:
        amount = 1
    if horizontal == None:
        horizontal = 0
    if vertical == None:
        vertical = 0
    if data == None:
        data = GetParticalData(name)
    item = {'item': {'id': 'part', 'data': {'particle': name.replace("\"",""), 'cluster': {'amount': int(amount), 'horizontal': float(horizontal), 'vertical': float(vertical)}, 'data': data}}, 'slot': slot}
    return item

def GetParticalData(name,motion=[0,0,0],motionVariation= 100,material=None,color=16777215,colorVariation=0,size=1.0,sizeVariation=0):
    particalData = {}
    name = name.replace("\"","")
    particalFeilds = fileHandling.CodeTools.GetParticalFeilds(name)
    if particalFeilds!= None:
        if "Motion" in particalFeilds:
            if motion != None:
                particalData["x"],particalData["y"],particalData["z"] = motion
            else:
                particalData["x"],particalData["y"],particalData["z"] = [0,0,0]
        if "Motion Variation" in particalFeilds:
            if motionVariation != None:
                particalData["motionVariation"] = motionVariation
            else:
                particalData["motionVariation"] =100
        if "Material" in particalFeilds:
            if material == None:
                particalData["material"]=fileHandling.CodeTools.GetParticalMaterial(name)
            else:
                particalData["material"] = material
        if "Color" in particalFeilds:
            if color != None:
                particalData["rgb"] = color
            else:
                particalData["rgb"] = 16777215
        if "Color Variation" in particalFeilds:
            if colorVariation != None:
                particalData["colorVariation"] = colorVariation
            else:
                particalData["colorVariation"] = 0
        if "Size" in particalFeilds:
            if size != None:
                particalData["size"] = size
            else:
                particalData["size"] = 1.0
        if "Size Variation" in particalFeilds:
            if sizeVariation != None:
                particalData["sizeVariation"] = sizeVariation
            else:
                particalData["sizeVariation"] = 0
    return particalData

def GetItemItem(minecraftid=None,count= 1,name = None,lore= None,unbreakable=False,enchantments=None,hideFlags=False,json=None,slot = 0):
    if json == None:
        itemDict = {"id":str(minecraftid.replace("\"",""))}
        if count == None:
            itemDict["Count"] = 1
        else:
            itemDict["Count"]=int(count)
        if enchantments != None:
            enchants =[]
            for ench in enchantments:
                if len(ench) == 2:
                    enchants.append({"id":ench[0].replace("\"",""),"lvl":ench[1]})
                else:
                    enchants.append({"id":ench[0].replace("\"",""),"lvl":1})
            itemDict["tag"]={"Enchantments":enchants}
        if unbreakable == True:
            if "tag" in itemDict:
                itemDict["tag"]["Unbreakable"] = 1
            else:
                itemDict["tag"] = {"Unbreakable":1}
        if hideFlags:
            if "tag" in itemDict:
                itemDict["tag"]["HideFlags"] =127
            else:
                itemDict["tag"] = {"HideFlags":127}
        if name != None:  
            name = name.replace("\"","",1) 
            name = name.rstrip("\"")
            if "tag" in itemDict:
                itemDict["tag"]["display"]={"Name":eval(convertToDFItemName(name))}
            else:
                itemDict["tag"]={"display":{"Name":eval(convertToDFItemName(name))}}        
            
            
        if lore != None:
            loresplit = lore.split("\\n")
            loreConvert = []
            for part in loresplit:
                part = part.replace("\"","",1) 
                part = part.rstrip("\"")
                loreConvert.append(eval(convertToDFItemName(part)))

            if "tag" in itemDict:
                if "display" in itemDict["tag"]:
                    itemDict["tag"]["display"]["Lore"] = (loreConvert)
                else:
                    itemDict["tag"]["display"] = {"Lore":(loreConvert)}
            else:
                itemDict["tag"] = {"display":{"Lore":(loreConvert)}}
        itemDict = str(itemDict)
    else:
        itemDict = json
    item =  {'item': {'id': 'item', 'data': {'item': itemDict}}, 'slot': slot}
    return item

def GetBaseActionItem(actionName):
    itemDict,actionName= GetItemDict(actionName)               
    items =[]
    for tag in itemDict["tags"]:
        item = {"id": "bl_tag", "data": {}}       
            
        option= tag["defaultOption"]
        block = fileHandling.CodeTools.GetCodeBlockByName(itemDict["codeblockName"])["identifier"]
        item["data"] = {"option":option,"tag":tag["name"],"action":actionName,"block":block}
        item = {"item":item}
        item["slot"] = tag["slot"]
        items.append(item)
   
    return items

def GetExpandedActionOption(action,option):
    itemDict,action= GetItemDict(action) 
    for tag in itemDict["tags"]:
        options = tag["options"]
        for opt in options:       
            if opt["name"].replace(" ","") == option.replace("\"","").replace(" ",""):
                return opt["name"]

def GetItemDict(action):
    itemDict = fileHandling.CodeTools.GetActionByName(action)
    if itemDict == None: 
        itemDict = fileHandling.CodeTools.GetActionByCodeBlock(action)     
        if  itemDict == None:             
            itemDict = fileHandling.CodeTools.GetActionByAliase(action)
        else: 
            action = "dynamic"
    return itemDict,action

#text format convertion
textColors = {
    "dark_red":"&4",
    "red":"&c",
    "gold":"&6",
    "yellow":"&e",
    "dark_green":"&2",
    "green":"&a",
    "aqua":"&b",
    "dark_aqua":"&3",
    "dark_blue":"&1",
    "blue":"&9",
    "light_purple":"&d",
    "dark_purple":"&5",
    "white":"&f",
    "gray":"&7",
    "dark_gray":"&8",
    "black":"&0",
}

textModifiers = {
    '"obfuscated":true':"&k",
    '"bold":true':"&l",
    '"strikethrough":true':"&m",
    '"underline":true':"&n",
    '"italic":true':"&o",
    "":"&r",
}
def convertToDFItemName(name):
    '''Takes name such as &l&aHello and converts it to "{"extra":[{"bold":true,"color":"green","text":"Hello"}],"text":""}"'''
    skipIndex = []
    text = []
    currentTextData = {}
    currentText = ""
    findingCurrentText = False
    for i in range(0,len(name)):
        if i not in skipIndex:
            character = name[i]
            if character == "&":
                if i != len(name)-1:
                    textCode = "&"+name[i+1]
                    if textCode in textColors.values() or textCode in textModifiers.values():
                        skipIndex.append(i+1)
                        if findingCurrentText:
                            currentTextData["text"] = currentText
                            currentText = ""
                            findingCurrentText = False
                            text.append(currentTextData)
                            currentTextData = {}
                        if textCode in textColors.values():
                            currentTextData["color"] = list(textColors.keys())[list(textColors.values()).index(textCode)]
                        if textCode in textModifiers.values():
                            modifier = list(textModifiers.keys())[list(textModifiers.values()).index(textCode)]
                            if modifier != "":
                                currentTextData[modifier.split(":")[0].replace('"','')] = True
                    else:
                        currentText += "&"
                else:
                    currentText += "&"
            else:
                if i != len(name)-1:
                    findingCurrentText = True
                    currentText += character
                else:
                    currentText += character
                    currentTextData["text"] = currentText
    text.append(currentTextData)
    text = {"extra":text,"text":""}
    return "'"+json.dumps(text,separators=(',', ':'))+"'"#at some point i need to stop doing this probaly never but 