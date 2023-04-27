#custom coding for df
import math as maths
import os
import time
import random
import pyperclip
import numpy as np
#pygame start

import pygame

pygame.init()
pygame.display.set_caption("diamondFireCodeing gameing")
import pygameGUI
#import other scripts
import fileHandling
import parse
clock = pygame.time.Clock()
#constant
WinSize = (1000,1000)
BgColour = (37,41,47)
#get the right file to write the nbt data to 
#see if there is a config file saying somthing diffrent to default and if so use that mincraft location
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

HotbarFile = mincraftFolder+"hotbar.nbt"
CodeToolsFile = "dfcode.json"
fileHandling.CodeTools.loadFileData(CodeToolsFile)
EventBlocks = fileHandling.CodeTools.LoadIdsForBlock()
win = pygame.display.set_mode(WinSize,pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.SRCALPHA | pygame.RESIZABLE)
fpsCounter = pygameGUI.FPSCounter()
#main functions
def update():
    try:
        codeGUI.update()
        codeInput.update()
        pygameGUI.updateGui()
    except Exception as e:#if there is an error save the current code before it crashes
        codeGUI.saveText()
        raise e

def render():
    win.fill(BgColour)
    codeInput.render()
    codeGUI.render()

    #fpsCounter.render(win,60)
    fpsCounter.cap(60)
    pygame.display.flip()
    
#other def

