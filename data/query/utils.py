class QueryBase:
    def __init__(self, table=None) -> None:
        self.table = table

    def get_query(self):
        print("Query Base Get Query")
        return (None, None)
    
    def get_command(self):
        return self.get_query()[0]

    def get_params(self):
        return self.get_query()[1]

class HasWhereQueryBase(QueryBase):
    def __init__(self, table=None, **kwargs) -> None:
        super().__init__(table=table)
        
        self._where = ""
        self._where_params = []
        
    #Not great but couldn't find a better way.
    def add_where(self, *, equals=None, less=None, lessOrEquals=None, greater=None, greaterOrEquals=None, sep=" AND ", between=None, like=None, sep_from_before=" AND "):
        """
            'equals', 'less', 'lessOrEquals', 'greater', 'greaterOrEquals', 'like' are all dictionaries.
            'sep' means separator between these statements.
            'between' is a tuple with the format (min, max, columnName).
            'sep_from_before' is the separator between these statement and others before.

            returns SelectQuery object.
        """
        assert equals or less or lessOrEquals or greater or greaterOrEquals or between or like

        if self._where:
            self._where += sep_from_before

        self._where += "("
        add_sep = False
        if equals:
            self._add_where(equals, statement="=", sep=sep)
            add_sep = True

        if less:
            if add_sep:
                self._where += sep
            self._add_where(less, statement="<", sep=sep)
            add_sep = True
            
        if lessOrEquals:
            if add_sep:
                self._where += sep
            self._add_where(lessOrEquals, statement="<=", sep=sep)
            add_sep = True

        if greater:
            if add_sep:
                self._where += sep
            self._add_where(greater, statement=">", sep=sep)
            add_sep = True
            
        if greaterOrEquals:
            if add_sep:
                self._where += sep
            self._add_where(greaterOrEquals, statement=">=", sep=sep)
            add_sep = True

        if between and len(between) == 3:
            if add_sep:
                self._where += sep

            self._where += f'{between[2]} BETWEEN ? AND ?'
            self._where_params.extend((between[0], between[1]))
            add_sep = True
            
        if like:
            if add_sep:
                self._where += sep

            self._add_where(like, statement=" LIKE ", sep=sep)
            add_sep = True

        self._where +=")"
        return self

    def _add_where(self, dicti, statement, sep):
        for i, kandv in enumerate(dicti.items()):
            k, v = kandv
            self._where += f'{k}{statement}?'
            self._where_params.append(v)

            if (i != len(dicti)-1):
                self._where += sep

    def check_where(self, key, value):
        return key in self._where and value in self._where_params
        
class HasToSetQueryBase(QueryBase):
    def __init__(self, table=None, setDict: dict=None) -> None:
        super().__init__(table=table)
        
        self._toSet = setDict if setDict else {}
        self.columns = [x for x in setDict] if setDict else []

    def get_values(self):
        return self._toSet.copy()
        
    def set_values(self, **values):
        for k, v in values.items():
            self._toSet[k] = v

            if k not in self.columns:
                self.columns.append(k)
                
        return self
        
    def length(self):
        return len(self._toSet)
