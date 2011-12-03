import unittest
import os, sys, shutil, re

sys.path.insert(0, os.path.abspath(os.path.abspath(__file__ )+ "/../../../"))

import tracks

from tracks.tests.test_config import TRACKS_URL, TRACKS_USERNAME, TRACKS_PASSWORD

from mock import Mock, patch

def mock_net_request(request_string, func):
  with patch.object(os, 'popen') as mock_method:
    class MockFileObject():
      def read(self):
        return request_string 
    mock_method.return_value = MockFileObject()
    func()

class TestTracksClient(unittest.TestCase):

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
When the user fills in one of the three corp_landing forms, SugarCRM gets updated with lead information
</description>
<id type="integer">1</id>
<last-reviewed type="datetime">2008-08-17T22:44:18-04:00</last-reviewed>
<name>corp_landing form project</name>
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

  def test_setOptions(self):
    self.client.setOptions({'url' : TRACKS_URL, 
      'username' : TRACKS_USERNAME, 'password' : TRACKS_PASSWORD})
    with self.assertRaises(RuntimeError) as cm:
      self.client.setOptions({'url' : TRACKS_URL})
    with self.assertRaises(RuntimeError) as cm:
      self.client.setOptions({'url' : TRACKS_URL, 
        'username' : TRACKS_USERNAME})

  def test_loginErrorHandling(self):
    with self.assertRaises(RuntimeError) as cm:
      self.client.getRawTodos()
    self.client.setOptions({'url' : TRACKS_URL, 
      'username' : TRACKS_USERNAME + 'wrong', 
      'password' : TRACKS_PASSWORD + 'wrong'})

    def try_to_get_todos():
      self.client.getRawTodos()

    with self.assertRaises(RuntimeError) as cm:
      mock_net_request('Login unsuccessful.', try_to_get_todos)

  def test_getRawTodos(self):
    self.client.setOptions({'url' : TRACKS_URL, 'username' : TRACKS_USERNAME, 'password' : TRACKS_PASSWORD})

    def get_raw_todos():
      self.assertRegexpMatches(self.client.getRawTodos(), r'<todo>')

    mock_net_request(self.todos_xml, get_raw_todos)

  def test_getTodos(self):
    self.client.setOptions({'url' : TRACKS_URL, 'username' : TRACKS_USERNAME, 'password' : TRACKS_PASSWORD})
    def get_todos():
      self.assertTrue(isinstance(self.client.getTodos(), list))
    mock_net_request(self.todos_xml, get_todos)

  def test_getRawContexts(self):
    self.client.setOptions({'url' : TRACKS_URL, 'username' : TRACKS_USERNAME, 'password' : TRACKS_PASSWORD})
    def get_contexts():
      self.assertRegexpMatches(self.client.getRawContexts(), r'<context>')
    mock_net_request(self.contexts_xml, get_contexts)

  def test_getContexts(self):
    self.client.setOptions({'url' : TRACKS_URL, 'username' : TRACKS_USERNAME, 'password' : TRACKS_PASSWORD})

    def get_contexts():
      self.assertTrue(isinstance(self.client.getContexts(), list))
    mock_net_request(self.contexts_xml, get_contexts)

  def test_getRawProjects(self):
    self.client.setOptions({'url' : TRACKS_URL, 'username' : TRACKS_USERNAME, 'password' : TRACKS_PASSWORD})

    def get_projects():
      self.assertRegexpMatches(self.client.getRawProjects(), r'<project>')
    mock_net_request(self.projects_xml, get_projects)

  def test_getProjects(self):
    self.client.setOptions({'url' : TRACKS_URL, 'username' : TRACKS_USERNAME, 'password' : TRACKS_PASSWORD})

    def get_projects():
      self.assertTrue(isinstance(self.client.getProjects(), list))
    mock_net_request(self.projects_xml, get_projects)

  def test_addProject(self):
    self.client.setOptions({'url' : TRACKS_URL, 'username' : TRACKS_USERNAME, 'password' : TRACKS_PASSWORD})
    def add_project():
      self.client.addProject({'name' : 'Foo'})
    mock_net_request(self.projects_xml, add_project)


if __name__ == '__main__':
  unittest.main()
