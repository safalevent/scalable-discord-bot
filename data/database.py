import logging
import sqlite3
import traceback
import asqlite
import typing as t

from . import query
from .datapath import get_datafile_path

databaseName = "bot.db"

detect_types = sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES

databasePath = get_datafile_path(databaseName)

class Column:
    def __init__(self, name: str, columnType: str, specialities: t.List[str]=None) -> None:
        if (specialities == None):
            specialities = []
            
        self.name = name
        self.type = columnType
        self.specialities = specialities

class Table:
    def __init__(self, tableName, unique_key_names: t.Union[t.List, t.Any], *, columns: t.List[Column], database: str=None, auto_increment=False):
        """Unique keys must be integer."""
        self.table = tableName

        if not isinstance(unique_key_names, list):
            unique_key_names = [unique_key_names]
        self.unique_keys = unique_key_names

        if database:
            self.databasePath = get_datafile_path(database)
        else:
            self.databasePath = databasePath

        self._create_table(auto_increment=auto_increment, columns=columns)
        
    def _create_table(self, auto_increment=False, columns=[]):
        try:
            conn = sqlite3.connect(self.databasePath, detect_types=detect_types)
            cursor = conn.cursor()
            cursor.execute(f'''PRAGMA table_info("{self.table.strip("[]")}")''')
            result = cursor.fetchall()
            if len(result) == 0:
                if (len(self.unique_keys) > 1):
                    command = f'''CREATE TABLE {self.table} ({", ".join([f'{key} integer NOT NULL' for key in self.unique_keys])},
                        CONSTRAINT pk_tableId PRIMARY KEY ({",".join(self.unique_keys)}))'''
                else:
                    type_and_rest = f'integer NOT NULL PRIMARY KEY{" AUTOINCREMENT" if auto_increment else ""}'
                    command = f'''CREATE TABLE {self.table} ({self.unique_keys[0]} {type_and_rest})'''

                cursor.execute(command)
                    
            conn.commit()
        
            for column in columns:
                cursor.execute(f"pragma table_info('{self.table.strip('[]')}')")
                curr_columns = cursor.fetchall()
                curr_columns = [x[1] for x in curr_columns]
                if (not column.name in curr_columns):
                    self._add_column(column.name, column.type, column.specialities)
                    
            conn.close()
            
        except Exception as er:
            logging.exception(er)

    async def _drop_table(self):
        async with asqlite.connect(self.databasePath, detect_types=detect_types) as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(f'DROP TABLE {self.table}')
                
            await conn.commit()

    async def _check_unique_key(self, unique_key):
        """Checks if unique key is valid. And fixes it if needed."""
        assert unique_key != None
        if not isinstance(unique_key, list):
            unique_key = [unique_key]
        assert len(unique_key) == len(self.unique_keys)

        return unique_key
        

    async def _get_columns(self):
        async with asqlite.connect(self.databasePath, detect_types=detect_types) as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(f'SELECT name FROM pragma_table_info("{self.table}")')
                columns = await cursor.fetchall()
                return [x[0] for x in columns]

    def _add_column(self, columnName, dataType, specialities: t.Optional[list]):
        conn = sqlite3.connect(self.databasePath, detect_types=detect_types)
        cursor = conn.cursor()
        command = f'ALTER TABLE {self.table} ADD {columnName} {dataType}'
        if (specialities and len(specialities) > 0):
            command += " "
            command += " ".join(specialities)
        cursor.execute(command)

        conn.commit()
        conn.close()



    async def _get(self, selectQuery: query.SelectQuery):
        async with asqlite.connect(self.databasePath, detect_types=detect_types) as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(*selectQuery.get_query())
                return await cursor.fetchall()

    async def _update(self, updateQuery: query.UpdateQuery):
        if updateQuery.length() == 0:
            return

        async with asqlite.connect(self.databasePath, detect_types=detect_types) as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(*updateQuery.get_query())

            await conn.commit()

    async def _insert(self, insertQuery: query.InsertQuery):
        async with asqlite.connect(self.databasePath, detect_types=detect_types) as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(*insertQuery.get_query())
                
            await conn.commit()

    async def _delete(self, deleteQuery: query.DeleteQuery):
        async with asqlite.connect(self.databasePath, detect_types=detect_types) as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(*deleteQuery.get_query())

            await conn.commit()
    
    async def get_column_list(self) -> t.List[str]:
        return await self._get_columns()

    async def check_column(self, column: Column):
        return await self.add_column(column)
        
    async def add_column(self, column: Column):
        if (not column.name in await self.get_column_list()):
            return self._add_column(column.name, column.type, column.specialities)

    async def get_or_create(self, unique_key):
        unique_key = await self._check_unique_key(unique_key)

        data = await self.get_with(unique_key)
        if not data:
            await self.set(unique_key)
            data = await self.get_with(unique_key)
        return data

    async def get_with(self, unique_key, selectQuery: query.SelectQuery=None) -> t.Optional[sqlite3.Row]:
        unique_key = await self._check_unique_key(unique_key)

        if not selectQuery:
            selectQuery = query.SelectQuery()

        for k, v in zip(self.unique_keys, unique_key):
            if not selectQuery.check_where(k,v):
                selectQuery.add_where(equals={k:v})

        if not selectQuery.table:
            selectQuery.table = self.table
                
        selectQuery.set_limit(1)

        result_row = await self._get(selectQuery)
        return result_row[0] if len(result_row) != 0 else None

    async def get_one(self, selectQuery: query.SelectQuery) -> sqlite3.Row:
        selectQuery.set_limit(1)
        result = await self.get(selectQuery)
        return result[0] if result else None
        
    async def get(self, selectQuery: query.SelectQuery) -> t.List[sqlite3.Row]:
        if not selectQuery.table:
            selectQuery.table = self.table

        return await self._get(selectQuery)

    async def get_column(self, columnName) -> t.List[t.Any]:
        column_rows = await self._get(query.SelectQuery(table=self.table, columns=[columnName]))
        return [x[0] for x in column_rows]

    async def get_all(self) -> t.List[sqlite3.Row]:
        return await self._get(query.SelectQuery(table=self.table))

    async def set(self, unique_key=None, setQuery: query.SetQuery=None):
        if not setQuery:
            setQuery = query.SetQuery()

        if not setQuery.table:
            setQuery.table = self.table

        if not unique_key:
            assert setQuery.length() != 0
            if isinstance(setQuery, query.InsertQuery):
                if isinstance(setQuery, query.SetQuery):
                    setQuery = setQuery.get_insert_query()
                await self._insert(setQuery)
                
            elif isinstance(setQuery, query.UpdateQuery):
                await self._update(setQuery)
            return

        unique_key = await self._check_unique_key(unique_key)

        if (await self.get_with(unique_key)):
            for k, v in zip(self.unique_keys, unique_key):
                if not setQuery.check_where(k, v):
                    setQuery.add_where(equals={k:v})

            if isinstance(setQuery, query.SetQuery):
                setQuery = setQuery.get_update_query()
            return await self._update(setQuery)

        else:
            values = setQuery.get_values()
            for k, v in zip(self.unique_keys, unique_key):
                if k not in values:
                    setQuery.set_values(**{k:v})

            if isinstance(setQuery, query.SetQuery):
                setQuery = setQuery.get_insert_query()
            return await self._insert(setQuery)

    async def delete(self, deleteQuery: query.DeleteQuery):
        """Make sure to give information that is unique for the entry."""
        if not deleteQuery.table:
            deleteQuery.table = self.table

        return await self._delete(deleteQuery)

    async def copy_to_table_on_another_db(self, dbName: str, target_table_name: str):
        async with asqlite.connect(self.databasePath, detect_types=detect_types) as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(f'ATTACH DATABASE "{get_datafile_path(dbName)}" AS new_db')
                await cursor.execute(f'INSERT INTO new_db.{target_table_name} SELECT * FROM {self.table};')

            await conn.commit()

    async def list_tables(self):
        async with asqlite.connect(self.databasePath, detect_types=detect_types) as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables_column = await cursor.fetchall()
                return [x[0] for x in tables_column if not (x[0].startswith("sqlite_") or x[0].startswith("_"))]

    async def write_to_file(self, fileName: str, selectQuery=None) -> str:
        if not selectQuery:
            selectQuery = query.SelectQuery()

        if (not fileName.endswith(".csv")):
            fileName += ".csv"
        
        data = await self.get(selectQuery)
        filePath = get_datafile_path(fileName)
        with open(filePath, "w", encoding="utf-8") as file:
            if len(data) > 0:
                file.write("; ".join(map(str, data[0].keys())) + "\n")
                
            for row in data:
                file.write(";".join(map(str, row)) + "\n")

        return filePath