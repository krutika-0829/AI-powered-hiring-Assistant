import streamlit as st
import requests


BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Resume AI System",
    layout="wide"
)

st.title("AI Resume Screening System")
menu = st.sidebar.selectbox(
    "Select Feature",
    [
        "Upload Resumes",
        "Ask Questions",
        "Job Description Matching"
    ]
)



if menu == "Upload Resumes":
   st.header("Upload PDF Resumes")
   uploaded_files = st.file_uploader(
        "Choose PDF files",
        type=["pdf"],
        accept_multiple_files=True
    )

   if st.button("Upload Resumes"):

      if uploaded_files:

        files = []
        for file in uploaded_files:
            files.append(("files",(file.name,file,"application/pdf")))

        try:
                response = requests.post(
                    f"{BASE_URL}/upload_resume",
                    files=files
                )

                data = response.json()

                if response.status_code == 200:
                    st.success(data["message"])

                else:
                    st.error(data)

        except Exception as e:
                st.error(f"Error: {e}")

      else:
        st.warning("Please upload at least one PDF file")




elif menu == "Ask Questions":

    st.header("Ask Questions About Candidates")

    query = st.text_area(
        "Enter your question",
        placeholder="Example: What are Michelle Lopez's design skills?"
    )

    if st.button("Get Answer"):

        if query.strip() != "":

            payload = {
                "query": query
            }

            try:

                response = requests.post(
                    f"{BASE_URL}/user_query",
                    json=payload
                )

                data = response.json()

                if response.status_code == 200:

                    st.subheader("Answer")
                    st.write(data["result"])

                else:
                    st.error(data)

            except Exception as e:
                st.error(f"Error: {e}")

        else:
            st.warning("Please enter a question")




elif menu == "Job Description Matching":

    st.header("Resume Matching By Job Description")

    jd = st.text_area(
        "Enter Job Description",
        height=250,
        placeholder="Paste the job description here..."
    )

    if st.button("Match Candidates"):

        if jd.strip() != "":

            payload = {
                "text": jd
            }

            try:

                response = requests.post(
                    f"{BASE_URL}/job_description",
                    json=payload
                )

                data = response.json()

                if response.status_code == 200:

                    st.subheader("Matching Results")
                    st.write(data["result"])

                else:
                    st.error(data)

            except Exception as e:
                st.error(f"Error: {e}")

        else:
            st.warning("Please enter a job description")
    