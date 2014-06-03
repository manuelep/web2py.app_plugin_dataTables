# coding: utf8
# prova qualcosa come

from plugin_dataTables import jspaths, plugin_name

def index(): return dict(message="hello from examples.py")

@auth.requires_login()
def rpadroni():

    query = db.rpadroni.id>10

    dataTables.rpadroni._setAttributes(sAjaxSource = URL(
        plugin_name, 'ajax', extension='json', 
        args=('rpadroni', ), 
        vars=dict(_query=query.as_json()))
    )

    # 1. load the necessary js libs
    for lib in jspaths: response.files.append(lib)
    # 2. define parameters in namespace
    plugin_dataTables = dict(
        rpadroni = dataTables.rpadroni.attributes
    )

    return dict(rpadroni=dataTables.rpadroni.get_html(), plugin_dataTables=plugin_dataTables)

@auth.requires_login()
def myjoin():

    # 1. load the necessary js libs
    for lib in jspaths: response.files.append(lib)
    # 2. define parameters in namespace
    plugin_dataTables = dict(
        myjoin = dataTables.myjoin.attributes
    )

    return dict(myjoin=dataTables.myjoin.get_html(), plugin_dataTables=plugin_dataTables)

