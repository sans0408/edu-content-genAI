# AI-Powered Educational Content Generator

This project provides an AI-powered application designed to generate personalized educational content such as quizzes and flashcards based on user input. The application is built using Streamlit and can be run locally on your machine.

## Getting Started

Follow these steps to set up and run the application:

### 1. Clone the Repository

First, clone this repository to your local machine:

```bash
git clone https://github.com/sans0408/edu-content-genAI.git
cd edu-content-genAI
```

### 2. Create a Separate Folder to Run the Code

Create a new folder to keep the code isolated:

```bash
mkdir educational-content-generator
cd educational-content-generator
```

### 3. Open the Terminal

Ensure you're in the correct directory and open the terminal.

### 4. Create a Virtual Environment

Create a virtual environment to manage your dependencies:

```bash
python -m venv venv-name
```

Replace `venv-name` with the name you'd like to give your virtual environment.

### 5. Activate the Virtual Environment

Activate the virtual environment:

- On Windows:
  ```bash
  .\venv-name\Scripts\activate
  ```
- On macOS/Linux:
  ```bash
  source venv-name/bin/activate
  ```

### 6. Install Required Dependencies

Make sure you have Ollama installed on your PC. Then, install the necessary Python dependencies using the following command:

```bash
pip install -q -r requirements.txt
```

### 7. Run the Application

Finally, run the application using the following command:

```bash
streamlit run app.py
```

### 8. The Application is Ready to Use

Once the above command is executed, the application will start, and you can access it through your web browser. Enjoy using the AI-powered educational content generator!
