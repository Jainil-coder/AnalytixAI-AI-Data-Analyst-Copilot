import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json

from utils.gemini_client import client, MODEL
from utils.prompts import SYSTEM_PROMPT, build_analysis_prompt


ANALYSIS_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "reasoning_summary": {
            "type": "STRING"
        },
        "analysis_tasks": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "operation": {
                        "type": "STRING",
                        "enum": [
                            "summary",
                            "missing_values",
                            "duplicates",
                            "correlation",
                            "histogram",
                            "boxplot",
                            "countplot",
                            "scatter",
                            "bar",
                            "line",
                            "groupby",
                            "outliers",
                            "value_counts"
                        ]
                    },
                    "x_column": {
                        "type": ["STRING", "NULL"]
                    },
                    "y_column": {
                        "type": ["STRING", "NULL"]
                    },
                    "group_column": {
                        "type": ["STRING", "NULL"]
                    },
                    "aggregation": {
                        "type": "STRING",
                        "enum": ["sum", "mean", "median", "count"]
                    },
                    "title": {
                        "type": "STRING"
                    }
                },
                "required": [
                    "operation",
                    "x_column",
                    "y_column",
                    "group_column",
                    "aggregation",
                    "title"
                ]
            }
        }
    },
    "required": [
        "reasoning_summary",
        "analysis_tasks"
    ]
}


def create_plan(question, df):

    metadata = get_dataset_metadata(df)

    prompt = build_analysis_prompt(
        question,
        json.dumps(metadata, indent=2, default=str)
    )

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config={
            "system_instruction": SYSTEM_PROMPT,
            "response_mime_type": "application/json",
            "response_json_schema": ANALYSIS_SCHEMA,
            "temperature": 0.1
        }
    )

    if not response.text:
        raise ValueError("Gemini could not generate an analysis plan.")

    plan = json.loads(response.text)

    if not isinstance(plan.get("analysis_tasks"), list):
        raise ValueError("Invalid analysis plan returned by Gemini.")

    return plan

sns.set_theme(style="whitegrid")


def get_dataset_metadata(df):

    metadata = {
        "rows": len(df),
        "columns": len(df.columns),
        "column_details": {}
    }

    for col in df.columns:

        metadata["column_details"][col] = {
            "dtype": str(df[col].dtype),
            "unique_values": int(df[col].nunique()),
            "missing_values": int(df[col].isna().sum()),
            "sample_values": (
                df[col].dropna().head(5).astype(str).tolist()
            )
        }

    return metadata


def get_eda_summary(df):

    numeric_cols = df.select_dtypes(
        include=np.number
    ).columns.tolist()

    categorical_cols = df.select_dtypes(
        include=["object", "category", "bool"]
    ).columns.tolist()

    summary = {
        "shape": df.shape,
        "duplicates": int(df.duplicated().sum()),
        "missing_values": df.isna().sum().to_dict(),
        "numeric_summary": {},
        "categorical_summary": {}
    }

    if numeric_cols:
        summary["numeric_summary"] = (
            df[numeric_cols].describe().round(2).to_dict()
        )

    for col in categorical_cols:
        summary["categorical_summary"][col] = (
            df[col].value_counts().head(10).to_dict()
        )

    return summary


