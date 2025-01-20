import json
import time
from collections import defaultdict

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests

import streamlit as st

# API base URL and token storage
API_BASE_URL = "http://localhost:8050/api"  # Replace with your actual API base URL
token = st.session_state.get("jwt_token", None)


# Function to make authenticated requests to the API
def make_api_request(endpoint, method="GET", data=None):
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{API_BASE_URL}/{endpoint}"

    if method == "GET":
        response = requests.get(url, headers=headers)
    elif method == "POST":
        response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200 or response.status_code == 201:
        return response.json()
    else:
        st.error(f"Error: {response.status_code} - {response.text}")
        return None


# Page 1: Login page for JWT token input
def login_page():
    st.title("Syncwise - Login")
    token_input = st.text_input("Enter JWT Token", type="password")
    if token_input:
        st.session_state["jwt_token"] = token_input
        st.success("Logged in successfully!")
        st.session_state["page"] = "Identify Subjects"  # Redirect to the next page
        st.rerun()  # Re-run to go to the next page


# Page 2: Identify Subjects
def identify_subjects():
    st.title("Identify Subjects")
    usn = st.text_input("Enter USN")
    result_url = st.text_input("Enter Result URL")

    if usn and result_url:
        data = {"usn": usn, "result_url": result_url}
        response = make_api_request("identify/", method="POST", data=data)
        if response:
            subjects = response.get("subjects", [])
            if subjects:
                st.write("Subjects Identified:")
                st.session_state["identified_subjects"] = subjects
                for subject in subjects:
                    st.write(f"{subject['sub_name']} ({subject['sub_code']})")
            else:
                st.warning("No subjects found.")
        else:
            st.warning("Failed to identify subjects.")

    if st.button("Next: Add Subjects to DB"):
        st.session_state["page"] = "Add Subjects to DB"
        st.rerun()


# Page 3: Add Subjects to DB
def add_subjects_to_db():
    st.title("Add Credits to Subjects")
    subjects = st.session_state.get("identified_subjects", [])

    if subjects:
        subject_data = []
        col1, col2 = st.columns(2)  # Create two columns
        for index, subject in enumerate(subjects):
            sub_name = subject["sub_name"]
            sub_code = subject["sub_code"]

            if index % 2 == 0:
                with col1:
                    st.markdown(f"##### {sub_name} ({sub_code})")
                    credits = st.number_input(
                        f"{sub_code} Credits:", min_value=1, max_value=10
                    )
                    sem = st.number_input(
                        f"{sub_code} Semester:", min_value=1, max_value=8
                    )
                    subject_data.append(
                        {
                            "sub_name": sub_name,
                            "sub_code": sub_code,
                            "credits": credits,
                            "sem": sem,
                        }
                    )
            else:
                with col2:
                    st.markdown(f"##### {sub_name} ({sub_code})")
                    credits = st.number_input(
                        f"{sub_code} Credits:", min_value=1, max_value=10
                    )
                    sem = st.number_input(
                        f"{sub_code} Semester:", min_value=1, max_value=8
                    )
                    subject_data.append(
                        {
                            "sub_name": sub_name,
                            "sub_code": sub_code,
                            "credits": credits,
                            "sem": sem,
                        }
                    )

        if st.button("Add Subjects"):
            response = make_api_request("subjects/", method="POST", data=subject_data)
            if response:
                st.write("Subjects added to database successfully!")
                st.session_state["subjects_in_db"] = response
            else:
                st.error("Failed to add subjects.")

        if st.button("Next: Scrape Results"):
            st.session_state["page"] = "Scrape Results"
            st.rerun()


# Page 4: Scrape Results by Batch
def scrape_batch_results():
    st.title("Scrape Results by Batch")
    batch = st.number_input("Enter Batch", min_value=1)
    semester = st.number_input("Enter Semester", min_value=1, max_value=8)
    result_url = st.text_input("Enter Result URL")

    if batch and semester and result_url and st.button("Scrape Results"):
        data = {"batch": batch, "semester": semester, "result_url": result_url}
        response = make_api_request("scrape/batch/", method="POST", data=data)
        if response:
            redis_names = response.get("redis_name")
            st.session_state["scraping_in_progress"] = redis_names
            st.write(f"Scraping task started. Tracking ID: {redis_names}")
        else:
            st.error("Failed to start scraping.")

    if st.button("Next: Track Progress"):
        st.session_state["page"] = "Track Progress"
        st.rerun()


