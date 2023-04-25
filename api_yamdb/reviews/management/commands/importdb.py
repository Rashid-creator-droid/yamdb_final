import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from django.shortcuts import get_object_or_404

from reviews.models import (
    User,
    Category,
    Genre,
    Title,
    Comment,
    Review,
    TitleGenre,
)

USERS = 'users.csv'
CATEGORY = 'category.csv'
GENRE = 'genre.csv'
TITLE = 'titles.csv'
GENRE_TITLE = 'genre_title.csv'
COMMENTS = 'comments.csv'
REVIEW = 'review.csv'


def get_reader(file):
    csv_path = os.path.join(settings.BASE_DIR, 'static/data/', file)
    csv_file = open(csv_path, encoding='utf-8')
    reader = csv.DictReader(csv_file, delimiter=',')
    return reader


def import_users():
    csv_reader = get_reader(USERS)
    for row in csv_reader:
        obj, created = User.objects.get_or_create(
            id=row['id'],
            username=row['username'],
            email=row['email'],
            role=row['role'],
            bio=row['bio'],
            first_name=row['first_name'],
            last_name=row['last_name'],
        )
    print(f'{USERS} успешно импортировалось!')


def import_category():
    csv_reader = get_reader(CATEGORY)
    for row in csv_reader:
        obj, created = Category.objects.get_or_create(
            id=row['id'],
            name=row['name'],
            slug=row['slug'],
        )
    print(f'{CATEGORY} успешно импортировалось!')


def import_genre():
    csv_reader = get_reader(GENRE)
    for row in csv_reader:
        obj, created = Genre.objects.get_or_create(
            id=row['id'],
            name=row['name'],
            slug=row['slug'],
        )
    print(f'{GENRE} успешно импортировалось!')


def import_title():
    csv_reader = get_reader(TITLE)
    for row in csv_reader:
        obj_category = get_object_or_404(Category, id=row['category'])
        obj, created = Title.objects.get_or_create(
            id=row['id'],
            name=row['name'],
            year=row['year'],
            category=obj_category,
        )
    print(f'{TITLE} успешно импортировалось!')


def import_genre_title():
    csv_reader = get_reader(GENRE_TITLE)
    for row in csv_reader:
        obj_genre = get_object_or_404(Genre, id=row['genre'])
        obj_title = get_object_or_404(Title, id=row['title'])
        obj, created = TitleGenre.objects.get_or_create(
            id=row['id'],
            genre=obj_genre,
            title=obj_title,
        )
    print(f'{GENRE_TITLE} успешно импортировалось!')


def import_comments():
    csv_reader = get_reader(COMMENTS)
    for row in csv_reader:
        obj_review = get_object_or_404(Review, id=row['review_id'])
        obj_author = get_object_or_404(User, id=row['author'])
        obj, created = Comment.objects.get_or_create(
            id=row['id'],
            review=obj_review,
            text=row['text'],
            author=obj_author,
            pub_date=row['pub_date'],
        )
    print(f'{COMMENTS} успешно импортировалось!')


def import_review():
    csv_reader = get_reader('review.csv')
    for row in csv_reader:
        obj_title = get_object_or_404(Title, id=row['title_id'])
        obj_author = get_object_or_404(User, id=row['author'])
        obj, created = Review.objects.get_or_create(
            id=row['id'],
            title=obj_title,
            text=row['text'],
            author=obj_author,
            score=row['score'],
            pub_date=row['pub_date'],
        )
    print(f'{REVIEW} успешно импортировалось!')


class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            import_users()
            import_category()
            import_genre()
            import_title()
            import_review()
            import_comments()
        except Exception as error:
            print(f'Ошибка импорта {error}')
