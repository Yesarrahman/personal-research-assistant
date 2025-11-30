# Personal Research Assistant Agent
**Multi-Agent AI System for Automated Web Research**  
**Google AI Agents Intensive – Capstone Project**  
**Track:** Concierge Agents  
**Author:** Yesar Rahman  
**Date:** November 2025

---

## 📋 Table of Contents
- [Overview](#overview)
- [Problem Statement](#problem-statement)
- [Solution](#solution)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Technical Details](#technical-details)
- [Results & Impact](#results--impact)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

---

## Overview
The **Personal Research Assistant Agent** is an intelligent multi-agent system that automates web research tasks.  
It uses three specialized AI agents powered by **Google Gemini 2.5** to search, analyze, and synthesize information from multiple sources—reducing research time from **hours to minutes**.

### Quick Stats

| Metric | Value |
|--------|-------|
| **Time Savings** | 92% reduction (2–3 hours → 10–15 minutes) |
| **Sources Analyzed** | 5–10 per query |
| **AI Models** | Gemini 2.5 Flash-Lite & Flash |
| **Agents** | 3 specialized agents |
| **Lines of Code** | ~800 |

---

## Problem Statement

### The Challenge
Conducting research online is time-consuming, overwhelming, and prone to errors.

#### 1. Time Consumption
- Manual research takes hours  
- Students spend 10–15 hours per paper  
- Professionals lose hours weekly on market research

#### 2. Information Overload
- Millions of Google results  
- Hard to evaluate credibility  
- Wasted time filtering

#### 3. Poor Synthesis
- Manually summarizing multiple sources  
- High cognitive load  
- Error-prone

#### 4. Context Loss
- Research rarely completed in one session  
- Have to rebuild mental context

#### 5. Citation Management
- Manual APA formatting  
- Easy to make mistakes

### Who This Affects
- **Students**
- **Professionals**
- **Journalists**
- **Researchers**
- **General learners**

---

## Solution

### Multi-Agent Research Automation
The system uses a **coordinated multi-agent workflow**:

User Query → Coordinator → Researcher → Summarizer → Final Report


### Agent Breakdown

---

### 1. Coordinator Agent (Gemini 2.5 Flash-Lite)
- Analyzes user queries  
- Creates research plans  
- Identifies key focus areas  

---

### 2. Researcher Agent (Gemini 2.5 Flash)
- Optimized search queries  
- Fetches sources via Google Custom Search API  
- Filters and validates sources  

---

### 3. Summarizer Agent (Gemini 2.5 Flash-Lite)
- Synthesizes information  
- Produces structured reports  
- Generates APA citations  

---

### Value Proposition

| Before | After |
|--------|-------|
| 2–3 hours of research | 10–15 minutes automated |
| 3–5 manually read sources | 5–10 sources auto-analyzed |
| Scattered notes | Structured report |
| Lost context | Session memory |
| Manual APA citations | Auto-generated |

---

## Key Features

### 🧠 Multi-Agent Architecture
- Three specialized AI agents  
- Clear roles & workflow  

### 🔎 Intelligent Search
- Query optimization  
- Credibility scoring  
- Search fallback (mock data)  

### 🧾 Comprehensive Synthesis
- Multi-source summaries  
- Structured report  
- Key findings  

### 💾 Session Management
- Saves previous queries  
- Handles follow-ups  

### 🛡 Robust Error Handling
- Clear error messages  
- Graceful fallback logic  

---

## 🏗 Architecture

### System Design Diagram

┌───────────────────────────────┐
│ User Interface (main.py) │
└───────────────┬───────────────┘
▼
┌───────────────────────────────┐
│ ResearchAssistantSystem │
└─────┬──────────┬──────────┬────┘
│ │ │
▼ ▼ ▼
┌──────────┐ ┌──────────┐ ┌─────────────┐
│Coordinator│ │Researcher│ │Summarizer │
└──────────┘ └─────┬────┘ └─────────────┘
▼
┌──────────────────────┐
│ Google Custom Search │
└──────────────────────┘


---

## 📦 Installation

### Prerequisites
- Python 3.9+
- Google Gemini API Key
- (Optional) Google Custom Search API Key

---

### Step 1 — Clone Repository
```bash
git clone https://github.com/yourusername/research-assistant-agent.git
cd research-assistant-agent

### Step 2 — Create Virtual Environment
python -m venv venv
venv\Scripts\activate   # Windows

source venv/bin/activate   # Mac/Linux

Step 2 — Create Virtual Environment
python -m venv venv
venv\Scripts\activate   # Windows

source venv/bin/activate   # Mac/Linux

Step 3 — Install Dependencies
pip install -r requirements.txt

Step 4 — Configure Environment

Create a .env file:

GOOGLE_API_KEY=your_gemini_api_key

GOOGLE_SEARCH_API_KEY=your_search_api_key
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id

Step 5 — Run Project
python main.py

💻 Usage
Basic Run
python main.py

Example Output
📋 Query: What is quantum computing?
📚 Sources: 5
📄 Summary: ...
🔑 Key Findings: ...
📚 Sources: ...

Follow-Up

The system supports follow-up queries using the same session context.

📁 Project Structure
research-assistant-agent/
│
├── main.py
├── requirements.txt
├── .env
├── README.md
├── LICENSE
│
├── agents/
│   ├── coordinator.py
│   ├── researcher.py
│   └── summarizer.py
│
└── utils/
    └── session_manager.py

🔧 Technical Details
Technologies Used
Technology	Purpose
Python 3.9+	Core language
Google Gemini API	AI processing
Custom Search API	Web search
Dotenv	Environment variables
🤝 Contributing
git checkout -b feature/AmazingFeature
git commit -m "Add feature"
git push origin feature/AmazingFeature

📄 License

This project is under the MIT License.

🙏 Acknowledgments

Google Gemini API

Python

Kaggle community

Google AI Agents Intensive course

📞 Contact

Author: Yesar Rahman
Email: yesarrahman@gmail.com

GitHub: https://github.com/Yesarrahman

LinkedIn: https://www.linkedin.com/in/yesar-rahman-04463643/

⭐ GitHub Stats


