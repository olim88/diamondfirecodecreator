#parser for the code
#import
from enum  import Enum,auto
import os
from xml.etree.ElementTree import ParseError
import fileHandling
import CreateBlock
#converts each line of code into a list of tokes (lexer) 
#then converts it to a dict of the key values and data types
class token(Enum):#text tokens
    Keyword  = auto()
    Action = auto()
    Null = auto()
    Identifier = auto()
    Lable = auto()
    DataTypeLable = auto()
    String= auto()
    Num = auto()
    SlotNum = auto()
    BracketO = auto()
    BracketC = auto()
    parenthesisO = auto()
    parenthesisC = auto()
    Dot = auto()
    Comma = auto()
    Space = auto()
    Comment = auto()
    Target = auto()


class TokenObject:
    def __init__(self,token,text,startIndex,endIndex):
        self.token = token
        self.text = text
        self.startIndex = startIndex
        self.endIndex = endIndex


def lexLine(line:str):
    '''converts a line in to a list of its key parts e.g. [TokenObject(token.Keyword,"if",0),TokenObject(...'''
    lexedLine = []
    startIndex = 0
    currentString = ""
    hadBracket = False #if there has been a bracket to see if a lable is a keyword or identifier
    if line != "":
        currentToken = getNewToken(line[0],False)[0]
    for endindex, nextChar in enumerate(line):#loops through every character until the currentString resembles a token 
        #output the tokens that end based appon the nextchar    
        match currentToken:
            case token.Null:
                if nextChar in ["."," ","("]:
                    if nextChar == "(":
                        currentToken = token.Action
                    elif nextChar == ".":
                        currentToken = token.Keyword
                    currentToken,currentString,startIndex,lexedLine,hadBracket =outputToken(currentToken,currentString,startIndex,endindex,lexedLine,nextChar,hadBracket)
            case token.Identifier:
                if currentString[-1:] == "=": #if it a finished lable not an identifier
                    currentToken = token.Lable
                    currentToken,currentString,startIndex,lexedLine,hadBracket =outputToken(currentToken,currentString,startIndex,endindex,lexedLine,nextChar,hadBracket)
                elif nextChar in [","," ",")","]", "(",":"]:
                    if nextChar == "(":
                        currentToken = token.DataTypeLable
                    currentToken,currentString,startIndex,lexedLine,hadBracket =outputToken(currentToken,currentString,startIndex,endindex,lexedLine,nextChar,hadBracket)
            case token.String:
                if nextChar in [","," ",")","]",":"]and currentString.count("\"") == 2:
                    currentToken,currentString,startIndex,lexedLine,hadBracket =outputToken(currentToken,currentString,startIndex,endindex,lexedLine,nextChar,hadBracket)
            case token.Num:
                if nextChar in [","," ",")","]",":"]:
                    currentToken,currentString,startIndex,lexedLine,hadBracket =outputToken(currentToken,currentString,startIndex,endindex,lexedLine,nextChar,hadBracket)
            case token.SlotNum:
                if nextChar in [","," ","]",")"]:
                    currentToken,currentString,startIndex,lexedLine,hadBracket =outputToken(currentToken,currentString,startIndex,endindex,lexedLine,nextChar,hadBracket)
            case token.Target:
                if nextChar in [","," ","]",")"]:
                    currentToken,currentString,startIndex,lexedLine,hadBracket =outputToken(currentToken,currentString,startIndex,endindex,lexedLine,nextChar,hadBracket)

            case token.Comment:
                pass
            case token.Space:
                if nextChar != " ":
                    currentToken,currentString,startIndex,lexedLine,hadBracket =outputToken(currentToken,currentString,startIndex,endindex,lexedLine,nextChar,hadBracket)
            case _:#if not checks to si if finished is needed e.g. comma
                currentToken,currentString,startIndex,lexedLine,hadBracket =outputToken(currentToken,currentString,startIndex,endindex,lexedLine,nextChar,hadBracket)
        currentString += nextChar
            
        
    #add the last unended token when done
    if line != "": #if there is an empty line there is nothing to add to the lexed line
        currentToken,currentString,startIndex,lexedLine,hadBracket =outputToken(currentToken,currentString,startIndex,len(line)+1,lexedLine,nextChar,hadBracket) #comments will always be added here as you cant end them

    return lexedLine