class GUI():
    def __init__(self):
        '''sets up the main gui elements e.g. the buttons'''
        #create the gui
        self.rowSlider = pygameGUI.slider("mainGUI",0,0,100,40,text="Hot Bar Row: 0",backgroundColor=(41,44,53),outlineColor =(159,167,180),fontType= "gui/Minecraft.ttf")
        self.currentSlotLable = pygameGUI.textBox("mainGUI",110,0,300,20,text="Current Slot: 0",outline=False,editable=False,backgroundColor=(37,41,47),fontType= "gui/Minecraft.ttf")
        self.slotButtons = []
        for i in range(1,10):
            self.slotButtons.append(pygameGUI.button("mainGUI",100*i,20,100,20,imageLocate="gui/slotButton.png",text="slot "+str(i),background=False,outline=False,fontType= "gui/Minecraft.ttf",oneClick=True))
        
        self.SaveToFileButton = pygameGUI.button("mainGUI",0,50,100,60,text="Save",backgroundColor=(41,44,53),outlineColor =(159,167,180),fontType= "gui/Minecraft.ttf",oneClick=True)
        self.CompileToHotBarButton = pygameGUI.button("mainGUI",0,120,100,60,text="Save To Hotbar",backgroundColor=(41,44,53),outlineColor =(159,167,180),fontType= "gui/Minecraft.ttf",oneClick=True)
        self.LoadFromHotBarButton = pygameGUI.button("mainGUI",0,190,100,60,text="Load From HotBar",backgroundColor=(41,44,53),outlineColor =(159,167,180),fontType= "gui/Minecraft.ttf",oneClick=True)
        self.sugestionScroll = pygameGUI.slider("mainGUI",0,260,100,25,backgroundColor=(41,44,53),outlineColor =(159,167,180))
        self.mainScrollBar = pygameGUI.slider("mainGUI",260,2,740,16,backgroundColor=(41,44,53),outlineColor =(159,167,180))
        #other vars
        codeInput.currentCode = ""
        self.currentRow = 0
        self.currentSlot = 0
        self.confirmGUI = None
        #call setupts
        self.loadText()

    def PositionGUI(self,windowSize):
        '''when the window is reasised re position pop up gui to the center'''
        if self.confirmGUI != None:
            self.confirmGUI.PositionGUI(windowSize)



    def update(self):
        '''update the variables used in the code and process the input of the buttons'''
        #change vars
        if self.confirmGUI == None:
            #scroll sugestionsSuface
            if codeInput.sugestionScroll != self.sugestionScroll.slidedPercent:
                codeInput.sugestionScroll = self.sugestionScroll .slidedPercent
                codeInput.renderToSurface()
            if codeInput.mainCodeScroll != self.mainScrollBar.slidedPercent:
                codeInput.mainCodeScroll = self.mainScrollBar .slidedPercent
                codeInput.renderToSurface()
            #update the slots
            oldrow,oldslot = self.currentRow,self.currentSlot
            self.currentRow = int(self.rowSlider.slidedPercent * 8)
            for count,slot in enumerate(self.slotButtons):
                if slot.click:
                    self.currentSlot = count
            if oldrow != self.currentRow or oldslot != self.currentSlot:
                self.saveText(oldrow,oldslot)
                self.loadText()
            #save and load file
            if self.SaveToFileButton.click:
                self.saveText()
            if self.CompileToHotBarButton.click:
                self.saveText()
                parse.parser("saveCode/row"+str(self.currentRow)+"/slot"+str(self.currentSlot)+".txt",self.currentRow,self.currentSlot)
                try:
                    parse.parser("saveCode/row"+str(self.currentRow)+"/slot"+str(self.currentSlot)+".txt",self.currentRow,self.currentSlot)
                except Exception as e:
                    self.confirmGUI = confirmPopupMenu(str(e))
            if self.LoadFromHotBarButton.click:
                self.confirmGUI = confirmPopupMenu("this will overright you current code do you realy want to load code from your hotbar.")
        else:
            #get input from the confimation gui
            self.confirmGUI.update()
            if self.confirmGUI.confermed == False:
                self.confirmGUI = None
            elif self.confirmGUI.confermed:
                if self.confirmGUI.message == "this will overright you current code do you realy want to load code from your hotbar.":
                    self.loadCodeFromHotBarItem()
                self.confirmGUI = None
        #edit the GUI
        self.rowSlider.text = "Hot Bar Row: "+str(self.currentRow+1)
        self.currentSlotLable.text = "Current SLot: "+str(self.currentSlot+1)

   
    def saveText(self,row=None, slot=None):
        '''saves the text to a text file corisponding to a row and slot'''
        if row == None:
            row = self.currentRow
            slot = self.currentSlot
        with open("saveCode/row"+str(row)+"/slot"+str(slot)+".txt","w")as f:
                f.write(codeInput.currentCode)    
    def loadText (self):
        '''loads the text the text file of the current slot'''
        if os.path.exists("saveCode/row"+str(self.currentRow)+"/slot"+str(self.currentSlot)+".txt"):
            with open("saveCode/row"+str(self.currentRow)+"/slot"+str(self.currentSlot)+".txt","r")as f:                
                codeInput.clearcache()
                codeInput.currentCode = f.read()
                codeInput.renderToSurface()
        else:
            codeInput.currentCode = ""
            codeInput.renderToSurface()
    def loadCodeFromHotBarItem(self):
        '''bring up the comfirm gui to load code from the hotbar'''
        codeInput.clearcache()
        codeInput.currentCode = "#temp i dont have the stuff to load it yet\ndef.func.test()"
        codeInput.renderToSurface()

    def render(self):
        '''render the gui to the screen'''
        pygameGUI.displayGui(win,"mainGUI")
        if self.confirmGUI != None:

            self.confirmGUI.render()

