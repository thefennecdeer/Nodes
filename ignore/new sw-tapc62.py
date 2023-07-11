'''Computer Node Wifi Wake'''

### Libraries required by this Node
import java.lang.System
import subprocess



### Parameters used by this Node
system = java.lang.System.getProperty('os.name')
arch = java.lang.System.getProperty('sun.arch.data.model').lower()



### Functions used by this Node
def shutdown():
  if(system=="Windows 7" or system=="Windows 8" or system=="Windows 10"):
    # shutdown WIN
    returncode = subprocess.call("rundll32.exe powrprof.dll,SetSuspendState 0,1,0", shell=True)
  elif(system=="Mac OS X"):
    # shutdown OSX
    # nodel process must have sudo rights to shutdown command
    returncode = subprocess.call("sudo shutdown -h -u now", shell=True)
  else:
    print 'unknown system: ' + system

def restart():
  if(system=="Windows 7" or system=="Windows 8" or system=="Windows 10"):
    # restart WIN
    returncode = subprocess.call("shutdown -r -f -t 0", shell=True)
  elif(system=="Mac OS X"):
    # restart OSX
    returncode = subprocess.call("sudo shutdown -r now", shell=True)
  else:
    print 'unknown system: ' + system

def mute():
  if(system=="Windows 7" or system=="Windows 8" or system=="Windows 10"):
    returncode = subprocess.call("nircmd"+arch+".exe mutesysvolume 1", shell=True)
  elif(system=="Mac OS X"):
    returncode = subprocess.call("osascript -e 'set volume output muted true'", shell=True)
  else:
    print 'unknown system: ' + system

def unmute():
  if(system=="Windows 7" or system=="Windows 8" or system=="Windows 10"):
    returncode = subprocess.call("nircmd"+arch+".exe mutesysvolume 0", shell=True)
    print returncode
  elif(system=="Mac OS X"):
    returncode = subprocess.call("osascript -e 'set volume output muted false'", shell=True)
  else:
    print 'unknown system: ' + system

def set_volume(vol):
  if(system=="Windows 7" or system=="Windows 8" or system=="Windows 10"):
    winvol = (65535/100)*vol
    returncode = subprocess.call("nircmd"+arch+".exe setsysvolume "+str(winvol), shell=True)
  elif(system=="Mac OS X"):
    returncode = subprocess.call("osascript -e 'set volume output volume "+str(vol)+"'", shell=True)
    # raspberry pi volume: "amixer cset numid=1 -- 20%"
    # returncode = subprocess.call("amixer cset numid=1 -- "+str(vol)+"%", shell=True)
  else:
    print 'unknown system: ' + system



### Local actions this Node provides
def local_action_PowerOff(arg = None):
  """{"title":"PowerOff","desc":"Turns this computer off.","group":"Power"}"""
  print 'Action PowerOff requested'
  shutdown()

def local_action_Restart(arg = None):
  """{"title":"Restart","desc":"Restarts this computer.","group":"Power"}"""
  print 'Action Restart requested'
  restart()

def local_action_MuteOn(arg = None):
  """{"title":"MuteOn","desc":"Mute this computer.","group":"Volume"}"""
  print 'Action MuteOn requested'
  lookup_local_action("Muting").call("On")

def local_action_MuteOff(arg = None):
  """{"title":"MuteOff","desc":"Un-mute this computer.","group":"Volume"}"""
  print 'Action MuteOff requested'
  lookup_local_action("Muting").call("Off")

def local_action_SetVolume(arg = None):
  """{"title":"SetVolume","desc":"Set volume.","schema":{"title":"Drag slider to adjust level.","type":"integer","format":"range","min": 0, "max": 100,"required":"true"},"group":"Volume"}"""
  print 'Action SetVolume requested - '+str(arg)
  set_volume(arg)

### Mute Injection 2023

local_event_Muting = LocalEvent({'group': 'Mute', 'order': next_seq(), 'schema': {'type': 'string', 'enum': ['On', 'Off']}}) 
def local_action_Muting(arg=None): 

  '''{"group": "Mute", "schema": {"type": "string", "enum": ["On", "Off"]}}'''   

  if arg == 'On': 
    Mute.call(True)
   # PUT ACTUAL MUTE ON CODE HERE, CHECK PRE-EXISTING ACTIONS 

  elif arg == 'Off': 
    Mute.call(False)
    # PUT ACTUAL MUTE OFF CODE HERE, CHECK PRE-EXISTING ACTIONS 

# This gets us most of the way there, but if you press the mute-on or mute-off buttons, it wont update our new action/event 

# so find where the two OLD mute actions are defined, and make it call our new action 

# so something like: 


def local_action_MuteOn(arg=None): 
  lookup_local_action("Muting").call('On') 

   

# and for the mute off  

  

def local_action_MuteOff(arg=None): 

  lookup_local_action("Muting").call('Off') 

  local_event_Mute = LocalEvent({ 'group': 'Volume', 'order': next_seq(), 'schema': { 'type': 'boolean' }})

@local_action({ 'group': 'Mute', 'order': next_seq(), 'schema': { 'type': 'boolean' } })
def Mute(arg):
    console.info('Mute %s action' % arg)

    # some of this for backwards compatibility
    if arg in [ True, 1, 'On', 'ON', 'on' ]:
        mute()
    elif arg in [ False, 0, 'Off', 'OFF', 'off']:
        unmute()
    else:
        console.warn('Mute: arg missing')
        return
    
  
DEFAULT_FREESPACEMB = 0.5
param_FreeSpaceThreshold = Parameter({'title': 'Freespace threshold (GB)', 'schema': {'type': 'integer', 'hint': DEFAULT_FREESPACEMB}})

local_event_Status = LocalEvent({'group': 'Status', 'order': next_seq(), 'schema': {'type': 'object', 'properties': {
        'level': {'type': 'integer', 'order': 1},
        'message': {'type': 'string', 'order': 2}}}})

from java.io import File

def check_status():
  # unfortunately this pulls in removable disk drives
  # roots = list(File.listRoots())
  
  roots = [File('.')] # so just using current drive instead
  
  warnings = list()
  
  roots.sort(lambda x, y: cmp(x.getAbsolutePath(), y.getAbsolutePath()))
  
  for root in roots:
    path = root.getAbsolutePath()
    
    total = root.getTotalSpace()
    free = root.getFreeSpace()
    usable = root.getUsableSpace()
    
    if free < (param_FreeSpaceThreshold or DEFAULT_FREESPACEMB)*1024*1024*1024L:
      warnings.append('%s has less than %0.1f GB left' % (path, long(free)/1024/1024/1024))
      
  if len(warnings) > 0:
    local_event_Status.emit({'level': 2, 'message': 'Disk space is low on some drives: %s' % (','.join(warnings))})
    
  else:
    local_event_Status.emit({'level': 0, 'message': 'OK'})

Timer(check_status, 150, 10) # check status every 2.5 mins (10s first time)
      
### Main
def main(arg = None):
  # Start your script here.
  print 'Nodel script started.'
