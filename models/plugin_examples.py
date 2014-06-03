# coding: utf8

from gluon.contrib.populate import populate

db.define_table("rpadroni",
    Field('first_name'),
    Field('last_name'),
    Field.Virtual('age', lambda row: 2)
)

db.define_table("ranimali",
    Field('pet_name', represent=lambda v, _: v.upper()),
    Field('padrone', 'reference rpadroni', requires=IS_IN_DB(db, 'rpadroni.id', '%(last_name)s')),
    Field.Method('age', lambda row: 4)
)

for table_name in ('rpadroni', 'ranimali', ):
    if db(db[table_name].id>0).count()==0:
        for i in range(2):
            populate(db[table_name],100)
            db.commit()

dataTables.add('rpadroni', db.rpadroni)

query = (db.rpadroni.id==db.ranimali.padrone)
dataTables.add_by_query('myjoin', query, db.rpadroni.ALL, db.ranimali.pet_name)

response.menu += [
    (T('Examples'), False, None, [
        (T('First'), False, URL('plugin_examples', 'rpadroni'), ),
        (T('Second'), False, URL('plugin_examples', 'myjoin'), ),
    ], )
]
