import maya.cmds as cmds
import subprocess, tempfile, os, platform, time
import maya.mel as mel

###########################################################################
#  Change the RizomUV path to your location                               #
###########################################################################
rizomPath = r'/Applications/RizomUV.2022.0.app'
#osx path is usually "/Applications/RizomUV.2018.0.app"
#Export
def sendToRizom(*args):
  # cmds.refresh()
  # maya.cmds.toggleWindowVisibility(RizomWindow)
  # cmds.minimizeApp()
  obj = cmds.ls( selection=True, geometry=True, ap=True, dag=True)
  exportFile = tempfile.gettempdir() + os.sep + "ODRizomExport.obj"
  ## Setting RizomUV
  luascript = """
        ZomSet({Path="Vars.Viewport.ColorMapIDDisplayMode", Value=1})
        ZomSet({Path="Prefs.UI.Display.Select", Value=false})
        ZomSet({Path="Prefs.UI.Display.MultiUVSet", Value=false})
        ZomSet({Path="Prefs.UI.Display.AlignStraightenFlip", Value=true})
        ZomSet({Path="Prefs.UI.Display.AutoSelect", Value=true})
        ZomSet({Path="Prefs.UI.Display.Help", Value=false})
        ZomSet({Path="Prefs.UI.Display.Seams", Value=false})
        ZomSet({Path="Prefs.Default.Packing.MaxScaling", Value=1e+06})
        ZomSet({Path="Prefs.Default.Packing.MinScaling", Value=0})
        ZomSet({Path="Prefs.MousePresetMode", Value=2})
        ZomSet({Path="Prefs.PackOptions.MixScales", Value=true})
        ZomSet({Path="Prefs.UI.Display.ScriptLog", Value=false})
        """
  f = open(tempfile.gettempdir() + os.sep + "riz.lua", "w")
  f.write(luascript.replace("odfilepath", exportFile.replace("\\", "/")))
  f.close()
  
  cmds.file(exportFile, f=1, pr=1, typ="OBJexport", es=1, op="groups=1;ptgroups=1;materials=1;smoothing=1;normals=1")
  
  if cmds.checkBox('uvcheck', query=True, value=True):
    cmd = '"' + rizomPath + '" "' + exportFile + '"' + '" -cfi "' + tempfile.gettempdir() + os.sep + "riz.lua" + '"'
  else:
    cmd = '"' + rizomPath + '" /nu "' + exportFile + '"' + '" -cfi "' + tempfile.gettempdir() + os.sep + "riz.lua" + '"'
  if platform.system() == "Windows":
    subprocess.Popen(cmd)
  else:
    # Exctue
    os.system('open -W "' + rizomPath + '" --args "'+ exportFile +'" -cfi "'+tempfile.gettempdir() + os.sep + 'riz.lua"')

  #Close Rizom
  originalOBJs = cmds.ls( selection=True, geometry=True, ap=True, dag=True)
  if cmds.checkBox('linecheck', query=True, value=True):
    f = open(exportFile, "r")
    lines = f.readlines()
    f.close()

    f = open(exportFile, "w")
    for line in lines:
      if not line.startswith("#ZOMPROPERTIES"):
        f.write(line)
    f.close()

  cmds.file(exportFile, i=1, typ="OBJ", pr=1, op="mo=1", ns="ODRIZUV")
  cmds.select("ODRIZUV*:*")
  importedOBJs = cmds.ls(selection=True, geometry=True, o=True, s=False)
  cmds.select(clear=True)

  actualReplacedUVOJBs = []
  for obj in originalOBJs:
    for imp in importedOBJs:
      if obj.replace("Shape", "") in imp:
        cmds.polyTransfer(obj.replace("Shape", ""), vc=0, uv=1, v=0, ao=imp[:-5])
        actualReplacedUVOJBs.append(obj.replace("Shape", ""))
        break

  for obj in importedOBJs:
    try:
      print( "+0")

      cmds.select(obj[:-5], r=True)
      cmds.delete()
    except Exception as e:
      print('Cache: Clear Done')
      

  for obj in actualReplacedUVOJBs:
    print( "+1")
    cmds.select(obj, add=True)

  print("end getFromRizom")

