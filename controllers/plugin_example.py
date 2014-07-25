# -*- coding: utf-8 -*-

from plugin_dataTables import jspaths, plugin_name

# @auth.requires_login()
def example1():

    # 1. Load the necessary js libs
    for lib in jspaths: response.files.append(lib)
    # 2. Define parameters for the js namespace
    dataTables = {mytable1.id: mytable1.attributes}

    return dict(rpadroni=mytable1.html(), plugin_dataTables=dataTables)

def example2():

    # 1. Load the necessary js libs
    for lib in jspaths: response.files.append(lib)
    # 2. Define parameters for the js namespace
    dataTables = {mytable2.id: mytable2.attributes}

    return dict(rpadroni=mytable2.html(), plugin_dataTables=dataTables)