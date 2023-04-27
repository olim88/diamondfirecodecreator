#handle opening and saveing files for the hotbar an the list of instructions
try:
    import nbtlib
    import ast
    import gzip
    import io
    import base64
    import json
except:
    import os 
    os.system("pip install nbtlib")
    import nbtlib
    import ast
    import gzip
    import io
    import base64
    import json
class Hotbar():
    def GetBaseItemName(title,name):
        itemname = "{\"extra\":[{\"bold\":true,\"italic\":false,\"underlined\":false,\"strikethrough\":false,\"obfuscated\":false,\"color\":\"green\",\"text\":\""+title +" \"},{\"bold\":false,\"italic\":false,\"color\":\"gold\",\"text\":\"» \"},{\"italic\":false,\"color\":\"green\",\"text\":\""+ name+ "\"}],\"text\":\"\"}"
        baseItem = """{'id': 'minecraft:netherite_block', 'Count': 1, 'tag': {'PublicBukkitValues': {'hypercube:codetemplatedata':REPLACE}, 'display': {'Name': '"""+itemname+"""'}}}"""
        return baseItem
    def Load(hotbarFile,row,index):
        
        file = nbtlib.load(hotbarFile)
        info = (ast.literal_eval(file[str(row)][index]["tag"]["PublicBukkitValues"]["hypercube:codetemplatedata"]))
        code = bytes(info["code"],"utf-8")
        code = base64.b64decode(code)
        code = gzip.decompress(code)
        code = ast.literal_eval(code.decode("utf-8") )
        
        return code# author,name, version

    def Save(hotbarFile,row, index,code,title="Code",name="Custom Code Block",author="Df Code Gen",blockname="codeBlock",version=1,):#code as as dict
        file = nbtlib.load(hotbarFile)
        code = gzip.compress(bytes(str(code),"utf-8"))
        code = base64.b64encode(code)
        code = (str)(code.decode("utf-8"))              
        itemDict = {"author":author,"name":blockname,"version":version,"code":code}
        item = Hotbar.GetBaseItemName(title,name).replace("REPLACE","\""+str(itemDict)+"\"")
        file[str(row)][index]=nbtlib.parse_nbt(item)
        file.save()

class CodeTools:
    filedata = {}
    def loadFileData(file):
        with open(file,"r",encoding='utf-8') as f:
            CodeTools.filedata = json.load(f)

    def LoadTools(file=""):
        if file =="":
            return CodeTools.filedata
        else:
            with open(file,"r",encoding='utf-8') as f:
                filedata = json.load(f)
                return filedata

    def LoadActionType(neededaction): #load all actions based on the block that they are used for
        filedata = CodeTools.filedata
        actions = []
        for action in filedata["actions"]:
            if action["codeblockName"] == neededaction:
                actions.append(action["name"])
        return actions
    def LoadActionArgs(actionName):
        action = CodeTools.GetActionByName(actionName)
        if action == None:
            action = CodeTools.GetActionByAliase(actionName)
        if action == None:
            action = CodeTools.GetActionByCodeBlock(actionName)
        actionVars = []
        if "tags" in action:
            for tag in action["tags"]:
                name = tag["name"].replace(" ","")
                actionVars.append(name[0].lower() + name.replace(name[0],"",1)+"=")
            
        return actionVars

    def LoadActionArgsOptions(actionArg,actionName):
        action = CodeTools.GetActionByName(actionName)
        if action == None:
            action = CodeTools.GetActionByAliase(actionName)
        if action == None:            
            action = CodeTools.GetActionByCodeBLock(actionName)
        actionArgOptions = []        
        for tag in action["tags"]:
            name = tag["name"].replace(" ","")
            name =name[0].lower() + name.replace(name[0],"",1)
            if name == actionArg:
                for option in tag["options"]:
                    actionArgOptions.append(option["name"])
        return actionArgOptions

    def LoadParticalNames():
        filedata = CodeTools.filedata
        particles = [] 
        for particle in filedata["particles"]:
            particles.append(particle["icon"]["name"]) 
        return particles
    def LoadItemNames():
        with open("minecraftBlocks.txt","r") as f:
            return [line.replace("\n","") for line in f.readlines() ]
    def LoadGvNames():
        filedata = CodeTools.filedata
        gvs = [] 
        for particle in filedata["gameValues"]:
            gvs.append(particle["icon"]["name"]) 
        return gvs

    def LoadSoundNames():
        filedata = CodeTools.filedata
        sounds = [] 
        for particle in filedata["sounds"]:
            sounds.append(particle["icon"]["name"]) 
        return sounds
    
    def LoadPotionNames():
        filedata = CodeTools.filedata
        Potions = [] 
        for particle in filedata["potions"]:
            Potions.append(particle["icon"]["name"]) 
        return Potions
    def getActionAguments(actionName):
        action = CodeTools.GetActionByName(actionName)
        if "arguments" in action["icon"]:
            args = action["icon"]["arguments"]
            return args
        else:
            return None
    def GetActionByName(actionName):
       filedata = CodeTools.filedata 
       for action in filedata["actions"]:
            if action["name"] == actionName:
                return action
    
    def GetActionByCodeBlock(codeblockName):#changed name slitle fix error if
        filedata = CodeTools.filedata 
        for action in filedata["actions"]:
            if action["codeblockName"] == codeblockName:
                return action
    def GetActionByAliase(aliase):
        filedata = CodeTools.filedata 
        for action in filedata["actions"]:            
            if action["aliases"] != None:
                if len(action["aliases"])>0:                    
                    if action["aliases"][0] == aliase:
                        return action

    def GetCodeBlockByName(codeblockName):
        filedata = CodeTools.filedata 
        for block in filedata["codeblocks"]:
                if block["name"] == codeblockName:
                    return block

    def GetCodeBlockByID(codeblockID):
        filedata = CodeTools.filedata 
        for block in filedata["codeblocks"]:
                if block["identifier"] == codeblockID:
                    return block
                    
    def LoadIdsForBlock():#type of block e.g. ACTION
        filedata = CodeTools.filedata
        ids = {}
        for block in filedata["codeblocks"]:           
            ids[block["name"]] = block["identifier"]
        return ids

    def GetParticalFeilds(partName):
        filedata = CodeTools.filedata 
        for part in filedata["particles"]:
                if part["icon"]["name"] == partName:
                    return part["fields"]
    def GetParticalMaterial(partName):
        filedata = CodeTools.filedata 
        for part in filedata["particles"]:
                if part["icon"]["name"] == partName:
                    return part["icon"]["material"]


def LoadJsonFile(file):
    with open(file,"r",encoding='utf-8') as f:
                filedata = json.load(f)
                return filedata
    


         
