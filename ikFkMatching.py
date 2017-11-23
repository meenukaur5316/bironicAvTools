'''
    MODULE: MatchingIkFk

    AUTHOR: Veronica Tello 7/21/2017

    VERSION: 1.3

    USAGE: ikFkMatching allows the animator to match ik and fk controls. 
           Contains Project Avatarah game rig specific information. 
           if using other rigs, this can be run without a ui and with the appropriate information:
               MIF = MatchingIkFk(ik control, pole vector control, list of fk controls, list of ik joints, list of fk joints, ('arm' or 'leg'), ui=False, projAvatarah=False)
               
    
    List of functions:
        avatarahCtrlCheck()
    List of methods from class MatchingIkFk:
        __init__()
        checkSelection()
        fkToIk()
        ikToFk()
        matchAnkle()
        bruteMatchingIk()
        returnMVector(obj)
        constrainMoveKey(driver, driven, constraintType)
        UI()
      
        
    NOTES: Still having issues with completely perfect matching on non-planar/shifted joints
    
'''

import itertools
from pymel.all import *
import maya.OpenMaya as om

#nested dictionary of rig joints for Tartarus, Proteus and Astrea. Separated by [rig][side][limb][joint]
projAvatarahIkFkJnts = {
                        'Tartarus' : 
                            {
                            'left' :
                                {
                                'arm' :
                                    {
                                    'fk' : [DependNodeName(u'fkj_left_arm_shldr_00_jnt'), DependNodeName(u'fkj_left_arm_elb_00_jnt'), DependNodeName(u'fkj_left_arm_wrist_00_jnt')],
                                    'ik' : [DependNodeName(u'ikj_left_arm_shldr_00_jnt'), DependNodeName(u'ikj_left_arm_elb_00_jnt'), DependNodeName(u'ikj_left_arm_wrist_00_jnt')]
                                    },
                                'leg' :
                                    {
                                    'fk' : [DependNodeName(u'fk_left_leg_hip_00_jnt'), DependNodeName(u'fk_left_leg_knee_00_jnt'), DependNodeName(u'fk_left_leg_ankle_00_jnt')],
                                    'ik' : [DependNodeName(u'ik_left_leg_hip_00_jnt'), DependNodeName(u'ik_left_leg_knee_00_jnt'), DependNodeName(u'ik_left_leg_ankle_00_jnt')]
                                    }
                                },
                            'right' : 
                                {
                                'arm' :
                                    {
                                    'fk' : [DependNodeName(u'fkj_right_arm_shldr_00_jnt'), DependNodeName(u'fkj_right_arm_elb_00_jnt'), DependNodeName(u'fkj_right_arm_wrist_00_jnt')],
                                    'ik' : [DependNodeName(u'ikj_right_arm_shldr_00_jnt'), DependNodeName(u'ikj_right_arm_elb_00_jnt'), DependNodeName(u'ikj_right_arm_wrist_00_jnt')]
                                    },
                                'leg' :
                                    {
                                    'fk' : [DependNodeName(u'fk_leg_hip_00_jnt'), DependNodeName(u'fk_leg_knee_00_jnt'), DependNodeName(u'fk_leg_ankle_00_jnt')],
                                    'ik' : [DependNodeName(u'ik_right_leg_hip_00_jnt'), DependNodeName(u'ik_right_leg_knee_00_jnt'), DependNodeName(u'ik_right_leg_ankle_00_jnt')]
                                    }
                                }
                            },                            
                        'Proteus' : 
                            {
                            'left' :
                                {
                                'arm' :
                                    {
                                    'fk' : [DependNodeName(u'fkj_rig_jnt_left_shld'), DependNodeName(u'fkj_rig_jnt_left_elb'), DependNodeName(u'fkj_rig_jnt_left_wrist')],
                                    'ik' : [DependNodeName(u'ikj_rig_jnt_left_shld'), DependNodeName(u'ikj_rig_jnt_left_elb'), DependNodeName(u'ikj_rig_jnt_left_wrist')]
                                    },
                                'leg' :
                                    {
                                    'fk' : [DependNodeName(u'fkj_jnt_left_leg_hipFk_jnt'), DependNodeName(u'fkj_jnt_left_leg_kneeFk_jnt'), DependNodeName(u'fkj_jnt_left_leg_ankleFk_jnt')],
                                    'ik' : [DependNodeName(u'ikj_jnt_left_leg_hipIk_jnt'), DependNodeName(u'ikj_jnt_left_leg_kneeIk_jnt'), DependNodeName(u'ikj_jnt_left_leg_ankleIk_jnt')]
                                    }
                                },
                            'right' : 
                                {
                                'arm' :
                                    {
                                    'fk' : [DependNodeName(u'fkj_rig_jnt_right_shld'), DependNodeName(u'fkj_rig_jnt_right_elb'), DependNodeName(u'fkj_rig_jnt_right_wrist')],
                                    'ik' : [DependNodeName(u'ikj_rig_jnt_right_shld'), DependNodeName(u'ikj_rig_jnt_right_elb'), DependNodeName(u'ikj_rig_jnt_right_wrist')]
                                    },
                                'leg' :
                                    {
                                    'fk' : [DependNodeName(u'fkj_jnt_right_leg_hipFk_jnt'), DependNodeName(u'fkj_jnt_right_leg_kneeFk_jnt'), DependNodeName(u'fkj_jnt_right_leg_ankleFk_jnt')],
                                    'ik' : [DependNodeName(u'ikj_jnt_right_leg_hipIk_jnt'), DependNodeName(u'ikj_jnt_right_leg_kneeIk_jnt'), DependNodeName(u'ikj_jnt_right_leg_ankleIk_jnt')]
                                    }
                                }
                            },
                        'Astrea' : 
                            {
                            'left' :
                                {
                                'arm' :
                                    {
                                    'fk' : [DependNodeName(u'fk_jnt_left_arm_shld_00'), DependNodeName(u'fk_jnt_left_arm_elb_00'), DependNodeName(u'fk_jnt_left_arm_wrist_00')],
                                    'ik' : [DependNodeName(u'ik_jnt_left_arm_shld_00'), DependNodeName(u'ik_jnt_left_arm_elb_00'), DependNodeName(u'ik_jnt_left_arm_wrist_00')]
                                    },
                                'leg' :
                                    {
                                    'fk' : [DependNodeName(u'fk_jnt_left_leg_hip_01'), DependNodeName(u'fk_jnt_left_leg_knee_00'), DependNodeName(u'fk_jnt_left_leg_ankle_00')],
                                    'ik' : [DependNodeName(u'ik_jnt_left_leg_hip_02'), DependNodeName(u'ik_jnt_left_leg_knee_00'), DependNodeName(u'ik_jnt_left_leg_ankle_00')]
                                    }
                                },
                            'right' : 
                                {
                                'arm' :
                                    {
                                    'fk' : [DependNodeName(u'fk_jnt_right_arm_shld_00'), DependNodeName(u'fk_jnt_right_arm_elb_00'), DependNodeName(u'fk_jnt_right_arm_wrist_00')],
                                    'ik' : [DependNodeName(u'ik_jnt_right_arm_shld_00'), DependNodeName(u'ik_jnt_right_arm_elb_00'), DependNodeName(u'ik_jnt_right_arm_wrist_00')]
                                    },
                                'leg' :
                                    {
                                    'fk' : [DependNodeName(u'fk_jnt_right_leg_hip_00'), DependNodeName(u'fk_jnt_right_leg_knee_00'), DependNodeName(u'fk_jnt_right_leg_ankle_00')],
                                    'ik' : [DependNodeName(u'ik_jnt_right_leg_hip_00'), DependNodeName(u'ik_jnt_right_leg_knee_00'), DependNodeName(u'ik_jnt_right_leg_ankle_00')]
                                    }
                                }
                            }
                        }

