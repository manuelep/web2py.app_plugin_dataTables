# coding: utf8
# prova qualcosa come

@service.json
@auth.requires(request.client=='127.0.0.1', requires_login=True)
def ajax():
    """ The data source controller for ajax DataTables """
    dtname = request.args(-1)
    kw = request.vars
    return _ajax(dtname, **kw)