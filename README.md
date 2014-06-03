web2py.dev_plugin_dataTables
============================

This web2py application is intended to be a demo application for "plugin_dataTables".

It contains project files for a web2py plugin plus some demo models and controllers.

The "plugin_dataTables" is a web2py framwork plugin[1] with the aim of an easier
integration of the jQuery[2] plugin DataTables[3] in order to use the advanced
DataTables interface options to browse data coming from every database query.

Installation steps
==================

1. Clone the repository

    $ git clone git@github.com:manuelep/web2py.app_plugin_dataTables.git app_plugin_dataTables

2. Pull and checkout into the branch containing DataTables as submodule

    $ cd app_plugin_dataTables/
    $ git branch -v
    $ git pull origin DataTables
    $ git checkout DataTables

3. Init and update the DataTable submodule

    $ git submodule init
    $ git submodule update

4. BAck to the branch master

    $ git checkout master

Footnote:
---------

[1] http://web2py.com/books/default/chapter/29/12/components-and-plugins#Plugins
[2] http://jquery.com/
[3] http://datatables.net/
