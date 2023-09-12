                                                                                                            
@echo off

set _NCS=1
call :_colorprep

:MainMenu
color 07
title Nodel Service Installer
mode 95, 35

echo:       
call :_color %Inverse% "                                 Nodel Service Installer v1.0                                  " 
call :_color2 %_White% "                         	                                          " %Grey% " Fennecdeer Creative " 
echo:       
call :_color2 %_White% "         " %Underline% "New Service:"
echo:
call :_color2 %_White% "               [1] " %_Yellow% "Install New Service"

echo:        _______________________________________________________________________________

echo:                                                                     
call :_color2 %_White% "         " %Underline% "Downloads:"
call :_color2 %_White% "         " %Grey% "[Opens in web browser]"
echo:
echo:               [2] Download Java 8 JDK
echo:               [3] Download Latest Nodelhost JAR
echo:               [4] Download Latest Nodel Host Service EXE
echo:               [5] Download Python 2.5 


echo:        _______________________________________________________________________________

echo:                                                                     
call :_color2 %_White% "         " %Underline% "Extras:"
echo:
call :_color2 %_White% "               [6] " %_Red% "Uninstall Service"
echo:        _______________________________________________________________________________
echo:
echo:
echo:
echo:
echo:
call :_color2 %_White% "         " %_Green% "Enter a menu option in the keyboard [1, 2, 3, 4, 5, 6]: "


choice /C 123456 /N

set _erl=%errorlevel%


if %_erl%==6  setlocal & cls & call :Uninstall                                      & cls & endlocal & goto :MainMenu 
if %_erl%==5  setlocal & cls & call :DownloadPython                                      & cls & endlocal 
if %_erl%==4  setlocal & cls & call :DownloadNodelService                                      & cls & endlocal
if %_erl%==3  setlocal & cls & call :DownloadNodelHost                                      & cls & endlocal
if %_erl%==2  setlocal & cls & call :DownloadJava                                      & cls & endlocal 
if %_erl%==1  setlocal & cls & call :Install                                      & cls & endlocal
goto :MainMenu

::========================================================================================================================================
:Install
echo:
call :_color2 %_White% "                                     " %Inverse% " Installing Service "
echo:        _______________________________________________________________________________
echo:

call :_color3 %_White% "       Move all those files you downloaded " %_Yellow% "[except the Python Installer]" %_White% " into folder" 
call :_color2 %_White% "       within your Nodel installation named 'Service' " %Grey% "[e.g. C:\Nodel\Service]."
echo:
call :_color %_White% "       The folder structure should look like:"
echo:
echo:         - C:\Nodel\Service\jdk###-b##\ [after extracting the zip file]
echo:         - C:\Nodel\Service\nodelhost-###-#.#-rev.jar
echo:         - C:\Nodel\Service\NodelHostsvc.exe.x64
echo:         - C:\Nodel\Service\NodelHostsvcw.exe
echo:
echo:        _______________________________________________________________________________
echo:

@REM Default values, if the user is feeling dangerous 
set SHORTROLE=Main
set NODEL_JAR=nodelhost-release-2.2.1-rev448.jar
set JAVA_VERSION=jdk8u382-b05
set NODEL_HOME=C:\Nodel
set SERVICE_HOME=C:\Nodel\Service

call :_color2 %_White% "       - Name of the service? " %Grey% "[Main]"
set /p SHORTROLE= ""
call :_color2 %_White% "       - Location of the Nodel Install? " %Grey% "[C:\Nodel]"
set /p NODEL_HOME= ""
call :_color2 %_White% "       - Location of the Nodel JAR? " %Grey% "[nodelhost-release-2.2.1-rev448.jar]"
set /p NODEL_JAR= ""
call :_color2 %_White% "       - Location of the Java JDK folder? " %Grey% "[jdk8u382-b05]"
set /p JAVA_VERSION= ""
call :_color2 %_White% "       - Location of the Nodel Service Folder? " %Grey% "[C:\Nodel\Service]"
set /p SERVICE_HOME= ""

rem The rest of these parameters are all derived from the user parameters above:

rem The short name of the Windows service (e.g. "nodel-main")
set NAME=nodel-%SHORTROLE%

