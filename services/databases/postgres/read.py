from fastapi import HTTPException
from psycopg import sql, AsyncConnection
from typing import Type, TypeVar, Optional
from pydantic import BaseModel

schema_type = TypeVar("schema_type", bound=BaseModel)

class ReadBuilder:
    def __init__(self, connection: AsyncConnection = None):
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
        self._joins = []
        self._table_alias = None
        self._distinct = False

    def distinct(self):
        self._distinct = True
        return self

    def join(self, join_type: str, table: str, on: str, alias: Optional[str] = None,
             model: Optional[Type[BaseModel]] = None, use_prefix: bool = True):
        join_clause = {
            "type": join_type.upper(),
            "table": table,
            "alias": alias,
            "on": on,
            "model": model,
            "use_prefix": use_prefix  # NEW!
        }
        self._joins.append(join_clause)
        return self

    def select_joins(self):
        for join in self._joins:
            model = join.get("model")
            alias = join.get("alias")
            use_prefix = join.get("use_prefix", True)

            if model and alias:
                for field in model.model_fields.keys():
                    field_path = f"{alias}.{field}"
                    alias_name = f"{alias}_{field}" if use_prefix else field
                    self._select.append((field_path, alias_name))
        return self

    def build_group_by_clause(self):
        if self._group_by_fields:
            identifiers = [sql.Identifier(col) for col in self._group_by_fields]
            return sql.SQL(" GROUP BY ") + sql.SQL(", ").join(identifiers)
        return sql.SQL("")

    def select(self, columns: Type[schema_type]):
        # Store field names as (field, None) to match the expected format
        self._select = [(field, None) for field in columns.model_fields.keys()]
        return self

    def select_fields(self, *fields: str, alias_map: Optional[dict[str, str]] = None):
        alias_map = alias_map or {}
        for field in fields:
            alias = alias_map.get(field)
            self._select.append((field, alias))
        return self

    def from_table(self, table: str, alias: Optional[str] = None):
        self._table = table
        self._table_alias = alias
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
            select_parts = []
            for col, alias in self._select:
                # Handle already qualified fields like "bp.id"
                if "." in col:
                    table_alias, column_name = col.split(".", 1)
                    column_sql = sql.SQL("{}.{}").format(
                        sql.Identifier(table_alias), sql.Identifier(column_name)
                    )
                else:
                    # If no table prefix, assume it's from the base table
                    if self._table_alias:
                        column_sql = sql.SQL("{}.{}").format(
                            sql.Identifier(self._table_alias), sql.Identifier(col)
                        )
                    else:
                        column_sql = sql.Identifier(col)

                if alias:
                    select_parts.append(
                        sql.SQL("{} AS {}").format(column_sql, sql.Identifier(alias))
                    )
                else:
                    select_parts.append(column_sql)

            select_clause = sql.SQL(", ").join(select_parts)

        from_clause = sql.SQL("FROM {}").format(sql.SQL("{} AS {}").format(sql.Identifier(self._table), sql.Identifier(self._table_alias)) if self._table_alias else sql.Identifier(self._table))

        # Add JOINs
        join_clauses = []
        for join in self._joins:
            join_type = sql.SQL(join["type"] + " JOIN")
            table_id = sql.Identifier(join["table"])
            alias = sql.Identifier(join["alias"]) if join["alias"] else None
            on_clause = sql.SQL(join["on"])  # Keep raw string — if safe
            alias_sql = sql.SQL("AS ") + alias if alias else sql.SQL("")
            join_clause = sql.SQL(" {} {} {} ON {}").format(
                join_type,
                table_id,
                alias_sql,
                on_clause
            )
            join_clauses.append(join_clause)

        select_prefix = sql.SQL("SELECT DISTINCT ") if self._distinct else sql.SQL("SELECT ")
        query = select_prefix + select_clause + sql.SQL(" ") + from_clause + sql.SQL("").join(join_clauses)

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



# class Dog(BaseModel):
#     pop: str
#     hell: str
#
# builder = (
#     ReadBuilder()
#     .distinct()
#     .select_fields("hello", "power", alias_map={"hello": "he", "power": "po"})
#     .from_table("table_a", alias="a")
#     .join("LEFT", "table_b",  "a.b_id = b.id", alias="b")
#     .join("RIGHT", "table_b", "a.b_id = b.id", alias="b")
#     .where(ReadBuilder.get_field_name(Dog, "pop"), "active")
# )
#
#
#
# print(builder.debug_sql())