def execute_task(df, task):

    operation = task["operation"]

    x_col = task.get("x_column")
    y_col = task.get("y_column")
    group_col = task.get("group_column")

    agg = task.get("aggregation", "mean")
    title = task.get("title") or operation.replace("_", " ").title()

    # Validate columns
    for col in [x_col, y_col, group_col]:

        if col is not None and col not in df.columns:
            raise ValueError(f"Invalid column: {col}")

    result = None
    fig = None

    # SUMMARY
    if operation == "summary":

        result = df.describe(
            include="all"
        ).to_string()

    # MISSING VALUES
    elif operation == "missing_values":

        result = df.isnull().sum().to_string()

        missing = df.isnull().sum()
        missing = missing[missing > 0]

        if not missing.empty:
            fig, ax = plt.subplots(figsize=(10, 5))
            sns.barplot(
                x=missing.index,
                y=missing.values,
                ax=ax
            )
            ax.set_title("Missing Values by Column")
            ax.set_ylabel("Missing Count")
            ax.tick_params(axis="x", rotation=45)

    # DUPLICATES
    elif operation == "duplicates":

        result = (
            f"Duplicate rows: {df.duplicated().sum()}"
        )

    # CORRELATION
    elif operation == "correlation":

        numeric = df.select_dtypes(
            include=np.number
        )

        if numeric.shape[1] < 2:
            return "At least two numerical columns are required.", None

        correlation = numeric.corr()

        result = correlation.round(3).to_string()

        fig, ax = plt.subplots(figsize=(10, 7))

        sns.heatmap(
            correlation,
            annot=True,
            cmap="coolwarm",
            center=0,
            ax=ax
        )

        ax.set_title(title)

    # HISTOGRAM
    elif operation == "histogram":

        if not x_col or not pd.api.types.is_numeric_dtype(df[x_col]):
            raise ValueError("Histogram requires a numerical x_column.")

        fig, ax = plt.subplots(figsize=(9, 5))

        sns.histplot(
            data=df,
            x=x_col,
            kde=True,
            ax=ax
        )

        ax.set_title(title)

        result = df[x_col].describe().to_string()

    # BOXPLOT
    elif operation == "boxplot":

        if not x_col:
            raise ValueError("Boxplot requires an x_column.")

        fig, ax = plt.subplots(figsize=(9, 5))

        if y_col:
            if not pd.api.types.is_numeric_dtype(df[y_col]):
                raise ValueError("Boxplot y_column must be numeric.")

            sns.boxplot(
                data=df,
                x=x_col,
                y=y_col,
                ax=ax
            )
        else:
            if not pd.api.types.is_numeric_dtype(df[x_col]):
                raise ValueError("Boxplot requires a numerical x_column.")

            sns.boxplot(
                data=df,
                x=x_col,
                ax=ax
            )

        ax.set_title(title)

        result = "Boxplot generated."

    # COUNTPLOT
    elif operation == "countplot":

        if not x_col:
            raise ValueError("Countplot requires an x_column.")

        fig, ax = plt.subplots(figsize=(10, 5))

        sns.countplot(
            data=df,
            x=x_col,
            order=df[x_col].value_counts().head(15).index,
            ax=ax
        )

        ax.set_title(title)
        ax.tick_params(axis="x", rotation=45)

        result = df[x_col].value_counts().head(15).to_string()

    # SCATTER
    elif operation == "scatter":

        if not x_col or not y_col:
            raise ValueError("Scatter requires x_column and y_column.")

        if not (
            pd.api.types.is_numeric_dtype(df[x_col])
            and pd.api.types.is_numeric_dtype(df[y_col])
        ):
            raise ValueError("Scatter requires two numerical columns.")

        fig, ax = plt.subplots(figsize=(9, 5))

        sns.scatterplot(
            data=df,
            x=x_col,
            y=y_col,
            ax=ax
        )

        ax.set_title(title)

        result = (
            df[[x_col, y_col]]
            .corr()
            .round(3)
            .to_string()
        )

    # BAR
    elif operation == "bar":

        if not x_col or not y_col:
            raise ValueError("Bar chart requires x_column and y_column.")

        if not pd.api.types.is_numeric_dtype(df[y_col]):
            raise ValueError("Bar chart y_column must be numeric.")

        grouped = (
            df.groupby(x_col, dropna=False)[y_col]
            .agg(agg)
            .sort_values(ascending=False)
            .head(20)
        )

        fig, ax = plt.subplots(figsize=(10, 5))

        grouped.plot(
            kind="bar",
            ax=ax
        )

        ax.set_title(title)
        ax.set_ylabel(f"{agg} of {y_col}")
        ax.tick_params(axis="x", rotation=45)

        result = grouped.to_string()

    # LINE / TREND
    elif operation == "line":

        if not x_col or not y_col:
            raise ValueError("Line chart requires x_column and y_column.")

        dates = pd.to_datetime(
            df[x_col],
            errors="coerce"
        )

        values = pd.to_numeric(
            df[y_col],
            errors="coerce"
        )

        trend = pd.DataFrame({
            "date": dates,
            "value": values
        }).dropna()

        trend = (
            trend.groupby("date")["value"]
            .agg(agg)
            .sort_index()
        )

        if trend.empty:
            raise ValueError("No valid date and numerical values.")

        fig, ax = plt.subplots(figsize=(11, 5))

        trend.plot(
            ax=ax,
            marker="o"
        )

        ax.set_title(title)
        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)

        result = trend.head(1000).to_string()

    # GROUPBY
    elif operation == "groupby":

        if not group_col or not y_col:
            raise ValueError("Groupby requires group_column and y_column.")

        if not pd.api.types.is_numeric_dtype(df[y_col]):
            raise ValueError("Groupby y_column must be numeric.")

        grouped = (
            df.groupby(group_col, dropna=False)[y_col]
            .agg(agg)
            .sort_values(ascending=False)
            .head(20)
        )

        result = grouped.to_string()

        fig, ax = plt.subplots(figsize=(10, 5))

        grouped.plot(
            kind="bar",
            ax=ax
        )

        ax.set_title(title)
        ax.tick_params(axis="x", rotation=45)

    # OUTLIERS
    elif operation == "outliers":

        if not x_col or not pd.api.types.is_numeric_dtype(df[x_col]):
            raise ValueError("Outlier detection requires a numeric x_column.")

        values = pd.to_numeric(df[x_col], errors="coerce").dropna()

        q1 = values.quantile(0.25)
        q3 = values.quantile(0.75)

        iqr = q3 - q1

        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr

        outliers = df[
            (pd.to_numeric(df[x_col], errors="coerce") < lower)
            | (pd.to_numeric(df[x_col], errors="coerce") > upper)
        ]

        result = (
            f"Lower bound: {lower:.2f}\n"
            f"Upper bound: {upper:.2f}\n"
            f"Outlier count: {len(outliers)}\n\n"
            f"{outliers.head(100).to_string(index=False)}"
        )

    # VALUE COUNTS
    elif operation == "value_counts":

        if not x_col:
            raise ValueError("Value counts requires x_column.")

        result = (
            df[x_col]
            .value_counts(dropna=False)
            .head(20)
            .to_string()
        )

    else:
        raise ValueError(f"Unsupported operation: {operation}")

    return result, fig