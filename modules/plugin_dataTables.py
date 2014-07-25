#!/usr/bin/env python
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

from gluon import *
from gluon.storage import Storage
import collections
from json import loads as jsloads

from gluon.dal import Field, FieldVirtual

plugin_name = 'plugin_dataTables'

jspaths = (
    URL('static', plugin_name+'/DataTables/media/css/jquery.dataTables.css'),
    URL('static', plugin_name+'/css/dataTables.custom.css'),
    #URL('static', plugin_name+'/DataTables/media/js/jquery.js'),
    URL('static', plugin_name+'/DataTables/media/js/jquery.dataTables.js'),
)

class DataTable(object):
    """ """

    def __init__(self, table, id='mytable', query=None, lang=None):

        self.id = id
        self.db = table._db
        self.table = table
        self.lang = lang
        if query is None and table._tablename in self.db.tables:
            self.query = table.id>0
        elif not query is None:
            self.query = query
        else:
            raise ValueError("A query has to be specified")
        self._conf_columns()
        self.configure()

    def __iter__(self):
        """ """
        for f in  self.table:
            yield f.name, f
        for k, f in self.table.items():
            if not k.startswith('_') and isinstance(f, FieldVirtual):
                yield f.name, f

    def items(self):
        return [i for i in self]

    def __getitem__(self, k):
        """ maybe an odd definition """
        if isinstance(k, int):
            return self.scolumns[k][1]
        else:
            return self.kcolumns[k]

    def _conf_columns(self):
        self.scolumns = self.items()
        self.kcolumns = dict(self.scolumns)

    def dbset(self, query=None, **kw):
        if query is None:
            query = self.query
        else:
            query = self.query & query
        return self.db(query, **kw)

    def select(self, query=None, **kw):
        return self.dbset(query).select(self.table.ALL, **kw)

    def _aoColumns(self, *aos, **owrs):
        """Should be used for internal purposes.
        Returns the value for the aoColumns parameter.
        aos  {dict}: list of dictionaries which mandatory keys are "name", "label";
        owrs {dict}: (overwrites) keyed dictionaries with the same mandatory key as above.
        """
        
        def _aoColumn(_, field):
            if field.name in owrs:
                custom = owrs.get(field.name)
                if not 'name' in custom:
                    custom['name'] = field.name
            else:
                custom = {}

            defaults = {
                "mData": field.name,
                "sName": field.name,
                "sTitle": str(field.label),
                "bVisible": field.readable,
                "bSortable": isinstance(field, Field) and field.type not in ('json', ),
            }
            # TODO: gestire meglio la colonna info
            if field.name=='info':
                defaults["class"] = 'details-control'
            return dict(defaults, **custom)
        
        return map(lambda c: _aoColumn(*c), self)

    def configure(self, **kw):
        """ Setup the configuration """
        
        aoColsSetup = {} if not 'aoColumns' in kw else kw.pop('aoColumns')
        
        defaults = dict( 
            sAjaxSource = URL(plugin_name, 'ajax', extension='json', args=(self.id, )),
            aoColumns = self._aoColumns(**aoColsSetup)
        )
        if not self.lang is None:
            defaults['oLanguage'] = {"sUrl": URL('static', plugin_name, 'dataTables.%s.txt' % self.lang)}

        self.attributes = dict(defaults, **kw)

    def html(self, **kw):
        """ """
        colspan = len(self.attributes['aoColumns'])
        default = {
            "web2py_grid": dict(_class="web2py_grid"),
            "web2py_table": dict(_class="web2py_table"),
            self.id: dict(_class="display", _id=self.id, _style="width: 100%"),
            "empty_td": dict(_colspan=colspan, _class="dataTables_empty")
        }
        pars = deep_update(default, kw)
        msg = "Loading data from server... please wait"
        return DIV(
            DIV(
                TABLE(
                    TBODY(TR(TD(msg, **pars["empty_td"]))),
                    **pars[self.id]
                ),
                **pars["web2py_table"]
            ),
            **pars["web2py_grid"]
        )

# Coutesy of: http://stackoverflow.com/questions/3232943/update-value-of-a-nested-dictionary-of-varying-depth
def deep_update(d, u):
    for k, v in u.iteritems():
        if isinstance(v, collections.Mapping):
            r = deep_update(d.get(k, {}), v)
            d[k] = r
        else:
            d[k] = u[k]
    return d

# Courtesy of: http://www.web2pyslices.com/slice/show/1593/class-for-building-db-queries-from-python-dictionaries
class QueryParser(object):
    """ This class is intended as an interface for reading queries submitted
    via json or other client protocols
    """

    def __init__(self, db):
        self.dquery = None
        self._db = db

    def parse(self, dquery):
        self.dquery = dquery
        return self.build(self.dquery)

    def build(self, d):
        op, first, second = (d["op"], d["first"],
                             d.get("second", None))
        built = None
        db = self._db

        if op in ("AND", "OR"):
            if not (type(first), type(second)) == (dict, dict):
                raise SyntaxError("Invalid AND/OR query")
            if op == "AND":
                built = self.build(first) & self.build(second)
            else: built = self.build(first) | self.build(second)

        elif op == "NOT":
            if first is None:
                raise SyntaxError("Invalid NOT query")
            built = ~self.build(first)
        else:
            # normal operation (GT, EQ, LT, ...)
            if isinstance(second, dict) and "tablename" in second:
                right = db[second["tablename"]][second["fieldname"]]
            else: right = second
            left = db[first["tablename"]][first["fieldname"]]

            if op == "EQ": built = left == right
            elif op == "NE": built = left != right
            elif op == "GT": built = left > right
            elif op == "GE": built = left >= right
            elif op == "LT": built = left < right
            elif op == "LE": built = left <= right
            elif op == "CONTAINS": built = left.contains(right)
            elif op == "BELONGS": built = left.belongs(right)
            else: raise SyntaxError("Operator not supported")

        return built

def json_to_query(db, obj):
    if isinstance(obj, basestring):
        obj = jsloads(obj)
    return QueryParser(db).parse(obj)
