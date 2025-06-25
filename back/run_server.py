import os
import sys
import django
from django.core.management import execute_from_command_line
from dotenv import load_dotenv

load_dotenv()  # .env 파일 로드

if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pelworld.settings')
    # Django 설정 초기화
    django.setup()
    
    # runserver 명령 실행
    execute_from_command_line(['manage.py', 'runserver', '0.0.0.0:8721'])
