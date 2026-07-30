import streamlit as st
import pandas as pd
import plotly.express as px # type: ignore[import-untyped] # plot
import sqlite3
import datetime as dt
from typing import cast
from db_fxn import (create_table, read_data, add_task, edit_task_data,
                    get_unique_tasks, get_task, get_task_from_id, delete_task)

SHOW_COLUMNS = ["ID", "Task", "Status", "Created At", "Due Date", "Updated At"]

def display_tasks(df: pd.DataFrame,
                  expander_name: str ="Your Todo") -> None:
    with st.expander(expander_name):
        st.dataframe(df)


def display_updated_tasks(conn: sqlite3.Connection) -> None:
    updated_todos: list[tuple] = read_data(conn)
    updated_df = pd.DataFrame(updated_todos, columns=SHOW_COLUMNS)
    display_tasks(updated_df, "Updated Todos")


def select_a_task(conn: sqlite3.Connection, task_name: str) -> tuple:
    # Get all task with the same name
    select: list[tuple] = get_task(conn, task_name)
    # st.write(selected)
    selected_ids: list[int] = [select[i][0] for i in range(len(select))]
    selected_id: int = st.selectbox("Select task ID", selected_ids)
    selected = get_task_from_id(conn, selected_id)
    return selected


def main(conn) -> None:
    st.title("Todo App with Streamlit")

    # Todo 1: Menu (CRUD - Create Read Update Delete)
    menu: list[str] = ["Create", "View Task", "Update", "Delete", "About"]
    choice = st.sidebar.selectbox("Menu", menu)

    # Todo 2: Create table
    create_table(conn)

    # Todo 3: Load todo
    todos: list[tuple] = read_data(conn)
    df = pd.DataFrame(todos, columns=SHOW_COLUMNS)
    # print(todos)

    # Todo 4: Add new task
    if choice == menu[0]:
        st.subheader("Add task")

        # layout
        col1, col2 = st.columns([3, 1])
        with col1:
            task_name: str | None = st.text_area("Enter your task:") # multilines text

        with col2:
            task_status: str = st.selectbox("Status", ["ToDo", "Doing", "Done"])
            due_date: dt.date  = cast(dt.date, st.date_input("Due date"))

        if st.button("Add task"):
            if task_name:
                add_task(conn, task_name, task_status, due_date)
                st.success(f"Task added successfully: {task_name}")
            else:
                st.error("Please enter a valid task")

    # Todo 5: View all tasks
    elif choice == menu[1]:
        st.subheader("View tasks")
        display_tasks(df)

        with st.expander("Status"):
            status_count: pd.DataFrame = df["Status"].value_counts().to_frame()

            # without resetting index, "Status" is not a column, but index, can not be used as px.pie argument
            status_count = status_count.reset_index() 
            st.dataframe(status_count)

            status_pie = px.pie(status_count, names="Status", values="count")
            st.plotly_chart(status_pie)

    # Todo 6: Edit task
    elif choice == menu[2]:
        st.subheader("Edit/Update tasks")
        display_tasks(df)

        # Get unique task names
        edit_tasks_list: list[str] = [item[0] for item in get_unique_tasks(conn)]
        edit_select_task: str | None = st.selectbox("Select task", edit_tasks_list,
                                   index=None, placeholder="Task to edit") # optional

        if edit_select_task:
            edit_selected_task: tuple = select_a_task(conn, edit_select_task)

            # Unpack task information
            # selected_task_id: int = edit_selected_task[0]
            selected_task_name: str = edit_selected_task[1]
            selected_task_status: str = edit_selected_task[2]
            # selected_task_created_at: str = edit_selected_task[3]
            selected_task_due_date: str = edit_selected_task[4]
            # selected_task_updated_at: str = edit_selected_task[5]

            # Layout
            col1, col2 = st.columns([3, 1])
            with col1:
                new_task_name: str | None = st.text_area("Edit task:",
                                                         placeholder="New task")  # multilines text

            with col2:
                new_task_status: str = st.selectbox("Status", ["ToDo", "Doing", "Done"])

                # make st.data_input return data as dt.date
                new_due_date: str | dt.date = cast(dt.date,
                                                   st.date_input(f"Due date"))

            if st.button("Edit task"):
                # In case user only change 1 information, not all
                if not new_task_name:
                    new_task_name = selected_task_name

                edit_task_data(conn,
                               selected_task_name,
                               selected_task_status,
                               selected_task_due_date,
                               new_task_name,
                               new_task_status,
                               new_due_date)
                st.success(f"Successfully edit task: {new_task_name}")

                # Show updated data
                display_updated_tasks(conn)


    # Todo 7: Delete task
    elif choice == menu[3]:
        st.subheader("Delete task")
        display_tasks(df)

        # Get unique task names
        delete_tasks_list: list[str] = [item[0] for item in get_unique_tasks(conn)]
        delete_select_task: str | None = st.selectbox("Select task", delete_tasks_list,
                                               index=None, placeholder="Task to delete", key="select_to_delete")  # optional

        if delete_select_task:
            delete_selected_task: tuple = select_a_task(conn, delete_select_task)
            st.warning("Think carefully before deleting task")
            delete_button = st.button("Delete")

            if delete_button:
                # Unpack task information
                to_delete_task_name: str = delete_selected_task[1]
                to_delete_task_status: str = delete_selected_task[2]
                to_delete_task_due_date: str = delete_selected_task[4]

                delete_task(conn, to_delete_task_name, to_delete_task_status, to_delete_task_due_date)
                st.success(f"Successfully deleted task: {to_delete_task_name}")

                # Show updated data
                display_updated_tasks(conn)

    # Todo 8: About
    else:
        st.subheader("About")
        st.write("Thank you for using this application")

if __name__ == '__main__':
    # sqlite3 will be imported from db_fxn if import *
    # 1 connection for all functions, instead of connecting again on each function
    with sqlite3.connect('data.db') as connection:
        main(connection)
    connection.close()
    pass
