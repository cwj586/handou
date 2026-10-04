@echo off
setlocal
set CSC=C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe
set R1=/r:C:\Windows\Microsoft.NET\Framework64\v4.0.30319\WPF\PresentationCore.dll
set R2=/r:C:\Windows\Microsoft.NET\Framework64\v4.0.30319\WPF\PresentationFramework.dll
set R3=/r:C:\Windows\Microsoft.NET\Framework64\v4.0.30319\WPF\WindowsBase.dll
set R4=/r:C:\Windows\Microsoft.NET\Framework64\v4.0.30319\System.Xaml.dll
cd /d "%~dp0"
%CSC% /nologo /target:winexe /platform:anycpu /out:bin\BeanPet.exe %R1% %R2% %R3% %R4% BeanPet.cs BeanFrames.g.cs
if errorlevel 1 (echo BUILD1-FAIL & exit /b 1)
%CSC% /nologo /define:QUICK /target:winexe /platform:anycpu /out:bin\BeanPetTest.exe %R1% %R2% %R3% %R4% BeanPet.cs BeanFrames.g.cs
if errorlevel 1 (echo BUILD2-FAIL & exit /b 1)
echo BUILD-OK
