web2py.dev_plugin_dataTables
============================

This web2py application is intended to be a demo application for "plugin_dataTables".

It contains project files for a web2py plugin plus some demo models and controllers.

The "plugin_dataTables" is a [web2py framwork plugin][] with the aim of an easier
integration of the [jQuery][] plugin [DataTables][] in order to use the advanced
DataTables interface options to browse data coming from any database query.

Installation steps
==================

#### 1. Clone the repository


```sh
git clone git@github.com:manuelep/web2py.app_plugin_dataTables.git app_plugin_dataTables
```

#### 2. Pull and checkout into the branch containing DataTables as submodule

```sh
cd app_plugin_dataTables/
git branch -v
git pull origin DataTables
git checkout DataTables
```

#### 3. Init and update the DataTable submodule

```sh
git submodule init
git submodule update
```

#### 4. Back to the branch master

```sh
git checkout master
```

Plugin integration in applications
==================================

In order to adopt this plugin in other web2py applications, after installing this
whole application, you can use the web2py admin interface to download the plugin
package and upload the files in your app.

[web2py framwork plugin]: http://web2py.com/books/default/chapter/29/12/components-and-plugins#Plugins
[jQuery]: http://jquery.com/
[DataTables]: http://datatables.net/
