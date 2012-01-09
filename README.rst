What Is It?
-----------
This is a simple Python client library for accessing a Tracks installation
(`Tracks <https://github.com/TracksApp/tracks>`_ GTD todo list web application)

This library was developed in conjunction with the `todo.txt-python library <https://github.com/tristil/todo.txt-python>`_,
for interfacing with local todo.txt files, and is included as a sub-project in the 
`Tracks-Sync extension <https://github.com/tristil/Todo.txt-Tracks-Sync>`_ for todo.txt.

Major caveats for using this library are:

* It may not see much more active development.
* I don't understand relative module inclusion in Python very well. There's a
  lot of appending the path of the parent directory to the paths list.

Usage
-----

::

  # Instantiate the client
  client = TracksClient() 

  # Set connection options
  client.setOptions({'url' : 'http://tracks.example.com', 'username' : 'username', 'password' : 'password'})

  # Get the objects from the server
  todos = client.getTodos()
  contexts = client.getContexts()
  projects = client.getProjects()

  # Add objects to the server
  client.addContext({'name' : 'Foo'})
  client.addProject({'name' : 'Foo'})
  client.addTodo({
        'description' : 'Thing to Do', 
        'context' : 'work',
        'project' : 'bigproject', 
        }
      )

Feedback
--------
If somebody actually has a use for this library and has additional
requirements/ bugs / patches, go ahead and submit them as Github issues and I
will respond to them as quickly as possible.
