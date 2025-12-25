from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db import models
from questions.models import Question, QuestionLike, Profile, Answer, AnswerLike, Tag

def tag(request, tag):
    questions = Question.objects.by_tag(tag)
    page = paginate(questions, request)

    return render(request, 'questions/tag.html', {
        'questions': page.object_list,
        'tag': tag
    })


def paginate(objects_list, request, per_page=10):
    page_num = request.GET.get('page', 1) 
    paginator = Paginator(objects_list, per_page)
    
    try:
        page = paginator.page(page_num)
    except (PageNotAnInteger, ValueError):
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)
        
    return page

def index(request):
    tag_name = request.GET.get("tag")

    if tag_name:
        questions = Question.objects.by_tag(tag_name)  # Фильтрация по тегу
    else:
        questions = Question.objects.new()  # Новые вопросы

    page = paginate(questions, request)

    popular_tags = Tag.objects.annotate(
        num_questions=models.Count('question')
    ).order_by('-num_questions')[:15]

    return render(request, 'questions/index.html', {
        'questions': page.object_list,
        'page_obj': page,
        'tags': popular_tags,
        'active_tag': tag_name,
    })


def hot_questions(request):
    questions = Question.objects.hot()  
    page = paginate(questions, request, per_page=3)

    popular_tags = Tag.objects.annotate(num_questions=models.Count('question')).order_by('-num_questions')[:15]

    return render(request, 'questions/hot.html', {
        'page_obj': page,
        'questions': page.object_list,
        'tags': popular_tags,
    })


def ask(request):
    return render(request, 'questions/ask.html')

def signup(request):
    return render(request, 'questions/signup.html')

def login(request):
    return render(request, 'questions/login.html')

def settings(request):
    return render(request, 'questions/settings.html')

def question(request, question_id):
    current_question = get_object_or_404(Question, id=question_id)
    answers = current_question.answer_set.all()
    page = paginate(answers, request, per_page=5)
    
    return render(request, 'questions/question.html', {
        'question': current_question,
        'answers': page.object_list,
        'page_obj': page
    })

@login_required
def like_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    profile = request.user.profile
    
    like, created = QuestionLike.objects.get_or_create(user=profile, question=question)
    
    if not created:
        like.delete()
    
    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def like_answer(request, answer_id):
    answer = get_object_or_404(Answer, id=answer_id)
    profile = request.user.profile 

    like, created = AnswerLike.objects.get_or_create(user=profile, answer=answer)

    if not created:
        like.delete()

    return redirect(request.META.get('HTTP_REFERER', '/'))
