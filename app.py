import streamlit as st
import json
import re
import pandas as pd
import altair as alt
import ollama   

summary_prompts = {
    'Weak': f'''You are an AI assistant who generates very detailed academic notes of the user's topic. It should revise all the basic concepts.
Use the following format:
**Topic Summary - [Topic]:**
[Summary in documented format]''',
    'Average': '''You are an AI assistant who generates a detailed academic summary of the user's topic. It should quickly revise important concepts.
Use the following format:
**Topic Summary - [Topic]:**
[Summary in documented format]''',
    'Advanced': f'''You are an AI assistant who generates a academic summary of the user's topic. It should quickly revise key concepts, but in depth.
Use the following format:
**Topic Summary - [Topic]:**
[Summary in documented format]'''
}

quiz_prompts = {
    'Weak': '''You are an AI assistant who creates a basic conceptual quiz based on the user's topic.
(The square brackets are placeholders)
Generate a quiz of 10 questions in the following format, provide the answer after each question:
    
**Quiz on [Topic]:**\n
**Instructions:** Choose the correct answer for each question. All the best!

**Question [Question number]:**[Question]

A)[Option A]
B)[Option B]
C)[Option C]
D)[Option D]
        
Answer: [Answer Option]''',
    'Average': '''You are an AI assistant who creates a moderate level quiz based on the user's topic.
(The square brackets are placeholders)
Generate a quiz of 10 questions in the following format, provide the answer after each question:
    
**Quiz on [Topic]:**\n
**Instructions:** Choose the correct answer for each question. All the best!

**Question [Question number]:**[Question]

A)[Option A]
B)[Option B]
C)[Option C]
D)[Option D]
        
Answer: [Answer Option]''',
    'Advanced': '''You are an AI assistant who creates a hard quiz based on the user's topic.
(The square brackets are placeholders)
Generate a quiz of 10 questions in the following format, provide the answer after each question:
    
**Quiz on [Topic]:**\n
**Instructions:** Choose the correct answer for each question. All the best!

**Question [Question number]:**[Question]

A)[Option A]
B)[Option B]
C)[Option C]
D)[Option D]
        
Answer: [Answer Option]'''
}

flashcard_prompts = {
    'Weak':'''You are an AI assistant who creates flashcards with basic questions and short answers based on the user's topic. Refer the following context for flashcards: {summary[2]['content']}
    \nGenerate 10 flashcards in the same format:
    
    **Card [Card number]:**
    Front: [Question]
    Back: [Answer]''',
    'Average':'''You are an AI assistant who creates flashcards with concept based questions and short answers based on the user's topic. Refer the following context for flashcards: {summary[2]['content']}
    \nGenerate 10 flashcards in the same format:
    
    **Card [Card number]:**
    Front: [Question]
    Back: [Answer]''',
    'Advanced':'''You are an AI assistant who creates flashcards with tough questions and short answers based on the user's topic. Refer the following context for flashcards: {summary[2]['content']}
    \nGenerate 10 flashcards in the same format:
    
    **Card [Card number]:**
    Front: [Question]
    Back: [Answer]'''
}

