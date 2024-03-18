import pandas as pd
import streamlit as st
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)
import mimetypes
import sqlite3
import getpass, os

st.set_page_config(layout='wide')

username = getpass.getuser()
domain_username = os.getenv('USERDOMAIN')+ "\\" + username
if "pwcglb" in domain_username.lower():
    st.title("SQL Automation For Client Analysis")

    st.subheader("Single File Layout")

    def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        """
        Adds a UI on top of a dataframe to let viewers filter columns

        Args:
            df (pd.DataFrame): Original dataframe

        Returns:
            pd.DataFrame: Filtered dataframe
        """
        modify = st.checkbox("Add filters")

        if not modify:
            return df

        df = df.copy()

        # Try to convert datetimes into a standard format (datetime, no timezone)
        for col in df.columns:
            if is_object_dtype(df[col]):
                try:
                    df[col] = pd.to_datetime(df[col])
                except Exception:
                    pass

            if is_datetime64_any_dtype(df[col]):
                df[col] = df[col].dt.tz_localize(None)

        modification_container = st.container()

        with modification_container:
            to_filter_columns = st.multiselect("Filter dataframe on", df.columns)
            for column in to_filter_columns:
                left, right = st.columns((1, 20))
                left.write("↳")
                # Treat columns with < 10 unique values as categorical
                if is_categorical_dtype(df[column]) or df[column].nunique() < 10:
                    default_values = df[column].unique().tolist()
                    user_cat_input = right.multiselect(f"Values for {column}", default_values, default=default_values)
                    df = df[df[column].isin(user_cat_input)]
                elif is_numeric_dtype(df[column]):
                    _min = float(df[column].min())
                    _max = float(df[column].max())
                    step = (_max - _min) / 100
                    user_num_input = right.slider(
                        f"Values for {column}",
                        _min,
                        _max,
                        (_min, _max),
                        step=step,
                    )
                    df = df[df[column].between(*user_num_input)]
                elif is_datetime64_any_dtype(df[column]):
                    user_date_input = right.date_input(
                        f"Values for {column}",
                        value=(
                            df[column].min(),
                            df[column].max(),
                        ),
                    )
                    if len(user_date_input) == 2:
                        user_date_input = tuple(map(pd.to_datetime, user_date_input))
                        start_date, end_date = user_date_input
                        df = df.loc[df[column].between(start_date, end_date)]
                else:
                    user_text_input = right.text_input(
                        f"Substring or regex in {column}",
                    )
                    if user_text_input:
                        df = df[df[column].str.contains(user_text_input)]

        return df


    file = st.file_uploader("Please upload a .xlsx, .csv, or .sql file", type=["xlsx", "csv", "sql"])
    df = pd.DataFrame()

    if file is not None:
        file_info = mimetypes.guess_type(file.name)
        if file_info[0] == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
            xlsx = pd.ExcelFile(file)
            sheet_names = xlsx.sheet_names
            selected_sheet = st.selectbox("Select a sheet to display", sheet_names)
            if selected_sheet is not None:
                df = pd.read_excel(file, sheet_name=str(selected_sheet))
            else:
                df = pd.read_excel(file)
        elif file_info[0] == 'text/plain':
            if file.name.endswith('.sql'):
                # Read the SQL file content
                sql_content = file.getvalue().decode("utf-8")

                # Create an in-memory SQLite database
                conn = sqlite3.connect(":memory:")

                # Execute the SQL script
                conn.executescript(sql_content)

                # Fetch the result as a DataFrame
                query_result = conn.execute("SELECT * FROM your_table")
                df = pd.DataFrame(query_result.fetchall(), columns=[desc[0] for desc in query_result.description])

            elif file.name.endswith('.txt'):
                # Read the text file content
                text_content = file.getvalue().decode("utf-8")

                # Convert the text to a DataFrame
                data = {'Text': [text_content]}
                df = pd.DataFrame(data)
        else:
            st.write("File does not have a supported extension.")

        st.dataframe(filter_dataframe(df))


        st.warning("DOWNLOAD BUTTON WAS TAKEN OUT DUE TO \
        FILES GETTING CORRUPTED.")
