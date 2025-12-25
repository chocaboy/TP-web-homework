import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from faker import Faker
from questions.models import Profile, Tag, Question, Answer, QuestionLike, AnswerLike

fake = Faker('ru_RU')


class Command(BaseCommand):
    help = 'Заполнить базу тестовыми данными: users=ratio, questions=ratio*10, answers=ratio*100, tags=ratio, likes=ratio*200'

    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int, help='Коэффициент заполнения')

    def handle(self, *args, **options):
        ratio = options['ratio']
        self.stdout.write(f"Запуск заполнения с ratio = {ratio}")

        num_users = ratio
        num_questions = ratio * 10
        num_answers = ratio * 100
        num_tags = ratio
        num_likes = ratio * 200

        try:
            with transaction.atomic():
                users = self.create_users(num_users)
                profiles = self.create_profiles_for_all()
                tags = self.create_tags(num_tags)
                questions = self.create_questions(num_questions, profiles, tags)
                answers = self.create_answers(num_answers, questions, profiles)
                self.create_likes(num_likes, profiles, questions, answers)

            self.stdout.write(self.style.SUCCESS(
                f"Успешно создано:\n"
                f"  Пользователей: {num_users}\n"
                f"  Вопросов: {len(questions)}\n"
                f"  Ответов: {len(answers)}\n"
                f"  Тегов: {len(tags)}\n"
                f"  Лайков: {num_likes}"
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Ошибка: {e}"))
            raise

    def create_users(self, count):
        self.stdout.write(f"Создание {count} пользователей...")
        users = []
        for i in range(count):
            username = f"user_{i+1}"
            if not User.objects.filter(username=username).exists():
                user = User(
                    username=username,
                    email=f"{username}@example.com",
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                )
                user.set_password('test123')
                users.append(user)
        User.objects.bulk_create(users, ignore_conflicts=True)
        return list(User.objects.filter(username__startswith='user_')[:count])

    def create_profiles_for_all(self):
        self.stdout.write("Создание профилей для всех пользователей...")
        profiles = []
        for user in User.objects.all():
            profile, _ = Profile.objects.get_or_create(
                user=user,
                defaults={'avatar': 'default.jpg'}
            )
            profiles.append(profile)
        return profiles

    def create_tags(self, count):
        self.stdout.write(f"Создание {count} тегов...")
        base_tags = [
            'python', 'django', 'javascript', 'react', 'java', 'sql', 'docker',
            'git', 'html', 'css', 'api', 'rest', 'linux', 'devops', 'ai',
            'machine-learning', 'security', 'testing', 'cloud', 'aws'
        ]
        extended = (base_tags * (count // len(base_tags) + 1))[:count]
        tags = []
        for name in extended:
            tag, _ = Tag.objects.get_or_create(name=name)
            tags.append(tag)
        return tags

    def create_questions(self, count, profiles, tags):
        self.stdout.write(f"Создание {count} вопросов...")
        batch_size = 1000
        for i in range(0, count, batch_size):
            batch = []
            for j in range(i, min(i + batch_size, count)):
                q = Question(
                    title=f"Вопрос #{j+1}: {fake.sentence(nb_words=6)}",
                    text=fake.paragraph(nb_sentences=3),
                    user=random.choice(profiles),
                )
                batch.append(q)
            Question.objects.bulk_create(batch, ignore_conflicts=True)

        questions = list(Question.objects.order_by('id')[:count])
        self.assign_tags_to_questions(questions, tags)
        return questions

    def assign_tags_to_questions(self, questions, tags):
        self.stdout.write("Привязка тегов к вопросам...")
        through = Question.tags.through
        relations = []
        for q in questions:
            num = random.randint(1, min(3, len(tags)))
            for tag in random.sample(tags, num):
                relations.append(through(question=q, tag=tag))
        through.objects.bulk_create(relations, ignore_conflicts=True)

    def create_answers(self, count, questions, profiles):
        self.stdout.write(f"Создание {count} ответов...")
        batch_size = 1000
        for i in range(0, count, batch_size):
            batch = []
            for j in range(i, min(i + batch_size, count)):
                a = Answer(
                    question=random.choice(questions),
                    text=fake.paragraph(nb_sentences=2),
                    user=random.choice(profiles),
                    is_correct=random.random() < 0.1,
                )
                batch.append(a)
            Answer.objects.bulk_create(batch, ignore_conflicts=True)
        return list(Answer.objects.order_by('id')[:count])

    def create_likes(self, total_likes, profiles, questions, answers):
        self.stdout.write(f"Создание {total_likes} лайков...")
        q_likes = int(total_likes * 0.6)
        a_likes = total_likes - q_likes
        self.create_question_likes(q_likes, profiles, questions)
        self.create_answer_likes(a_likes, profiles, answers)

    def create_question_likes(self, count, profiles, questions):
        self.stdout.write(f"  Лайки на вопросы: {count}")
        likes = []
        for _ in range(count):
            user = random.choice(profiles)
            q = random.choice(questions)
            if not QuestionLike.objects.filter(user=user, question=q).exists():
                likes.append(QuestionLike(user=user, question=q))
            if len(likes) >= 1000:
                QuestionLike.objects.bulk_create(likes, ignore_conflicts=True)
                likes = []
        if likes:
            QuestionLike.objects.bulk_create(likes, ignore_conflicts=True)

    def create_answer_likes(self, count, profiles, answers):
        self.stdout.write(f"  Лайки на ответы: {count}")
        likes = []
        for _ in range(count):
            user = random.choice(profiles)
            a = random.choice(answers)
            if not AnswerLike.objects.filter(user=user, answer=a).exists():
                likes.append(AnswerLike(user=user, answer=a))
            if len(likes) >= 1000:
                AnswerLike.objects.bulk_create(likes, ignore_conflicts=True)
                likes = []
        if likes:
            AnswerLike.objects.bulk_create(likes, ignore_conflicts=True)