rem The title / display name part e.g. "Nodel Host (main)"
set TITLE=Nodel Host (%SHORTROLE%)

rem The description part
set DESC=The Nodel project.

rem The full path to the Nodel JAR
set NODEL_JAR_PATH=%SERVICE_HOME%\%NODEL_JAR%
if not exist %NODEL_JAR_PATH% (
  call :_color2 %_White% "                                 " %Red% " NODEL JAR NOT FOUND "
  call :_color2 %_White% "                                  " %Grey% " Make sure the name matches! "
  
  echo:
  call :_color2 %_White% "                                " %Inverse% " Press enter to restart"
  pause>nul
  cls
  goto :install
)
rem The Java home
set JAVA_HOME=%SERVICE_HOME%\%JAVA_VERSION%
if not exist %JAVA_HOME%\ (
  call :_color2 %_White% "                                     " %Red% " JAVA NOT FOUND "
  call :_color2 %_White% "                            " %Grey% " Make sure to extract the folder! "
  echo:
  call :_color2 %_White% "                                 " %Inverse% " Press enter to restart "
  pause>nul
  cls
  goto :install
)
rem The Java DLL entry-point used by the service
set JAVA_DLL=%JAVA_HOME%\jre\bin\server\jvm.dll

rem The file name of the service executable
set SVCNAME=%NAME%svc.exe
set SVC_PATH=%NODEL_HOME%\%SVCNAME%

rem The file name of the service controller user-interface
set SVCGUI=%NAME%svcw.exe
set SVCGUI_PATH=%NODEL_HOME%\%SVCGUI%

rem     (makes a copy of the process executable so that it can be spotted easily in process lists)
echo F|xcopy %SERVICE_HOME%\NodelHostsvc.exe.x64 %SVC_PATH%
echo F|xcopy %SERVICE_HOME%\NodelHostsvcw.exe %SVCGUI_PATH%


rem     (install the service)
%SVC_PATH% //IS --DisplayName "%TITLE%" --Description "%DESC%" --Startup auto --Jvm %JAVA_DLL% --StartMode jvm --StartClass org.nodel.nodelhost.Service --StartMethod start --StopMode jvm --StopClass org.nodel.nodelhost.Service --StopMethod stop --LogPath .\logs --Classpath %NODEL_JAR_PATH%

call :_color %_Green% "                                    Install Successful!"
call :_color2 %_White% "                                    " %Inverse% "Press ENTER to EXIT"
pause>nul
exit

::========================================================================================================================================
:Install2
rem     (run the configurator to allow user to check preferences or just start the service immediately)

%SVCGUI_PATH%

::========================================================================================================================================
:DownloadJava
start https://github.com/adoptium/temurin8-binaries/releases/download/jdk8u382-b05/OpenJDK8U-jdk_x64_windows_hotspot_8u382b05.zip
goto :MainMenu

::========================================================================================================================================
:DownloadNodelHost
start https://github.com/museumsvictoria/nodel/releases/latest
goto :MainMenu

::========================================================================================================================================
:DownloadNodelService
echo:
call :_color2 %_White% "                                     " %Inverse% " Downloading Service EXE "
echo:        _______________________________________________________________________________
echo:
echo:
echo:       The files you need to download are:
echo:
call :_color2 %_White% "               - NodelHostsvc.exe.x64 " %Grey% "[or NodelHostsvc.exe.x86 if on 32bit systems]"
call :_color %_White% "               - NodelHostsvcw.exe " 
echo:
call :_color2 %_White% "       To download from GitHub, click the exe, then press the download icon in the " %_Yellow% "top right."
echo:
echo:
echo:
echo:
echo:
echo:
echo:

echo:
echo:
echo:
call :_color2 %_White% "         " %_Green% "Press 1 to return to open the GitHub page, Press 2 to return to Main Menu."

choice /C 12 /N
set _erl=%errorlevel%
if %_erl%==1  setlocal & cls & call :DownloadNodelService2                                      & cls & endlocal & goto :MainMenu
if %_erl%==2  setlocal & call :MainMenu                                      & cls & endlocal & goto :MainMenu
goto :MainMenu

