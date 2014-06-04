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

from plugin_dataTables import DataTables, json_to_query
from json import dumps as jsdumps
from json import loads as jsloads


dataTables = DataTables()

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

    if not dtname in dataTables:
        raise HTTP(400, "Oggetto '%s' non definito." % dtname)

    default_params.update(kw)

    sEcho = int(default_params.get('sEcho')) or 0

    iSortingCols = int(default_params.get('iSortingCols')) \
        or len([k for k,j in default_params.items() \
            if k.startswith('iSortCol_')])

    mCol = [(k,v) for k,v in default_params.items() if k.startswith('mData')]

    dt = dataTables[dtname]

    # WARNING: needs tests
    orderby = None
    for n in range(iSortingCols):
        index = int(default_params['iSortCol_%s' % n])
        if default_params.get('sSortDir_%s' % n) in ('desc',):
            orderby_i = ~dt.fields[index]
        else:
            orderby_i = dt.fields[index]
        if orderby is None:
            orderby = orderby_i
        else:
            orderby |= orderby_i
    dt.selection_vars['orderby'] = orderby

    Min = 0 if not default_params.get('iDisplayStart') else int(default_params.get('iDisplayStart'))
    Len = default_params.get('iDisplayLength')
    Max = None if not Len else Min + int(Len)
    dt.selection_vars['limitby'] = None if not Max else (Min, Max, )

    query = dt.query
    if '_query' in kw:
        query &= json_to_query(db, kw['_query'])

    dbset = dt.db(query)
    res = dbset.select(*dt.selection_args, **dt.selection_vars)

    aaData = []
    if len(dt.tables)==1:
        for n,row in enumerate(res):
            aaData.append({})
            for k,v in row.as_dict().items():
                if not dt.table is None and k in dt.table.fields:
                    field = dt.table[k]
                    if not field.represent is None:
                        rendered = field.represent(v, row)
                    else:
                        rendered = v
                else:
                    rendered = v
                aaData[n][k] = rendered

    else:
        for n,row in enumerate(res):
            aaData.append({})

            for tabname, values in row.as_dict().items():
                for field_name, field_value in values.items():
                    if not dt.table is None and field_name in dt.table.fields:
                        field = dt.table[field_name]
                    else:
                        field = db[tabname]

            nrow = dict(sum(map(lambda d: d.items(), row.as_dict().values()), []))
            for k,v in nrow.items():
                if not dt.table is None and k in dt.table.fields:
                    field = dt.table[k]
                    if not field.represent is None:
                        rendered = field.represent(v, nrow)
                    else:
                        rendered = v
                else:
                    rendered = v
                    guess_field = [f for f in dt.fields if f.name==k]
                    if len(guess_field)>0:
                        field = guess_field[0]
                        if not field.represent is None:
                            rendered = field.represent(v, nrow)

                aaData[n][k] = rendered

    iTotalRecords = '%s' % dt.db(dt.query, ignore_common_filters=True).count()
    iTotalDisplayRecords = '%s' % dbset.count()

    out = {
        "sEcho": sEcho,
        "iTotalRecords": iTotalRecords,
        "iTotalDisplayRecords": iTotalDisplayRecords,
        "aaData": aaData
    }

    return out