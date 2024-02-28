''' 
##### **Quest 2 App Node:** _Learning Studio Flavour_  <sup>v3.5.2</sup> 

___

_Requires [ADB Platform Tools](https://developer.android.com/tools/releases/platform-tools) to be installed at either `C:/content/` or an otherwise specified location in the node config._

Based on regular app node - but will only launch the application once both **the Headset is detected as a device by the computer**, and **the computer is detected as a valid Quest Link target by the headset.**
Will quit and restart application upon re-connection.

If Quest Link is unable to be launched, the headset will restart and begin the process again. 

Things included with this flavour:

* "Nodes to Trigger" - Tell another application/node to do something once this node's application has actually launched. In this case, we are telling it the table to launch the main .bat script, which is tied to the "MainStart" action.

_Use the `Jump Controls` group of actions to skip past the wait screen!_

'''
from time import sleep
import itertools
from org.nodel.core import BindingState

# <parameters ---
param_PowerStateOnStart = Parameter({'title': 'Running state on Node Start','order': next_seq(), 'schema': {'type': 'string', 'enum': ['On', 'Off', '(previous)']},
                                     'desc': 'What "power" state to start up in when the node itself starts, typically on boot'})

param_members = Parameter({'title': 'Nodes to trigger', 'order': next_seq(), 'schema': {'type': 'array', 'items': {'type': 'object', 'properties': {
   'name': {'title': 'Simple name (can assume context)', 'type': 'string', 'order': 1}
    }}
}})

param_ToolPath = Parameter({'title': 'ADB Platform Tools Path (ONLY SET IF THEY HAVE BEEN MOVED FROM C:\Content!)', 'order': next_seq(), 'required': True, 'schema': {'type': 'string', 'hint': '(e.g. "C:\Content\platform-tools")'},
                           'desc': 'The full path to the USB ADB platform-tools'})

param_AppPath = Parameter({'title': 'App. Path (required, executable name with or without path)', 'order': next_seq(),'required': True, 'schema': {'type': 'string', 'hint': '(e.g. "C:\\MyApps\\myapp.exe" or "somethingOnThePath.exe")'},
                           'desc': 'The full path to the application executable'})

param_AppArgs = Parameter({'title': 'App. Args', 'order': next_seq(), 'schema': {'type': 'string', 'hint': 'e.g. --color BLUE --title What\'s\\ Your\\ Story? --subtitle \"Autumn Surprise!\"'},
                           'desc': 'Application arguments, space delimeted, backslash-escaped'})

param_AppWorkingDir = Parameter({'title': 'App. Working Dir.', 'order': next_seq(), 'schema': {'type': 'string', 'hint': 'e.g. c:\\temp'},
                                 'desc': 'Full path to the working directory'})

param_FeedbackFilters = Parameter({'title': 'Console Feedback filters','order': next_seq(), 'schema': {'type': 'array', 'items': {'type': 'object', 'properties': {
                                     'type': {'type': 'string', 'enum': ['Include', 'Exclude'], 'order': 1},
                                     'filter': {'type': 'string', 'order': 2}}}}})



# --->


# <signals ---

local_event_Running = LocalEvent({'group': 'Monitoring', 'schema': {'type': 'string', 'enum': ['On', 'Off']},
                                  'desc': 'Locks to the actual running state of the application process'})

local_event_DesiredPower = LocalEvent({'group': 'Power', 'schema': {'type': 'string', 'enum': ['On', 'Off']},
                                       'desc': 'The desired "power" (or running state), set using the action'})

local_event_Power = LocalEvent({'group': 'Power', 'schema': {'type': 'string', 'enum': ['On', 'Partially On', 'Off', 'Partially Off']},
                                'desc': 'The "effective" power state using Nodel power conventions taking into account actual and desired'})

local_event_LastStarted = LocalEvent({'group': 'Monitoring', 'schema': {'type': 'string'}, # holds dates
                                      'desc': 'The last time the application started'}) 

local_event_FirstInterrupted = LocalEvent({'group': 'Monitoring', 'schema': {'type': 'string'}, # holds dates
                                           'desc': 'The first time the process was "interrupted" (meaning it died prematurely)'})

