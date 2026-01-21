from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from questions.models import Profile, Question, Answer, Tag


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your login'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '*******'})
    )


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    avatar = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter your login'})
        self.fields['email'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter your Email here'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': '************'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': '************'})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data.get('email')
        if commit:
            user.save()
            avatar = self.cleaned_data.get('avatar')
            profile, _ = Profile.objects.get_or_create(user=user)
            if avatar:
                profile.avatar = avatar
            profile.save()
        return user


class UserForm(forms.ModelForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ('username', 'email')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('avatar',)
        widgets = {
            'avatar': forms.ClearableFileInput(attrs={'class': 'form-control'})
        }


class QuestionForm(forms.ModelForm):
    tags = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter tags separated by commas'})
    )

    class Meta:
        model = Question
        fields = ['title', 'text', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter question title'}),
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 10, 'placeholder': 'Enter question text'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) < 10:
            raise forms.ValidationError("Заголовок должен содержать не менее 10 символов")
        return title

    def clean_text(self):
        text = self.cleaned_data.get('text')
        if len(text) < 20:
            raise forms.ValidationError("Текст должен содержать не менее 20 символов")
        return text

    def save(self, commit=True):
        question = super().save(commit=False)
        if self.user:
            profile, _ = Profile.objects.get_or_create(user=self.user)
            question.user = profile

        if commit:
            question.save()
            self._save_tags(question)
        return question

    def _save_tags(self, question):
        tags_input = self.cleaned_data.get('tags', '')
        if tags_input:
            tag_names = [name.strip() for name in tags_input.split(',') if name.strip()]
            for tag_name in tag_names:
                tag, created = Tag.objects.get_or_create(name=tag_name)
                question.tags.add(tag)


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter your answer here...'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.question = kwargs.pop('question', None)
        super().__init__(*args, **kwargs)

    def clean_text(self):
        text = self.cleaned_data.get('text')
        if len(text) < 10:
            raise forms.ValidationError("Ответ должен быть длиннее 10 символов.")
        return text

    def save(self, commit=True):
        answer = super().save(commit=False)
        if self.user and self.question:
            profile, _ = Profile.objects.get_or_create(user=self.user)
            answer.user = profile
            answer.question = self.question

        if commit:
            answer.save()
        return answer