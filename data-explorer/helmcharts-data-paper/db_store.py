import sqlite3

DB = 'cve2023.sqlite'


def init_db():
    connection = sqlite3.connect(DB)
    with open('schema.sql') as f:
        connection.executescript(f.read())
    connection.close()


def persist_package(data: tuple, table_name: str):
    connection = sqlite3.connect(DB)
    cursor = connection.cursor()
    try:
        cursor.execute(
            f'insert into {table_name} (uuid, name, org, org_and_name, additional_info, available_versions, count_versions, uuid_version_ref) values(?,?,?,?,?,?,?,?)',
            data)
    except sqlite3.IntegrityError as e:
        print(e)
        print(f'unique constraint violated: {data[0]} {data[1]}')
    connection.commit()
    connection.close()


def update_package_name(data: tuple, table_name: str):
    connection = sqlite3.connect(DB)
    cursor = connection.cursor()
    try:
        cursor.execute(f'update {table_name} set name = ?, org_and_name = ? where uuid = ?', data)
    except sqlite3.IntegrityError as e:
        print(e)
        print(data)
    connection.commit()
    connection.close()


def update_package(data: tuple, table_name: str):
    connection = sqlite3.connect(DB)
    cursor = connection.cursor()
    try:
        cursor.execute(f'update {table_name} set available_versions = ?, count_versions = ?, '
                       f'uuid_version_ref = ? where uuid = ?', data)
    except sqlite3.IntegrityError as e:
        print(e)
        print(data)
    connection.commit()
    connection.close()


def persist_cve(data: tuple, table_name: str):
    connection = sqlite3.connect(DB)
    cursor = connection.cursor()
    try:
        cursor.execute(f'insert into {table_name} (uuid, name, cve_report_json, version) values(?,?,?,?)', data)
    except sqlite3.IntegrityError as e:
        print(e)
        print(data[0], data[1])
    connection.commit()
    connection.close()


def persist_cve_metrics(data: tuple, table_name: str):
    connection = sqlite3.connect(DB)
    cursor = connection.cursor()
    try:
        cursor.execute(f'insert into {table_name} (uuid, metrics) values(?,?)', data)
    except sqlite3.IntegrityError as e:
        print(e)
        print(data[0], data[1])
    connection.commit()
    connection.close()


def search_uuid(uuid: str, table_name: str):
    connection = sqlite3.connect(DB)
    cursor = connection.cursor()
    cursor.execute(f'select * from {table_name} where uuid = ?', (uuid,))
    result = cursor.fetchone()
    connection.close()
    return result


if __name__ == '__main__':
    connection = sqlite3.connect(DB)
    cursor = connection.cursor()
    cursor.execute('vacuum')