local_event_LastInterrupted = LocalEvent({'group': 'Monitoring', 'schema': {'type': 'string'}, # holds dates
                                           'desc': 'The last time the process was "interrupted" (meaning it died/stopped prematurely)'})


local_event_QuestLinkStatus = LocalEvent({'group': '', 'schema': {'type': 'string', 'enum': ['On', 'Off',]},
                                'desc': 'The status of the Quest Link connection'})


local_event_HeadsetConnectionStatus = LocalEvent({'group': '', 'schema': {'type': 'string', 'enum': ['On', 'Off',]},
                                'desc': 'The status of the physical headset connection'})

local_event_Battery = LocalEvent({'schema': {'type': 'string'}, 
                                           'desc': 'Current Battery Level'})

local_event_SerialNumber = LocalEvent({'group' : 'Headset Info','order': next_seq(),'schema': {'type': 'string'}, 
                                           'desc': 'Serial Number of headset'})
local_event_OSVersion = LocalEvent({'group' : 'Headset Info','order': next_seq(),'schema': {'type': 'string'}, 
                                           'desc': 'Current OS version'})

# ensure these signals aggressively persist their values 
# (by default Nodel is very relaxed which is not ideal for clients that may deal with more interruptions)

def initMember(memberInfo):
  name = mustNotBeBlank('name', memberInfo['name'])                        
  disappears = memberInfo.get('disappears')
  isGroup = memberInfo.get('isGroup')
  
  create_remote_action('Member %s On' % (name), {'title': '"%s" On' % (name), 'group': 'Members Restart'}, suggestedNode=name, suggestedAction="PowerOn")
  create_remote_action('Member %s Off' % (name), {'title': '"%s" Off' % (name), 'group': 'Members Restart'}, suggestedNode=name, suggestedAction="PowerOff")
  nodestotrigger.append(create_remote_action('Member %s Launch Main' % (name), {'title': '"%s" Launch Main' % (name), 'group': 'Members Restart'}, suggestedNode=name, suggestedAction="MainStart"))

  def default_handler(arg):
    
      #lookup_remote_action('"%s" %s' % (name),  
    lookup_remote_action('Member %s Launch Main' % (name)).call()
    #lookup_remote_action('Member %s Off' % (name)).call()
    #call(lambda: lookup_remote_action('Member %s On' % (name)).call(),5)

  def basic_meta(name, state):
    return {
      'title': '%s' % name,
      'order': next_seq()
    }  
  create_local_action(
    name='Table App Restart',
    metadata=basic_meta('Table App Restart', "Restart"),
    handler=default_handler
  )


@after_main
def ensurePersistSignals():
  def ensure(s): # variable capture requires separate function
    s.addEmitHandler(lambda arg: s.persistNow())
  
  for s in [ local_event_Running, local_event_DesiredPower, local_event_Power, 
             local_event_LastStarted, local_event_FirstInterrupted, local_event_LastInterrupted ]:
    ensure(s)

# --- signals>


# <main ---

import os    # path functions
import sys   # launch environment info

errmsg = []
timeouts = 0
QUESTTIMEOUT = 2

global questconnected
global nodestotrigger


_resolvedAppPath = None # includes entire path
_platformTools = None
isXRLaunched = False
questconnected = False
firstboot = True
nodestotrigger = []

def main():
  # App Path MUST be specified
  if is_blank(param_AppPath):
    console.error('No App. Path has been specified, nothing to do!')
    _process.stop()
    return
  if is_blank(param_ToolPath):
    console.info('ADB Platform Tools Path not set, presuming C:\content\platform-tools')
    global _platformTools
    _platformTools = "C:\\Content\\platform-tools\\" + "adb.exe"
    if not os.path.isfile(_platformTools):
      console.error('The ADB Platform Tools Path could not be found - [%s]' % _platformTools)
      return
  else:
    global _platformTools
    _platformTools = param_ToolPath + "adb.exe"
  # check if a full path has been provided i.e. does it contain a backslash "\" 
  if os.path.sep in param_AppPath: # e.g. 
    global _resolvedAppPath
    _resolvedAppPath = param_AppPath # use full path
    finishMain()
  for memberInfo in lookup_parameter('members') or []:
    initMember(memberInfo)
  else:
    # otherwise test the path using 'where.exe' (Windows) or 'which' (Linux)
    
    # e.g. > where notepad
    #      < C:\Windows\System32\notepad.exe
    #      < C:\Windows\notepad.exe

    def processFinished(arg):
      global _resolvedAppPath

      if arg.code == 0: # 'where.exe' succeeded
        paths = arg.stdout.splitlines()
        if len(paths or EMPTY) > 0:
          _resolvedAppPath  = paths[0]
        
      if is_blank(_resolvedAppPath):
        _resolvedAppPath = param_AppPath

      finishMain()

    # path not fully provided so use 'where' to scan PATH environment, (has to be done async)
    whereCmd = 'where' if os.environ.get('windir') else 'which'
    quick_process([ whereCmd, param_AppPath], finished=processFinished)

