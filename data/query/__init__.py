from . import utils

class SelectQuery(utils.HasWhereQueryBase):
    def __init__(self, columns=None, limit=None, order_by=None, table=None, natural_join=None) -> None:
        super().__init__(table=table)
        self.columns = []
        if columns:
            if not isinstance(columns, list): columns = [columns]
            self.columns.extend(columns)

        self.limit = limit
        self._order_by = order_by
        self._natural_join_with_table = natural_join

    def get_query(self):
        """Returns the query as (command, (params))."""
        params = []
        command = f'''SELECT {", ".join(self.columns) if len(self.columns) > 0 else "*"}'''
        command += f' FROM {self.table}'

        if (self._natural_join_with_table):
            command += f' NATURAL JOIN {self._natural_join_with_table}'

        if (self._where):
            command += " WHERE " + self._where
            params.extend(self._where_params)

            command = command.strip()
        
        if self.limit:
            command += " LIMIT ?"
            params.append(self.limit)
            
            command = command.strip()

        if self._order_by:
            command += " ORDER BY ?"
            params.append(self._order_by)
            
            command = command.strip()

        # print("Select")
        # print((command, tuple(params)))
        return (command, tuple(params))
        
    def specify_columns(self, *columnNames):
        self.columns.extend(columnNames)

    def set_limit(self, limit: int):
        self.limit = limit

    def set_order_by(self, columnName: str):
        self._order_by = columnName

class UpdateQuery(utils.HasToSetQueryBase, utils.HasWhereQueryBase):
    def __init__(self, setDict=None, table=None) -> None:
        super().__init__(table=table, setDict=setDict)
        

    def get_query(self):
        command = f'UPDATE {self.table}'
        params = []

        toSetStr = ""
        for i, kandv in enumerate(self._toSet.items()):
            k, v = kandv
            toSetStr += f'{k}=?'
            params.append(v)

            if (i != len(self._toSet)-1):
                toSetStr += ", "

        command += f" SET {toSetStr}"

        if (self._where):
            command += f" WHERE {self._where}"
            params.extend(self._where_params)

        # print("Update")
        # print((command, tuple(params)))
        return (command, tuple(params))


class InsertQuery(utils.HasToSetQueryBase):
    def __init__(self, setDict=None, table=None) -> None:
        super().__init__(table=table, setDict=setDict)

        self._copyFrom = None

    def get_query(self):
        command = f'INSERT INTO {self.table}'
        params = []
        if self._copyFrom:
            if self.columns:
                command += f'({", ".join(self.columns)})'
                
            selectCommand, selectParams = self._copyFrom.get_query()

            command += " " + selectCommand
            params.extend(selectParams)
            
        else:
            columns = self._toSet.keys()
            columnsStr = ", ".join(columns)

            valuesStr = ""
            for column in columns:
                valuesStr += "?, "

                val = self._toSet[column]
                params.append(val)
            valuesStr = valuesStr.strip(", ")

            command += f'({columnsStr}) VALUES ({valuesStr})'

        # print("Insert")
        # print((command, tuple(params)))
        return (command, tuple(params))

    def set_copy_from(self, selectQuery: SelectQuery):
        self._copyFrom = selectQuery

    def length(self):
        """Returns 1 if it can't determine the length."""
        if self._copyFrom:
            count = 1
        else:
            count = super().length()
        return count

class SetQuery(UpdateQuery, InsertQuery):
    def __init__(self, setDict=None, table=None) -> None:
        super().__init__(table=table, setDict=setDict)

    def get_update(self):
        updateQuery = UpdateQuery(table=self.table, setDict=self._toSet)
        updateQuery._where = self._where
        updateQuery._where_params = self._where_params

        return updateQuery

    def get_insert(self):
        insertQuery = InsertQuery(table=self.table, setDict=self._toSet)
        return insertQuery

class DeleteQuery(utils.HasWhereQueryBase):
    def __init__(self, order_by=None, table=None) -> None:
        super().__init__(table=table)

        self._order_by = order_by
        
    def get_query(self):
        """Returns the query as (command, (params))."""
        params = []
        command = f'''DELETE FROM {self.table}'''

        if (self._where):
            command += " WHERE " + self._where
            params.extend(self._where_params)

            command = command.strip()
        
        if self._order_by:
            command += " ORDER BY ?"
            params.append(self._order_by)
            
            command = command.strip()

        # print("Delete")
        # print((command, tuple(params)))
        return (command, tuple(params))

    def set_order_by(self, columnName: str):
        self._order_by = columnName