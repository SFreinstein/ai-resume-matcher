# AI Resume Matcher

An intelligent, full-stack web application that allows users to upload their resumes and receive AI-generated matches with job listings. Powered by Google’s **Gemini API**, **FastAPI**, **PostgreSQL**, and a simple **Streamlit frontend**, this app demonstrates the use of semantic similarity in real-world job applications.

---

## 🌟 Features

✅ User registration and login (JWT-secured)  
✅ Resume upload (.txt or .pdf)  
✅ AI-powered job-resume matching  
✅ Top 5 relevant jobs returned with similarity scores  
✅ Easily extensible and Dockerized for deployment  

---

## 📁 Project Structure

```
AI-Resume-Matcher/
├── backend/
│   ├── main.py            # FastAPI app & endpoints
│   ├── llm.py             # Gemini API integration
│   ├── models.py          # SQLAlchemy ORM models
│   ├── db.py              # PostgreSQL session config
│   └── config.py          # Loads environment variables
├── frontend/
│   ├── app.py             # Streamlit app
│   └── requirements.txt   # Frontend Python packages
├── docker-compose.yml     # Multi-container Docker setup
├── .env                   # Secrets and config (not committed to Git)
└── README.md              # This file
```

---

## 🧠 How It Works

1. User registers and logs in (password is hashed and verified).
2. User uploads their resume (`.txt` or `.pdf`).
3. Backend stores resume and queries job listings.
4. For each job:
   - Resume and job description are sent to the **Gemini API**.
   - Similarity score is returned.
   - Top 5 matches are saved and returned to the frontend.
5. The user views the top matches in Streamlit.

---

## 🔐 Setup Environment Variables

Create a file named `.env` in the root directory:

```env
# .env
SECRET_KEY=key123
DATABASE_URL=postgresql://user:password@db:5432/mydatabase
GEMINI_API_KEY=your_actual_gemini_api_key
GEMINI_API_URL=https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-pro:generateContent
```

📝 Get your Gemini API key and info here:  
👉 https://aistudio.google.com/app/apikey

---

## ⚙️ Running the Project

### 🐧 Ubuntu Terminal (Linux)

```bash
# Navigate to your project directory
cd ~/AI-Resume-Matcher

# Build and run the containers
sudo docker-compose up --build
```

### 🪟 Windows Terminal (PowerShell or CMD)

```powershell
# Navigate to your project directory
cd C:\Path\To\AI-Resume-Matcher

# Build and run the containers
docker-compose up --build
```

---

## 🔎 Access the App

- 🌐 Frontend: [http://localhost:8501](http://localhost:8501)  
- 📘 Backend docs (Swagger UI): [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🧪 Sample Job Data

The backend seeds sample job data automatically at startup:

| Job Title          | Description                                                   |
|--------------------|---------------------------------------------------------------|
| Software Engineer  | Develop backend services using Python and FastAPI.            |
| Data Scientist     | Analyze datasets and build ML models using Python.            |
| Frontend Developer | Build responsive UIs using React and JavaScript.              |
| DevOps Engineer    | Manage CI/CD pipelines, Docker containers, cloud infra.       |
| AI Researcher      | Research and implement AI models in natural language tasks.   |

---

## 🙋 FAQ

**Q: Can I change the job list?**  
Yes! You can modify or extend `seed_jobs()` in `main.py` or add a database UI later.

**Q: Where are user sessions stored?**  
Session tokens are stored in memory using JWTs. No persistent sessions.

**Q: What if I don’t get any matches?**  
Ensure your `.env` and Gemini key are valid, and that the resume is well-formed.

---

## 📎 License

This project is for educational use and demonstration purposes. No license restrictions, but please cite or credit when used.

---