def finishMain():
  if not os.path.isfile(_resolvedAppPath):
    console.error('The App. Path could not be found - [%s]' % _resolvedAppPath)
    return
  
  # App Working Directory is optional
  if not is_blank(param_AppWorkingDir) and not os.path.isdir(param_AppWorkingDir):
    console.error('The App. working directory was specified but could not be found - [%s]' % param_AppWorkingDir)
    return

  # if not os.path.isfile()

  # recommend that the process sandbox is used if one can't be found

  # later versions of Nodel have the sandbox embedded (dynamically compiled)
  usingEmbeddedSandbox = False
  try:
    from org.nodel.toolkit.windows import ProcessSandboxExecutable
    usingEmbeddedSandbox = True
  except:
    usingEmbeddedSandbox = False

  if not usingEmbeddedSandbox and os.environ.get('windir') and not (os.path.isfile('ProcessSandbox.exe') or os.path.exists('%s\\ProcessSandbox.exe' % sys.exec_prefix)):
    console.warn('-- ProcessSandbox.exe NOT FOUND BUT RECOMMENDED --')
    console.warn('-- It is recommended the Nodel Process Sandbox launcher is used on Windows --')
    console.warn('-- The launcher safely manages applications process chains, preventing rogue or orphan behaviour --')
    console.warn('--')
    console.warn('-- Use Nodel jar v2.2.1.404 or later OR download ProcessSandbox.exe asset manually from https://github.com/museumsvictoria/nodel/releases/tag/v2.1.1-release391 --')
    
  # ready to start, dump info
    
  console.info('This node will issue a warning status if it detects application interruptions i.e. crashing or external party closing it (not by Node)')
  if usingEmbeddedSandbox:
    console.info('(embedded Process Sandbox detected and will be used)')

  # start the list with the application path
  cmdLine = [ _resolvedAppPath ]
  
  # turn the arguments string into an array of args
  if not is_blank(param_AppArgs):
    cmdLine.extend(decodeArgList(param_AppArgs))

  # use working directory is specified
  if not is_blank(param_AppWorkingDir):
    _process.setWorking(param_AppWorkingDir)    

  _process.setCommand(cmdLine)
    
  console.info('Full command-line: [%s]' % ' '.join(cmdLine))
                  
  if param_PowerStateOnStart == 'On':
    lookup_local_action('Power').call('On')
  
  elif param_PowerStateOnStart == 'Off':
    lookup_local_action('Power').call('Off')

  else:
    if local_event_DesiredPower.getArg() != 'On':
      console.info('(desired power was previously off so not starting)')
      _process.stop()

    # otherwise process will start itself
def listDeviceOutput(arg):
  if len(arg.stdout.split()) > 4: #len counts from 1 
    console.info('Device Attached: %s' % arg.stdout.split()[4])
    local_event_SerialNumber.emit('%s' % arg.stdout.split()[4])
    global hasntdisconnected
    global questconnected
    questconnected = True
    hasntdisconnected = True
    local_event_HeadsetConnectionStatus.emit("On")
  else:
  # lookup_local_action('Power').call('Off')
    global hasntdisconnected
    global when
    local_event_HeadsetConnectionStatus.emit("Off")
    local_event_QuestLinkStatus.emit("Off")
    when = local_event_HeadsetConnectionStatus.getTimestamp().toString('E dd-MMM h:mm a')
    console.error("No Devices Connected!")
    hasntdisconnected = False

