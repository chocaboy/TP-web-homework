from django.shortcuts import render
from django.core.paginator import Paginator

QUESTIONS = []
for i in range(1,30):
  QUESTIONS.append({
    'title': 'title ' + str(i),
    'id': i - 1,
    'text': 'text' + str(i),
    'tags': ['tag' + str(i - 1), 'tag' + str(i)],
})
  
ANSWERS = []
for i in range(1,3):
    ANSWERS.append({
    'text': 'answer_text' + str(i),
})
    
USER = {
    'login': 'Dr. Pepper log',
    'nickname': 'Dr. Pepper',
    'email': 'DrPepper@mail.ru',
    'password': 'DrPepper',    
}

def index(request, *args, **kwargs):
    paginator = Paginator(QUESTIONS, per_page=3)
    page = request.GET.get('page', 1)
    question_page = paginator.page(page)
    return render(request, 'questions/index.html', context={"questions": question_page})

def hotQuestions(request, *args, **kwargs):
    paginator = Paginator(QUESTIONS[::-1], per_page=3)
    page = request.GET.get('page', 1)
    hot_question_page = paginator.page(page)
    return render(request, 'questions/hot.html', context={"questions": hot_question_page})

def tag(request, *args, **kwargs):
    tag_name = kwargs.get('tag')
    filtered = [q for q in QUESTIONS if tag_name in q['tags']]
    paginator = Paginator(filtered, per_page=1)
    page = request.GET.get('page', 1)
    filtered_tag_page = paginator.page(page)
    return render(request, 'questions/tag.html', {"questions": filtered_tag_page, "tag": tag_name})

def question(request, *args, **kwargs):
    return render(request, 'questions/question.html', context={"question": QUESTIONS[kwargs.get('id')], "answers": ANSWERS})

def login(request, *args, **kwargs):
    return render(request, 'questions/login.html')

def signup(request, *args, **kwargs):
    return render(request, 'questions/signup.html')

def ask(request, *args, **kwargs):
    return render(request, 'questions/ask.html')

def settings(request, *args, **kwargs):
    return render(request, 'questions/settings.html', context={"user": USER})
