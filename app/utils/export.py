"""
Export utility module for converting database query results to CSV format.

This module provides functionality to export query results from SQLite database
to CSV files with optional headers.
"""
import csv
import sqlite3
from typing import List, Optional, Tuple


def export_query_to_csv(
    connection: sqlite3.Connection,
    query: str,
    params: Optional[Tuple] = None,
    output_path: str = "",
    headers: Optional[List[str]] = None
) -> None:
    """Export SQL query results to a CSV file.
    
    Executes the provided SQL query and writes the results to a CSV file
    with optional column headers.
    
    Args:
        connection: SQLite database connection object.
        query: SQL SELECT query to execute.
        params: Optional tuple of query parameters for parameterized queries.
        output_path: File path where CSV will be written.
        headers: Optional list of column header names. If provided, will be
                written as the first row of the CSV file.
    
    Returns:
        None
    """
    cursor = connection.cursor()
    cursor.execute(query, params or ())
    rows = cursor.fetchall()
    
    with open(output_path, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        if headers:
            writer.writerow(headers)
        for row in rows:
            writer.writerow([row[column_name] for column_name in row.keys()])