#nested dictionary of controls' naming convention, separated by [side][limb][control]
projAvatarahRigCtrls = {
                        'left' : 
                            {
                            'arm' :
                                {
                                'ikCtl' : DependNodeName(u'ik_left_arm'), 
                                'pvCtl' : DependNodeName(u'left_arm_poleVec'),
                                'fkCtl' : [DependNodeName(u'fk_left_shld'), 
                                           DependNodeName(u'fk_left_elb'), 
                                           DependNodeName(u'fk_left_wrist')]
                                },
                            'leg' :
                                {
                                'ikCtl' : DependNodeName(u'ik_left_leg'),
                                'pvCtl' : DependNodeName(u'left_leg_poleVec'),
                                'fkCtl' : [DependNodeName(u'fk_left_hip'), 
                                           DependNodeName(u'fk_left_knee'),
                                           DependNodeName(u'fk_left_ankle')]
                                }
                            }, 
                        'right' :
                            {
                            'arm' :
                                {
                                'ikCtl' : DependNodeName(u'ik_right_arm'),
                                'pvCtl' : DependNodeName(u'right_arm_poleVec'),
                                'fkCtl' : [DependNodeName(u'fk_right_shld'), 
                                           DependNodeName(u'fk_right_elb'), 
                                           DependNodeName(u'fk_right_wrist')], 
                                },
                            'leg' :
                                {
                                'ikCtl' : DependNodeName(u'ik_right_leg'),     
                                'pvCtl' : DependNodeName(u'right_leg_poleVec'),
                                'fkCtl' : [DependNodeName(u'fk_right_hip'), 
                                           DependNodeName(u'fk_right_knee'), 
                                           DependNodeName(u'fk_right_ankle')]
                                },  

                            }
                       }     

