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
[Summary in markdown format]''',
    'Average': '''You are an AI assistant who generates a detailed academic summary of the user's topic. It should quickly revise important concepts.
Use the following format:
**Topic Summary - [Topic]:**
[Summary in markdown format]''',
    'Advanced': f'''You are an AI assistant who generates a academic summary of the user's topic. It should quickly revise key concepts, but in depth.
Use the following format:
**Topic Summary - [Topic]:**
[Summary in markdown format]'''
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

st.set_page_config(
        page_title="Educational Content Gen",
        page_icon="📝"
        )

def load_student_data():
    '''Reads student scores from file using json module'''
    with open("student_scores.json", "r") as file:
        return json.load(file)

def save_student_data(data):
    '''Writes updated student data to file using json module'''
    with open("student_scores.json", "w") as file:
        json.dump(data, file, indent=4)

def get_student_category(score):
    '''Maps student scores to student categories'''
    if 1 <= score <= 5:
        return "Weak"
    elif 5 < score < 7.5:
        return "Average"
    else:
        return "Advanced"

def teacher_interface(student_data):
    '''Display the teacher's interface for updating scores'''
    st.header("User Role: Teacher", divider = 'blue')
    
    # Score Updation
    st.subheader(" \n\nUpdate Student Score", divider = 'gray')
    roll_no = st.text_input("Enter Student Roll Number")
    score = st.number_input("Enter CGPA Score", min_value=1.0, max_value=10.0, step=0.1)
    
    if st.button("Update Score"):
        if not roll_no.isdigit() or not (1 <= int(roll_no) <= 10):
            st.error("Invalid roll number. Please enter a roll number between 1 and 10.")
        elif not (1 <= score <= 10):
            st.error('Enter valid CGPA Score (1-10).')
        else:
            for student in student_data["students"]:
                if student["roll_no"] == roll_no:
                    student["score"] = score
                    save_student_data(student_data)
                    st.success(f"Test score for roll number {roll_no} updated to {score}.")
                    break

    # Student category for a specific roll number
    st.divider()
    st.subheader(" \n\nCheck Student Category", divider = 'gray')
    roll_no = st.text_input("Enter Your Roll Number")
    if st.button(f"Check category"):
        if not roll_no.isdigit() or not (1 <= int(roll_no) <= 10):
                st.warning("Invalid roll number. Please enter a roll number between 1 and 10.")
        else:
            roll_no = int(roll_no)
            student_found = None
            for student in student_data["students"]:
                if int(student["roll_no"]) == roll_no:
                    student_found = student
                    break

            if student_found:
                category = get_student_category(student_found["score"])
                div = {"Weak":'red',"Average":'blue',"Advanced":'green'}
                st.subheader(f"Student {roll_no} is in category: _{category}_", divider = div[category])

    # Comprehensive Student Performance Chart
    st.divider()
    st.subheader(" \n\nView student performance chart", divider = 'gray')
    if st.button('View Chart'):
        student_list = []
        for student in student_data["students"]:
            category = get_student_category(student["score"])
            student_list.append({
                "Roll Number": int(student["roll_no"]),
                "Score": student["score"],
                "Category": category
            })
        df = pd.DataFrame(student_list)
        
        # Display chart using altair
        st.subheader("Class Performance Chart")
        chart = alt.Chart(df).mark_bar().encode(
            x=alt.X('Roll Number:O', sort='ascending'),
            y='Score:Q',
            color={'field':'Category', 'type':'nominal', "scale": {"range": ["#85f496", "#83eef2", "#db4053"]}},
            tooltip=['Roll Number', 'Score', 'Category']
        ).interactive()
        
        st.altair_chart(chart, use_container_width=True)

def system_interface(student_data):
    '''Display all students' scores'''
    st.header("User Role: System Admin", divider = 'blue')
    
    if st.button("Display Student Scores"):
        student_list = []
        for student in student_data["students"]:
            category = get_student_category(student["score"])
            student_list.append({
                "Roll Number": student["roll_no"],
                "CGPA Score": student["score"],
                "Learner Category": category
            })
        
        df = pd.DataFrame(student_list)
        
        st.dataframe(df, hide_index = True, use_container_width = True, )

if 'clicked' not in st.session_state: # Initialise session_state for button click
    st.session_state.clicked = False

def click_button():
    '''Permanently mark clicked as True to avoid termination of 'if button clicked' block'''
    st.session_state.clicked = True

def submit_quiz():
    st.session_state.quiz_submitted = True

def student_interface(student_data):
    '''Student Interface that generates educational content - summary, quiz and flashcards'''
    st.header("User Role: Student", divider = 'blue')
    
    roll_no = st.text_input("Enter Your Roll Number")
    st.button('Revise Topics', on_click=click_button)

    if st.session_state.clicked: # if button is clicked, content will be displayed
        if not roll_no.isdigit() or not (1 <= int(roll_no) <= 10):
            st.warning("Invalid roll number. Please enter a roll number between 1 and 10.")
        else:
            roll_no = int(roll_no)
            student_found = None
            for student in student_data["students"]:
                if int(student["roll_no"]) == roll_no:
                    student_found = student
                    break

            if student_found:
                category = get_student_category(student_found["score"])

                # Select a topic to study
                topic = st.selectbox("Select Topic", ["Data Structures and Algorithms", "Object-Oriented Programming"], index = None, placeholder = "Select topic" )
                page = st.selectbox("Choose study mode", ["Summary", "Topic Quiz", "Flashcards"], index = None, placeholder = "Select mode")
                
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
                        
                        # Regular expression to match questions and answer options
                        pattern1 = r"\*\*Question (\d+):\*\* (.*?)\n\n\s*A\) (.*?)\n\s*B\) (.*?)\n\s*C\) (.*?)\n\s*D\) (.*?)\n\n"
                        
                        # Find all matches
                        matches = re.findall(pattern1, qz, re.DOTALL)
                        
                        # Create a nested dictionary from the matches
                        qd = {
                            f"{question_number}. {question_text}": {
                                "A": option_a.strip(),
                                "B": option_b.strip(),
                                "C": option_c.strip(),
                                "D": option_d.strip()
                            }
                            for question_number, question_text, option_a, option_b, option_c, option_d in matches
                        }

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
                            st.write(f"{question}\n\nYour answer: {st.session_state.answers[question]}")
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
                            st.button("View your answers")
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
    student_data = load_student_data()

    if role == "Teacher":
        teacher_interface(student_data)
    elif role == "System Admin":
        system_interface(student_data)
    else:
        student_interface(student_data)