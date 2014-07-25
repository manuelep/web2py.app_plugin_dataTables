# coding: utf8

from gluon.custom_import import track_changes; track_changes(True)
from plugin_DataTables import DataTable
from gluon.contrib.populate import populate

extended_dal = False
try:
    from plugin_dal_extensions.dalp import DALplus
except ImportError:
    edb = db
else:
    try:
        edb = DALplus('postgres:psycopg2://postgres:postgres@localhost:5432/plugin_datatables_2',pool_size=1,check_reserved=['all'])
    except:
        edb = db
    else:
        extended_dal = True

edb.define_table("padroni",
    Field('first_name'),
    Field('last_name'),
)

edb.define_table("animali",
    Field('pet_name', represent=lambda v, _: v.upper()),
    Field('padrone', 'reference padroni', requires=IS_IN_DB(db, 'padroni.id', '%(last_name)s')),
)

if extended_dal:
    join_query = (edb.padroni.id==edb.animali.padrone)
    
    edb.create_view('pvsa', join_query,
        edb.animali.id,
        edb.animali.pet_name.with_alias('pname'),
        edb.padroni.first_name.with_alias('fname'),
        edb.padroni.last_name.with_alias('lname'),
    #   comment in the next line every time you change this query
    #     replace = True
    )
    
    edb.define_view('pvsa',
        Field('fname', label=T("master first name")),
        Field('lname', label=T("master last name")),
        Field('pname', label=T("Pet name")),
        Field.Virtual('vtest', lambda r: XML(A(I(_class="icon icon-ok"), _class="btn"))),
    )

# Popuate example tables
for table_name in ('padroni', 'animali', ):
    if edb(edb[table_name].id>0).count()==0:
        for i in range(2):
            populate(edb[table_name], 100)
            db.commit()

mytable1 = DataTable(edb.padroni, id='mytable1')
if extended_dal:
    mytable2 = DataTable(edb.pvsa, id='mytable2')

# Shortcut menu to the example controller function

example_menu = [(T('simple table'), False, URL('plugin_example', 'example1'), )]
if extended_dal:
    example_menu.append((T('view'), False, URL('plugin_example', 'example2'), ))

response.menu += [
    (T('Examples'), False, None, example_menu, )
]