class confirmPopupMenu():
    def __init__(self,confirmMessage):
        '''initilise the buttons for the comfrimation with given text'''
        pygameGUI.clearGuiGroup("confirmGUI")
        self.confermed = None
        self.message = confirmMessage
        self.position = (200,300)
        self.surface =pygame.Surface((600,400),pygame.HWSURFACE)
        self.confermTextBox = pygameGUI.textBox("confirmGUI",0,0,2000,200,text=confirmMessage,editable=False,xAlinment=2,yAlinment=2,fontType= "gui/Minecraft.ttf",backgroundColor=(41,44,53),outlineColor =(159,167,180))
        self.yesButton = pygameGUI.button("confirmGUI",20,230,270,140,text="YES",fontType= "gui/Minecraft.ttf",backgroundColor=(41,44,53),outlineColor =(159,167,180))
        self.NoButton = pygameGUI.button("confirmGUI",310,230,270,140,text="NO",fontType= "gui/Minecraft.ttf",backgroundColor=(41,44,53),outlineColor =(159,167,180))
        self.PositionGUI(WinSize)
    def update(self):
        '''check if an option has bean choses'''
        if self.yesButton.click:
            self.confermed = True
        elif self.NoButton.click:
            self.confermed = False
    def PositionGUI(self,windowSize):
        '''center and resize the gui to the window when it is re scaled'''
        surfaceWidth,surfaceHeight =0.6*windowSize[0] ,0.4*windowSize[1]
        self.surface =pygame.Surface((surfaceWidth,surfaceHeight),pygame.HWSURFACE)
        self.position =( 0.2*windowSize[0],0.3*windowSize[1])
        self.yesButton.renderdOfsetX = -self.position[0]
        self.yesButton.renderdOfsetY = -self.position [1]
        self.yesButton.x = surfaceWidth * 0.033
        self.yesButton.y = surfaceHeight * 0.575
        self.yesButton.width = surfaceWidth * 0.45
        self.yesButton.height = surfaceHeight * 0.233
        self.yesButton.loadGuiToSurface()
        self.NoButton.renderdOfsetX = -self.position [0]
        self.NoButton.renderdOfsetY = -self.position [1]
        self.NoButton.x =  surfaceWidth * 0.516
        self.NoButton.y = surfaceHeight * 0.575
        self.NoButton.width = surfaceWidth * 0.45
        self.NoButton.height = surfaceHeight * 0.233
        self.NoButton.loadGuiToSurface()
        self.confermTextBox.width = surfaceWidth
        self.confermTextBox.height = surfaceHeight/2
        self.confermTextBox.updateRender()
        self.confermTextBox.textUpdate = True
    def render(self):
        '''render the gui to the window with a background'''
        self.surface.fill((41,44,53))
        pygameGUI.displayGui(self.surface,"confirmGUI")
        win.blit(self.surface,self.position )



