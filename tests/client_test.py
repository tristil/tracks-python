import unittest
import os, sys, shutil, re, urllib2

sys.path.insert(0, os.path.abspath(os.path.abspath(__file__ )+ "/../../../"))

import tracks

from mock import Mock, patch

class TestTracksClient(unittest.TestCase):

  def mock_net_request(self, response_string, func, expected_post_data = None):
    with patch.object(urllib2, 'urlopen') as mock_method:
      class MockFileObject():
        call_count = 0
        def read(self):
          if isinstance(response_string, list):
            response = response_string[self.call_count]
            self.call_count += 1
            return response
          else:
            return response_string 
      mock_method.return_value = MockFileObject()
      func()

    if expected_post_data:
      last_call = mock_method.call_args_list[-1]
      self.assertEqual(expected_post_data, last_call[1])

  todos_xml = """\
<todos type="array">
<todo>
<completed-at type="datetime" nil="true"/>
<context-id type="integer">2</context-id>
<created-at type="datetime">2011-03-16T22:30:20-04:00</created-at>
<description>Add task text to Chromodoro</description>
<due type="datetime" nil="true"/>
<id type="integer">293</id>
<notes/>
<project-id type="integer">25</project-id>
<recurring-todo-id type="integer" nil="true"/>
<show-from type="datetime" nil="true"/>
<state>active</state>
<updated-at type="datetime">2011-03-16T22:30:20-04:00</updated-at>
<tags type="array"/>
</todo>
<todo>
<completed-at type="datetime" nil="true"/>
<context-id type="integer">2</context-id>
<created-at type="datetime">2011-03-15T00:26:15-04:00</created-at>
<description>Fix retrieve password scenarios</description>
<due type="datetime" nil="true"/>
<id type="integer">292</id>
<notes>1) When username doesn't exist 2) Labels fade out?</notes>
<project-id type="integer">23</project-id>
<recurring-todo-id type="integer" nil="true"/>
<show-from type="datetime" nil="true"/>
<state>active</state>
<updated-at type="datetime">2011-03-16T22:29:54-04:00</updated-at>
<tags type="array">
<tag>
<created-at type="datetime">2010-11-15T00:22:57-05:00</created-at>
<id type="integer">19</id>
<name>coding</name>
<updated-at type="datetime">2010-11-15T00:22:57-05:00</updated-at>
</tag>
</tags>
</todo>
</todos>
"""

  contexts_xml = """\
<contexts type="array">
<context>
<created-at type="datetime">2008-08-17T22:47:05-04:00</created-at>
<hide type="boolean">false</hide>
<id type="integer">1</id>
<name>work</name>
<position type="integer">1</position>
<updated-at type="datetime">2008-08-17T22:47:05-04:00</updated-at>
</context>
<context>
<created-at type="datetime">2008-08-17T22:56:22-04:00</created-at>
<hide type="boolean">false</hide>
<id type="integer">2</id>
<name>home</name>
<position type="integer">2</position>
<updated-at type="datetime">2008-08-17T22:56:22-04:00</updated-at>
</context>
</contexts>
"""

  projects_xml = """\
<projects type="array">
<project>
<completed-at type="datetime">2009-01-04T21:53:59-05:00</completed-at>
<created-at type="datetime">2008-08-17T22:44:18-04:00</created-at>
<default-context-id type="integer" nil="true"/>
<default-tags nil="true"/>
<description>
A big project
</description>
<id type="integer">1</id>
<last-reviewed type="datetime">2008-08-17T22:44:18-04:00</last-reviewed>
<name>bigproject</name>
<position type="integer">1</position>
<state>completed</state>
<updated-at type="datetime">2009-01-04T21:53:59-05:00</updated-at>
</project>
<project>
<completed-at type="datetime" nil="true"/>
<created-at type="datetime">2009-10-29T22:32:21-04:00</created-at>
<default-context-id type="integer" nil="true"/>
<default-tags nil="true"/>
<description nil="true"/>
<id type="integer">17</id>
<last-reviewed type="datetime">2009-10-29T22:32:21-04:00</last-reviewed>
<name>Backup</name>
<position type="integer">1</position>
<state>active</state>
<updated-at type="datetime">2010-11-15T00:45:55-05:00</updated-at>
</project>
</projects>
"""

  def setUp(self):
    self.client = tracks.TracksClient()
    self.maxDiff = None

  def setupOptions(self):
    self.client.setOptions({'url' : 'http://tracks.example.com', 'username' : 'username', 'password' : 'password'})

  def test_addDoneTodo(self):
    self.setupOptions()
    def add_todo():
      self.client.getContexts()
      self.client.getProjects()
      tracks_id = self.client.addTodo({
        'description' : 'Thing to Do', 
        'context' : 'work',
        'project' : 'bigproject', 
        'done' : True, 
        'completed' : '2011-10-30'
        }
      )
      self.assertEqual('201',tracks_id)


    expected_xml_payload = {'data' : "<todo><description>Thing to Do</description><project_id>1</project_id><context_id>1</context_id><status>completed</status><completed-at type='datetime'>2011-10-30T00:00:00Z</completed-at></todo>" }

    add_todo_response = """\
HTTP/1.1 201 Created
Location: http://tracks.example.com/todos/201.xml
"""
    self.mock_net_request([self.contexts_xml, self.projects_xml, add_todo_response], add_todo, expected_xml_payload)

  def test_addTodo(self):
    self.setupOptions()
    def add_todo():
      self.client.getContexts()
      self.client.getProjects()
      self.client.addTodo({
        'description' : 'Thing to Do', 
        'context' : 'work',
        'project' : 'bigproject', 
        }
      )
    expected_xml_payload = {'data' : "<todo><description>Thing to Do</description><project_id>1</project_id><context_id>1</context_id></todo>" }
    self.mock_net_request([self.contexts_xml, self.projects_xml, ""], add_todo, expected_xml_payload)

  def test_setOptions(self):
    self.setupOptions()
    with self.assertRaises(RuntimeError) as cm:
      self.client.setOptions({'url' : 'http://tracks.example.com'})
    with self.assertRaises(RuntimeError) as cm:
      self.client.setOptions({'url' : 'http://tracks.example.com', 
        'username' : 'username'})

  def test_loginErrorHandling(self):
    with self.assertRaises(RuntimeError) as cm:
      self.client.getRawTodos()
    self.client.setOptions({'url' : 'http://tracks.example.com', 
      'username' : 'username' + 'wrong', 
      'password' : 'password' + 'wrong'})
    def try_to_get_todos():
      self.client.getRawTodos()
    with self.assertRaises(RuntimeError) as cm:
      self.mock_net_request('Login unsuccessful.', try_to_get_todos)

  def test_getRawTodos(self):
    self.setupOptions()
    def get_raw_todos():
      self.assertRegexpMatches(self.client.getRawTodos(), r'<todo>')
    self.mock_net_request(self.todos_xml, get_raw_todos)

  def test_getTodos(self):
    self.setupOptions()
    def get_todos():
      self.assertTrue(isinstance(self.client.getTodos(), list))
    self.mock_net_request(self.todos_xml, get_todos)

  def test_getRawContexts(self):
    self.setupOptions()
    def get_contexts():
      self.assertRegexpMatches(self.client.getRawContexts(), r'<context>')
    self.mock_net_request(self.contexts_xml, get_contexts)

  def test_getContexts(self):
    self.setupOptions()
    def get_contexts():
      self.assertTrue(isinstance(self.client.getContexts(), list))
    self.mock_net_request(self.contexts_xml, get_contexts)

  def test_getRawProjects(self):
    self.setupOptions()
    def get_projects():
      self.assertRegexpMatches(self.client.getRawProjects(), r'<project>')
    self.mock_net_request(self.projects_xml, get_projects)

  def test_getProjects(self):
    self.setupOptions()

    def get_projects():
      self.assertTrue(isinstance(self.client.getProjects(), list))
    self.mock_net_request(self.projects_xml, get_projects)

  def test_addProject(self):
    self.setupOptions()
    def add_project():
      self.client.addProject({'name' : 'Foo'})
    expected_xml = 'http://tracks.example.com/projects.xml -d "<project><name>Foo</name></project>"'
    self.mock_net_request(self.projects_xml, add_project)

  def test_addContext(self):
    self.setupOptions()
    def add_project():
      self.client.addContext({'name' : 'Foo'})
    expected_xml = 'http://tracks.example.com/contexts.xml -d "<context><name>Foo</name></context>"'
    self.mock_net_request(self.projects_xml, add_project)

if __name__ == '__main__':
  unittest.main()
