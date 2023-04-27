#compies the code intoblocks 
import os
import CreateBlock
import fileHandling
import copy
import json
HotbarFile = os.getenv('APPDATA')+"/.minecraft/hotbar.nbt"
codeConversions = fileHandling.LoadJsonFile("CodeConversions.json")

spacedNames = ["SetBossBar","GetDirection","SetDirection","SetItemEnchants","GetItemEnchants","SetPose","TextMatches","SetBlock"]#list of actions that for some reason have spaces
def ParseCode(textfile,hotBarrow,hotBarslot):
    with open(textfile,"r") as f:
        lines = f.readlines()
    code = []
    for lineIndex,line in enumerate(lines):
        line = line.replace("\n","")
        if line.replace(" ","") != "" and not(line.replace(" ","").startswith("#")):
            try:
                lineComp = parseLine(splitArgs(line,"#")[0])
                code.append(lineComp)
                if lineComp == None:
                    raise Exception("invalid Code line:",lineIndex)
            except:
                raise Exception("invalid Code line:",lineIndex)

    codeblocks = CreateBlock.GroupBlocks(code)
    print(codeblocks)
    fileHandling.Hotbar.Save(HotbarFile,str(hotBarrow),hotBarslot,codeblocks)

def parseLine(line): 
    block = None 
    line = RemoveNonTextSpaces(line)
    for code in codeConversions.items():
        value = code[1]
        if (line.startswith(value[0])):
            blockType = code[0]
            if blockType == "if_var_not":
                blockType = "if_var"
                notBlock = True
            elif blockType == "if_player_not":
                blockType = "if_player"
                notBlock = True
            elif blockType == "if_entity_not":
                blockType = "if_entity"
                notBlock = True
            elif blockType == "if_game_not":
                blockType = "if_game"
                notBlock = True
            else:
                notBlock = False
            if line == "{"  :
                block = CreateBlock.CreateBracket("open")
                break
            elif line == "}":   
                block = CreateBlock.CreateBracket("close") 
                break  
            line = line.replace(value[0],"")
            if value[1] == "ACTION" and len(value)==2:
                actionType = line
                data = None
                items = None
            elif value[1] == "ACTION" and value[2] == "ARGS":                
                line =line.split("(",1)
                actionType = processAction(line[0])
                items = ProcessArgs(line[1].rsplit(")",1)[0],actionType)
                data = None               

            if value[1] == "VAR":
                actionType = None
                line = line.split("(",1)
                data = line[0]
                items = ProcessArgs(line[1].rstrip(")"),fileHandling.CodeTools.GetCodeBlockByID(blockType)["name"])     
            block = CreateBlock.CreateBlock(blockType,actionType,items,data,notBlock)

            break
            
    if block != None:        
        return block
def processAction(action):
    if action in spacedNames:
        return " "+action+ " "
    else:
        return action
def ProcessArgs(args,actionType = None):
    args = splitArgs(args)
    items =[]
    chestVars = []
    for slot,arg in enumerate(args): 
        if arg !="":
            if not(ifCharOutOfBracket(arg,"=")):#ints strings and vars
                if ifCharOutOfBracket(arg,":"):
                    arg,currentSlot = splitArgs(arg,":")
                else:
                    currentSlot = slot
                if arg.startswith("\"") :
                    arg = arg.strip("\"").rstrip("\"")
                    arg = arg.replace("&","§")
                    item = CreateBlock.GetValueItem(arg,"txt",currentSlot)
                elif arg.split(".")[0].isnumeric():
                    item = CreateBlock.GetValueItem(arg,"num",currentSlot)
                elif arg.startswith("sound("):
                    splitList = arg.strip("sound(").rstrip(")").replace("\"","").split(",")
                    sound,pitch,volume = splitList+ [None] * (3 - len(splitList))
                    item = CreateBlock.GetSoundItem(sound,pitch,volume,currentSlot)
                elif arg.startswith("location("):
                    splitList =arg.strip("location(").rstrip(")").replace("\"","").split(",")
                    x,y,z,pitch,yaw = splitList+ [None] * (5 - len(splitList))
                    item = CreateBlock.GetLocationValueItem(x,y,z,pitch,yaw,currentSlot)    
                elif arg.startswith("vector("):
                    splitList =arg.strip("vector(").rstrip(")").replace("\"","").split(",")
                    x,y,z = splitList+ [None] * (3 - len(splitList))
                    item = CreateBlock.GetVecotorItem(x,y,z,currentSlot)                    
                elif arg.startswith("potion("):
                    splitList =arg.strip("potion(").rstrip(")").replace("\"","").split(",")
                    pot,duration,amp = splitList+ [None] * (3 - len(splitList))
                    item = CreateBlock.GetPotionItem(pot,duration,amp,currentSlot )
                elif arg.startswith("gv("):
                    splitList =arg.strip("gv(").rstrip(")").replace("\"","").split(",")
                    type,target = splitList+ [None] * (2- len(splitList))
                    item = CreateBlock.GetGValueItem(type,target,currentSlot)
                elif arg.startswith("particle("):
                    splitList =splitArgs(arg.strip("particle(").rstrip(")").replace("\"",""))
                    item = ConvertParticalItem(splitList,currentSlot)
                elif arg.startswith("item("):
                    itemArgs = arg.replace("item(","",1).rstrip(")")
                    item = ConvertItemItem(itemArgs,currentSlot)
                  
                else:
                    if arg[0] in "$~":                        
                        scope = arg[0]
                        arg = arg[1:]
                    else:
                        scope = ""
                    item = CreateBlock.GetValueVarItem(arg,scope,currentSlot)             
                items.append(item)
            else:
                arg = arg[0].upper() + arg.strip(arg[0])
                chestVars.append(arg)
    try:
        chestItems = CreateBlock.GetBaseActionItem(actionType)             
        for item in chestItems: 
            if len(chestVars) >0:
                for  chestVar in chestVars:                    
                    if (item["item"]["data"]["tag"]).replace(" ","") == chestVar.split("=")[0]:
                        item["item"]["data"]["option"] = CreateBlock.GetExpandedActionOption(actionType,chestVar.split("=")[1])
            items.append(item)   
                   
            
    except Exception as e:
        print(e,args)
    return items

