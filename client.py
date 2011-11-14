import os
from xml.dom import minidom

# A client for the Tracks API
class TracksClient:
  todos = []
  contexts = []
  projects = []

  def __init__(self, options = None):
    if isinstance(options, dict):
      self.setOptions(options)

  def setOptions(self, options):
    for value in ['url', 'username', 'password']:
      if value not in options:
        raise RuntimeError('Must supply ' + value)
      else:
        setattr(self, value, options[value])

  def getTracksUrl(self, type = 'todo'):
    for value in ['url', 'username', 'password']:
      try:
        getattr(self, value)
      except:
        raise RuntimeError(value + ' is not set')
    if type == 'todo':
      return self.url + "/todos.xml"
    elif type == 'context':
      return self.url + "/contexts.xml"
    elif type == 'project':
      return self.url + "/projects.xml"


  def checkAuthenticated(self):
    if self.raw_response.strip() == "Login unsuccessful.":
      raise RuntimeError('Login unsuccessful.')

  def getProjects(self):
    self.getRawProjects()
    self.parseProjects()
    return self.projects

  def parseProjects(self):
    self.parseXml('project')

  def getContexts(self):
    self.getRawContexts()
    self.parseContexts()
    return self.contexts

  def parseContexts(self):
    self.parseXml('context')

  def getContextById(self, id):
    for context in self.contexts:
      if context['id'] == id:
        return context
    return False

  def getProjectById(self, id):
    for project in self.projects:
      if project['id'] == id:
        return project
    return False


  def parseTodos(self):
    self.parseXml('todo')
    for todo in self.todos:
      if 'context-id' in todo:
        context = self.getContextById(todo['context-id'])
        if context:
          todo['context'] = context['name']

      if 'project-id' in todo:
        project = self.getProjectById(todo['project-id'])
        if project:
          todo['project'] = project['name']


  def parseXml(self, type):
    setattr(self, type + 's', [])

    response_xml = minidom.parseString(self.raw_response)
    elements = response_xml.getElementsByTagName(type)
    for element in elements:
      item  = {}
      for node in element.childNodes:
        if node.nodeName != '#text':
          if len(node.childNodes) > 0:
            innerHTML = node.childNodes[0].nodeValue
            item[node.nodeName] = innerHTML
      getattr(self, type + 's').append(item)

  def getTodos(self):
    self.getContexts()
    self.getProjects()
    self.getRawTodos()
    self.parseTodos()
    return self.todos

  def getRawTodos(self):
    self.todos_url = self.getTracksUrl('todo') 
    self.makeRequest(self.todos_url)
    self.checkAuthenticated()
    return self.raw_response

  def getRawContexts(self):
    self.contexts_url = self.getTracksUrl('context') 
    self.makeRequest(self.contexts_url)
    self.checkAuthenticated()
    return self.raw_response

  def getRawProjects(self):
    self.projects_url = self.getTracksUrl('project') 
    self.makeRequest(self.projects_url)
    self.checkAuthenticated()
    return self.raw_response

  def makeRequest(self, url):
    authentication = '-u' + self.username + ':' + self.password
    stdout_handle = os.popen("curl --silent " + authentication + " " + url, 'r')
    self.raw_response = stdout_handle.read()
    return self.raw_response