def Status_listDeviceOutput(arg):
  global hasntdisconnected
  if len(arg.stdout.split()) > 4: #len counts from 1 
    #console.info('Headset %s Found Again!' % arg.stdout.split()[4])
    global questconnected
    global firsttimedisconnect
    questconnected = True
    hasntdisconnected = True
    local_event_HeadsetConnectionStatus.emit("On")
    oculusCheck_timer.setInterval(10)
    linkCheck_timer.start()
  else:
    global questconnected
    local_event_HeadsetConnectionStatus.emit('Off')
    if hasntdisconnected == True:
      global when
      when = local_event_HeadsetConnectionStatus.getTimestamp().toString('E dd-MMM h:mm a')
      console.error("Lost connection to headset! Missing since: %s" % when)
      hasntdisconnected = False
    linkCheck_timer.stop()
    questconnected = False
    oculusCheck_timer.setInterval(5)

def firstCheckXRState(arg):
  if "FAILED" in arg.stdout:
    console.error("In a weird state! Rebooting Quest...")
    quick_process([_platformTools, 'reboot'])
  else:
    quick_process([_platformTools, 'shell "dumpsys activity activities | grep ResumedActivity"'], finished=firstLaunch)
    
def firstLaunch(arg):
  global questconnected
  lookup_local_action('DisableProximity').call()
  if "xrstreamingclient" in arg.stdout and questconnected == True:
    local_event_QuestLinkStatus.emit('On')
    isXRLaunched = True
    quick_process([_platformTools, 'shell "logcat -c; logcat -s VrApi -m 5 | grep FPS"'], timeoutInSeconds=5, finished=firstCheckFrames)
  else:
    lookup_local_action('EnableShell').call()
    LaunchLink.call()

def firstCheckFrames(arg):
  global timeouts
  if arg:
    if "FPS" in arg.stdout:
      trim = arg.stdout.split("FPS=", 1)[1].split("/", 1)[1].split(",")[0]
      if trim == "0":
        console.error("Quest Link in bad state! Rebooting Quest...")
        timeouts = 0
        quick_process([_platformTools, 'reboot'])
      else:
        console.log('Quest Link already on!')
        call(lambda: lookup_local_action('LaunchApp').call(),5)
  else:
    console.error("Quest Link in bad state! Rebooting Quest...")
    quick_process([_platformTools, 'reboot'])

# --- main>
def oculusStartup():
  quick_process([_platformTools, 'devices'], finished=listDeviceOutput)
  quick_process([_platformTools, 'shell "logcat -c && logcat xrstreamingclient -d | grep RPCServer"'], finished=firstCheckXRState) 
  
# ----- Custom Quest Actions, also available as Jump Controls ------

@local_action({'group': 'Jump Controls', 'title': 'Launch Quest Link', 'order': next_seq()})  
def LaunchLink():
  lookup_local_action('DisableProximity').call()
  console.info("Launching Quest Link")
  quick_process([_platformTools, 'shell am start -S com.oculus.xrstreamingclient/.MainActivity'])

    
@local_action({'group': 'Jump Controls', 'title': 'Launch Application', 'order': next_seq()})  
def LaunchApp():
  global firstboot
  failtest = False
  if local_event_DesiredPower.getArg() == 'On':
    for nodes in nodestotrigger:
      if nodes.getBindingState() != BindingState.Wired:
        failtest = True
    if failtest == False:
      lookup_local_action('DisableShell').call()
      lookup_local_action('KillShell').call()
      call(lambda: lookup_local_action('EnableProximity').call(),30)
      if firstboot == True:
        call(lambda: lookup_local_action('Table App Restart').call(),5)
        firstboot = False
      if local_event_Running.getArg() == 'Off':
         _process.start();
    else:
      console.error("Table not ready, make sure the Table PC is on/ready and the node is bound in config!")

                    
@local_action({'group': 'Jump Controls', 'title': 'Reboot Headset', 'order': next_seq()})  
def RebootHeadset():
  quick_process([_platformTools, 'reboot'])
  oculusCheck_timer.setInterval(10)
  call(lambda: oculusCheck_timer.start(),3)
  _process.stop()


@local_action({'group': 'Jump Controls', 'title': 'Kill Shell', 'order': next_seq()})  
def KillShell():
  quick_process([_platformTools, 'shell am force-stop com.oculus.vrshell'])

