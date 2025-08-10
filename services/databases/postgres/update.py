from psycopg import sql, AsyncConnection
from pydantic import BaseModel
from typing import TypeVar, Optional, Union

schema_type = TypeVar("schema_type", bound=BaseModel)

class UpdateQueryBuilder:
    """
    A utility class for building and executing parameterized SQL UPDATE statements
    using an asynchronous PostgreSQL connection (psycopg3) and Pydantic models.

    This builder supports:
    - Specifying the target table.
    - Providing update values via a Pydantic model.
    - Defining WHERE conditions to target rows for update.
    - Optionally returning specific fields after the update.
    - Checking for record existence before performing the update.

    Example usage:
        builder = (
            UpdateQueryBuilder(connection)
            .into_table("users")
            .values(UserUpdateModel(name="Alice Updated"))
            .where({"id": "some-uuid"})
            .check_exists({"id": "some-uuid"})
            .returning("id", "name")
        )
        result = await builder.execute()
    """

    def __init__(self, connection: AsyncConnection):
        """
        Initialize the UpdateQueryBuilder.

        Args:
            connection (AsyncConnection): An active asynchronous PostgresSQL connection
                                          (from psycopg3) used for executing the query.
        """
        self.connection: AsyncConnection = connection
        self._table: Optional[str] = None
        self._data: Optional[BaseModel] = None
        self._where_conditions: Optional[dict[str, any]] = None
        self._returning_fields: list[str] = []
        self._check_exists: Optional[dict[str, any]] = None
        self._raw_query: Optional[sql.SQL] = None
        self._raw_params: Optional[dict] = None

    def into_table(self, table: str) -> "UpdateQueryBuilder":
        """
        Specify the name of the table to update.

        Args:
            table (str): The name of the target database table.

        Returns:
            UpdateQueryBuilder: The current instance for method chaining.
        """
        self._table = table
        return self

    def raw(self, raw_query: Union[str, sql.SQL], params: dict) -> "UpdateQueryBuilder":
        """
        Provide a raw SQL query and parameter dictionary to execute directly.

        Args:
            raw_query (str | sql.SQL): The raw SQL query to be executed.
            params (dict): The parameter dictionary to be used in the query.

        Returns:
            UpdateQueryBuilder: The current instance with raw mode enabled.
        """
        self._raw_query = raw_query
        self._raw_params = params
        return self

    def values(self, data: schema_type) -> "UpdateQueryBuilder":
        """
        Provide the data to update using a Pydantic model.

        Args:
            data (schema_type): A Pydantic model instance containing the column-value pairs
                                to be updated.

        Returns:
            UpdateQueryBuilder: The current instance for method chaining.
        """
        self._data = data
        return self

    def where(self, conditions: dict[str, any]) -> "UpdateQueryBuilder":
        """
        Specify the WHERE conditions to identify which rows to update.

        Args:
            conditions (dict[str, any]): A dictionary where keys are column names and values
                                         are the expected values to filter rows.

        Returns:
            UpdateQueryBuilder: The current instance for method chaining.
        """
        self._where_conditions = conditions
        return self

    def check_exists(self, conditions: dict[str, any]) -> "UpdateQueryBuilder":
        """
        Specify column-value conditions to check whether a matching record exists
        before performing the update.

        Args:
            conditions (dict[str, any]): A dictionary where keys are column names and values
                                         are the expected values to check for existence.

        Returns:
            UpdateQueryBuilder: The current instance for method chaining.
        """
        self._check_exists = conditions
        return self

    def returning(self, *fields: str) -> "UpdateQueryBuilder":
        """
        Specify one or more fields to return after the update operation.

        Args:
            *fields (str): One or more column names to return from the updated row(s).

        Returns:
            UpdateQueryBuilder: The current instance for method chaining.
        """
        self._returning_fields.extend(fields)
        return self

    def build(self):
        """
        Construct the SQL UPDATE statement and associated parameter values.

        Raises:
            ValueError: If the table name, update data, or WHERE conditions have not been provided.

        Returns:
            tuple:
                - query (psycopg.sql.Composed): A composable SQL query object ready for execution.
                - params (dict): A dictionary of column-value mappings to be used as parameters
                                 in the SQL execution.

        Example:
            query, params = builder.build()
        """
        if not self._table:
            raise ValueError("Table name must be provided.")
        if not self._data:
            raise ValueError("Update data must be provided.")
        if not self._where_conditions:
            raise ValueError("WHERE conditions must be provided to avoid updating all rows.")

        update_fields = list(self._data.model_fields.keys())
        update_values = self._data.model_dump()

        set_sql = sql.SQL(", ").join(
            sql.SQL("{} = {}").format(sql.Identifier(field), sql.Placeholder(field)) for field in update_fields
        )

        where_clauses = [
            sql.SQL("{} = {}").format(sql.Identifier(k), sql.Placeholder(f"where_{k}"))
            for k in self._where_conditions
        ]
        where_sql = sql.SQL(" AND ").join(where_clauses)

        # Combine params: update values and where values with different keys to avoid collision
        params = {**update_values}
        params.update({f"where_{k}": v for k, v in self._where_conditions.items()})

        query = sql.SQL("UPDATE {} SET {} WHERE {}").format(
            sql.Identifier(self._table),
            set_sql,
            where_sql,
        )

        if self._returning_fields:
            returning_sql = sql.SQL(", ").join(map(sql.Identifier, self._returning_fields))
            query += sql.SQL(" RETURNING ") + returning_sql

        return query, params

    async def _record_exists(self):
        """
        Internal method to check if a record already exists in the target table
        based on the column-value conditions specified via `check_exists()`.

        Returns:
            bool: True if a matching record exists, False otherwise.

        Raises:
            Exception: If the SELECT query execution fails due to a database error.
        """
        if not self._check_exists:
            return False

        where_clauses = [
            sql.SQL("{} = {}").format(sql.Identifier(k), sql.Placeholder(k))
            for k in self._check_exists
        ]
        where_sql = sql.SQL(" AND ").join(where_clauses)

        query = sql.SQL("SELECT 1 FROM {} WHERE {} LIMIT 1").format(
            sql.Identifier(self._table),
            where_sql
        )

        try:
            async with self.connection.cursor() as cursor:
                await cursor.execute(query, self._check_exists)
                return await cursor.fetchone() is not None
        except Exception as e:
            raise Exception(f"Failed to check if exists due to error: {e}")

    async def execute(self):
        """
        Execute the UPDATE query using the provided connection and data.

        This method performs the following steps:
        1. If `check_exists()` was used, it first checks whether a record with the
           given conditions exists in the table.
           - If no such record exists, an exception is raised.
        2. Builds and executes the UPDATE query with parameterized values.
        3. Optionally returns specified fields if `returning()` was used.

        Returns:
            dict | None:
                - If `returning()` fields were specified, returns a dictionary of the updated row.
                - Otherwise, returns None.

        Raises:
            Exception: If the record does not exist or the update fails due to a database error.

        Example:
            result = await builder.execute()
        """

        # Execute raw SQL if specified
        if self._raw_query:
            try:
                async with self.connection.cursor() as cursor:
                    await cursor.execute(self._raw_query, self._raw_params)

                    if self._returning_fields:
                        row = await cursor.fetchone()
                        if row:
                            column_names = [desc[0] for desc in cursor.description]
                            return dict(zip(column_names, row))
                    return None
            except Exception as e:
                raise Exception(f"Failed to execute raw SQL: {e}")


        if await self._record_exists() is False:
            raise Exception(
                f"""No matching record found in table {self._table.replace('_', ' ')
                .title() if '_' in self._table else self._table.capitalize()} for the given conditions."""
            )

        query, params = self.build()
        try:
            async with self.connection.cursor() as cursor:
                await cursor.execute(query, params)

                if self._returning_fields:
                    row = await cursor.fetchone()
                    if row is not None:
                        column_names = [desc[0] for desc in cursor.description]
                        return dict(zip(column_names, row))
                return None

        except Exception as e:
            raise Exception(
                f"""Failed to update record in table {self._table.replace('_', ' ')
                .title() if '_' in self._table else self._table.capitalize()} due to error: {e}"""
            )
