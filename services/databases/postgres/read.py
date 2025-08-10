from fastapi import HTTPException
from psycopg import sql, AsyncConnection
from typing import Type, TypeVar, Optional
from pydantic import BaseModel

schema_type = TypeVar("schema_type", bound=BaseModel)

class ReadBuilder:
    def __init__(self, connection: AsyncConnection):
        self.connection: AsyncConnection = connection
        self._order_by_fields = []
        self._group_by_fields = []
        self._select = []
        self._table = None
        self._where = []
        self._order_by = None
        self._order_desc = False
        self._limit = None
        self._offset = None
        self._params = {}

    def build_group_by_clause(self):
        if self._group_by_fields:
            identifiers = [sql.Identifier(col) for col in self._group_by_fields]
            return sql.SQL(" GROUP BY ") + sql.SQL(", ").join(identifiers)
        return sql.SQL("")

    def select(self, columns: Type[schema_type]):
        self._select = list(columns.model_fields.keys())
        return self

    def select_fields(self, *fields: str):
        self._select = list(set(self._select + list(fields)))
        return self

    def from_table(self, table: str):
        self._table = table
        return self

    def where(self, column: str, value):
        if column is None:
            raise ValueError("Value of column can't be None")
        condition = f"{column} = %({column})s"
        self._where.append(condition)
        self._params[column] = value
        return self

    def order_by(self, column: str, descending=False):
        if column is None:
            raise ValueError("Value of column can't be None")

        self._order_by_fields.append((column, descending))
        return self

    def group_by(self, column: str):
        if column is None:
            raise ValueError("Group by column can't be None")
        self._group_by_fields.append(column)
        return self

    def limit(self, count: int):
        self._limit = count
        return self

    def offset(self, count: int):
        self._offset = count
        return self

    def build(self):
        if not self._table:
            raise ValueError("Table name cannot be empty")

        if not self._select:
            select_clause = sql.SQL("*")
        else:
            select_clause = sql.SQL(", ").join(map(sql.Identifier, self._select))

        query = sql.SQL("SELECT {} FROM {}").format(
            select_clause,
            sql.Identifier(self._table)
        )

        if self._where:
            where_clause = sql.SQL(" WHERE ") + sql.SQL(" AND ").join(
                sql.SQL(cond) for cond in self._where
            )
            query += where_clause

        if self._group_by_fields:
            query += self.build_group_by_clause()

        if self._order_by_fields:
            order_clauses = []
            for column, descending in self._order_by_fields:
                direction = sql.SQL("DESC") if descending else sql.SQL("ASC")
                order_clauses.append(
                    sql.SQL("{} {}").format(sql.Identifier(column), direction)
                )
            query += sql.SQL(" ORDER BY ") + sql.SQL(", ").join(order_clauses)

        if self._limit is not None:
            query += sql.SQL(" LIMIT %(limit)s")
            self._params['limit'] = self._limit

        if self._offset is not None:
            query += sql.SQL(" OFFSET %(offset)s")
            self._params['offset'] = self._offset

        return query, self._params

    async def fetch_all(self):
        query, param = self.build()
        try:
            async with self.connection.cursor() as cursor:
                await cursor.execute(query, param)
                rows = await cursor.fetchall()
                column_names = [desc[0] for desc in cursor.description]
                result = [dict(zip(column_names, row)) for row in rows]
                return result
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error occurred while fetching data: {e}")

    async def fetch_one(self):
        query, param = self.build()
        try:
            async with self.connection.cursor() as cursor:
                await cursor.execute(query, param)
                row = await cursor.fetchone()
                if row is None:
                    return None
                column_names = [desc[0] for desc in cursor.description]
                return dict(zip(column_names, row))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error occurred while fetching one: {e}")

    def debug_sql(self):
        query, params = self.build()
        return query.as_string(self.connection), params

    @staticmethod
    def get_field_name(model: Type[BaseModel], field_name: str) -> Optional[str]:
        """
        Returns the field name if it exists in the model, else None.

        Example:
            get_model_field_name(AnnualPlan, "name")  ➜ "name"
            get_model_field_name(AnnualPlan, "fake")  ➜ None
        """
        return field_name if field_name in model.model_fields else None


