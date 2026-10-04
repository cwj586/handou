Set ws = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
toolsDir = fso.GetParentFolderName(WScript.ScriptFullName)
projDir = fso.GetParentFolderName(toolsDir)
binDir = fso.BuildPath(projDir, "pet\bin")
exePath = fso.BuildPath(binDir, "BeanPet.exe")
If Not fso.FileExists(exePath) Then
  WScript.Echo "EXE NOT FOUND: " & exePath
  WScript.Quit 1
End If
desk = ws.ExpandEnvironmentStrings("%USERPROFILE%") & "\Desktop"
lnkPath = fso.BuildPath(desk, ChrW(25000) & ChrW(35910) & ".lnk")
Set lnk = ws.CreateShortcut(lnkPath)
lnk.TargetPath = exePath
lnk.WorkingDirectory = binDir
lnk.Description = "BeanPet"
lnk.Save
WScript.Echo "OK " & lnkPath
