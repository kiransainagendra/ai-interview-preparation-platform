from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from PyPDF2 import PdfReader
import google.generativeai as genai

from .forms import ResumeUploadForm
from .models import Resume


def extract_text_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    return text


def analyze_resume_with_ai(resume_text):
    text = resume_text.lower()

    skill_keywords = [
        "python", "java", "django", "flask", "html", "css", "javascript",
        "sql", "mysql", "postgresql", "mongodb", "aws", "azure", "git",
        "github", "machine learning", "deep learning", "artificial intelligence",
        "data structures", "react", "node", "api", "rest", "bootstrap",
        "pandas", "numpy", "scikit-learn", "power bi", "excel"
    ]

    found_skills = []
    for skill in skill_keywords:
        if skill in text:
            found_skills.append(skill.title())

    if not found_skills:
        found_skills = ["Basic Programming"]

    important_skills = ["Python", "Django", "REST API", "PostgreSQL", "GitHub", "Deployment", "SQL"]
    missing_skills = []

    for skill in important_skills:
        if skill.lower() not in text:
            missing_skills.append(skill)

    score = 50
    score += min(len(found_skills) * 4, 35)

    if "project" in text or "projects" in text:
        score += 5
    if "certification" in text or "certifications" in text:
        score += 5
    if "github" in text:
        score += 3
    if "linkedin" in text:
        score += 2

    score = min(score, 95)

    technical_questions = []

    if "python" in text:
        technical_questions.append("Explain Python OOP concepts with an example.")
    if "django" in text:
        technical_questions.append("Explain Django MVT architecture.")
    if "sql" in text or "mysql" in text or "postgresql" in text:
        technical_questions.append("What is the difference between SQL joins?")
    if "machine learning" in text or "artificial intelligence" in text:
        technical_questions.append("Explain overfitting and underfitting in machine learning.")
    if "aws" in text:
        technical_questions.append("What AWS services have you used and why?")

    while len(technical_questions) < 5:
        technical_questions.append("Explain one technical concept from your resume clearly.")

    return f"""
Resume Score: {score}/100

Profile Summary:
This resume is suitable for a fresher software developer profile. The candidate shows skills in {", ".join(found_skills[:7])}. The profile can be improved further by adding stronger project explanations, deployed links, and measurable achievements.

Strengths:
- Detected skills: {", ".join(found_skills)}
- Shows learning ability and technical interest
- Suitable for entry-level software development roles
- Contains relevant academic or technical background

Weaknesses:
- Project impact can be explained more clearly
- Achievements should include numbers or measurable results
- Resume should highlight GitHub and deployed project links more strongly

Missing Skills:
- {", ".join(missing_skills) if missing_skills else "Good core skill coverage found"}

Suggested Improvements:
- Add live deployed project links
- Add GitHub repository links for each project
- Mention tech stack clearly under every project
- Add measurable results such as accuracy, time saved, users, or performance improvement
- Add this Django AI Interview Platform as a major project

Technical Interview Questions:
1. {technical_questions[0]}
2. {technical_questions[1]}
3. {technical_questions[2]}
4. {technical_questions[3]}
5. {technical_questions[4]}

HR Interview Questions:
1. Tell me about yourself based on your resume.
2. Why should we hire you as a fresher?
3. What are your strengths and weaknesses?

Project-Based Questions:
1. Explain your best project from your resume.
2. What problem did your project solve?
3. What challenges did you face while building it?
4. How would you improve that project further?
"""
@login_required
def upload_resume(request):
    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES)

        if form.is_valid():
            resume = form.save(commit=False)
            resume.user = request.user

            extracted_text = extract_text_from_pdf(request.FILES['resume_file'])
            resume.extracted_text = extracted_text

            ai_analysis = analyze_resume_with_ai(extracted_text)
            resume.analysis = ai_analysis

            resume.save()
            return redirect('resume_result', resume_id=resume.id)
    else:
        form = ResumeUploadForm()

    return render(request, 'resumes/upload_resume.html', {'form': form})


@login_required
def resume_result(request, resume_id):
    resume = Resume.objects.get(id=resume_id, user=request.user)
    return render(request, 'resumes/result.html', {'resume': resume})