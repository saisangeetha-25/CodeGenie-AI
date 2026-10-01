# 🤖 CodeGenie AI – AI Code Generator & Explainer

**CodeGenie AI** is an AI-powered web application that helps users generate and understand code using natural language.

This project was developed as part of the **Infosys Springboard Virtual Internship 6.0 – Batch 13**, providing hands-on experience in Generative AI, Large Language Models, Python web development, API integration, and database management.

## 🚀 What is CodeGenie AI?

CodeGenie AI allows users to describe what they want to build in natural language and receive:

* AI-generated code
* A clear explanation of the generated code
* Syntax-highlighted code
* Options to save and manage generated code
* Code history and bookmarks

The project aims to make coding assistance more accessible by combining natural language interaction with Generative AI.

## ✨ Features

### 👤 User Features

* User registration and login
* Profile management
* AI-powered code generation
* AI-powered code explanation
* Code history
* Bookmark generated code
* Feedback submission
* Export generated code
* Login activity tracking

### 🛠️ Admin Features

* Admin authentication
* Admin dashboard
* User management
* Feedback management
* Usage analytics
* Login tracking

## 🧠 How It Works

```text
User enters a coding requirement
            ↓
       Flask Backend
            ↓
      OpenRouter API
            ↓
        GPT Model
            ↓
     Generated Code
            ↓
   Code Explanation
            ↓
     User Interface
```

Users can describe their requirement in natural language, and the application sends the request to an AI model through the OpenRouter API. The generated code and explanation are then displayed through the Flask web application.

## 🛠️ Tech Stack

| Technology     | Usage                           |
| -------------- | ------------------------------- |
| Python         | Application development         |
| Flask          | Web framework                   |
| SQLite         | Database                        |
| HTML           | Frontend structure              |
| CSS            | Styling                         |
| JavaScript     | Frontend interactions           |
| OpenRouter API | AI/LLM integration              |
| GPT Model      | Code generation and explanation |
| Prism.js       | Syntax highlighting             |
| Git & GitHub   | Version control                 |

## 📂 Project Structure

```text
CodeGenie-AI/
│
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
├── render.yaml
├── README.md
│
├── static/
│   ├── images/
│   ├── style.css
│   └── theme.js
│
└── templates/
    ├── landing.html
    ├── home.html
    ├── login.html
    ├── register.html
    ├── profile.html
    ├── history.html
    ├── bookmarks.html
    ├── feedback.html
    ├── analytics.html
    └── admin/
```

## 💻 Running the Project Locally

### 1. Clone the repository

```bash
git clone https://github.com/saisangeetha-25/CodeGenie-AI.git
cd CodeGenie-AI
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file based on `.env.example` and add your own API credentials.

Example:

```env
OPENROUTER_API_KEY=your_api_key_here
SECRET_KEY=your_secret_key_here
```

**Never commit your `.env` file or API keys to GitHub.**

### 5. Run the application

```bash
python app.py
```

Then open the local URL shown by Flask in your browser.

## 🎯 Learning Outcomes

Building CodeGenie AI helped me gain practical experience in:

* Python development
* Flask web application development
* Generative AI integration
* Large Language Models (LLMs)
* Prompt engineering
* REST/API integration
* SQLite database integration
* User authentication
* Frontend development
* Git and GitHub
* Building AI-powered applications

## 🎓 Internship Context

This project was developed as part of the:

**Infosys Springboard Virtual Internship 6.0 – Batch 13**

The internship provided an opportunity to apply technical concepts in a practical project and gain hands-on experience in AI and software development.

## 🔮 Future Enhancements

Possible future improvements include:

* AI-powered code debugging
* Code optimization suggestions
* Additional programming language support
* Improved code analysis
* Voice-based coding prompts
* Deployment as a publicly accessible web application

## 👩‍💻 Author

**Sai Sangeetha Padakanti**

B.Tech – Computer Science and Engineering

GitHub:
https://github.com/saisangeetha-25

LinkedIn:
https://www.linkedin.com/in/saisangeethapadakanti

---

⭐ If you find this project interesting, feel free to explore the repository.
