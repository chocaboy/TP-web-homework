from django.urls import path

from questions import views

app_name = 'questions'

urlpatterns = [
    path('', views.index, name="new_questions"),
    path('hot/', views.hot_questions, name="hot_questions"),
    path('ask/', views.ask, name="ask"),
    path('signup/', views.signup, name="signup"),
    path('login/', views.login, name="login"),
    path('settings/', views.settings, name="settings"),
    path('question/<int:question_id>/', views.question, name="question"),
    path('question/<int:question_id>/like/', views.like_question, name='like_question'),
    path('answer/<int:answer_id>/like/', views.like_answer, name='like_answer'),
    path('tag/<str:tag>/', views.tag, name='tag'),
]