# Page 5: Track Scraping Progress
def track_scraping_progress():
    st.title("Track Scraping Progress")
    redis_names = st.session_state.get("scraping_in_progress", None)

    for redis_name in redis_names:
        progress_bar = st.progress(0)

        while True:
            response = make_api_request(f"scrape/progress/{redis_name}/", method="GET")
            if response:
                progress = response.get("details", {})
                total = int(progress.get("total", 0))
                progress_count = int(progress.get("progress", 0))
                errors = progress.get("errors", [])

                if total > 0:
                    progress_percentage = int((progress_count / total) * 100)
                    progress_bar.progress(progress_percentage)
                    st.write(
                        f"Scraping Progress: {progress_count}/{total} ({progress_percentage}%)"
                    )
                else:
                    st.write("Total tasks not available.")

                if errors != "[]":
                    st.warning(f"Errors: {errors}")

                if progress_count == total:
                    st.success("Scraping completed!")
                    break
            else:
                st.warning("Unable to track progress.")
                break

            time.sleep(5)  # Wait before fetching progress again
    else:
        st.warning("No scraping task in progress.")

    if st.button("Next: Compute Performance"):
        st.session_state["page"] = "Compute Performance"
        st.rerun()


# Page 6: Compute Student Performance
def compute_performance():
    st.title("Compute Student Performance")
    batch = st.number_input("Enter Batch", min_value=1)
    semester = st.number_input("Enter Semester", min_value=1, max_value=8)

    if batch and semester and st.button("Compute Performance"):
        data = {"batch": batch, "semester": semester}
        response = make_api_request("scrape/performance/", method="POST", data=data)
        if response:
            st.success("Student performance computed successfully!")
        else:
            st.error("Failed to compute performance.")

    if st.button("Next: View Results"):
        st.session_state["page"] = "View Results"
        st.rerun()