class CodeInput():
    def __init__(self,x,y,bgColour):
        '''initilise the code input area with all neaded vars'''
        #main vars
        self.x = x
        self.y = y
        self.bgColour = bgColour   
        #code flags
        fileHandling.CodeTools.loadFileData("dfcode.json")
        self.instructionFormats = fileHandling.CodeTools.LoadTools("codeFormating.json")["instructionFormats"]
        self.argumentFormats = fileHandling.CodeTools.LoadTools("codeFormating.json")["argumentFormats"]
        self.cachedActionLists = {} # format actiontile:list
        self.cachedLines ={}
        self.currentSugestions = []
        self.currentSugestionFilter = ""
        self.loadedInVarNames = []#list of all the veriable names that have been loaded between files
        self.sugestionScroll = 0 #the amount the sugestions have been scrolled set by the main gui silder
        self.mainCodeScroll = 0 #the amount the main code has been scrolled set by the main gui silder
        #text vars
        self.currentCode = ""
        self.fontSize = 20
        self.fontColour = (211,211,223)
        self.blockCountColour = (100,100,100)
        self.textColour = (84,252,252)
        self.numColour = (252,84,84)
        self.varColour = (252,252,84)
        self.equalVarColour = (234,21,239)
        self.commentColour = (94,154,85)
        self.targetColour = (120,120,160)
        self.mainFont = pygame.font.Font("gui/Minecraft.ttf",self.fontSize)
        self.sugestFont = pygame.font.Font("gui/Minecraft.ttf",int(self.fontSize/2))
        self.cursorIndex = 0        
        #undo vars
        self.maxUndo = 1000
        self.cachedCode = []
        self.cachedRedo = []
        self.cachedTimer = 0.1
        self.lastChashTime = time.time()-self.cachedTimer
        #input vars
        self.currentPressed = None
        self.keyStartTime  = time.time()
        self.keyRepeatTime = 0.5
        #call func
        self.updateScale()     
    def updateScale(self):
        '''resize when window is scaled'''
        self.width = WinSize[0]-100
        self.height = WinSize[1]-40
        self.surface = pygame.Surface((self.width,self.height),pygame.HWSURFACE)
        self.sugestionsSuface = pygame.Surface((100,WinSize[1]-300),pygame.HWSURFACE | pygame.SRCALPHA)
        self.renderToSurface()

    def clearcache(self):
        '''reset vars when the code is changed'''
        self.cachedActionLists = {}
        self.cachedLines ={}
        self.currentCode = ""
        self.cachedCode = []
        self.cachedRedo = []
        self.cursorIndex = 0 
        
    def getTextInput(self):
        '''get the input from the keyboad and process it into text or action'''
        mods = pygame.key.get_mods()
        for event in pygameGUI.events:
            if event.type == pygame.KEYDOWN  :# see if a key is pressed
                if event.key == pygame.K_RETURN: # add a new line when enters pressed
                    self.currentPressed= "\n"                    
                    self.keyStartTime = time.time()
                    self.addText(self.currentPressed)
                elif event.key == pygame.K_BACKSPACE: # delete a letter if backspace is pressed
                    self.currentPressed= -1
                    self.keyStartTime = time.time()
                    self.addText(self.currentPressed)
                elif mods&pygame.KMOD_CTRL and event.key == pygame.K_z: #undo
                    self.currentPressed= -2                    
                    self.keyStartTime = time.time()
                    self.addText(self.currentPressed)
                elif mods&pygame.KMOD_CTRL and event.key == pygame.K_y: #redo
                    self.currentPressed= -3                  
                    self.keyStartTime = time.time()
                    self.addText(self.currentPressed)
                elif event.key == pygame.K_DELETE: # delete a letter if backspace is pressed
                    self.currentPressed= -4
                    self.keyStartTime = time.time()
                    self.addText(self.currentPressed)
                elif event.key == pygame.K_TAB: #use tab to auto compleate sugestions else add spaces 
                    self.autoCompleateSugestion()
                elif mods&pygame.KMOD_CTRL and event.key == pygame.K_v: #paste
                    self.addText(pyperclip.paste())
                # move the cursor with arrow keys
                elif event.key == pygame.K_LEFT:
                    self.currentPressed= -5
                    self.keyStartTime = time.time()
                    self.addText(self.currentPressed)
                elif event.key == pygame.K_RIGHT:
                    self.currentPressed= -6
                    self.keyStartTime = time.time()
                    self.addText(self.currentPressed)
                elif event.key == pygame.K_DOWN:
                    self.currentPressed= -7
                    self.keyStartTime = time.time()
                    self.addText(self.currentPressed)
                elif event.key == pygame.K_UP:
                    self.currentPressed= -8
                    self.keyStartTime = time.time()
                    self.addText(self.currentPressed)
                    
                
                #input the rest of the text
                else:                    
                    self.currentPressed=event.unicode
                    self.keyStartTime = time.time()
                    self.addText(self.currentPressed)

            elif event.type == pygame.KEYUP  :# see if a key is pressed
                if event.key == pygame.K_RETURN and self.currentPressed =="\n": # stop pressing new line when letgo
                    self.currentPressed= None
                elif event.key == pygame.K_BACKSPACE and self.currentPressed == -1: 
                    self.currentPressed= None
                elif self.currentPressed == event.unicode :
                        self.currentPressed= None# add the text to the box when text is presed:
                elif mods&pygame.KMOD_CTRL and event.key == pygame.K_z and self.currentPressed ==-2: #undo
                    self.currentPressed= None
                elif mods&pygame.KMOD_CTRL and event.key == pygame.K_y and self.currentPressed ==-3: #undo
                    self.currentPressed= None
                elif event.key == pygame.K_DELETE and self.currentPressed ==-4: # delete a letter if backspace is pressed
                    self.currentPressed= None
                elif event.key == pygame.K_LEFT and self.currentPressed ==-5:
                    self.currentPressed= None
                elif event.key == pygame.K_RIGHT and self.currentPressed ==-6:
                    self.currentPressed= None
                elif event.key == pygame.K_DOWN and self.currentPressed ==-7:
                    self.currentPressed= None
                elif event.key == pygame.K_UP and self.currentPressed ==-8:
                    self.currentPressed= None
        if self.currentPressed != None and self.keyRepeatTime < time.time()-self.keyStartTime:
            self.addText(self.currentPressed)

    def cachUndo(self):
        '''every set amount of time save the current text to a list to be moved back to when un done'''
        if time.time()-self.lastChashTime >self.cachedTimer:
            if self.cachedCode != []:
                if self.cachedCode[len(self.cachedCode)-1] != self.currentCode and self.cachedRedo == []:
                    self.cachedCode.append(self.currentCode)                
                    if len(self.cachedCode)>self.maxUndo:
                        self.cachedCode.pop(0)
                    self.lastChashTime  = time.time()
            elif self.cachedRedo == []:
                self.cachedCode.append(self.currentCode) 
                self.lastChashTime  = time.time()
                
    def autoCompleateSugestion(self):
        '''when called it filters the sugestions and auto compleats the the top sugestion or to a tab if there is no sugestion'''
        topFilteredSugestion = "    "
        options = self.currentSugestions + self.loadedInVarNames
        for sugestion in options:
            if sugestion.startswith(self.currentSugestionFilter):
                topFilteredSugestion = sugestion.replace(self.currentSugestionFilter,"",1)  
                break
        self.addText(topFilteredSugestion)  
    def calculateUpDownArrow(self,updown):
        '''updown is a bool true for up calculates the chars that the cursor needs to move to go up or down'''
        if updown:
            index,line,indentAmount = self.getCurrentLine()
            if index >0:
                preLine = self.currentCode.split("\n")[index-1]  
                self.cursorIndex -=  + max(len(preLine)+1,len(line)+indentAmount+2)
        else:
            index,line,indentAmount = self.getCurrentLine()
            if index < self.currentCode.count("\n"):
                nextLine = self.currentCode.split("\n")[index+1]  
                self.cursorIndex +=min(len(line)+1,- indentAmount +len(nextLine))

    def addText(self,text): #-1 backspace, -2 undo, -3 redo, -4, dell,-5 left, -6 right, -7 down, - 8 up
        '''adds the text to the code or processes custom keybord inputs e.g. left arrow'''
        oldLineCount = self.currentCode.count("\n")+1
        if text == -1:
            if self.cursorIndex >0:
                self.cachedRedo = []
                self.currentCode = self.currentCode[:self.cursorIndex-1]+ self.currentCode[self.cursorIndex:]
                self.cursorIndex -=1
        elif text == -2:
            if self.cachedCode != []:
                self.cachedRedo.append(self.currentCode)
                self.currentCode = self.cachedCode[len(self.cachedCode)-1]
                self.cachedCode.pop(len(self.cachedCode)-1)
                
        elif text == -3:
            if self.cachedRedo != []:
                self.cachedCode.append(self.currentCode)
                self.currentCode = self.cachedRedo[len(self.cachedRedo)-1]
                self.cachedRedo.pop(len(self.cachedRedo)-1)
        elif text == -4:
            self.cachedRedo = []
            self.currentCode = self.currentCode[:self.cursorIndex]+ self.currentCode[self.cursorIndex+1:]
        elif text == -5:
            if self.cursorIndex >0:
                self.cursorIndex -= 1
        elif text == -6:
            if self.cursorIndex<len(self.currentCode):
                self.cursorIndex += 1
        elif text == -7:
            self.calculateUpDownArrow(False)
        elif text == -8:
            self.calculateUpDownArrow(True)
        
        elif text != "":
            self.cachedRedo = []
            self.currentCode = self.currentCode[:self.cursorIndex] + text + self.currentCode[self.cursorIndex:]
            self.cursorIndex += len(text)

        if self.currentCode.count("\n")+1 != oldLineCount:#if the lines are changed reprocess lines
            self.cachedLines={} 
            
          
        self.currentSugestions,self.currentSugestionFilter = self.compileCurrentLine() 
        

        self.renderToSurface()

    def renderToSurface(self):
        '''renders all the code and sugestions to there windows'''
        self.surface.fill(self.bgColour)
        self.sugestionsSuface.fill((0,0,0,0)) #clear the thing
        self.displayCurrentCode()
        self.displayCurentSugestions()

    def getCurrentLine(self):
        '''returns the current line of code and the index of the line and the index in the line'''
        charCount = 0
        lines = self.currentCode.split("\n")
        for index,line in enumerate(lines):
            charCount += len(line)+len("\n")
            if charCount >self.cursorIndex:                
                lineIndex = (self.cursorIndex -(charCount ))
                return index,line,lineIndex
        #if the index is out of range because of some undo action or somthing reset it to the maximum number
        self.cursorIndex = len(self.currentCode)
        return index,line,len(line)

    def compileCurrentLine(self,lineIndexIn = None):
        '''formats the line and returns a list of sugestions and the current filter for the line (set lineIndex to a value if you only need to format the line)'''
        if lineIndexIn is None:
            lineInfo = self.getCurrentLine()
            line = lineInfo[1]
            cursorIndex = lineInfo[2]
            lineIndex = lineInfo[0]
        else: #only the line is needed if it is just getting colour coded
            line = self.currentCode.split("\n")[lineIndexIn] 
            lineIndex = lineIndexIn
        lexedLine = parse.lexLine(line)
        posibleStarts = list(self.instructionFormats.keys())
        posibleDataTypes = list(self.argumentFormats.keys())
        formatText = [] #2d array of strings and the colour for that string
        finalSugestions = []#a string of values the user could be trying to type in
        sugestionFilter = "" # the value that is currently being edited by the user
        lineStart = ""
        action = ""
        currentEditIndex = -1
        for index,part in enumerate(lexedLine): # find the starter for the line
            if part.token == parse.token.Keyword or part.token == parse.token.Dot:
                lineStart += part.text
            if part.token == parse.token.Action:
                action = part.text
            if lineIndexIn is None:
                if part.startIndex <=(len(line)+cursorIndex) <= part.endIndex  :
                    
                    currentEditIndex = index

        keywordColour = [211,211,223]
        actionColour = [211,211,223]
        if lineStart in posibleStarts:
            currentInstructionFormat = self.instructionFormats[lineStart]
            keywordColour = currentInstructionFormat["Maincolour"]
            if "actionColour" in currentInstructionFormat.keys():
                actionColour = currentInstructionFormat["actionColour"]

        for token in lexedLine:
            match token.token :
                case parse.token.Keyword:
                    formatText.append([token.text,keywordColour])
                case parse.token.Action:
                    formatText.append([token.text,actionColour])
                case parse.token.Identifier:
                    formatText.append([token.text,self.varColour])
                case parse.token.Lable:
                    formatText.append([token.text,self.equalVarColour])
                case parse.token.DataTypeLable:
                    if token.text in posibleDataTypes:
                        formatText.append([token.text,self.argumentFormats[token.text]["colour"]])
                    else:
                        formatText.append([token.text,self.fontColour])
                case parse.token.String:
                    formatText.append([token.text,self.textColour])
                case parse.token.Num:
                    formatText.append([token.text,self.numColour])
                case parse.token.Comment:
                    formatText.append([token.text,self.commentColour])
                case parse.token.Target:
                    formatText.append([token.text,self.targetColour])
                case _:
                    formatText.append([token.text,self.fontColour])


        self.cachedLines[lineIndex] = formatText  
        if lineIndexIn is None :#only get sugestions if needed
            if line != "":
                #edit the sugestion if it can be done from the the current edditing token
                if lexedLine[currentEditIndex].token in [parse.token.Dot,parse.token.Comma,parse.token.BracketO,parse.token.BracketC,parse.token.Space]:
                    sugestionFilter = ""
                else: #if the user has just used a seperater there will be no sugestion filter
                    sugestionFilter = lexedLine[currentEditIndex].text
                if lexedLine[currentEditIndex].token == parse.token.Comment: 
                    finalSugestions = []    
                elif  lexedLine[currentEditIndex].token  == parse.token.Target:
                    finalSugestions = ["@Default","@Killer","@Damager","@Shooter","@Victim","@AllPlayers"]    
                elif lexedLine[currentEditIndex].token == parse.token.Action:
                    if lineStart in posibleStarts:
                        if "actionTitle" in currentInstructionFormat:
                            finalSugestions = fileHandling.CodeTools.LoadActionType(currentInstructionFormat["actionTitle"]) 
                        else:
                            pass #at some point set it to list of funcitons
                elif (lexedLine[currentEditIndex].token == parse.token.Null) or (lexedLine[currentEditIndex].token == parse.token.Dot):                        
                    if lineStart in posibleStarts:#the type of block is done it just needs the action
                        if "actionTitle" in currentInstructionFormat:#only get sugestions if action at some point maby sugestion some fuction names instead
                            finalSugestions = fileHandling.CodeTools.LoadActionType(currentInstructionFormat["actionTitle"]) 
                    else:
                        sugestionFilter = lineStart + lexedLine[currentEditIndex].text
                        finalSugestions = posibleStarts
                else:
                    if lineStart in posibleStarts: #load the defalut sugestion for the action type if it is valid
                        if   "actionTitle" in currentInstructionFormat  :
                            if action in fileHandling.CodeTools.LoadActionType(currentInstructionFormat["actionTitle"]):
                                chestVars = fileHandling.CodeTools.getActionAguments(action) 
                                for var in chestVars:
                                    if "description" in var:
                                        text = var["description"][0]
                                        if var["optional"]:
                                            text += "*"
                                        finalSugestions.append(text)
                                finalSugestions += fileHandling.CodeTools.LoadActionArgs(action)
                                        
                        elif "codeBlockID"in currentInstructionFormat  :
                            finalSugestions = fileHandling.CodeTools.LoadActionArgs(currentInstructionFormat["codeBlockID"])
                    hadComma = False
                    hadBracket = False
                    lastValue = None #saves the last value that was set as we go back to be used when geting optional variables or other things
                    for index in range (currentEditIndex,-1,-1):#loop backwards to find the last thing that change the sugestion
                        if lexedLine[index].token == parse.token.Comma:
                            hadComma = True
                        elif lexedLine[index].token == parse.token.BracketC:
                            hadBracket = True
                            break
                        elif lexedLine[index].token == parse.token.Num or lexedLine[index].token == parse.token.String:
                            lastValue = lexedLine[index].text
                        elif lexedLine[index].token == parse.token.Lable and not hadComma:#if the last thing to be started was a chest var
                            if "actionTitle" in currentInstructionFormat  :#if it is an action block
                                options = fileHandling.CodeTools.LoadActionArgsOptions(lexedLine[index].text.rstrip("="),action)
                            else:                                
                                options = fileHandling.CodeTools.LoadActionArgsOptions(lexedLine[index].text.rstrip("="),currentInstructionFormat["codeBlockID"])
                            finalSugestions = []
                            for sugestion in options:
                                finalSugestions.append('"'+sugestion+'"') 
                            break 
                        elif lexedLine[index].token == parse.token.DataTypeLable:
                            if lexedLine[index].text in posibleDataTypes:
                                finalSugestions = []
                                if not(hadComma) and "initialSugestion" in self.argumentFormats[lexedLine[index].text]:#if its the first argument of the data type sugest values for it
                                    match self.argumentFormats[lexedLine[index].text]["initialSugestion"]:
                                        case "sound":
                                            names = fileHandling.CodeTools.LoadSoundNames()
                                        case "potion":
                                            names = fileHandling.CodeTools.LoadPotionNames()
                                        case "gv":
                                            names = fileHandling.CodeTools.LoadGvNames()
                                        case "particle":
                                            names = fileHandling.CodeTools.LoadParticalNames()
                                        case "item":
                                            names = fileHandling.CodeTools.LoadItemNames()
                                    if names[0][0]!= "\"":#if they dont already have speach marks
                                        for name in names:
                                            finalSugestions.append('"'+name+'"')
                                    else:
                                        finalSugestions = names + finalSugestions
                                if "conditionalVars" in self.argumentFormats[lexedLine[index].text]:#if there is conditional options get these options
                                    match lexedLine[index].text:
                                        case "particle":
                                            if lastValue != None:
                                                extra = fileHandling.CodeTools.GetParticalFeilds(lastValue.replace("\"",""))
                                                if extra is not None:
                                                    for option in extra:                                                    
                                                        finalSugestions.append( option.replace(" ","") + "=")
                                finalSugestions += self.argumentFormats[lexedLine[index].text]["needVars"] + self.argumentFormats[lexedLine[index].text]["optionalVars"]
                               
            return finalSugestions, sugestionFilter

  
    def addCurrentVars(self,line):
        '''save a list of all the arguments that has been used''' # can no remove args if its un used yet
        for part in line:
            if part[1] == self.varColour:
                if part[0] not in self.loadedInVarNames and part[0] != "":
                    self.loadedInVarNames.append(part[0])

    def displayCurentSugestions(self):
        '''displays the list of filtered sugestions down the side'''        
        lineHeight = self.sugestFont.render("TEST",1,self.fontColour).get_height()
        count = 0 
        xofset = -self.sugestionScroll * 100 
        for sugestion in self.currentSugestions:
            if sugestion.startswith(self.currentSugestionFilter):
                if sugestion.endswith("="):#if its a arg starter
                    renSugest = self.sugestFont.render(sugestion,1,self.equalVarColour )
                elif sugestion.endswith("\""):#if its a text string for the arg sugestion
                    renSugest = self.sugestFont.render(sugestion,1,self.textColour )
                else:# if its just what the arg needs to be
                    renSugest = self.sugestFont.render(sugestion,1,self.fontColour)
                self.sugestionsSuface.blit(renSugest,(xofset,lineHeight*count))
                count += 1
        for var in self.loadedInVarNames:
            if var.startswith(self.currentSugestionFilter):
                renvar = self.sugestFont.render(var,1,self.varColour)
                self.sugestionsSuface.blit(renvar,(xofset,lineHeight*count))
                count += 1
    
    def displayCurrentCode(self):        
        '''renders the current code to the surface'''
        srollOfset = -self.mainCodeScroll * 2000
        lineHeight = self.mainFont.render("TEST",1,self.fontColour).get_height()
        blockCount = 0#the amout of blocks used by the code
        for lineIndex in range (0,self.currentCode.count("\n")+1):            
            if not(lineIndex in self.cachedLines):                 
                self.compileCurrentLine(lineIndex) 
                self.addCurrentVars(self.cachedLines[lineIndex])#chach the vars of the line if it is new
            ofsetX = 40 + srollOfset # just over the length of the number so it is constnat for all lines
            
            #render the rest of the line
            for part in self.cachedLines[lineIndex]:      
                if (part[0] == "{"):#the open bracket replaces the buffer block of the block before so dose not need to be counted either
                    blockCount -= 2 
                line = self.mainFont.render(part[0],1,part[1])   
                self.surface.blit(line,(ofsetX,lineIndex*lineHeight))
                ofsetX += line.get_width()
            #render the line number this needs to probaly be got from the lexed line as it is a bit scuf atm but i cba to fix it have fun
            if self.cachedLines[lineIndex] != []: #if not an empty line
                if not(self.cachedLines[lineIndex][0][0].startswith( "#")): #if it is not a comment                    
                        blockCount += 2
            line = self.mainFont.render(str(blockCount)+": ",1,self.blockCountColour)   
            self.surface.blit(line,(0,lineIndex*lineHeight))
    def displayCursor(self):
        '''displays the cursor to the user'''
        ofsetX = 40 +(-self.mainCodeScroll * 2000)#the numbering ofset
        lineNum,line,indexInLine = self.getCurrentLine()
        if line != "":
            preCursorText = line[:len(line)+indexInLine+1]
        else:
            preCursorText = ""
        renderedText = self.mainFont.render(preCursorText,1,self.fontColour)
        lineWidth,lineHeight = renderedText.get_width(),renderedText.get_height()
        if lineWidth+self.x+ofsetX >self.x:
            pygame.draw.rect(win,self.fontColour,(lineWidth+self.x+ofsetX,self.y + lineHeight*lineNum,5,lineHeight))
    def update(self):
        '''updates text input and caches undo'''
        self.getTextInput()
        self.cachUndo()
    def render(self):
        '''render the code and sugestions to the screen'''
        win.blit(self.sugestionsSuface,(0,300))
        win.blit(self.surface,(self.x,self.y))
        self.displayCursor()

#start
CodeTools = fileHandling.CodeTools.LoadTools(CodeToolsFile)
codeInput = CodeInput(100,40,(41,44,45))
#print(fileHandling.Hotbar.Load(HotbarFile,0,0))
codeGUI = GUI()


#main loop
running = True
while running:# run main funcitons
    update()
    render() 
    pygameGUI.events = []
    for event in pygame.event.get(): # if quit clicked close window
        pygameGUI.events.append(event)
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.VIDEORESIZE:
            if event.w < 1000:
                width = 1000
            else:
                width = event.w
            if event.h < 300:
                height = 300
            else:
                    height = event.h
            WinSize = (width, height)
            pygame.display.set_mode(WinSize,pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.SRCALPHA | pygame.RESIZABLE)
            codeGUI.PositionGUI(WinSize)
            codeInput.updateScale()