::========================================================================================================================================
:DownloadNodelService2
start https://github.com/museumsvictoria/nodel/tree/master/nodel-windows/service
goto :DownloadNodelService
::========================================================================================================================================
:DownloadPython
start https://www.python.org/ftp/python/2.5/python-2.5.msi
goto :MainMenu

::========================================================================================================================================
:Uninstall
SETLOCAL EnableDelayedExpansion


echo:
call :_color2 %_White% "                                     " %Red% " Uninstalling Service "
echo:        _______________________________________________________________________________
set ServiceName= nodel-mainsvc
set ServicePath= C:\Nodel\nodel-mainsvc.exe

call :_color2 %_White% "       - Name of the service to uninstall? " %Grey% "[Check services.msc for the service name]"
set /p ServiceName= 

call :_color2 %_White% "       - Location of Service exe? " %Grey% "[C:\Nodel\nodel-mainsvc.exe]"
set /p ServicePath= 

call :_color3 %_White% "       " %Red% "- Are you sure??" %_Red% " [y or n]"
set /p Confirmation= ""

if "%Confirmation%" EQU "y" ( goto :Uninstall2 ) 
if "%Confirmation%" EQU "n" ( goto :MainMenu ) 

goto :MainMenu




::========================================================================================================================================
:Uninstall2

echo:
%ServicePath% //DS
echo:
echo:
echo:
call :_color2 %_White% "                                    " %Red% " Uninstallation completed! "
echo:
call :_color2 %_White% "                                     " %Inverse% " Press ENTER to EXIT "
goto :MainMenu




