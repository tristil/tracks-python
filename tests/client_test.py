import unittest
import os, sys, shutil, re

sys.path.insert(0, os.path.abspath(os.path.abspath(__file__ )+ "/../../../"))

import tracks

from tracks.tests.test_config import TRACKS_URL, TRACKS_USERNAME, TRACKS_PASSWORD

class TestTracksClient(unittest.TestCase):
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
    with self.assertRaises(RuntimeError) as cm:
      self.client.getRawTodos()

  def test_getRawTodos(self):
    self.client.setOptions({'url' : TRACKS_URL, 'username' : TRACKS_USERNAME, 'password' : TRACKS_PASSWORD})
    self.assertRegexpMatches(self.client.getRawTodos(), r'<todo>')

  def test_getTodos(self):
    self.client.setOptions({'url' : TRACKS_URL, 'username' : TRACKS_USERNAME, 'password' : TRACKS_PASSWORD})
    self.assertTrue(isinstance(self.client.getTodos(), list))

  def test_getRawContexts(self):
    self.client.setOptions({'url' : TRACKS_URL, 'username' : TRACKS_USERNAME, 'password' : TRACKS_PASSWORD})
    self.assertRegexpMatches(self.client.getRawContexts(), r'<context>')

  def test_getContexts(self):
    self.client.setOptions({'url' : TRACKS_URL, 'username' : TRACKS_USERNAME, 'password' : TRACKS_PASSWORD})
    self.assertTrue(isinstance(self.client.getContexts(), list))

  def test_getRawProjects(self):
    self.client.setOptions({'url' : TRACKS_URL, 'username' : TRACKS_USERNAME, 'password' : TRACKS_PASSWORD})
    self.assertRegexpMatches(self.client.getRawProjects(), r'<project>')

  def test_getProjects(self):
    self.client.setOptions({'url' : TRACKS_URL, 'username' : TRACKS_USERNAME, 'password' : TRACKS_PASSWORD})
    self.assertTrue(isinstance(self.client.getProjects(), list))


if __name__ == '__main__':
  unittest.main()