@local_action({'group': 'Jump Controls', 'title': 'Disable Shell', 'order': next_seq()})  
def DisableShell():
  quick_process([_platformTools, 'shell pm disable-user com.oculus.vrshell'])

@local_action({'group': 'Jump Controls', 'title': 'Enable Shell', 'order': next_seq()})  
def EnableShell():
  quick_process([_platformTools, 'shell pm enable com.oculus.vrshell'])
  quick_process([_platformTools, 'shell am start -S com.oculus.vrshell'])


@local_action({'group': 'Jump Controls', 'title': 'Disable Guardian', 'order': next_seq()})  
def DisableGuardian():
  quick_process([_platformTools, 'shell setprop debug.oculus.guardian_pause 1'])

@local_action({'group': 'Jump Controls', 'title': 'Disable Proximity', 'order': next_seq()})  
def DisableProximity():
  quick_process([_platformTools, 'shell am broadcast -a com.oculus.vrpowermanager.prox_close'])

@local_action({'group': 'Jump Controls', 'title': 'Enable Proximity', 'order': next_seq()})  
def EnableProximity():
  quick_process([_platformTools, 'shell am broadcast -a com.oculus.vrpowermanager.automation_disable'])


local_event_PowerOn = LocalEvent({ 'group': 'Power', 'title': 'On', 'order': next_seq(), 'schema': { 'type': 'boolean' }})

local_event_PowerOff = LocalEvent({ 'group': 'Power', 'title': 'Off', 'order': next_seq(), 'schema': { 'type': 'boolean' }})

@local_action({'group': 'Power', 'order': next_seq(), 'schema': {'type': 'string', 'enum': ['On', 'Off']},
               'desc': 'Also used to clear First Interrupted warnings'})
def Power(arg):
  # clear the first interrupted
  local_event_FirstInterrupted.emit('')
  if arg == 'On'and local_event_DesiredPower.getArg() == 'Off':
    local_event_DesiredPower.emit('On')
    #_process.start()
    oculusStartup()
    oculusCheck_timer.setInterval(10)
    linkCheck_timer.setInterval(10)
    oculusCheck_timer.start()
    linkCheck_timer.start()
  elif arg == 'Off':
    local_event_DesiredPower.emit('Off')
    oculusCheck_timer.stop()
    linkCheck_timer.stop()
    local_event_Running.emit('Off')
    _process.stop()
    global firstboot
    firstboot = True
    
@local_action({'group': 'Power', 'title': 'On', 'order': next_seq()})
def PowerOn():
  Power.call('On')
  
@local_action({'group': 'Power', 'title': 'Off', 'order': next_seq()})
def PowerOff():
  Power.call('Off')  


@before_main
def sync_RunningEvent():
  local_event_Running.emit('Off')
  local_event_HeadsetConnectionStatus.emit('Off')
  local_event_QuestLinkStatus.emit('Off')
    
def determinePower(arg):
  desired = local_event_DesiredPower.getArg()
  running = local_event_Running.getArg()
  
  if desired == None:      state = running
  elif desired == running: state = running
  else:                    state = 'Partially %s' % desired
    
  local_event_Power.emit(running)
  local_event_PowerOn.emit(running == 'On')
  local_event_PowerOff.emit(running == 'Off')
    
@after_main
def bindPower():
  local_event_Running.addEmitHandler(determinePower)
  local_event_DesiredPower.addEmitHandler(determinePower)
  
# --- power>


# <process ---

def process_started():
  console.info('application started!')
  local_event_Running.emit('On')
  local_event_LastStarted.emit(str(date_now()))
  
def process_stopped(exitCode):
  console.info('application stopped! exitCode:%s' % exitCode)
  
  nowStr = str(date_now()) # so exact timestamps are used
  
  if local_event_DesiredPower.getArg() == 'On':
    local_event_LastInterrupted.emit(nowStr)

    # timestamp 'first interrupted' ONCE
    if len(local_event_FirstInterrupted.getArg() or '') == 0:
      local_event_FirstInterrupted.emit(nowStr)
  
  local_event_Running.emit('Off')

