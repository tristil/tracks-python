import os, urllib, urllib2, sys, base64
from xml.dom import minidom
from pipes import quote

# A client for the Tracks API
class TracksClient:
  todos = []
  contexts = []
  projects = []

  verbose = False

  def __init__(self, options = None):
    if isinstance(options, dict):
      self.setOptions(options)

    if options and 'verbose' in options and options['verbose'] == True:
      self.verbose =  True

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
      # add node to self.todos list, e.g.
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

  def addProject(self, data):
    self.projects_url = self.getTracksUrl('project') 

    xml = '<project>'
    if 'name' in data:
      xml += '<name>' + data['name'] + '</name>'
    xml += '</project>'

    self.makeRequest(self.projects_url, 'post', xml)
    self.checkAuthenticated()
    return self.raw_response

  def addContext(self, data):
    self.contexts_url = self.getTracksUrl('context') 

    xml = '<context>'
    if 'name' in data:
      xml += '<name>' + data['name'] + '</name>'
    xml += '</context>'

    self.makeRequest(self.contexts_url, 'post', xml)
    self.checkAuthenticated()
    return self.raw_response

  def addTodo(self, data):
    self.todos_url = self.getTracksUrl('todo') 
    xml = '<todo>'
    if 'description' in data:
      xml += '<description>' + data['description'] + '</description>'

    if 'project' in data:
      for project in self.projects:
        if project['name'] == data['project']:
          xml += '<project_id>' + project['id'] + '</project_id>'
          break
    if 'context' in data:
      for context in self.contexts:
        if context['name'] == data['context']:
          xml += '<context_id>' + context['id'] + '</context_id>'
          break
    xml += '</todo>'
    self.makeRequest(self.todos_url, 'post', xml)
    self.checkAuthenticated()
    return self.raw_response


  def makeRequest(self, url, method = 'get', xml = None):
    request = urllib2.Request(url)
    request.add_header('Content-Type', 'text/xml')
    base64string = base64.encodestring('%s:%s' % (self.username, self.password))[:-1]
    request.add_header("Authorization", "Basic %s" % base64string)

    handle = None
    try:
      handle = urllib2.urlopen(request, data = xml)
    except IOError, e:
      print e
      print "Failed to connect to remote Tracks instance " + url

    self.raw_response = handle.read()

    return self.raw_response