::===============================================================================
:_color
if %_NCS% EQU 1 (
if defined _unattended ( echo %~2) else ( echo %esc%[%~1%~2%esc%[0m)
) else (
if defined _unattended (echo %~2) else (call :batcol %~1 "%~2")
)
exit /b

::========================================================================================================================================
:_color2
if %_NCS% EQU 1 (
echo %esc%[%~1%~2%esc%[%~3%~4%esc%[0m
) else (
call :batcol %~1 "%~2" %~3 "%~4"
)
exit /b

::========================================================================================================================================
:_color3
if %_NCS% EQU 1 (
echo %esc%[%~1%~2%esc%[%~3%~4%esc%[%~5%~6%esc%[0m
) else (
call :batcol %~1 "%~2" %~3 "%~4" %~5 "%~6"
)
exit /b

::========================================================================================================================================

:batcol
pushd %_coltemp%
if not exist "'" (<nul >"'" set /p "=.")
setlocal
set "s=%~2"
set "t=%~4"
call :_batcol %1 s %3 t
del /f /q "'"
del /f /q "`.txt"
popd
exit /b

::========================================================================================================================================

:_batcol
setlocal EnableDelayedExpansion
set "s=!%~2!"
set "t=!%~4!"
for /f delims^=^ eol^= %%i in ("!s!") do (
  if "!" equ "" setlocal DisableDelayedExpansion
    >`.txt (echo %%i\..\')
    findstr /a:%~1 /f:`.txt "."
    <nul set /p "=%_BS%%_BS%%_BS%%_BS%%_BS%%_BS%%_BS%"
)
if "%~4"=="" echo(&exit /b
setlocal EnableDelayedExpansion
for /f delims^=^ eol^= %%i in ("!t!") do (
  if "!" equ "" setlocal DisableDelayedExpansion
    >`.txt (echo %%i\..\')
    findstr /a:%~3 /f:`.txt "."
    <nul set /p "=%_BS%%_BS%%_BS%%_BS%%_BS%%_BS%%_BS%"
)
echo(
exit /b

::========================================================================================================================================

:_colorprep
if %_NCS% EQU 1 (
for /F %%a in ('echo prompt $E ^| cmd') do set "esc=%%a"
set     "Red="41;97m""
set    "Gray="100;97m""
set   "Black="30m""
set   "Green="42;97m""
set    "Blue="44;97m""
set  "Yellow="43;97m""
set "Magenta="45;97m""
set "_Magenta="40;95m""
set    "_Red="40;91m""
set  "_Green="40;92m""
set   "_Blue="40;94m""
set  "_White="40;37m""
set "_Yellow="40;93m""

set "Grey="40;90m""
set "Inverse="1;7m""
set "Underline="4;4m""

exit /b
)
for /f %%A in ('"prompt $H&for %%B in (1) do rem"') do set "_BS=%%A %%A"
set "_coltemp=%SystemRoot%\Temp"
set     "Red="CF""
set    "Gray="8F""
set   "Black="00""
set   "Green="2F""
set    "Blue="1F""
set  "Yellow="6F""
set "Magenta="5F""
set    "_Red="0C""
set  "_Green="0A""
set   "_Blue="09""
set  "_White="07""
set "_Yellow="0E""


exit /b


::========================================================================================================================================                                                                                    
                                                                                       
:::                             .                              .                             
:::                            ?@"                            '&j                            
:::                           '$$$>                          ,B$$,                           
:::                           `$$$$z,                      `r$$$$;                           
:::                            c$$$$$z:                  "x$$$$$8.                           
:::                            .]@$$$$$%[`            '+W$$$$$$|.                            
:::                              .:/B$$$$$I          `$$$$$@rI.                              
:::        .l|;                   `  ^$$$$#          |$$$$;  ^                   "\<'        
:::       ;@c'                    t%\If$$$$"        .$$$$#;1&M                    .f$-       
:::      `$$t(|(1]~I,`.           .+z$$$$$$u        }$$$$$$W[.           .`";<]1(|(($$I      
:::      1$$$$$$$$$$$$$@v1i^.        ';x$$$$^      .$$$$zi'        .`I}x%$$$$$$$$$$$$$z      
:::      *fz$$$$$$$$$$$$$$$$$W\i`      .$$$$j      ]$$$$`      `I1#$$$$$$$$$$$$$$$$$W\$.     
:::      @; ^x$$$$$$$$$$$$$$$$$$$$ri`   ($$$$^    .@$$$#   ';/B$$$$$$$$$$$$$$$$$$$*, `$'     
:::      Bi   `|$$$$$$$$$$$$$$$$$$$$$8),,$$$$*    /$$$$<"[M$$$$$$$$$$$$$$$$$$$$$r^   "$'     
:::      z1     '\$$$$$$$$$$$$$$$$$$$$$$$$$$$$+  ,$$$$$$$$$$$$$$$$$$$$$$$$$$$$n`     !$      
:::      [M       `u$$$$$$$$$$$$$$$$$$$$$$$$$$$l:8$$$$$$$$$$$$$$$$$$$$$$$$$$M,       tu      
:::      `$^        ?$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$/        .$I      
:::       uc      `[;$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$<-,      )8       
:::       ^$I      +$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$|      ^$!       
:::        }B`     `>M$$$$$$$$$$$$$$$$j>:,>z$$$$$$$$W_,,!|@$$$$$$$$$$$$$$$8-"     .Mx        
:::         \B^    `8$$$$$$$$$$$$$$$$^      >$$$$$$1      '%$$$$$$$$$$$$$$$@:    '#v.        
:::          {$i    ,v$$$$$$$$$$$$$$#        [$$$$x        ($$$$$$$$$$$$$$#i    ,Br.         
:::           "Wx'  I$$$$$$$$$$$$$$$$\".     `$$$$l      `[$$$$$$$$$$$$$$$$}  .(BI           
:::            ._%)` }$$$$$$$$$$$$$$$$$$*|_I:c$$$$W;;~)v@$$$$$$$$$$$$$$$$$r '-%).            
:::              ._8n,iB$$$$$$$$$$$$$$$$$$$$$%cuuc&$$$$$$$$$$$$$$$$$$$$$$?"/B{'              
:::                 ^}*n8$$$$$$$$$$$$$$$$$$$$n+. i/$$$$$$$$$$$$$$$$$$$$Bu#(,                 
:::                    ',-t#$$$$$$$$$$$$$$$$$$$#v$$$$$$$$$$$$$$$$$$$Wj[:'                    
:::                          .'`",:;;;::x$$$$$$$$$$$$$$*;::;;:,"^`.                          
:::                                      `]&$$$$$$$$B(^                                      
:::                                         ^]M$$8)"                                         
:::                                            ..                                            
                                                                                          
:::                                    Fennecdeer Creative                                                                                          
                                                                                                                                            
                                                                                        