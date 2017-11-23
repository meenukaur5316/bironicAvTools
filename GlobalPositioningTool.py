'''
    MODULE: GlobalPositioning

    AUTHOR: Veronica Tello

    DATE: 7/5/2017

    VERSION: 2.0

    USAGE: GlobalPositioning allows the animator to move their pose based on a chosen pivot, a control or locator. 
    
    List of methods for class GlobalPositioning:
        __init__()
        getPivotCtrl()
        deleteObj(obj)
        avatarahCtrlCheck(pivot)
        getTargetCtrls()
        placeLocAtTargetCtrls()
        capturePose()
        constrainMoveKey(driver, driven, constraintType)
        positionPose()
        cleanUpScene()
        UI()
      
        
    NOTES:
    Login Form
'''

from pymel.all import *
import itertools

class GlobalPositioning:    

    def __init__(self):
        #instance variables
        self.projAvatarahRigs = ['Astrea', 'Proteus', 'Tartarus']
        self.projAvatarahRigCtrls = [DependNodeName(u'ik_left_arm'), 
                                     DependNodeName(u'ik_right_arm'), 
                                     DependNodeName(u'ik_right_leg'),     
                                     DependNodeName(u'ik_left_leg'),
                                     DependNodeName(u'COG_ctrl'), 
                                     DependNodeName(u'right_leg_poleVec'),
                                     DependNodeName(u'left_leg_poleVec'),
                                     DependNodeName(u'left_arm_poleVec'),
                                     DependNodeName(u'right_arm_poleVec')]
        self.targetCtrls = []
        self.pivotCtrl = ''
        self.locatorPivot = 'locatorPivot'
        self.locScale = [50, 50, 50]
        self.selectPivotMessage = 'Please select a control to be the pivot.'
        self.gpLocSuffix = '_gpLoc'
        self.targetCtrlLoc = []
        self.targetCtrlLocGrp = ''
        self.targetCtrlLocGrpVis = 0
        self.targetCtrlLocGrpNm = 'targetCtrlLoc_Grp'
        self.pivotTargetCon = ''
        
        #UI   
        self.windowName = 'globalPositioningToolWin'
        self.uiLabel = 'Global Positioning Tool'
        self.winWidth = 400
        self.winHeight = 350
        self.winSizing = False
        self.instructions = 'Moves the rig\'s pose to match the pivot\'s change in location and orientation'
        self.pivotDscrpt = 'Select the control that will be the pivot. \n\nIf using the locator option, position the locator before hitting Capture Pose.\n'
        self.targetDscrpt = 'Select the target controls that will be moved(ex: ik controls, cog control, pole vector controls, etc)\n\n*Note: If pole vector controls are not in world space, select those controls last.'
        self.captureBtnLbl = 'Capture Pose'
        self.positionBtnLbl = 'Snap Pose'
        self.pivotOptionList = ['use selected object', 'use locator']
        self.pivotSetBtnLbl = 'Set Pivot'
        self.targetBtnLbl = 'Set Target Controls'
        self.pivotTxtLbl = 'Pivot:'
        self.pivotMenu = 'pivotMenuWidget'
        self.pivotFieldBx = 'pivotFieldBxWidget'
        self.targetScroll = 'targetScrollWidget'
        self.btnH = 20
        self.btnW = 20
        self.UI()

        #scriptJob
        cycleCheck(evaluation=False)
        scriptJob(uid=[self.windowName, self.cleanUpScene])
        
    def getPivotCtrl(self):
        '''
            Checks the pivot type from the menu.
            Gets rid of 
        '''
        type = optionMenu(self.pivotMenu, q=True, value=True)
        if type == self.pivotOptionList[0]:
            #if the objects already exist, they get deleted 
            self.locatorPivot = self.deleteObj(self.locatorPivot)            
            self.targetCtrlLocGrp = self.deleteObj(self.targetCtrlLocGrp)
            if len(selected()):
                self.pivotCtrl = selected()[0]
            else:
                confirmDialog(m=self.selectPivotMessage)
                
        if type == self.pivotOptionList[-1]:
            self.locatorPivot = spaceLocator(n=self.locatorPivot)
            self.locatorPivot.setScale(self.locScale)
            self.pivotCtrl = self.locatorPivot
        textScrollList(self.pivotFieldBx, e=True,  removeAll=True)
        textScrollList(self.pivotFieldBx, e=True,  a=self.pivotCtrl)
        self.avatarahCtrlCheck(self.pivotCtrl)
        return self.pivotCtrl
    
    def deleteObj(self, obj):
        '''
            Deletes the object's name, not pymel object so there won't be a pymel error.
        '''
        if objExists(obj):
            try:
                delete(obj.name())
            except:
                print '%s is having a hard time getting deleted' %obj
            return ''
        else:
            return obj
    
    def avatarahCtrlCheck(self, pivot):
        '''
           Checks if the pivot control is part of an Avatarah game rig.
           If it is, it automatically populates the targetScroll list.
        ''' 
        for rig in self.projAvatarahRigs:
            if rig in str(pivot):
                textScrollList(self.targetScroll, e=True, removeAll=True)
                rigNamespace = pivot.namespace()
                self.targetCtrls = []
                for ctrl in self.projAvatarahRigCtrls: 
                    c = ctrl.addPrefix(rigNamespace)
                    c = PyNode(c)
                    self.targetCtrls.append(c)
                for sel in self.targetCtrls:
                    textScrollList(self.targetScroll, e=True, a=sel)
                self.positionMethod = 'constraint'                            
                return self.targetCtrls
        return False
            
    def getTargetCtrls(self):
        '''
           Clears the targetScroll list and repopulates it with the current selection.
        ''' 
        textScrollList(self.targetScroll, e=True, removeAll=True)
        for sel in selected():
            textScrollList(self.targetScroll, e=True, a=sel) 
        self.targetCtrls = selected()
        return self.targetCtrls
        
    def placeLocAtTargetCtrls(self):
        '''
           Places locators at the positions of the target locators.
           Positions an empty group at the location of the pivot control.
           Parents the locators to the group. 
        ''' 
        self.targetCtrlLocGrp = self.deleteObj(self.targetCtrlLocGrp)    
        self.targetCtrlLoc = []
        for ctrl in self.targetCtrls:
            ctrlLoc = spaceLocator(n=str(ctrl)+self.gpLocSuffix)
            self.constrainMoveKey(ctrl, ctrlLoc, 'parentConstraint')
            self.targetCtrlLoc.append(ctrlLoc)
        self.targetCtrlLocGrp = group(em=True, n=self.targetCtrlLocGrpNm)
        setAttr(self.targetCtrlLocGrp+'.v', self.targetCtrlLocGrpVis)
        self.constrainMoveKey(self.pivotCtrl, self.targetCtrlLocGrp, 'parentConstraint')
        parent(self.targetCtrlLoc, self.targetCtrlLocGrp)
        return self.targetCtrlLocGrp
        
    def capturePose(self):
        '''
            Constraints the group of target locators to the pivot control.
        ''' 
        if self.pivotCtrl:
            self.pivotTargetCon = self.deleteObj(self.pivotTargetCon) 
            self.placeLocAtTargetCtrls()
            self.pivotTargetCon = parentConstraint(self.pivotCtrl, self.targetCtrlLocGrp, mo=True)
            select(cl=True)
        else:
            confirmDialog(m = 'Please choose a pivot before you capture pose.')
            
    def constrainMoveKey(self, driver, driven, constraintType):
        '''
            Constrains moves driven to driver location based on constraintType. Ex: 'parentConstraint', 'pointConstraint', etc. 
        '''
        execStr = 'con = %s(driver, driven, mo=False)' %(constraintType)
        exec(execStr)
        location = driven.getTranslation('world')
        rotation = driven.getRotation('world')
        delete(con.name())
        driven.setTranslation(location, 'world')
        driven.setRotation(rotation, 'world')
        return driver, driven, constraintType, location
        
    def positionPose(self):
        '''
            Moves the rig into place based on self.positionMethod(constraint, xform, or pymel)
            
        ''' 
        if self.pivotCtrl and self.pivotTargetCon:
            targetCtrlsTmp = list(self.targetCtrls)
            targetCtrlLocTmp = list(self.targetCtrlLoc)
            for i in targetCtrlsTmp:
                if i == str(self.pivotCtrl):
                    targetCtrlsTmp.remove(i)
            for i in targetCtrlLocTmp:
                if i == str(self.pivotCtrl)+self.gpLocSuffix:
                    targetCtrlLocTmp.remove(i)
            
            for ctrl, loc in itertools.izip(targetCtrlsTmp, targetCtrlLocTmp):
                try:
                    self.constrainMoveKey(loc, ctrl, 'pointConstraint')
                    ctrl.setRotation(loc.getRotation('world'), 'world')   
                except: 
                    #if the new fixes are made this won't be necessary
                    confirmDialog(m='Please get rid of any constraints on %s. \nThis tool will not work properly otherwise.' %(ctrl))
                                    
        if self.pivotCtrl and not self.pivotTargetCon:
            confirmDialog(m = 'Please capture pose first.')
        if not self.pivotCtrl:
            confirmDialog(m = 'Please set pivot and capture pose first.')
            
    def cleanUpScene(self):
        '''
            Deletes the group of locators in the scene.
            Turns on cycle check again.
        ''' 
        self.targetCtrlLocGrp = self.deleteObj(self.targetCtrlLocGrp)
        self.locatorPivot = self.deleteObj(self.locatorPivot)
        cycleCheck(evaluation=True)
        
    def UI(self):
        '''
            Generates the UI.
        '''    
        if window(self.windowName, exists = True):
            deleteUI(self.windowName)
        window(self.windowName, w = self.winWidth, h = self.winHeight, sizeable = self.winSizing)
        #main layout
        mainFormLayout = formLayout(p=self.windowName)
        uiTitle = text(l=self.uiLabel, p=mainFormLayout, ww=True)
        instructText = text(l=self.instructions, p=mainFormLayout, ww=True)
        #pivot frame layout
        pivotFrame = frameLayout(p=mainFormLayout, labelVisible=False, borderVisible=True, marginWidth=5, marginHeight=5, width=175, height=250)
        pivotText = text(p=pivotFrame, l=self.pivotDscrpt, ww=True, align='left')
        self.pivotMenu = optionMenu(p=pivotFrame)
        for obj in self.pivotOptionList:
            menuItem(p=self.pivotMenu, label=obj)
        pivotSetBtn = button(p=pivotFrame, l=self.pivotSetBtnLbl, height=self.btnH, c=Callback(self.getPivotCtrl))
        pivotTxtFieldLbl = text(p=pivotFrame, l=self.pivotTxtLbl, align='left')
        self.pivotFieldBx = textScrollList(p=pivotFrame, h=10)
        #target frame layout
        targetFrame = frameLayout(p=mainFormLayout, labelVisible=False, borderVisible=True, marginWidth=5, marginHeight=5, width=175, height=250)
        targetText = text(p=targetFrame, l=self.targetDscrpt, ww=True, align='left')
        targetBtn = button(l=self.targetBtnLbl, c=Callback(self.getTargetCtrls))
        self.targetScroll = textScrollList(p=targetFrame, height=20)
        #buttons at end of main layout
        captureBtn = button(p=mainFormLayout, l=self.captureBtnLbl, c=Callback(self.capturePose))
        positionBtn = button(p=mainFormLayout, l=self.positionBtnLbl, c=Callback(self.positionPose))
        formLayout(mainFormLayout, edit=True, attachForm=[
                                                          (uiTitle, "top", 5),
                                                          (uiTitle, "left", 5),
                                                          (uiTitle, "right", 5),
                                                          (instructText, "left", 5), 
                                                          (instructText, "right", 5),
                                                          (pivotFrame, "left", 5),
                                                          (targetFrame, "right", 5),
                                                          (captureBtn, "left", 5),
                                                          (captureBtn, "right", 5),
                                                          (positionBtn, "left", 5),
                                                          (positionBtn, "right", 5),
                                                          (positionBtn, "bottom", 5),
                                                         ],
                                          attachControl=[
                                                          (instructText, "top", 5, uiTitle),
                                                          (pivotFrame, "top", 5, instructText),
                                                          (targetFrame, "top", 5, instructText),
                                                          (targetFrame, "left", 5, pivotFrame),
                                                          (captureBtn, "top", 5, targetFrame),
                                                          (positionBtn, "top", 5, captureBtn),
                                                         ])        
        showWindow(self.windowName)
        
GP = GlobalPositioning()
