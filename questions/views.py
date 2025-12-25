from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from questions.models import Question, QuestionLike, Profile, Answer, AnswerLike, Tag
from questions.forms import LoginForm, SignUpForm, UserForm, ProfileForm, QuestionForm, AnswerForm


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


def get_popular_tags():
    return Tag.objects.annotate(
        num_questions=models.Count('question')
    ).order_by('-num_questions')[:15]


def index(request):
    tag_name = request.GET.get("tag")

    if tag_name:
        questions = Question.objects.by_tag(tag_name)
    else:
        questions = Question.objects.new()

    page = paginate(questions, request)

    return render(request, 'questions/index.html', {
        'questions': page.object_list,
        'page_obj': page,
        'tags': get_popular_tags(),
        'active_tag': tag_name,
    })


def hot_questions(request):
    questions = Question.objects.hot()  
    page = paginate(questions, request, per_page=3)

    return render(request, 'questions/hot.html', {
        'page_obj': page,
        'questions': page.object_list,
        'tags': get_popular_tags(),
    })


@login_required
def ask(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST, user=request.user)
        if form.is_valid():
            question = form.save()
            return redirect('questions:question', question_id=question.id)
    else:
        form = QuestionForm(user=request.user)
    
    return render(request, 'questions/ask.html', {
        'form': form,
        'tags': get_popular_tags(),
    })


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('questions:new_questions')
    else:
        form = SignUpForm()
    
    return render(request, 'questions/signup.html', {
        'form': form,
        'tags': get_popular_tags(),
    })


def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                next_url = request.GET.get('continue', 'questions:new_questions')
                return redirect(next_url)
            else:
                form.add_error(None, 'Invalid username or password')
    else:
        form = LoginForm()
    
    return render(request, 'questions/login.html', {
        'form': form,
        'tags': get_popular_tags(),
    })


@login_required
def logout(request):
    auth_logout(request)
    referer = request.META.get('HTTP_REFERER')
    if referer and any(page in referer for page in ['/settings/', '/ask/', '/profile/']):
        return redirect('questions:new_questions')
    return redirect(referer) if referer else redirect('questions:new_questions')


@login_required
def settings(request):
    user = request.user
    profile = user.profile
    
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('questions:settings')
    else:
        user_form = UserForm(instance=user)
        profile_form = ProfileForm(instance=profile)
    
    return render(request, 'questions/settings.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'tags': get_popular_tags(),
    })


def question(request, question_id):
    current_question = get_object_or_404(Question, id=question_id)
    answers = current_question.answer_set.all().order_by('-is_correct', '-created_at')
    page = paginate(answers, request, per_page=5)
    
    if request.method == 'POST' and request.user.is_authenticated:
        form = AnswerForm(request.POST, user=request.user, question=current_question)
        if form.is_valid():
            answer = form.save()
            page_num = request.GET.get('page', 1)
            return redirect(reverse('questions:question', args=[question_id]) + f'?page={page_num}#answer-{answer.id}')
    else:
        form = AnswerForm(user=request.user, question=current_question)
    
    return render(request, 'questions/question.html', {
        'question': current_question,
        'answers': page.object_list,
        'page_obj': page,
        'form': form,
        'tags': get_popular_tags(),
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


def tag(request, tag):
    questions = Question.objects.by_tag(tag)
    page = paginate(questions, request)

    return render(request, 'questions/tag.html', {
        'questions': page.object_list,
        'page_obj': page,
        'tag': tag,
        'tags': get_popular_tags(),
    })