# print out feedback from the console  
def process_feedback(line):
  inclusionFiltering = False
  
  keep = None
    
  for filterInfo in param_FeedbackFilters or []:
    filterType = filterInfo.get('type')
    ffilter = filterInfo.get('filter')
    matches = ffilter in line
      
    if filterType == 'Include':
      inclusionFiltering = True
      if matches:
        keep = True
          
    elif filterType == 'Exclude':
      if matches:
        keep = False

        
  if keep == None: # (not True or False)
    if not inclusionFiltering:
      # there are no Include filters in use so 'keep' defaults to True
      keep = True
      
    else:
      keep = False
  
  if keep:
    console.info('feedback> [%s]' % line)
    

_process = Process(None,
                  started=process_started,
                  stdout=process_feedback,
                  stdin=None,
                  stderr=process_feedback,
                  stopped=process_stopped)

# --->


# <status ---

local_event_Status = LocalEvent({'order': -100, 'group': 'Status', 'schema': {'type': 'object', 'properties': {
                                   'level': {'type': 'integer'},
                                   'message': {'type': 'string'}}}})


    
def isXRRunning(arg):
  global timeouts
  global questconnected
  if "xrstreamingclient" in arg.stdout:
    # verify that xrstreamingclient isnt stuck
    quick_process([_platformTools, 'shell "logcat -c && logcat xrstreamingclient -d | grep RPCServer"'], finished=checkXRState)
  elif questconnected == True:
    local_event_QuestLinkStatus.emit('Off')
    oculusCheck_timer.start()
    console.log("Haven't launched Quest Link, trying again...")
    #local_event_Running.emit('Off')
    #_process.stop()
    timeouts += 1
    LaunchLink.call()
    isXRLaunched = False
    if timeouts > QUESTTIMEOUT and isXRLaunched == False:
      console.error("Can't launch Quest Link! Rebooting Quest...")
      timeouts = 0
      quick_process([_platformTools, 'reboot'])
      #call(lambda: lookup_local_action('Power').call('On'), 35)
      #lookup_local_action('Power').call('Off')
  else:
    global questconnected
    questconnected = False
    console.log('Looking for Quest')
    timeouts = 0
    oculusCheck_timer.start()

def checkFrames(arg):
  global timeouts
  if arg:
    if "FPS" in arg.stdout:
      trim = arg.stdout.split("FPS=", 1)[1].split("/", 1)[1].split(",")[0]
      if trim == "0":
        console.error("Quest Link in bad state! Rebooting Quest...")
        timeouts = 0
        quick_process([_platformTools, 'reboot'])
      else:
        timeouts = 0
        call(lambda: lookup_local_action('LaunchApp').call(),10)
  else:
    console.error("Quest Link in bad state! Rebooting Quest...")
    timeouts = 0
    quick_process([_platformTools, 'reboot'])
   
    
def checkXRState(arg):
  global timeouts
  if "FAILED" in arg.stdout:
    console.error("Quest Link in bad state! Rebooting Quest...")
    timeouts = 0
    quick_process([_platformTools, 'reboot'])
  else:      
    oculusCheck_timer.stop()
    local_event_QuestLinkStatus.emit('On')
    isXRLaunched = True
    if local_event_Running.getArg() == "Off":
      _process.stop()
      quick_process([_platformTools, 'shell "logcat -c; logcat -s VrApi -m 5 | grep FPS"'], timeoutInSeconds=5, finished=checkFrames)

      
def getBatteryLevel(arg):
  if "level" in arg.stdout:
    local_event_Battery.emit('%s%%' % arg.stdout[9:])
    
def getOSVersion(arg):
  if arg.stdout != "":
    splitLines = arg.stdout.strip().split("=")
    local_event_OSVersion.emit('%s' % splitLines[1])

def linkCheck():
    quick_process([_platformTools, 'shell "dumpsys activity activities | grep ResumedActivity"'], finished=isXRRunning)
    quick_process([_platformTools, 'shell "dumpsys battery | grep level"'], finished=getBatteryLevel)
    quick_process([_platformTools, 'shell "dumpsys package com.oculus.vrshell | grep versionName"'], finished=getOSVersion)
    
def oculusCheck():
    quick_process([_platformTools, 'devices'], finished=Status_listDeviceOutput) 