def view_results():
    st.title("View Results and Performance")

    # Fetching data from API
    scores_response = make_api_request("scores/", method="GET")
    performance_response = make_api_request("student-performances/", method="GET")

    if scores_response and performance_response:
        # Process Scores
        scores_data = []
        for score in scores_response:
            student_scores = json.loads(score["marks"])
            scores_data.extend(student_scores)

        scores_df = pd.DataFrame(scores_data)

        scores_df["TOT"] = pd.to_numeric(scores_df["TOT"], errors="coerce")

        # Compute the average score per subject
        avg_scores = scores_df.groupby("Subject Code")["TOT"].mean().reset_index()

        # Compute FCD, FC, SC, Fail, and Absent counts per subject
        grade_counts = defaultdict(lambda: {"FCD": 0, "FC": 0, "SC": 0, "F": 0, "A": 0})
        for score in scores_data:
            subject_name = score["Subject Code"]
            total_marks = int(score["TOT"])
            result = score["Result"]

            if result == "P":
                if total_marks >= 75:
                    grade_counts[subject_name]["FCD"] += 1
                elif total_marks >= 60:
                    grade_counts[subject_name]["FC"] += 1
                else:
                    grade_counts[subject_name]["SC"] += 1
            elif result == "F":
                grade_counts[subject_name]["F"] += 1
            elif result == "A":
                grade_counts[subject_name]["A"] += 1

        # Display Average Score (Bar Chart)
        st.subheader("Average Score of Students in Each Subject")

        # Create a Plotly bar chart
        fig = px.bar(
            avg_scores,
            x="Subject Code",
            y="TOT",
            title="Average Score per Subject",
            labels={"Subject Code": "Subject Code", "TOT": "Average Total Score"},
            text="TOT",  # Display the score on top of each bar
        )

        # Customize the chart
        fig.update_traces(
            texttemplate="%{text:.2f}", textposition="outside"
        )  # Format and position text
        fig.update_layout(
            xaxis_title="Subject Code",
            yaxis_title="Average Total Score",
            yaxis=dict(showgrid=True),  # Add gridlines for better readability
            showlegend=False,
            title=dict(x=0.5),  # Center-align the title
        )

        # Render the chart in Streamlit
        st.plotly_chart(fig)

        # Display Grade Counts (Table)
        st.subheader("Student Performance Distribution (FCD, FC, SC, Fail, Absent)")
        grade_data = []
        for subject, counts in grade_counts.items():
            grade_data.append(
                {
                    "Subject Code": subject,
                    "FCD": counts["FCD"],
                    "FC": counts["FC"],
                    "SC": counts["SC"],
                    "Fail": counts["F"],
                    "Absent": counts["A"],
                }
            )
        grade_df = pd.DataFrame(grade_data)

        table_header = "| Subject Code | FCD | FC | SC | Fail | Absent |\n"
        table_header += "|------|------------|------|------------|------|------|\n"

        table_rows = ""
        for _, row in grade_df.iterrows():
            sub_code = row["Subject Code"]
            fcd = row["FCD"]
            fc = row["FC"]
            sc = row["SC"]
            f = row["Fail"]
            a = row["Absent"]

            table_rows += f"| {sub_code} | {fcd} | {fc} | {sc} | {f} | {a} |\n"

        st.markdown(table_header + table_rows)

        # Display Top 10 Scorers by SGPA (Leaderboard-style Table)
        st.subheader("Top 10 Scorers by SGPA")
        student_performance_df = pd.DataFrame(performance_response)
        student_performance_df.sort_values(by="sgpa", ascending=False, inplace=True)
        top_10_scorers = student_performance_df.head(10)
        # st.write(top_10_scorers[['id', 'sgpa']])
        # Display the leaderboard
        # Create a markdown table header
        table_header = "| Rank | Student ID | SGPA | Percentage |\n"
        table_header += "|------|------------|------|------------|\n"

        # Add rows to the table
        table_rows = ""
        i = 1
        for index, row in top_10_scorers.iterrows():
            rank = i
            i += 1
            student_id = row["id"]
            sgpa = row["sgpa"]
            percentage = row["percentage"]

            # Add each row to the table
            table_rows += f"| {rank} | {student_id} | {sgpa} | {percentage}% |\n"

        # Display the table in markdown
        st.markdown(table_header + table_rows)
        # Use markdown for a styled leaderboard row
        # st.markdown(f"**{index + 1}. Student ID: {student_id}** | SGPA: {sgpa} | Percentage: {percentage}%")

        # Display Pass, Fail, and Absent Percentage for Each Subject (Bar Chart)
        st.subheader("Pass, Fail, and Absent Percentage for Each Subject")
        pass_fail_counts = defaultdict(lambda: {"Pass": 0, "Fail": 0, "Absent": 0})
        # total_students = len(scores_response)

        for score in scores_data:
            subject_name = score["Subject Code"]
            result = score["Result"]
            if result == "P":
                pass_fail_counts[subject_name]["Pass"] += 1
            elif result == "F":
                pass_fail_counts[subject_name]["Fail"] += 1
            elif result == "A":
                pass_fail_counts[subject_name]["Absent"] += 1

        pass_fail_data = []
        for subject, counts in pass_fail_counts.items():
            total_subject_students = counts["Pass"] + counts["Fail"] + counts["Absent"]
            pass_percent = (counts["Pass"] / total_subject_students) * 100
            fail_percent = (counts["Fail"] / total_subject_students) * 100
            absent_percent = (counts["Absent"] / total_subject_students) * 100
            pass_fail_data.append(
                {
                    "Subject Name": subject,
                    "Pass (%)": pass_percent,
                    "Fail (%)": fail_percent,
                    "Absent (%)": absent_percent,
                }
            )

        pass_fail_df = pd.DataFrame(pass_fail_data)
        # pass_fail_plot = pass_fail_df.set_index('Subject Name')[['Pass (%)', 'Fail (%)', 'Absent (%)']].plot(kind='bar')
        # plt.title('Pass, Fail, and Absent Percentage per Subject')
        # plt.ylabel('Percentage')
        # st.pyplot(plt.gcf())
        # plt.clf()

        # Create a Plotly bar chart for Pass, Fail, and Absent percentages
        fig = go.Figure()

        # Add bars for each category
        fig.add_trace(
            go.Bar(
                x=pass_fail_df["Subject Name"],
                y=pass_fail_df["Pass (%)"],
                name="Pass (%)",
                marker_color="green",
            )
        )
        fig.add_trace(
            go.Bar(
                x=pass_fail_df["Subject Name"],
                y=pass_fail_df["Fail (%)"],
                name="Fail (%)",
                marker_color="red",
            )
        )
        fig.add_trace(
            go.Bar(
                x=pass_fail_df["Subject Name"],
                y=pass_fail_df["Absent (%)"],
                name="Absent (%)",
                marker_color="orange",
            )
        )

        # Customize the layout
        fig.update_layout(
            title="Pass, Fail, and Absent Percentage per Subject",
            xaxis_title="Subject Name",
            yaxis_title="Percentage",
            barmode="group",  # Bars will appear side by side
            xaxis=dict(tickangle=-45),  # Tilt x-axis labels for better readability
            legend_title="Category",
            # title=dict(x=0.5),  # Center-align the title
            height=600,  # Adjust chart height
        )

        # Render the chart in Streamlit
        st.plotly_chart(fig)

        # Display Overall Pass, Fail, and Absent Percentage (Pie Chart)
        st.subheader("Overall Pass, Fail, and Absent Percentage")
        overall_counts = {"Pass": 0, "Fail": 0, "Absent": 0}

        for score in scores_data:
            result = score["Result"]
            if result == "P":
                overall_counts["Pass"] += 1
            elif result == "F":
                overall_counts["Fail"] += 1
            elif result == "A":
                overall_counts["Absent"] += 1

        total = (
            overall_counts["Pass"] + overall_counts["Fail"] + overall_counts["Absent"]
        )
        pass_percent = (overall_counts["Pass"] / total) * 100
        fail_percent = (overall_counts["Fail"] / total) * 100
        absent_percent = (overall_counts["Absent"] / total) * 100

        # fig, ax = plt.subplots()
        # ax.pie([pass_percent, fail_percent, absent_percent], labels=['Pass', 'Fail', 'Absent'], autopct='%1.1f%%', startangle=90)
        # ax.axis('equal')
        # plt.title('Overall Pass, Fail, and Absent Percentage')
        # st.pyplot(fig)

        # Define the data for the pie chart
        labels = ["Pass", "Fail", "Absent"]
        values = [pass_percent, fail_percent, absent_percent]

        # Create the pie chart using Plotly Express
        fig = px.pie(
            values=values,
            names=labels,
            hole=0.4,  # Optional: Makes it a donut chart if you prefer
        )

        # Customize the chart
        fig.update_traces(
            textinfo="percent+label",  # Display percentage and label inside the chart
            marker=dict(colors=["green", "red", "orange"]),  # Assign colors
        )
        fig.update_layout(
            height=500,  # Adjust chart height
        )

        # Render the chart in Streamlit
        st.plotly_chart(fig)

        # Display Top Scores in Each Subject (Table)
        st.subheader("Top Scores in Each Subject")
        top_scores = []
        for subject, scores in scores_df.groupby("Subject Code"):
            top_score = scores.loc[scores["TOT"].idxmax()]
            print(top_score, flush=True)
            top_scores.append(
                {
                    "Subject Code": subject,
                    "Top Score": top_score["TOT"],
                }
            )

        top_scores_df = pd.DataFrame(top_scores)
        st.write(top_scores_df)

    # Navigation Button to go back to the start
    if st.button("Back to Start"):
        st.session_state["page"] = "Identify Subjects"
        st.rerun()


# Main app logic to navigate between pages
def main():
    if "jwt_token" not in st.session_state:
        st.session_state["page"] = "Login"  # Redirect to login page if not logged in

    page = st.session_state.get("page", "Login")

    if page == "Login":
        login_page()
    elif page == "Identify Subjects":
        identify_subjects()
    elif page == "Add Subjects to DB":
        add_subjects_to_db()
    elif page == "Scrape Results":
        scrape_batch_results()
    elif page == "Track Progress":
        track_scraping_progress()
    elif page == "Compute Performance":
        compute_performance()
    elif page == "View Results":
        view_results()


# Run the app
if __name__ == "__main__":
    main()
