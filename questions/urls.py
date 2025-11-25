from django.urls import path

from questions.views import index, question, hotQuestions, tag, login, signup, ask, settings

app_name = 'questions'

urlpatterns = [
    path('', index, name='new_questions'),
    path('hot/', hotQuestions, name='hot_questions'),
    path('tag/<str:tag>/', tag, name='tag'),
    path('question/<int:id>/', question, name='question'),
    path('login/', login, name='login'),
    path('signup/', signup, name='signup'),
    path('ask/', ask, name='ask'),
    path('settings/', settings, name='settings'),
]