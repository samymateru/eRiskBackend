from psycopg import sql, AsyncConnection
from typing import Optional, Dict, Any, List
from fastapi import HTTPException


class DeleteQueryBuilder:
    """
    A utility class for building and executing parameterized SQL DELETE statements
    using an asynchronous PostgreSQL connection (psycopg3).

    Supports:
    - Specifying the target table.
    - Adding WHERE conditions to filter which rows to delete.
    - Optionally checking if matching records exist before deletion.
    - Returning specific fields from deleted rows.

    Example usage:
        builder = (
            DeleteQueryBuilder(connection)
            .from_table("users")
            .where({"id": 5})
            .check_exists({"id": 5})
            .returning("id", "name")
        )
        result = await builder.execute()
    """

    def __init__(self, connection: AsyncConnection):
        """
        Initialize the DeleteQueryBuilder.

        Args:
            connection (AsyncConnection): An active async PostgreSQL connection.
        """
        self.connection: AsyncConnection = connection
        self._table: Optional[str] = None
        self._where_conditions: Optional[Dict[str, Any]] = None
        self._returning_fields: List[str] = []
        self._check_exists: Optional[Dict[str, Any]] = None

    def from_table(self, table: str) -> "DeleteQueryBuilder":
        """
        Specify the table to delete from.

        Args:
            table (str): Target table name.

        Returns:
            DeleteQueryBuilder: Self for chaining.
        """
        self._table = table
        return self

    def where(self, conditions: Dict[str, Any]) -> "DeleteQueryBuilder":
        """
        Add WHERE conditions to filter rows for deletion.

        Args:
            conditions (Dict[str, Any]): Column-value pairs for WHERE clause.

        Returns:
            DeleteQueryBuilder: Self for chaining.
        """
        self._where_conditions = conditions
        return self

    def check_exists(self, conditions: Dict[str, Any]) -> "DeleteQueryBuilder":
        """
        Specify conditions to check if records exist before deletion.

        Args:
            conditions (Dict[str, Any]): Column-value pairs to verify existence.

        Returns:
            DeleteQueryBuilder: Self for chaining.
        """
        self._check_exists = conditions
        return self

    def returning(self, *fields: str) -> "DeleteQueryBuilder":
        """
        Specify fields to return after deletion.

        Args:
            *fields (str): Column names to return.

        Returns:
            DeleteQueryBuilder: Self for chaining.
        """
        self._returning_fields.extend(fields)
        return self

    def build(self):
        """
        Build the DELETE SQL query and parameters.

        Raises:
            ValueError: If table or where conditions are missing.

        Returns:
            Tuple[sql.Composed, Dict[str, Any]]: Query and params dict.
        """
        if not self._table:
            raise ValueError("Table name must be specified with from_table().")
        if not self._where_conditions:
            raise ValueError("WHERE conditions must be specified with where().")

        where_clauses = [
            sql.SQL("{} = {}").format(sql.Identifier(k), sql.Placeholder(k))
            for k in self._where_conditions
        ]
        where_sql = sql.SQL(" AND ").join(where_clauses)

        query = sql.SQL("DELETE FROM {} WHERE {}").format(
            sql.Identifier(self._table),
            where_sql
        )

        if self._returning_fields:
            returning_sql = sql.SQL(', ').join(map(sql.Identifier, self._returning_fields))
            query += sql.SQL(" RETURNING ") + returning_sql

        return query, self._where_conditions

    async def _record_exists(self) -> bool:
        """
        Check if records matching _check_exists conditions exist.

        Returns:
            bool: True if at least one record exists, False otherwise.

        Raises:
            HTTPException: On database errors.
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
            raise HTTPException(status_code=400, detail=f"Existence check failed: {e}")

    async def execute(self):
        """
        Execute the DELETE query asynchronously.

        Raises:
            Exception: If record does not exist when checked, or query execution fails.

        Returns:
            dict | None:
                - A dictionary of returned fields if `returning()` was specified.
                - None if no returning fields or no rows deleted.
        """
        if self._check_exists:
            exists = await self._record_exists()
            if not exists:
                raise Exception(
                    f"Record does not exist in table "
                    f"{self._table.replace('_', ' ').title() if '_' in self._table else self._table.capitalize()}"
                )

        query, params = self.build()

        try:
            async with self.connection.cursor() as cursor:
                await cursor.execute(query, params)
                if self._returning_fields:
                    row = await cursor.fetchone()
                    if row:
                        column_names = [desc[0] for desc in cursor.description]
                        return dict(zip(column_names, row))
                return None
        except Exception as e:
            raise Exception(
                f"Failed to delete record from table "
                f"{self._table.replace('_', ' ').title() if '_' in self._table else self._table.capitalize()} due to error: {e}"
            )