def ifCharOutOfBracket(arg,charCheck):
    bracketDepth = 0
    for char in arg:
        if char == "(":
            bracketDepth += 1
        if char == ")":
            bracketDepth -= 1
        if bracketDepth == 0 and char == charCheck:
            return True
    return False

def splitArgs(args,symbol = ","):  
    inbracket = 0
    argsList = []
    index = 0
    for letter in args:
        if letter == "(":
            inbracket += 1
        if letter == ")":
            inbracket -= 1
        if inbracket == 0 and letter == symbol:
            argsList.append(args[0:index].rstrip(symbol))
            args = args[index:].strip(symbol)
            index = 0
        index += 1
    argsList.append(args)
    return argsList

def ConvertItemItem(args,slot):
    if args.startswith("json="):
        return CreateBlock.GetItemItem(json=args.replace("json=","",1),slot=slot)
    else:
        args = splitArgs(args.replace("\"",""))
        count = 1
        name = None
        lore = None
        unbreakable= False
        enchantments = None
        hideFlags = False
        blockId = None
        for arg in args:
            if arg.startswith("count="):
                count = int(arg.replace("count=",""))
            elif arg.startswith("name="):
                name = convertToDFItemName(arg.replace("name=",""))
            elif arg.startswith("lore="):
                lore = arg.replace("lore=","").split("\\n")
                for l in range(len(lore)):
                    lore[l]= eval(convertToDFItemName(lore[l]))
            elif arg.startswith("unbreakable="):
                if arg.replace("unbreakable=","",1) == "true":
                    unbreakable = True
            elif arg.startswith("enchantments="):
                enchants = splitArgs(arg.replace("enchantments=(","",1).rstrip(")"))
                enchantments=[]
                for enchant in enchants:                   
                   enchantments.append({"id":enchant.replace("enchant(","",1).split(",")[0] ,"lvl":int(enchant.replace("enchant(","",1).split(",")[1]) }) 
            elif arg.startswith("hideFlags="):
                if arg.replace("hideFlags=","",1) == "true":
                    hideFlags = True
            else:
                blockId = arg
        return CreateBlock.GetItemItem(blockId,count, name, lore, unbreakable,enchantments,hideFlags,slot)

def ConvertParticalItem(args,slot):      
    name = args[0]
    amount = 1
    horizontal = 0
    vertical = 0
    motion=[0,0,0]
    motionVariation= 100
    material=None
    color="FFFFFF"
    colorVariation=0
    size=1.0
    sizeVariation=0
    for arg in args:
        if arg.startswith("amount="):
            amount = int(arg.replace("amount=",""))
        elif arg.startswith("horizontal="):
            horizontal = float(arg.replace("horizontal=",""))
        elif arg.startswith("vertical="):
            vertical = float(arg.replace("vertical=",""))
        elif arg.startswith("motion="):
            motion = arg.replace("motion=","").strip("(").rstrip(")").split(",")
        elif arg.startswith("motionVariation="):
            motionVariation = int(arg.replace("motionVariation=",""))
        elif arg.startswith("material="):
            material = int(arg.replace("material=",""),16)
        elif arg.startswith("color"):
            color = int(arg.replace("color=",""))
        elif arg.startswith("colorVariation"):
            colorVariation = int(arg.replace("colorVariation=",""))
        elif arg.startswith("size="):
            size = float(arg.replace("size=",""))
        elif arg.startswith("sizeVariation"):
            sizeVariation = int(arg.replace("sizeVariation=",""))
    item = CreateBlock.getParticalItem(name,amount,horizontal,vertical,CreateBlock.GetParticalData(name,motion,motionVariation,material,color,colorVariation,size,sizeVariation),slot)
    return item
def RemoveNonTextSpaces(spacedLine):
    '''takes a line and then returns it only removing spaces that are not in strings'''
    newLine = ""
    inText = False
    for char in spacedLine:
        if inText:
            newLine += char
        elif char != " ":
            newLine += char
        if char == "\"":
            inText = not(inText)
    return newLine
        
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
    return "'"+json.dumps(text,separators=(',', ':'))+"'"