from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from faker import Faker

from posts.models import Post, Author, Category, Tag, CustomUser


class Command(BaseCommand):
    def handle(self, *args, **options):
        fake = Faker(['ru_RU'])
        for _ in range(10):
           Post.objects.create(
                author=Author.objects.create(bio=fake.first_name()
                                          ),
                title=fake.text(),
                content=fake.text(),
            )
           Author.objects.create(
               bio=fake.last_name(),
               user_id= CustomUser.objects.first().id,
           )
           Tag.objects.create(
               name=fake.name(),

           )
           Category.objects.create(
                name=fake.name(),
            )