#Auto UVs
def rizomAutoRoundtrip(*args):

  originalOBJs = cmds.ls( selection=True, geometry=True, ap=True, dag=True)
  exportFile = tempfile.gettempdir() + os.sep + "ODRizomExport.obj"
  cmds.file(exportFile, f=1, pr=1, typ="OBJexport", es=1, op="groups=1;ptgroups=1;materials=1;smoothing=1;normals=1")

  luascript = """ZomLoad({File={Path="odfilepath", ImportGroups=true, XYZ=true}, NormalizeUVW=true})
  --U3dSymmetrySet({Point={0, 0, 0}, Normal={1, 0, 0}, Threshold=0.01, Enabled=true, UPos=0.5, LocalMode=false})
  ZomSet({Path="Vars.Viewport.ColorMapIDDisplayMode", Value=1})
  ZomSelect({PrimType="Edge", Select=true, ResetBefore=true, ProtectMapName="Protect", FilterIslandVisible=true, Auto={Skeleton={}, Open=true, PipesCutter=true, HandleCutter=true}})
  ZomCut({PrimType="Edge"})
  ZomUnfold({PrimType="Edge", MinAngle=1e-005, Mix=1, Iterations=1, PreIterations=5, StopIfOutOFDomain=false, RoomSpace=0, PinMapName="Pin", ProcessNonFlats=true, ProcessSelection=true, ProcessAllIfNoneSelected=true, ProcessJustCut=true, BorderIntersections=true, TriangleFlips=true})
  ZomIslandGroups({Mode="DistributeInTilesEvenly", MergingPolicy=8322, GroupPath="RootGroup"})
  ZomPack({ProcessTileSelection=false, RecursionDepth=1, RootGroup="RootGroup", Scaling={Mode=2}, Rotate={}, Translate=true, LayoutScalingMode=2})
  ZomSave({File={Path="odfilepath", UVWProps=true}, __UpdateUIObjFileName=true})
  ZomQuit()
  """

  f = open(tempfile.gettempdir() + os.sep + "riz.lua", "w")
  f.write(luascript.replace("odfilepath", exportFile.replace("\\", "/")))
  f.close()
  cmd = '"' + rizomPath + '" -cfi "' + tempfile.gettempdir() + os.sep + "riz.lua" + '"'
  if platform.system() == "Windows":
    subprocess.call(cmd, shell=False)
  else:
    os.system('open -W "' + rizomPath + '" --args -cfi "'+tempfile.gettempdir() + os.sep + 'riz.lua"')
    #subprocess.Popen(["open", "-a", rizomPath, "--args", " -cfi ", tempfile.gettempdir() + os.sep + "riz.lua"])

  if cmds.checkBox('linecheck', query=True, value=True):
    f = open(exportFile, "r")
    lines = f.readlines()
    f.close()

    f = open(exportFile, "w")
    for line in lines:
      if not line.startswith("#ZOMPROPERTIES"):
        f.write(line)
    f.close()

  cmds.file(exportFile, i=1, typ="OBJ", pr=1, op="mo=1", ns="ODRIZUV")
  
  cmds.select("ODRIZUV*:*")
  importedOBJs = cmds.ls(selection=True, geometry=True, o=True, s=False)
  cmds.select(clear=True)

  actualReplacedUVOJBs = []
  for obj in originalOBJs:
    for imp in importedOBJs:
      if obj.replace("Shape", "") in imp:
        cmds.polyTransfer(obj.replace("Shape", ""), vc=0, uv=1, v=0, ao=imp[:-5])
        actualReplacedUVOJBs.append(obj.replace("Shape", ""))
        break

  for obj in importedOBJs:
    cmds.select(obj[:-5], r=True)
    cmds.delete()

  for obj in actualReplacedUVOJBs:
    cmds.select(obj, add=True)

# UI
RizomWindow = cmds.window(retain=True, title="RizomUV" ,maximizeButton=False, topEdge=0, leftEdge=1720)
cmds.window( RizomWindow, edit=True, visible=False)
cmds.columnLayout()
cmds.rowLayout( numberOfColumns=2 )
cmds.button( label='Export', width=70, command=sendToRizom, backgroundColor=[0.290,0.590,0.707])
cmds.button( label='Auto UVs', width=70, command=rizomAutoRoundtrip, align='right', backgroundColor=[0.8,0.537,0.2])
cmds.setParent("..")
cmds.rowLayout( numberOfColumns=2 )
cmds.checkBox('uvcheck', label='Exists UV', align='left')
cmds.checkBox('linecheck', label='Fix size', align='right')
cmds.setParent("..")
cmds.showWindow(RizomWindow)