def outputToken(currentToken,currentString,startIndex,endindex,lexedLine,nextChar,hadBracket):
    lexedLine.append(TokenObject(currentToken,currentString,startIndex,endindex-1))
    startIndex = endindex
    currentString = ""
    currentToken, hadBracket= getNewToken(nextChar,hadBracket)
    return currentToken,currentString,startIndex,lexedLine,hadBracket

def getNewToken(startingChar,hadBracket):
    '''gets the token for the next part of the line based on the first char'''
    #change the current token to fit the current string
    if startingChar == '"':
        currentToken = token.String
    elif startingChar.isdigit():
        currentToken = token.Num
    elif startingChar == "(":
        currentToken = token.BracketO
        hadBracket = True
    elif startingChar == ')':
        currentToken = token.BracketC
    elif startingChar =="[":
        currentToken = token.parenthesisO
    elif startingChar == "]":
        currentToken = token.parenthesisC
    elif startingChar == ".": 
        currentToken = token.Dot
    elif startingChar == ",": 
        currentToken = token.Comma
    elif startingChar == " ":
        currentToken = token.Space
    elif startingChar == "#":
        currentToken = token.Comment
    elif startingChar ==":":
        currentToken = token.SlotNum
    elif startingChar =="@":
        currentToken = token.Target
    elif hadBracket:
        currentToken = token.Identifier
    else:
        if startingChar in ["{","}"]:#i dont want to hardcode this but i dont see a better idear atm
            currentToken = token.Keyword
        else:
            currentToken = token.Null

    return currentToken, hadBracket

#now we can convert the code into the format used by diamond fire 

