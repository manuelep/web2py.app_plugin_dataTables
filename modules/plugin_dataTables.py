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
from storage import Storage
from gluon.dal import Query, Table, Field, FieldMethod, FieldVirtual, SQLALL
from json import loads as jsloads

plugin_name = 'plugin_dataTables'

jspaths = (
    URL('static', plugin_name+'/DataTables/media/css/jquery.dataTables.css'),
    URL('static', plugin_name+'/css/dataTables.custom.css'),
    #URL('static', plugin_name+'/DataTables/media/js/jquery.js'),
    URL('static', plugin_name+'/DataTables/media/js/jquery.dataTables.js'),
)

class DataTables(Storage):
    """ The DataTables container """

    def add(self, name, *args, **kw):
        """ Define new DataTable objects inside DataTables name space
        name {string}
        table {DAL/Table}
        lang {string}
        """
        # 1. Object definition
        self[name] = DataTable(name, *args, **kw)
        # 2. DataTables Attributes setting
        self[name]._setAttributes()

    def add_by_query(self, name, query, *args, **kw):
        """ Define new DataTable objects inside DataTables name space
        name {string}
        table {DAL/Query}
        table {DAL/Table}
        lang {string}
        """
        table = None if not 'table' in kw else kw.pop('table')
        lang = None if not 'lang' in kw else kw.pop('lang')
        # 1. Object definition
        self[name] = DataTable(name, table, lang)
        # 2. Load selection attributes and variables
        self[name].selection(query, *args, **kw)
        # 3. DataTables Attributes setting
        self[name]._setAttributes()

class DataTable(object):
    """ The DataTable object class """

    attributes = {
        "bJQueryUI": True,
        "sPaginationType": "full_numbers",
        "bFilter": False,
        "bProcessing": True,
        "bServerSide": True,
    }

    def __init__(self, id, table=None, lang=None):
        """ """
        self.id = id
        self.db = None
        self.table = table
        self.lang = lang
        self.tables = set()
        self.fields = []
        #self.virtual_fields = []
        self.selection_vars = {}
        self.selection_args = []

        if not table is None and table._tablename in table._db.tables and table._actual:
            self.selection(self.table.id>0, self.table.ALL)

    def selection(self, query, *fields, **kw):
        """ """
        self.query = query
        self.selection_vars = kw

        def _appendfield(field):
            if self.db is None and hasattr(field, '_db'):
                self.db = field._db
            if hasattr(field, '_table'):
                self.tables.add(field._table)
            if isinstance(field, (Field, FieldVirtual, )):
                self.fields.append(field)
            else:
                # what else?!?
                pass

        for field in fields:

            self.selection_args.append(field)
            if isinstance(field, SQLALL):
                for ff in field._table.fields:
                    _appendfield(field._table[ff])
                # Virtual fields
                for k,ff in filter(lambda c: isinstance(c[1], FieldVirtual), field._table.items()):
                    _appendfield(ff)
            else:
                _appendfield(field)

        self.attributes["aoColumns"] = self.aoColumns()

    def _setAttributes(self, name=None, **kw):
        """ """
        if not "oLanguage" in self.attributes and not "oLanguage" in kw and not self.lang is None:
            kw["oLanguage"] = {"sUrl": URL('static', plugin_name, 'dataTables.%s.txt' % self.lang)}
        if not "aoColumns" in kw and not self.attributes.get("aoColumns"):
            kw["aoColumns"] = self.aoColumns()
        if not "sAjaxSource" in self.attributes and not "sAjaxSource" in kw:
            kw["sAjaxSource"] = URL(plugin_name, 'ajax', extension='json', args=(name or self.id, ))
        self.attributes = dict(self.attributes, **kw)

    def aoColumns(self, **kw):
        """ """
        def _aoColumn(field):
            custom = kw.get(field.name) or {}
            defaults = {
                "mData": field.name,
                "sName": field.name,
                "sTitle": str(field.label),
                "bVisible": field.readable,
                "bSortable": isinstance(field, Field) and field.type not in ('json', ),
            }
            # TODO: gestire meglio la colonna info
            if field.name == 'info':
                defaults["class"] = 'details-control'
            return dict(defaults, **custom)

        fields = self.fields
        return map(_aoColumn, fields)

    def get_html(self, **kw):
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