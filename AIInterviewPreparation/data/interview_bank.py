"""
interview_bank.py
Question bank for the AI Mock Interview module (typed + voice answers).
"""

MOCK_INTERVIEW_QUESTIONS = [
    "Tell me about yourself.",
    "Why should we hire you?",
    "Describe your final year project.",
    "Explain your strengths.",
    "Explain your weaknesses.",
    "What are your career goals?",
    "Why do you want this job?",
    "How do you handle tight deadlines?",
    "Describe a time you solved a difficult technical problem.",
    "What is your greatest professional achievement?",
    "How do you keep your technical skills up to date?",
    "Describe your experience working in a team.",
    "What tools or technologies are you most comfortable with?",
    "How would you explain a complex technical concept to a non-technical person?",
    "What do you do when you don't know the answer to a problem?",
]

# Simple keyword-based evaluation hints used to give lightweight, offline
# "AI-style" feedback on typed/spoken answers without any external API.
EVALUATION_KEYWORDS = {
    "positive": [
        "experience", "team", "project", "learned", "improved", "achieved",
        "responsible", "led", "developed", "built", "solved", "communication",
        "collaborat", "result", "impact", "goal", "challenge", "skill",
    ],
    "filler": ["um", "uh", "like", "you know", "actually", "basically"],
}