#lists of rigs, sides, and limbs                     
projAvatarahRigs = ['Astrea', 'Proteus', 'Tartarus']
sideList = ['left', 'right']
limbList = ['arm', 'leg']

def avatarahCtrlCheck(obj):
    '''
      Checks if obj from an avatarah game rig. 
      If so, it returns ikCtl, pvCtl, fkCtls, ikJnts, fkJnts
    ''' 
    ikCtl = ''
    pvCtl = ''
    fkCtls = []
    ikJnts = []
    fkJnts = []
    for rig in projAvatarahRigs:
        if rig in str(obj):
            print rig
            rigNamespace = obj.namespace()
            for i in sideList:
                if i in str(obj):
                    side = i
            for i in limbList:
                if i in str(obj):
                    limb = i
            if side and limb:
                ikCtl = PyNode(projAvatarahRigCtrls[side][limb]['ikCtl'].addPrefix(rigNamespace))
                pvCtl = PyNode(projAvatarahRigCtrls[side][limb]['pvCtl'].addPrefix(rigNamespace))
                for fk in projAvatarahRigCtrls[side][limb]['fkCtl']:
                    fkCtls.append(PyNode(fk.addPrefix(rigNamespace)))
                for ik in projAvatarahIkFkJnts[rig][side][limb]['ik']:
                    ikJnts.append(PyNode(ik.addPrefix(rigNamespace)))
                for fk in projAvatarahIkFkJnts[rig][side][limb]['fk']:
                    fkJnts.append(PyNode(fk.addPrefix(rigNamespace)))                        
                return ikCtl, pvCtl, fkCtls, ikJnts, fkJnts, limb
    return False