class parser():
    def __init__(self,codeFileName,row,slot):#when created lloop through text then save the parsed output file
        #set main vars
        if os.path.isfile("minecraftfolder.txt"):
            with open("minecraftfolder.txt","r") as f:
                mincraftFolder = f.read().rstrip("\n")

        else:
            try:
                mincraftFolder = os.getenv('APPDATA')+"/.minecraft/"
            except:
                raise Exception( "can not find mincraft directory please create a text file called \"minecraftfolder.txt\" with the path to you mincraft installation1")
        if not(os.path.isdir(mincraftFolder)):
                    raise Exception( "can not find mincraft directory please create a text file called \"minecraftfolder.txt\" with the path to you mincraft installation2")

        self.HotbarFile = mincraftFolder+"hotbar.nbt"
        self.codeFormating = fileHandling.LoadJsonFile("codeFormating.json")
        self.blockLables = list(self.codeFormating["instructionFormats"].keys())
        self.FinalCode = []
        #parse the text
        with open(codeFileName,"r") as f:#load the text
            lines = f.readlines()
        for lineIndex,line in enumerate(lines):#parse each line
            line = line.replace("\n","")#remove line end
            try:
                parsedLine = self.parseLine(line)
                self.FinalCode.append(parsedLine)
            
            except ParseError as e:#handle the errors thrown when paseling the line
                if str(e) == "empty Line":
                    pass
                elif str(e) == "invalid Line Lable":
                    raise Exception(str(e)+" line:"+str(lineIndex)+" ("+line+")")
            

        #finish createing code and save to file        
        codeblocks = CreateBlock.GroupBlocks(self.FinalCode)
        print(codeblocks)
        fileHandling.Hotbar.Save(self.HotbarFile,str(row),slot,codeblocks)

    def parseLine(self,line):#this should be instead of the compiler witch is terible had coded poo
        '''lex and then pases a line and returns the needed dict for it to work'''
        lexedLine = lexLine(line)       
        lineLable, emptyLine,blockAction, target = self.getBlockLableAndActionAndEmptyAndTarget(lexedLine) 
        if emptyLine:            
            raise ParseError("empty Line") 
        if lineLable  not in self.blockLables:#if its not a valid lable 
            raise ParseError("invalid Line Lable")
        #block args
        blockName = ""
        actionType = None
        data = None
        NotBLock = False #if not block
        items = None
        subAction = None#still not implimented the format but used in a while loop so should not be to hard i think to do at some point idk why i am wrting an sa for this comment sorry 
        
        #get the block args
        blockFormatDict =  self.codeFormating["instructionFormats"][lineLable]
        #get block name and set actionIdetifier
        if "mainBlock" in blockFormatDict: #if its a sub aciton
            blockName = blockFormatDict["mainBlock"]
            blockActionType = blockAction
        elif "actionTitle" in blockFormatDict:#if its an action block e.g. not def or else
            blockName =blockFormatDict["actionTitle"]
            blockActionType = blockAction
        elif "codeBlockID" in blockFormatDict:
            blockName = blockFormatDict["codeBlockID"]
            blockActionType = blockFormatDict["codeBlockID"]
        else:#the block is a bracket so can be built now
            return CreateBlock.CreateBracket(blockFormatDict["open"])

        #if aplicable get action or block data
        if blockAction is not None:
            if "mainBlock" in blockFormatDict:
                print(";laskjfd")
                actionType = blockFormatDict["mainAction"]
                subAction = blockAction
            elif "actionTitle" in blockFormatDict:#if takes action or the blockaction is jsut the funciton name
                actionType = blockAction

            else:
                data = blockAction

        #get if its a if not or smthings
        if "not" in blockFormatDict:
            NotBLock = True

        #get the blocks items
        if blockFormatDict["takesArgs"]:      
            items = self.getItems(lexedLine,blockActionType)
        #create the final block 
        block = CreateBlock.CreateBlock(blockName,actionType,items,data,NotBLock,subAction,target)
        return block

    def getBlockLableAndActionAndEmptyAndTarget(self,lexedLine):
        '''returns the main lable of the line e.g. action.Player. and if that line is trying to have a lable but is incorrectly formated also returns the action of the block set to None if there is not one'''
        lable = ""
        empty = True
        action = None
        target = None
        for part in lexedLine:
            if part.token ==token.Keyword:
                empty = False
                lable += part.text
            elif part.token ==token.Dot:
                empty = False
                lable += part.text
            elif part.token == token.Target:#if the token is for a target
                target = part.text.replace("@","",1)
            elif part.token != token.Space:#unless there is just spaces break when the line changes to somthing else to be more efficient
                if part.token != token.Comment:#could be empty if a comment
                    empty = False
                    if action == None:
                        action = part.text      
        return lable,empty,action , target

    def getArgs(self,lexedline):
        '''returns all the chest option items and the given items'''
        args = []#a list of all the main args
        currentArg = {}#e.g. {type:token.DataTypeLable,value:location,args:[{type:token.Number,value:23}],slot:10} or {type:token.Number,value:23,args:[]}
        argDepth = 0 # how deap into an argument the value is
        lableDepth = -1 #what the arg depth was when the last lable was set 
        for part in lexedline:
            if part.token in [token.Identifier,token.String,token.Num,token.DataTypeLable,token.parenthesisO,token.Lable]:#if its a token that needs to be saved
                print(part.token)
                currentArg = self.setDepthArg({"type":part.token,"value":part.text,"args":[]} ,argDepth,currentArg)
            elif part.token == token.SlotNum:
                currentArg["slot"] = part.text             

            if part.token == token.DataTypeLable or part.token == token.parenthesisO or part.token == token.Lable:  
                          
                argDepth += 1
                if part.token == token.Lable:
                    lableDepth = argDepth                       
                
            elif part.token == token.Comma and lableDepth == argDepth:                
                lableDepth = -1
                argDepth -= 1
            elif part.token == token.parenthesisC or part.token == token.BracketC:
                argDepth -= 1

            if argDepth == 0 and not(currentArg == {}) and part.token in [token.Comma,token.Space]:
                args.append(currentArg)
                currentArg = {}
        if currentArg != {}:#if not empty add 
            args.append(currentArg)#add the last agument    
        print(args,"\n\n")
        return args

    def setDepthArg(self,value,initialDepth,wholeArg,depth = 0):#this dose some sus stuff with lists in lists
        '''returns the whole arg with the value added at the depth calling it self to get deep'''
        print(depth,initialDepth,value)
        if depth == initialDepth:            
            return value
        elif type(wholeArg)== list: #if its an even depth therefor it is an dictinary        
            return (self.setDepthArg(value,initialDepth,wholeArg[len(wholeArg)-1],depth))
        else: #its an odd depth so its a list
            depth += 1
            wholeArg["args"].append(self.setDepthArg(value,initialDepth,wholeArg["args"],depth))
            return wholeArg




    def getItems(self,lexedline,blockActionType):
        args = self.getArgs(lexedline)
        chestItems = CreateBlock.GetBaseActionItem(blockActionType)  #the base items for options in the chest
        items = []
        for slotIndex,arg in enumerate(args):
            if "slot" in arg:
                slot = int (arg["slot"].replace(":",""))
            else:
                slot = slotIndex
            if arg["type"] == token.Identifier:
                if arg["value"][0] in "$~":                        
                    scope = arg["value"][0]
                    value = arg["value"][1:]
                else:
                    value = arg["value"]
                    scope = ""
                items.append(CreateBlock.GetValueVarItem(value,scope,slot))

            elif arg["type"] == token.String:
                #convet string to valid format
                string = arg["value"].strip("\"").rstrip("\"")
                string = string.replace("&","§")
                #get string item
                items.append(CreateBlock.GetValueItem(string,"txt",slot))

            elif arg["type"] == token.Num:
                try:
                    items.append(CreateBlock.GetValueItem(arg["value"],"num",slot))
                except:
                    raise ParseError("invalid number")

            elif arg["type"] == token.Lable:#change the options in the chest if they are set
                for index in range(len(chestItems)): 
                    if (chestItems[index]["item"]["data"]["tag"]).replace(" ","").lower() == arg["value"].rstrip("=").lower():
                        chestItems[index]["item"]["data"]["option"] = CreateBlock.GetExpandedActionOption(blockActionType,arg["args"][0]["value"])
                        break
                    if index == len(chestItems):#if checked everything but no match throw error
                        raise ParseError("invalid Chest option")

            elif arg["type"] == token.DataTypeLable:#if custom data type is specified
                format = self.codeFormating["argumentFormats"][arg["value"]]                
                subArgs = []
                for part in arg["args"]:
                    if part["type"]!= token.Lable:
                        subArgs.append(part["value"])
                subArgs += [None] * 10 #fill rest so dose not error when value not given

                if format["optionalVars"] != []:#if there is optional argument
                    options = format["optionalVars"]
                    optionalArgs = [None] * len(format["optionalVars"])#set all values to nun so can be changed when set
                    if "conditionalVars" in format:#only particals at the moment but values than can be changed depending on the class or value e.g. coulour can only be changed for some particles
                        options += format["conditionalVars"]
                        optionalArgs += [None] * len(format["conditionalVars"])
                    for part in arg["args"]:
                        if part["type"] == token.Lable:
                            try:
                                index = options.index(part["value"])
                                if part["args"][0]["type"] == token.parenthesisO:#if its a list and not just a value
                                    list = []
                                    for var in part["args"][0]["args"]:
                                        if var["type"] == token.parenthesisO:#if its a list and not just a value
                                            sublist=[]
                                            for var2 in var["args"]:
                                                if var2["type"] == token.Num:
                                                    sublist.append(float(var2["value"]))
                                                else:
                                                    sublist.append(var2["value"])
                                            list.append(sublist)
                                        else:                                           
                                            if var["type"] == token.Num:
                                                list.append(float(var["value"]))
                                            else:
                                                list.append(var["value"])
                                    optionalArgs[index] = list
                                else:
                                    optionalArgs[index] = part["args"][0]["value"]
                            except:
                                raise ParseError("invalid item tag")

               

                match (arg["value"]):
                    case "location":
                        items.append(CreateBlock.GetLocationValueItem(subArgs[0],subArgs[1],subArgs[2],subArgs[3],subArgs[4],slot))
                    case "sound":
                        items.append(CreateBlock.GetSoundItem(subArgs[0],subArgs[1],subArgs[2],slot))
                    case "vector":
                        items.append(CreateBlock.GetVectorItem(subArgs[0],subArgs[1],subArgs[2],slot))
                    case "potion":
                        items.append(CreateBlock.GetPotionItem(subArgs[0],subArgs[1],subArgs[2],slot))
                    case "gv":
                        items.append(CreateBlock.GetGValueItem(subArgs[0],subArgs[1],slot))
                    case "particle":
                        items.append(CreateBlock.getParticalItem(subArgs[0],optionalArgs[0],optionalArgs[1],optionalArgs[2],CreateBlock.GetParticalData(subArgs[0],optionalArgs[3],optionalArgs[4],optionalArgs[5],optionalArgs[6],optionalArgs[7],optionalArgs[8],optionalArgs[9]),slot))
                    case "item":
                        items.append(CreateBlock.GetItemItem(subArgs[0],optionalArgs[0],optionalArgs[1],optionalArgs[2],optionalArgs[3],optionalArgs[4],optionalArgs[5],optionalArgs[6],slot))
                    case _:
                        raise ParseError("invalid data type lable")
                    
        return items+ chestItems
