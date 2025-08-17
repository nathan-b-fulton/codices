import kuzu

node_tables:dict = {'Datatype': {'ID': 'SERIAL PRIMARY KEY', 'literal': 'STRING', 'description': 'STRING'},
                    'Object': {'ID': 'SERIAL PRIMARY KEY', 'name': 'STRING', 'description': 'STRING'},
                    'Morphism': {'ID': 'SERIAL PRIMARY KEY', 'name': 'STRING', 'description': 'STRING'},
                    'Category': {'ID': 'SERIAL PRIMARY KEY', 'name': 'STRING', 'description': 'STRING'},
                    'Functor': {'ID': 'SERIAL PRIMARY KEY', 'name': 'STRING', 'description': 'STRING'},
                    'Natural_Transformation': {'ID': 'SERIAL PRIMARY KEY', 'name': 'STRING', 'description': 'STRING'}}


rel_tables:dict =  {'source': {'from': 'Morphism', 'to': 'Object', 'uniqueness': 'MANY_ONE'},
                    'target': {'from': 'Morphism', 'to': 'Object', 'uniqueness': 'MANY_ONE'},
                    'source': {'from': 'Morphism', 'to': 'Morphism', 'uniqueness': 'MANY_ONE'},
                    'target': {'from': 'Morphism', 'to': 'Morphism', 'uniqueness': 'MANY_ONE'},
                    'source': {'from': 'Functor', 'to': 'Category', 'uniqueness': 'MANY_ONE'},
                    'target': {'from': 'Functor', 'to': 'Category', 'uniqueness': 'MANY_ONE'},
                    'source': {'from': 'Natural_Transformation', 'to': 'Functor', 'uniqueness': 'MANY_ONE'},
                    'target': {'from': 'Natural_Transformation', 'to': 'Functor', 'uniqueness': 'MANY_ONE'},
                    'includes': {'from': 'Category', 'to': 'Object', 'uniqueness': 'ONE_MANY'},
                    'includes': {'from': 'Category', 'to': 'Morphism', 'uniqueness': 'ONE_MANY'},
                    'includes': {'from': 'Functor', 'to': 'Morphism', 'uniqueness': 'ONE_MANY'},
                    'includes': {'from': 'Natural_Transformation', 'to': 'Morphism', 'uniqueness': 'ONE_MANY'},
                    'property': {'from': 'Object', 'to': 'Datatype', 'fieldName': 'STRING'}
                    }


def create_table(connection, label:str, definition:dict, rel:bool=False):
    """ """
    t:str = "NODE"
    d:str = ""
    u:str = ""
    if rel:
        t = "REL"
        d = f"FROM {definition['from']} TO {definition['to']}, "
        u_or_none = definition.get('uniqueness')
        if u_or_none:
            u = f", {u_or_none}"
    table:str = f"CREATE {t} TABLE IF NOT EXISTS {label}({d}"
    for k, v in definition.items():
        if k not in ['uniqueness', 'from', 'to']:
            table += f"{k} {v}, "
    connection.execute(table[0:-2] + f"{u})")


def initialize_schema():
    """ """
    db = kuzu.Database("./kuzu_db")
    conn = kuzu.Connection(db)
    for l, d in node_tables.items():
        create_table(conn, l, d)
    for l, d in rel_tables.items():
        create_table(conn, l, d, True)


# initialize_schema()