class MatchingIkFk:
    
    def __init__(self, ikCtl='', pvCtl='', fkCtls='', ikJnts='', fkJnts='', limb='', projAvatarah=True, ui=True):
        #instance variables
        self.ikCtl = ikCtl
        self.pvCtl = pvCtl 
        self.fkCtls = fkCtls 
        self.ikJnts = ikJnts 
        self.fkJnts = fkJnts
        self.limb = limb
        self.projAvatarah = projAvatarah
        
        #ui variables
        self.windowName = 'ikFkMatchingWin'
        self.winWidth = 215
        self.winHeight = 87
        self.winSizing = True
        self.instructions = 'Select the IkFk Switch Control for the corresponding limb\nthen choose the matching style.'
        self.uiLabel = 'IK/FK Matching'
        self.fkToIkBtnLbl = 'FK to IK'
        self.ikToFkBtnLbl = 'IK to FK'
        if ui:
            self.UI()
            
    def checkSelection(self):
        '''
            Checks the selection and runs avatarahCtrlCheck function to get the corresponding information needed.
        '''
        if self.projAvatarah:
            try:
                #print selected()[0]
                self.ikCtl, self.pvCtl, self.fkCtls, self.ikJnts, self.fkJnts, self.limb = avatarahCtrlCheck(selected()[0])

            except:
                confirmDialog(m='Please select the limb\'s corresponding ikFk switch control')
        else:
            pass
    
    def fkToIk(self):
        '''
            Matches the fk to the ik position. 
        '''
        self.checkSelection()
        for ikJ, fkC in itertools.izip(self.ikJnts, self.fkCtls):
            rotIK = xform(ikJ, q=True, rotation=True)
            #rotFK = xform(fkC, q=True, ws=True, a=True, rotation=True)            
            xform(fkC, rotation=rotIK)
            #fkC.setRotation(ikJ.getRotation('world'), 'world')
            
    def ikToFk(self, orientObj=True, pvOffset=2):
        '''
            Matches the ik to the fk position.
        '''
        self.checkSelection()            
        if self.limb == 'arm':
            self.constrainMoveKey(self.fkJnts[-1], self.ikCtl, 'parentConstraint')
        if self.limb == 'leg':
            self.matchAnkle()
            
        #vector math
        fkWristVec = self.returnMVector(self.fkJnts[-1])
        fkElbVec = self.returnMVector(self.fkJnts[-2])
        fkShldrVec = self.returnMVector(self.fkJnts[0])
        #gets the mid-point between the two vectors
        midpnt = (fkWristVec + fkShldrVec)/2
        #get vector from midpnt to elbow from origin
        pvOrigin  = fkElbVec - midpnt
        #extends vector by offset 
        pvRaw = pvOrigin * pvOffset
        pvLocation = pvRaw + midpnt
        pvLoc = spaceLocator()
        pvLoc.setTranslation(pvLocation, 'world')
        self.constrainMoveKey(pvLoc, self.pvCtl, 'pointConstraint')
        delete(pvLoc)
        
        #self.bruteMatchingIk()
    
    def matchAnkle(self):
        '''
            Matches the ankle correctly when doing ik to fk position
            since the ik ankle control is oriented to the world and the fk ankle control is oriented to self.
        '''
        #gets the fk ankle's parent and ik ankle's parent
        fkAnkleParent = self.fkCtls[-1].getParent()
        ikAnkleParent = self.ikCtl.getParent()
        
        #saves the rotations of the fk controls
        hipRot = getAttr(self.fkCtls[0]+'.r')
        kneeRot = getAttr(self.fkCtls[1]+'.r')
        ankleRot = getAttr(self.fkCtls[2]+'.r')
        
        #sets the rotation of the fk controls to zero 
        #so the original location and orientation of fkAnkle parent can be found
        setAttr(self.fkCtls[0]+'.r', 0, 0, 0)
        setAttr(self.fkCtls[1]+'.r', 0, 0, 0)
        setAttr(self.fkCtls[2]+'.r', 0, 0, 0)
        
        #creates locators and snaps them to the position of the fkAnkle parent and ikAnkle parent
        fkTempLoc = spaceLocator(n='fkTempLoc')
        ikTempLoc = spaceLocator(n='ikTempLoc')
        delete(parentConstraint(fkAnkleParent, fkTempLoc, mo=False))
        delete(parentConstraint(ikAnkleParent, ikTempLoc, mo=False))
        
        #parents fkLoc to ikLoc, and reapplies original rotations to fk controls
        parent(ikTempLoc, fkTempLoc)
        setAttr(ikTempLoc+'.t', 0, 0, 0)
        setAttr(self.fkCtls[0]+'.r', hipRot)
        setAttr(self.fkCtls[1]+'.r', kneeRot)
        setAttr(self.fkCtls[2]+'.r', ankleRot)
        
        #snaps the fkLoc to the ankle control, which will move the ikLoc into the correct position and orientation, 
        #then the ik control can be then snapped to the locator position.
        delete(parentConstraint(self.fkCtls[-1], fkTempLoc))
        self.constrainMoveKey(ikTempLoc, self.ikCtl, 'parentConstraint')
        
        #clean up
        delete(ikTempLoc, fkTempLoc)
        
    def bruteMatchingIk(self):
        '''
            Brute matching of non-planar joints, ik to fk. The results aren't quite as hoped.
        '''
        tmpFkJnts = duplicate(self.fkJnts, po=True)
        tmpIk = ikHandle(n='tmpIk', solver='ikRPsolver', startJoint=tmpFkJnts[0], endEffector=tmpFkJnts[-1])[0]
        pvX = tmpIk.getAttr('poleVectorX')
        pvY = tmpIk.getAttr('poleVectorY')
        pvZ = tmpIk.getAttr('poleVectorZ')
        rawVec = dt.Vector(pvX, pvY, pvZ)
        elbLoc = self.fkJnts[1].getTranslation('world')
        loc = spaceLocator()     
        newVec = rawVec + elbLoc       
        loc.setTranslation(newVec, 'world')
                
    def returnMVector(self, obj):
        '''
            Gets the absolute, world space coordinates of the obj and returns the vector of obj.
        ''' 
        loc = xform(obj, q=True, ws=True, a=True, rp=True)
        vecLoc = om.MVector(loc[0], loc[1], loc[2])
        return vecLoc

    def constrainMoveKey(self, driver, driven, constraintType):
        '''
            Constrain moves driven to driver's position and/or orientation depending on type of constraint used.
        '''    
        execStr = 'con = %s(driver, driven, mo=False)' %(constraintType)
        exec(execStr)
        location = driven.getTranslation('world')
        rotation = driven.getRotation('world')
        delete(con.name())
        driven.setTranslation(location, 'world')
        driven.setRotation(rotation, 'world')
        return driver, driven, constraintType, location
        
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
        ikToFkBtn = button(p=mainFormLayout, l=self.ikToFkBtnLbl, w=100, c=Callback(self.ikToFk))
        fkToIkBtn = button(p=mainFormLayout, l=self.fkToIkBtnLbl, w=100, c=Callback(self.fkToIk))
        formLayout(mainFormLayout, e=True, attachForm=[(uiTitle, 'top', 5),
                                                       (uiTitle, 'left', 5),
                                                       (uiTitle, 'right', 5),
                                                       (instructText, 'left', 5),
                                                       (instructText, 'right', 5),
                                                       (ikToFkBtn, 'right', 5),
                                                       (fkToIkBtn, 'left', 5),
                                                       (fkToIkBtn, 'bottom', 5),
                                                       (ikToFkBtn, 'bottom', 5),
                                                       ], 
                                           attachControl=[(instructText, 'top', 5, uiTitle),
                                                          (ikToFkBtn, 'top', 10, instructText),
                                                          (fkToIkBtn, 'top', 10, instructText),
                                                          (fkToIkBtn, 'right', 5, ikToFkBtn),
                                                           ])       
        showWindow(self.windowName)

MIF = MatchingIkFk()            
              
    
