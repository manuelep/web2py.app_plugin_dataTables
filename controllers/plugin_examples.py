# coding: utf8

from plugin_dataTables import jspaths, plugin_name

@auth.requires_login()
def rpadroni():

    query = db.rpadroni.id>10

    # (Optional) Define a query filter
    dataTables.rpadroni._setAttributes(sAjaxSource = URL(
        plugin_name, 'ajax', extension='json', 
        args=('rpadroni', ), 
        vars=dict(_query=query.as_json()))
    )

    # 1. Load the necessary js libs
    for lib in jspaths: response.files.append(lib)
    # 2. Define parameters for the js namespace
    plugin_dataTables = dict(
        rpadroni = dataTables.rpadroni.attributes
    )

    return dict(rpadroni=dataTables.rpadroni.get_html(), plugin_dataTables=plugin_dataTables)

@auth.requires_login()
def myjoin():

    # 1. Load the necessary js libs
    for lib in jspaths: response.files.append(lib)
    # 2. Define parameters for the js namespace
    plugin_dataTables = dict(
        myjoin = dataTables.myjoin.attributes
    )

    return dict(myjoin=dataTables.myjoin.get_html(), plugin_dataTables=plugin_dataTables)