def statusCheck():
  # recently interrupted
  now = date_now()
  nowMillis = now.getMillis()
  errmsg = []
  # check for recent interruption within the last 4 days (to incl. long weekends)
  firstInterrupted = date_parse(local_event_FirstInterrupted.getArg() or '1960')
  firstInterruptedDiff = nowMillis - firstInterrupted.getMillis()
 
  
  lastInterrupted = date_parse(local_event_LastInterrupted.getArg() or '1960')
  if local_event_DesiredPower.getArg() == "On":
    if local_event_HeadsetConnectionStatus.getArg() != 'On':
      global when
      errmsg.append('Quest is not connected to computer, since: %s' % when)
    elif local_event_QuestLinkStatus.getArg() != 'On':
      errmsg.append('Quest Link is not running')
    elif local_event_Running.getArg() != 'On':
      errmsg.append('Application not running')
      #console.error("Application not launched, check to see if the Oculus software on the computer is in a weird state!")
    if errmsg:
      combinederrmsg = ', '.join(errmsg)
      local_event_Status.emit({'level': 2, 'message' : '%s' % combinederrmsg})
    elif firstInterruptedDiff < 4*24*3600*1000L: # (4 days)
      if firstInterrupted == lastInterrupted:
         timeMsgs = 'last time %s' % toBriefTime(lastInterrupted)
      else:
        timeMsgs = 'last time %s, first time %s' % (toBriefTime(lastInterrupted), toBriefTime(firstInterrupted))
        local_event_Status.emit({'level': 1, 'message': 'Application interruptions may be taking place (%s)' % timeMsgs})
    else:
      local_event_Status.emit({'level': 0, 'message': 'OK'})
  
statusCheck_timer = Timer(statusCheck, 30)
linkCheck_timer = Timer(linkCheck, 10, stopped=True)
oculusCheck_timer = Timer(oculusCheck, 10, stopped=True)

# --->


# <--- convenience functions

# Converts into a brief time relative to now
def toBriefTime(dateTime):
  now = date_now()
  nowMillis = now.getMillis()

  diff = (nowMillis - dateTime.getMillis()) / 60000 # in minutes
  
  if diff == 0:
    return '<1 min ago'
  
  elif diff < 60:
    return '%s mins ago' % diff

  elif diff < 24*60:
    return dateTime.toString('h:mm:ss a')

  elif diff < 365 * 24*60:
    return dateTime.toString('h:mm:ss a, E d-MMM')

  elif diff > 10 * 365*24*60:
    return 'never'
    
  else:
    return '>1 year'


# Decodes a typical process arg list string into an array of strings allowing for
# limited escaping or quoting or both.
#
# For example, turns:
#    --name "Peter Parker" --character Spider\ Man

# into:
#    ['--name', '"Peter Parker"', '--character', 'Spider Man']   (Python list)
#
def decodeArgList(argsString):
  argsList = list()
  
  escaping = False
  quoting = False
  
  currentArg = list()
  
  for c in argsString:
    if escaping:
      escaping = False

      if c == ' ' or c == '"': # put these away immediately (space-delimiter or quote)
        currentArg.append(c)
        continue      
      
    if c == '\\':
      escaping = True
      continue
      
    # not escaping or dealt with special characters, can deal with any char now
    
    if c == ' ': # delimeter?
      if not quoting: 
        # hit the space delimeter (outside of quotes)
        if len(currentArg) > 0:
          argsList.append(''.join(currentArg))
          del currentArg[:]
          continue

    if c == ' ' and len(currentArg) == 0: # don't fill up with spaces
      pass
    else:
      currentArg.append(c)
    
    if c == '"': # quoting?
      if quoting: # close quote
        quoting = False
        argsList.append(''.join(currentArg))
        del currentArg[:]
        continue
        
      else:
        quoting = True # open quote
  
  if len(currentArg) > 0:
      argsList.append(''.join(currentArg))

  return argsList

def mustNotBeBlank(name, s):
  if isBlank(s):
    raise Exception('%s cannot be blank')

  return s

def isBlank(s):
  if s == None or len(s) == 0 or len(s.strip()) == 0:
    return True
  
def isEmpty(o):
  if o == None or len(o) == 0:
    return True
# convenience --->
