from django.core.management.base import BaseCommand, CommandError
from slothTw.models import Course, Comment
from infernoWeb.models import User
import json

class Command(BaseCommand):
    help = 'Convenient Way to insert Course json into inferno'
    def add_arguments(self, parser):
            # Positional arguments
            parser.add_argument('pttFile', type=str)

    def handle(self, *args, **options):
        file = json.load(open(options['pttFile'], 'r'))
        for i in file:
            try:
                if len(i['article_title']['genra'].split()) == 1:
                    if i['article_title']['genra']=='通識':
                        dept = '通識教育中心'
                    elif '文' in i['article_title']['name']:
                        dept = '語言中心'
                    elif '球' in i['article_title']['name']:
                        dept = '體育室'
                    else:
                        dept = ''

                    obj, created = Course.objects.update_or_create(
                        name=i['article_title']['name'],
                        teacher=i['article_title']['teacher'],
                        defaults={
                            'dept':dept,
                            'ctype':i['article_title']['genra'],
                            'school':'nchu',
                            'book':i['content']['book'],
                            'benchmark':i['content']['exam'],
                            'avatar':'blackboard.png'
                        }
                    )
                    Comment.objects.create(course=obj, author=User.objects.all()[0], raw=i['content']['feedback'])
                    print(obj.id)
                elif len(i['article_title']['genra'].split()) == 2:
                    obj, created = Course.objects.update_or_create(
                        name=i['article_title']['name'],
                        teacher=i['article_title']['teacher'],
                        defaults={
                            'dept':i['article_title']['genra'].split()[0],
                            'ctype':i['article_title']['genra'].split()[-1],
                            'school':'nchu',
                            'book':i['content']['book'],
                            'benchmark':i['content']['exam'],
                            'avatar':'blackboard.png'
                        }
                    )
                    Comment.objects.create(course=obj, author=User.objects.all()[0], raw=i['content']['feedback'])
                    print(obj.id)
                else:
                    raise e
            except Exception as e:
                raise e