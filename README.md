# GenAI-Powered Legal Assistant for SMEs

## Problem Statement
Small and Medium Enterprises (SMEs) often sign complex legal contracts without fully understanding hidden risks, unfavorable clauses, or long-term obligations. This lack of clarity can lead to financial losses, compliance issues, and legal disputes..

## Solution
This project is a GenAI-powered legal assistant designed to help SMEs quickly understand business contracts.
The application analyzes uploaded contract documents and:

-Extracts and previews contract text
-Identifies key clauses (Payment, Termination, Confidentiality, Penalty, etc.)
-Assesses risk levels (Low / Medium / High) using rule-based logic
-Generates AI-based summaries, risk explanations, and suggestions in simple business language
-Provides a downloadable PDF report for record-keeping

The system is built with safe fallback mechanisms, ensuring the application remains functional even if AI services are unavailable.

## Tech Stack
-Python
-Streamlit (UI & deployment)
-Rule-based NLP (clause detection & risk scoring)
-OpenAI API (GenAI integration with fallback handling)
-PDF processing (PyPDF2, FPDF)
-Docker & Render (cloud deployment)

🚀 Features

-Upload contracts in PDF, DOCX, or TXT
-Clause classification and risk scoring
-AI-generated legal insights (summary, risks, suggestions)
-Secure handling of API keys via environment variables
-Audit logging using hashed contract content
-One-click PDF report generation

🌐 Live Deployment

👉 https://legal-genai-hackathon.onrender.com/ 

Project Status

Phase 1 Completed
-Core contract analysis pipeline implemented
-GenAI integration with safe error handling
-Fully deployed and publicly accessible web application
-Future phases can extend this system with advanced NLP models, multilingual support, and deeper legal reasoning.
