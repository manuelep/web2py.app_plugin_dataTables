# coding: utf8

##### ~ LICENCE NOTES ~ ########################################################
#
#    This file is part of plugin_dataTables.
#
#    plugin_dataTables is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    plugin_dataTables is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with plugin_dataTables. If not, see <http://www.gnu.org/licenses/>.
#
################################################################################

from plugin_dataTables import DataTable, json_to_query
from gluon.storage import Storage
from json import dumps as jsdumps
from json import loads as jsloads

def _ajax(dtname, **kw):
    """ Helper function for the ajax source controller """

    default_params = {
        'sEcho':0,
        #'iColumns':5,
        #'sColumns':
        'iDisplayStart':1,
        #'iDisplayLength':10,
        #mDataProp_0:engine
        #mDataProp_1:browser
        #mDataProp_2:platform
        #mDataProp_3:version
        #mDataProp_4:grade
        #sSearch:
        #bRegex:false
        #sSearch_0:
        #bRegex_0:false
        #bSearchable_0:true
        #...
        #'iSortCol_0':0
        #'sSortDir_0':asc
        'iSortingCols':0,
        #bSortable_0:true
        #...
    }

    dt = globals().get(dtname)
    if dt is None: raise HTTP(400, T("Table with name '%(dtname)s not recognized.'") % locals())

    default_params.update(kw)

    sEcho = int(default_params.get('sEcho')) or 0

    iSortingCols = int(default_params.get('iSortingCols')) \
        or len([k for k,j in default_params.items() \
            if k.startswith('iSortCol_')])

    mCol = [(k,v) for k,v in default_params.items() if k.startswith('mData')]

    # WARNING: needs tests
    orderby = None
    for n in range(iSortingCols):
        index = int(default_params['iSortCol_%s' % n])
        if default_params.get('sSortDir_%s' % n) in ('desc',):
            orderby_i = ~dt[index]
        else:
            orderby_i = dt[index]
        if orderby is None:
            orderby = orderby_i
        else:
            orderby |= orderby_i
    
    selection_vars = dict()
    selection_vars['orderby'] = orderby

    Min = 0 if not default_params.get('iDisplayStart') else int(default_params.get('iDisplayStart'))
    Len = default_params.get('iDisplayLength')
    Max = None if not Len else Min + int(Len)
    selection_vars['limitby'] = None if not Max else (Min, Max, )

    if '_query' in kw:
        query = json_to_query(db, kw['_query'])
    else:
        query = None

    res = dt.select(query, **selection_vars)
    aaData = []
    for row in res:
        data = {}
        for k,v in filter(lambda c: not callable(c[1]), row.items()):
            if not dt[k].represent is None:
                data[k] = dt[k].represent(v, row)
            else:
                data[k] = v
        aaData.append(data)

    iTotalRecords = '%s' % dt.dbset(ignore_common_filters=True).count()
    iTotalDisplayRecords = '%s' % dt.dbset(query).count()

    out = {
        "sEcho": sEcho,
        "iTotalRecords": iTotalRecords,
        "iTotalDisplayRecords": iTotalDisplayRecords,
        "aaData": aaData
    }

    return out
