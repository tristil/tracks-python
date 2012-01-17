import os, urllib, urllib2, sys, base64, re
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

  def getTracksUrl(self, type = 'todo', id = None):
    for value in ['url', 'username', 'password']:
      try:
        getattr(self, value)
      except:
        raise RuntimeError(value + ' is not set')
    if type == 'todo':
      if id:
        return self.url + "/todos/" + id + ".xml"
      else:
        return self.url + "/todos.xml"
    elif type == 'done_todo':
      return self.url + "/todos/done.xml"
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

  def parseDoneTodos(self):
    self.parseXml('done_todo')
    for todo in self.todos:
      if 'context-id' in todo:
        context = self.getContextById(todo['context-id'])
        if context:
          todo['context'] = context['name']

      if 'project-id' in todo:
        project = self.getProjectById(todo['project-id'])
        if project:
          todo['project'] = project['name']

      self.todos.append(todo)

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
    self.getRawDoneTodos()
    self.parseDoneTodos()

    return self.todos

  def getRawTodos(self):
    self.todos_url = self.getTracksUrl('todo') 
    self.makeRequest(self.todos_url)
    self.checkAuthenticated()
    return self.raw_response

  def getRawDoneTodos(self):
    self.done_todos_url = self.getTracksUrl('done_todo') 
    self.makeRequest(self.done_todos_url)
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


  def buildXml(self, todo):
    xml = '<todo>'
    if todo.getDescription() != None:
      xml += '<description>' + todo.getDescription() + '</description>'

    if todo.getProject() != None:
      if todo.getProject()  == 'default':
        xml += '<project_id>1</project_id>'
      else:
        for project in self.projects:
          if project['name'] == todo.getProject():
            xml += '<project_id>' + project['id'] + '</project_id>'
            break

    if todo.getContext() != None:
      if todo.getContext() == 'default':
        xml += '<context_id>1</context_id>'
      else:
        for context in self.contexts:
          if context['name'] == todo.getContext():
            xml += '<context_id>' + context['id'] + '</context_id>'
            break

    if todo.isDone() == True:
      xml += '<state>completed</state>'
      xml += "<completed-at type='datetime'>"+ todo.getCompletedDate() + 'T00:00:00Z'+"</completed-at>"

    xml += '</todo>'
    xml = unicode(xml).encode('unicode_escape')
    return xml

  def updateTodo(self, todo):
    if self.verbose:
      print "Updating todo: "
      print todo

    self.todos_url = self.getTracksUrl('todo', todo.getTracksId()) 
    xml = self.buildXml(todo)
    self.makeRequest(self.todos_url, 'put', xml)
    self.checkAuthenticated()

    return True

  def addTodo(self, todo):
    if self.verbose:
      print "Adding todo: "
      print todo

    self.todos_url = self.getTracksUrl('todo') 

    xml = self.buildXml(todo)
    
    self.makeRequest(self.todos_url, 'post', xml)
    self.checkAuthenticated()
    pattern = r'\/todos\/(\d+)'
    m = re.search(pattern, self.raw_response_headers.get('Location'))
    if m and m.group(1):
      tracks_id = m.group(1)
    else:
      tracks_id = None

    return tracks_id 


  def makeRequest(self, url, method = 'get', xml = None):
    request = urllib2.Request(url)
    request.add_header('Content-Type', 'text/xml')
    base64string = base64.encodestring('%s:%s' % (self.username, self.password))[:-1]
    request.add_header("Authorization", "Basic %s" % base64string)

    if method == 'put':
      request.get_method = lambda : 'PUT'

    if self.verbose:
      print "Requesting url " + url
      if xml:
        print "Sending xml payload: \n" + xml

    handle = None
    try:
      handle = urllib2.urlopen(request, data = xml)
    except IOError, e:
      if e.code == 201:
        handle = e
      else:
        print e
        print "Failed to connect to remote Tracks instance " + url

    self.raw_response = handle.read()
    self.raw_response_headers = handle.info()

    return self.raw_response
