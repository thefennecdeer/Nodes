'''This node pulls down the latest offical Nodel recipes. It is automatically created for convenience on first run and can be safely deleted or disabled once in production. Please see console and script for more information.'''

GREETING = '''

This node clones the official nodel-recipes repository at: 
- github.com/museumsvictoria/github

Once cloned, new nodes can be easily created or updated based on the latest recipes.

Deleting this node does not delete the actual recipes repository.

This node will refresh the recipes repository every 72 hours (differences only).

'''

console.warn(GREETING)

from org.nodel.jyhost import NodelHost
from org.eclipse.jgit.api import Git
from java.io import File
from java.net import Proxy, ProxySelector, SocketAddress, InetSocketAddress, URI
from java.util import Arrays, List


DEFAULT_NAME = "nodel-official-recipes"
DEFAULT_URI = "https://github.com/museumsvictoria/nodel-recipes"
param_repository = Parameter({'title': 'Repository','order': 1, 'schema': {'type': 'object', 'properties': {
        'name': {'type': 'string', 'hint': DEFAULT_NAME, 'order': 1},
        'uri': {'type': 'string', 'hint': DEFAULT_URI, 'order': 2}
}}})

param_proxy = Parameter({'title': 'Proxy','order': 2, 'schema': {'type': 'object', 'properties': {
        'address': {'title': 'Address', 'hint': '0.0.0.0', 'type': 'string', 'order': 1},
        'port': {'title': 'Port','hint': '3128', 'type': 'integer', 'order': 2},
        'useProxy': {'title': 'Use Proxy?', 'type': 'boolean', 'order': 3}
}}})


# sync every 72 hours, first after 10 seconds
Timer(lambda: lookup_local_action("SyncNow").call(), 72*3600, 10)

# the internet address
uri = DEFAULT_URI

# the nodel-recipes repo folder
folder = File(NodelHost.instance().recipes().getRoot(), DEFAULT_NAME)

# java subclass for selecting proxy, Jgit does NOT obey system proxies!!!
class GitProxySelector(ProxySelector):
  def __init__(self, newProxy):
    self.newProxy = newProxy
  # pattern matching for 
  def select(self, uri):
    if "github.com" in uri.getHost().lower():
      return Arrays.asList(self.newProxy)
    else:
      return Arrays.asList(Proxy.NO_PROXY)
  def connectFailed(uri, sa, ioe):
    if (uri == None or sa == None or ioe == None):
      console.error("Arguments can not be null.")

def configureProxy():
  if param_proxy != None:
    if param_proxy.get('useProxy') == True:
      address = param_proxy.get('address')
      port = param_proxy.get('port')
      if address != '' or port != None:
        # create a java proxy object with the parameters
        console.log("Use Proxy")
        proxy = Proxy(Proxy.Type.HTTP, InetSocketAddress(address, port))
      else:
        console.error('Proxy is ticked, but values aren\'t valid!')
        return # abort start
    else:
      # java remembers the proxy, we need to put it back to a direct connection
      proxy = Proxy.NO_PROXY
  else:
    # java remembers the proxy, we need to put it back to a direct connection
    proxy = Proxy.NO_PROXY
    
  ProxySelector.setDefault(GitProxySelector(proxy)) 

def main():
  if param_repository != None:
    global uri, folder

    uri = param_repository.get('uri') or DEFAULT_URI
    name = param_repository.get('name') or DEFAULT_NAME
    folder = File(NodelHost.instance().recipes().getRoot(), name)
 
  configureProxy()
  console.info('Clone and pull folder: "%s"' % folder.getAbsolutePath())
  #nodetoolkit.getHttpClient().setProxy("136.154.22.600:3128", None, None)

def local_action_SyncNow(arg=None):
  sync()

def sync():
  clone_if_necessary()
  pull()
  
def clone_if_necessary():
  if folder.exists():
    return
  
  console.info("Cloning %s..." % uri)
  
  try:
    git = None
    
    cmd = Git.cloneRepository()
    cmd.setURI(uri)
    cmd.setDirectory(folder)
    git = cmd.call()
    
    console.info("Cloning finished")
    
  finally:
    if git != None: git.close()
    
def pull():
  if not folder.exists():
    console.warn('repo folder does not exist; yet to clone or network issues?')
  
  console.info("Pulling repository...")
  
  try:
    git = None
    git = Git.open(folder)
    
    git.pull().call()
    
    console.info("Pull finished")
    
  finally:
    if git != None: git.close()
