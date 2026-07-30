import sqlite3
import datetime as dt
from datetime import datetime, UTC


# Database
# Table
# Fields / Columns
# DataType


def create_table(conn: sqlite3.Connection) -> None:
    # context manager will automatically commit
    # but does not close the connection
    with conn:
        c = conn.cursor()
        c.execute(
            # default using UTC timezone, not machine local's timezone to keep data uniform across different locations
            # can either convert to save the local timezone, or saving the UTC timezone and convert when querying

            # task_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT (should not and no need to use here)
            # IDs keep increasing and skip numbers, this is by design to maintain data integrity
            # 1. if UserA whose ID is 4 got deleted, and UserB is newly added with ID 4
                # UserB might get assigned to UserA's fields on other tables
            # 2. on Audit Logs (Nhật ký hệ thống) each ID should be unique, not repeated
                # Reusing IDs destroys the chronological (trình tự thời gian) order and makes tracking bugs or fraudulent (gian lận) activity impossible.
            # 3.Performance Optimization: To find missing ID gaps (e.g., checking which numbers between 1 and 1000 are unused),
                # SQLite would have to scan the entire table during every insert.
                # Simply taking the largest current ID + 1 keeps INSERT operations at maximum speed.
            """
            CREATE TABLE IF NOT EXISTS tasks (
                task_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                task TEXT NOT NULL,
                task_status TEXT DEFAULT "ToDo",
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                due_at DATE,
                updated_at TIMESTAMP
            )
            """
        )


def add_task(conn: sqlite3.Connection,
             task: str, task_status: str, due_at: dt.date) -> None:
    with conn:
        c = conn.cursor()
        c.execute("""INSERT INTO tasks (task, task_status, due_at) VALUES (?, ?, ?)""",
                  (task.strip(), task_status, due_at))


def read_data(conn: sqlite3.Connection) -> list[tuple]:
    with conn:
        c = conn.cursor()
        c.execute(
            # datetime(created_at, "localtime"): convert UTC to local machine time zone
            """
            SELECT 
                task_id,
                task,
                task_status,
                datetime(created_at, "localtime"),
                due_at,
                datetime(updated_at, "localtime")
            FROM tasks
            """
        )
        data: list[tuple] = c.fetchall()
        return data


def get_unique_tasks(conn: sqlite3.Connection) -> list[tuple]:
    """Get unique task names"""
    with conn:
        c = conn.cursor()
        c.execute("""SELECT DISTINCT task FROM tasks""")
        data: list[tuple] = c.fetchall()
        return data


def get_task(conn: sqlite3.Connection, task: str) -> list[tuple]:
    """Get all tasks that have the same name"""
    with conn:
        c = conn.cursor()
        c.execute("""SELECT * FROM tasks WHERE task = ?""",
                  (task,))
        data: list[tuple] = c.fetchall()
        return data


def get_task_from_id(conn: sqlite3.Connection, task_id: int) -> tuple:
    """Get a specific task by its ID"""
    with conn:
        c = conn.cursor()
        c.execute("""SELECT * FROM tasks WHERE task_id = ?""", (task_id,))
        return c.fetchone()


def edit_task_data(conn: sqlite3.Connection,
                   old_task: str, old_task_status: str, old_task_due_at: str | dt.date,
                   new_task: str | None, new_task_status: str, new_task_due_at: str | dt.date) -> None:
    updated_time: str = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")

    if not new_task:
        new_task = old_task

    with conn:
        c = conn.cursor()
        c.execute(
            """
            UPDATE tasks 
                SET task = ?, task_status = ?, due_at = ?, updated_at = ?
                WHERE task = ? and task_status = ? and due_at = ?
            """,
            (new_task, new_task_status, new_task_due_at, updated_time,
             old_task, old_task_status, old_task_due_at)
        )

def delete_task(conn: sqlite3.Connection,
                task: str, task_status: str, due_at: str) -> None:
    with conn:
        c = conn.cursor()
        c.execute(
            """
            DELETE FROM tasks 
                WHERE task = ? and task_status = ? and due_at = ?
            """,
            (task, task_status, due_at)
        )


if __name__ == '__main__':
    # with sqlite3.connect('data.db') as connect:
        # print(get_unique_tasks(connect))
        # print(read_data(connect))
        # print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    # context manager will automatically commit
    # still have to close conn manually
    # with sqlite3.connect('data.db') as conn:
    #     c = conn.cursor()
    #     conn.close()
    #
    # c.execute(
    #     """
    #     SELECT * FROM tasks
    #     """
    # )
    # data = c.fetchall()
    # print(data)

    pass