try:
    st.set_page_config(
            page_title="Educational Content Gen",
            page_icon="📝"
            )

    def save_student_data(data, filename="student_scores.csv"):
        '''Save the updated DataFrame to a CSV file'''
        data.to_csv(filename, index=False)
        st.success(f"Student data successfully saved to {filename}.")

    def load_student_data(filename="student_scores.csv"):
        '''Load student data from a CSV file'''
        return pd.read_csv(filename)

    def get_student_category(score):
        '''Maps student scores to student categories'''
        if 1 <= score <= 6:
            return "Weak"
        elif 6 < score < 9:
            return "Average"
        else:
            return "Advanced"

    def teacher_interface():
        st.header("User Role: Teacher", divider='blue')

        # Section to upload and view the CSV file
        st.subheader("\n\nUpload Student Scores CSV", divider='gray')
        passwd = 'teacher'
        passwd = st.text_input("Enter password",type='password')
        if st.checkbox("Enable Edits"):
            if passwd == 'teacher':
                uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

                if uploaded_file is not None:
                    df = pd.read_csv(uploaded_file)
                    st.dataframe(df,use_container_width=True)
                    if st.button("Save Uploaded Data"):
                        # Save or process the CSV data
                        df.to_csv("student_scores.csv", index=False)
                        st.success("CSV data has been saved successfully.")

            else:
                st.error("Incorrect Password! Access denied.")

        # Load student data
        df = load_student_data()

        # Check Student Category
        st.divider()
        st.subheader("Check Student Category", divider='gray')
        prn = st.text_input("Enter Student PRN to Check Category")
        if st.button("Check Category"):
            if not (prn in df['PRN'].astype(str).values):
                st.warning("Invalid PRN. Please enter a valid PRN.")
            else:
                avg_score = df.loc[df['PRN'] == prn, ["IE1", "MTE", "IE2", "ETE"]].mean(axis=1).values[0]
                category = get_student_category(avg_score)
                div = {"Weak": 'red', "Average": 'blue', "Advanced": 'green'}
                st.subheader(f"Student {prn} is in category: _{category}_", divider=div[category])

        # Comprehensive Student Performance Chart
        st.divider()
        st.subheader("View Student Performance Chart", divider='gray')

        if st.button('View Chart'):
            summary_df = df[['PRN', 'IE1', 'MTE', 'IE2', 'ETE']].copy()
            summary_df['Average Score'] = summary_df[['IE1', 'MTE', 'IE2', 'ETE']].mean(axis=1)
            summary_df['Category'] = summary_df['Average Score'].apply(get_student_category)

            # Display Pie Chart
            st.subheader("Class Performance Pie Chart")
            category_counts = summary_df['Category'].value_counts().reset_index()
            category_counts.columns = ['Category', 'Count']

            pie_chart = alt.Chart(category_counts).mark_arc().encode(
                theta=alt.Theta(field='Count', type='quantitative'),
                color=alt.Color(field='Category', type='nominal', scale=alt.Scale(range=["#85f496", "#83eef2", "#db4053"])),
                tooltip=['Category', 'Count']
            ).interactive()

            st.altair_chart(pie_chart, use_container_width=True)

        # View Top 5 Students per test
        st.divider()
        st.subheader("View Top 5 Students", divider='gray')
        test = st.selectbox("Select Test to View Top 5", df.columns[1:])
            
        if st.button("Show Top 5"):
            top_5_df = df[['PRN', test]].sort_values(by=test, ascending=False).head(5).reset_index(drop=True)
            st.table(top_5_df.style.hide(axis='index'))

        # View Top 5 Students overall
        st.divider()
        df['Total Score'] = df[['IE1', 'MTE', 'IE2', 'ETE']].sum(axis=1)
        st.subheader("Overall Toppers", divider='gray')
        top5 = df[['PRN', 'Total Score']].sort_values(by='Total Score', ascending=False).head(5)
        st.table(top5.style.hide(axis="index"))

    def system_interface():
        '''Display all students' scores'''
        st.header("User Role: System Admin", divider = 'blue')

        # Load student data
        df = load_student_data()

        # Editable CSV Option
        st.subheader("View and Edit Student Scores", divider='gray')

        psswd = 'admin'
        psswd = st.text_input('Enter password for admin rights:',type='password')
        if st.checkbox("Enable Edits"):
            if psswd == "admin":
                edited_df = st.data_editor(df,use_container_width=True)
                if st.button("Save Changes"):
                    save_student_data(edited_df)
            else:
                st.error("Incorrect Password for System Admin. Access denied.")

    if 'clicked' not in st.session_state: # Initialise session_state for button click
        st.session_state.clicked = False

    def click_button():
        '''Permanently mark clicked as True to avoid termination of 'if button clicked' block'''
        st.session_state.clicked = True

    def submit_quiz():
        st.session_state.quiz_submitted = True

    def student_interface():
        '''Student Interface that generates educational content - summary, quiz and flashcards'''
        st.header("User Role: Student", divider = 'blue')
        
        df = load_student_data()

        prn = st.selectbox("Select PRN",list(df['PRN'].values))
        st.button('Revise Topics', on_click=click_button)

        if st.session_state.clicked:  # if button is clicked, content will be displayed
            # Filter the row corresponding to the entered PRN
            student_row = df[df['PRN'] == prn]

            # Calculate the average score for non-null test values
            test_columns = ['IE1', 'MTE', 'IE2', 'ETE']
            scores = student_row[test_columns].dropna(axis=1, how='all').mean(axis=1).values[0]

            # Map the student category based on the aggregated score
            category = get_student_category(scores)

            # Select a topic to study
            topic = st.selectbox("Choose Topic",["Virtualization","Cloud Security","Word embedding in NLP","Types of tokenization",""])
            page = st.selectbox("Choose Study Mode", ["Summary", "Topic Quiz", "Flashcards"], index = None, placeholder = "Select mode")
            
            if page == "Summary":
                st.header("Summary")
                summary_prompt = summary_prompts[category]
                result = ollama.chat(model = "llama3.1:8b-instruct-q2_K", 
                                    messages = [{"role":"system","content":summary_prompt},
                                                {"role":"user","content":f'''User's topic: {topic}'''}])
                summary = result['message']['content']
                st.write(summary)

            elif page == "Topic Quiz":
                st.header("Quiz Questions")

                if 'saved_quiz_topic' not in st.session_state or st.session_state.saved_quiz_topic != topic:
                    quiz_prompt = quiz_prompts[category]                       
                    result = ollama.chat(model = "llama3.1:8b-instruct-q2_K", 
                                            messages = [{"role":"system","content":quiz_prompt},
                                                        {"role":"user","content":f'''User's topic: {topic}'''}])
                    qz = result['message']['content']
                    # print(qz)
                    # st.write(qz)
                    # Regular expression to extract the question, options, and answer
                    pattern1 = r"\*\*Question (\d+):\*\* (.*?)\n\n\s*A\) (.*?)\n\s*B\) (.*?)\n\s*C\) (.*?)\n\s*D\) (.*?)\n\n"

                    # Find matches
                    matches = re.findall(pattern1, qz, re.DOTALL)

                    # Process and create a dictionary from the matches
                    qd = {
                        f"{question_number}. {question_text}": {
                            "A": option_a.strip(),
                            "B": option_b.strip(),
                            "C": option_c.strip(),
                            "D": option_d.strip(),
                        }
                        for question_number, question_text, option_a, option_b, option_c, option_d in matches
                    }
                    # st.write(qd)
                    st.session_state.quiz_content = qd
                    st.session_state.saved_quiz_topic = topic  # Save the current topic
                    st.session_state.submitted = False
                    st.session_state.answers = {}

                # Retrieve the cached quiz content
                qd = st.session_state.quiz_content
                # st.write(qd)
                # Create radio buttons for each question
                for question in qd.keys():
                    st.divider()
                    if st.session_state.submitted:
                        # If quiz is submitted, show the selected answer and disable the radio button
                        st.write(f"{question}\n\nYour answer: {st.session_state.answers[question]}\n")

                    else:
                        # If quiz is not submitted, show the radio button to select an answer
                        answer = st.radio(
                            question,
                            [f"A. {qd[question]['A']}", f"B. {qd[question]['B']}", f"C. {qd[question]['C']}", f"D. {qd[question]['D']}"],
                            key=question
                        )
                        st.session_state.answers[question] = answer

                # Submit button
                if not st.session_state.submitted:
                    if st.button("Submit Quiz"):
                        st.session_state.submitted = True
                        st.write("Answers Submitted!")
                else:
                    st.warning("Your answers have been submitted. You cannot change them now.")

            elif page == "Flashcards":
                st.header("Flashcards")
                
                # Cache the flashcards to avoid regenerating them
                # Check if the topic has changed or flashcards need to be generated
                if 'saved_topic' not in st.session_state or st.session_state.saved_topic != topic:
                    flashcard_prompt = flashcard_prompts[category]
                    result = ollama.chat(model="llama3.1:8b-instruct-q2_K", 
                                        messages=[
                                            {"role": "system", "content": flashcard_prompt},
                                            {"role": "user", "content": f'''User's topic: {topic}'''}
                                        ])
                    flashcards = result['message']['content']
                    # print(flashcards)
                    st.session_state.flashcards = re.findall(r'Card \d+:.*?(?=Card \d+:|$)', flashcards, re.DOTALL)
                    st.session_state.saved_topic = topic  # Save the current topic


                cards = st.session_state.flashcards

                for i, card in enumerate(cards):
                    # Extract the front and back of the flashcard
                    front_match = re.search(r'Front:\s*(.*)Back:', card, re.DOTALL)
                    back_match = re.search(r'Back:\s*(.*)\*\*', card, re.DOTALL)
                    
                    if front_match:
                        front = re.sub(r'\s+', ' ', front_match.group(1)).strip()
                    else:
                        front = "No question provided."
                    
                    if back_match:
                        back = re.sub(r'\s+', ' ', back_match.group(1)).strip()
                    else:
                        back = "No answer provided."
                    
                    # Create a unique key for each flashcard state
                    key = f'flashcard_{i}'
                    
                    # Initialize the state if it doesn't exist
                    if key not in st.session_state:
                        st.session_state[key] = True
                    
                    # Button to flip the flashcard
                    if st.button(f"Flip Flashcard {i+1}", key=f"button_{key}"):
                        st.session_state[key] = not st.session_state[key]

                    # Display the question or the answer based on the state
                    if st.session_state[key]:
                        st.info(f"Question: {front}")
                    else:
                        st.info(f"Answer: {back}")

    if __name__ == "__main__":
        st.title("AI-Powered Educational Content Generator")
        # Select user role
        role = st.sidebar.selectbox("Select Your Role", ["Teacher", "System Admin", "Student"])

        if role == "Teacher":
            teacher_interface()
        elif role == "System Admin":
            system_interface()
        else:
            student_interface()

except Exception as e:
    st.error(f"An Exception Occurred: {e}")
