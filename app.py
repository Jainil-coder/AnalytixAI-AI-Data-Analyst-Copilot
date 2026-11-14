import json
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from utils.analysis_engine import (
    get_dataset_metadata,
    get_eda_summary,
    create_plan,
    execute_task
)

from utils.gemini_client import generate_response


st.set_page_config(
    page_title="AnalytixAI: AI Data Analyst Copilot",
    layout="wide"
)


st.title("AnalytixAI")

st.write(
    "Upload your dataset and interact with it. "
    "Ask questions, request analyses, and receive insights."
)


# --------------------------------------------------
# FILE UPLOAD
# --------------------------------------------------

uploaded = st.file_uploader(
    "Upload your CSV file",
    type=["csv"]
)


if uploaded:

    try:

        df = pd.read_csv(uploaded)

        if df.empty or len(df.columns) == 0:
            st.error("The uploaded CSV contains no usable data.")
            st.stop()

        if not df.columns.is_unique:
            st.error("Duplicate column names are not supported.")
            st.stop()

        # ------------------------------------------
        # DATASET PREVIEW
        # ------------------------------------------

        st.subheader("Dataset Preview")

        st.dataframe(
            df.head(10),
            use_container_width=True
        )

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Rows", f"{len(df):,}")
        col2.metric("Total Columns", len(df.columns))
        col3.metric(
            "Duplicate Rows",
            f"{df.duplicated().sum():,}"
        )

        # ------------------------------------------
        # AUTOMATIC EDA
        # ------------------------------------------

        with st.expander("Automatic Exploratory Data Analysis"):

            st.subheader("Dataset Information")

            metadata = get_dataset_metadata(df)

            st.json(metadata)

            eda = get_eda_summary(df)

            st.subheader("Numerical Statistics")

            numeric_cols = df.select_dtypes(
                include=np.number
            ).columns.tolist()

            if numeric_cols:
                st.dataframe(
                    df[numeric_cols].describe().T,
                    use_container_width=True
                )
            else:
                st.info("No numerical columns found.")

            st.subheader("Missing Values")

            missing = df.isna().sum()

            st.dataframe(
                missing.rename("Missing Count"),
                use_container_width=True
            )

            if missing.sum() > 0:

                fig, ax = plt.subplots(figsize=(10, 4))

                sns.barplot(
                    x=missing.index,
                    y=missing.values,
                    ax=ax
                )

                ax.set_title("Missing Values by Column")
                ax.tick_params(axis="x", rotation=45)

                st.pyplot(fig)
                plt.close(fig)

            st.subheader("Correlation Heatmap")

            if len(numeric_cols) >= 2:

                fig, ax = plt.subplots(figsize=(10, 6))

                sns.heatmap(
                    df[numeric_cols].corr(),
                    annot=True,
                    cmap="coolwarm",
                    center=0,
                    ax=ax
                )

                ax.set_title("Feature Correlation")

                st.pyplot(fig)
                plt.close(fig)

            st.subheader("Numerical Distributions")

            for column in numeric_cols[:8]:

                fig, ax = plt.subplots(figsize=(8, 3))

                sns.histplot(
                    df[column].dropna(),
                    kde=True,
                    ax=ax
                )

                ax.set_title(f"Distribution of {column}")

                st.pyplot(fig)
                plt.close(fig)

        # ------------------------------------------
        # NATURAL LANGUAGE ANALYSIS
        # ------------------------------------------

        st.divider()

        st.subheader("Ask Your Data Analyst")

        question = st.text_area(
            "What would you like to understand?",
            placeholder=(
                "Example: Analyze sales performance, "
                "identify the top-performing categories, "
                "and visualize monthly trends."
            )
        )

        if st.button("Analyze Dataset", type="primary"):

            if not question.strip():

                st.warning("Please enter an analytical question.")

            else:

                try:

                    # STEP 1: GEMINI PLANNING

                    with st.spinner(
                        "AnalytixAI thinking..."
                    ):

                        plan = create_plan(question, df)

                    st.subheader("Analysis Strategy")

                    st.write(plan["reasoning_summary"])

                    with st.expander("View Generated Analysis Plan"):

                        st.json(plan)

                    # STEP 2: PYTHON EXECUTION

                    results = []
                    successful_tasks = 0

                    st.subheader("Analysis Results")

                    for index, task in enumerate(
                        plan["analysis_tasks"],
                        start=1
                    ):

                        st.markdown(
                            f"### {index}. {task['title']}"
                        )

                        try:

                            with st.spinner(
                                f"Executing {task['operation']}..."
                            ):

                                result, fig = execute_task(df, task)

                            successful_tasks += 1

                            st.write(result)

                            results.append({
                                "title": task["title"],
                                "operation": task["operation"],
                                "result": result
                            })

                            if fig is not None:

                                st.pyplot(fig)
                                plt.close(fig)

                        except Exception as task_error:

                            st.warning(
                                f"Could not execute this task: {task_error}"
                            )

                    if successful_tasks == 0:

                        st.error(
                            "No analytical tasks could be completed."
                        )
                        st.stop()

                    # STEP 3: GEMINI INTERPRETATION

                    st.divider()

                    st.subheader("AI-Generated Insights")

                    analysis_results = json.dumps(
                        results,
                        indent=2,
                        default=str
                    )

                    insight_prompt = f"""
The following results were calculated directly
using an uploaded dataset.

USER QUESTION:
{question}

COMPUTED RESULTS:
{analysis_results[:12000]}

Act as a Senior Data Analyst.

Interpret the computed results and prepare a
professional analytical report.

Follow these instructions:

1. Directly answer the user's question.
2. Identify the most important findings.
3. Highlight meaningful patterns and trends.
4. Explain relevant statistical observations.
5. Mention potential anomalies when supported.
6. Include important numerical values.
7. Explain business implications cautiously.
8. Identify limitations of the analysis.
9. Recommend further analysis where appropriate.

STRICT RULES:

- Only use facts supported by computed results.
- Do not invent numerical values.
- Do not invent relationships.
- Do not claim correlation implies causation.
- If a conclusion cannot be established,
  explicitly mention that limitation.
- Do not pretend to have performed operations
  that are not included in the results.

FORMAT:

## Executive Summary

## Key Findings

## Statistical Observations

## Business Implications

## Recommendations

## Limitations
"""

                    with st.spinner(
                        "AnalytixAI is preparing your analytical report..."
                    ):

                        insights = generate_response(
                            insight_prompt,
                            system_instruction=(
                                "You are a Senior Data Analyst. "
                                "Provide accurate, evidence-based "
                                "interpretations of computed data. "
                                "Never fabricate findings."
                            )
                        )

                    st.markdown(insights)

                    st.success(
                        f"Completed {successful_tasks} analytical tasks."
                    )

                except Exception as exc:

                    st.error(
                        f"Analysis failed: {exc}"
                    )

    except Exception as exc:

        st.error(
            f"Could not process the uploaded CSV: {exc}"
        )