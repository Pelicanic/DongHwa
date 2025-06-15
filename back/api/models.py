# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Follow(models.Model):
    follower_user = models.OneToOneField('User', models.DO_NOTHING, primary_key=True)  # The composite primary key (follower_user_id, followed_user_id) found, that is not supported. The first column is selected.
    followed_user = models.ForeignKey('User', models.DO_NOTHING, related_name='follow_followed_user_set')
    followed_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'Follow'
        unique_together = (('follower_user', 'followed_user'),)


class Genre(models.Model):
    genre_id = models.IntegerField(primary_key=True)
    genre_name = models.CharField(unique=True, max_length=50)
    description = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Genre'


class Illustration(models.Model):
    illustration_id = models.BigAutoField(primary_key=True)
    paragraph = models.ForeignKey('Storyparagraph', models.DO_NOTHING)
    story = models.ForeignKey('Story', models.DO_NOTHING)
    image_url = models.CharField(max_length=255, blank=True, null=True)
    caption_text = models.TextField(blank=True, null=True)
    labels = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'Illustration'


class Paragraphqa(models.Model):
    qa_id = models.BigAutoField(primary_key=True)
    paragraph = models.ForeignKey('Storyparagraph', models.DO_NOTHING)
    story = models.ForeignKey('Story', models.DO_NOTHING)
    question_text = models.TextField()
    answer_text = models.TextField()
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'ParagraphQA'


class Paragraphversion(models.Model):
    version_id = models.BigAutoField(primary_key=True)
    paragraph = models.ForeignKey('Storyparagraph', models.DO_NOTHING)
    version_no = models.IntegerField()
    content_text = models.TextField(blank=True, null=True)
    generated_by = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'ParagraphVersion'
        unique_together = (('paragraph', 'version_no'),)


class Story(models.Model):
    story_id = models.AutoField(primary_key=True)
    author_user = models.ForeignKey('User', models.DO_NOTHING)
    title = models.CharField(max_length=200, blank=True, null=True)
    summary = models.TextField(blank=True, null=True)
    summary_4step = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    status = models.CharField(max_length=20, blank=True, null=True)
    author_name = models.CharField(max_length=100, blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    cover_img = models.CharField(max_length=255, blank=True, null=True)
    characters = models.TextField(blank=True, null=True)
    
    
    class Meta:
        managed = False
        db_table = 'Story'


class Storygenre(models.Model):
    story = models.OneToOneField(Story, models.DO_NOTHING, primary_key=True)  # The composite primary key (story_id, genre_id) found, that is not supported. The first column is selected.
    genre = models.ForeignKey(Genre, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'StoryGenre'
        unique_together = (('story', 'genre'),)


class Storyparagraph(models.Model):
    paragraph_id = models.BigAutoField(primary_key=True)
    story = models.ForeignKey(Story, models.DO_NOTHING)
    paragraph_no = models.IntegerField()
    content_text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'StoryParagraph'


class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    login_id = models.CharField(max_length=50, blank=True, null=True)
    password_hash = models.CharField(max_length=255)
    nickname = models.CharField(unique=True, max_length=50)
    email = models.CharField(max_length=100, blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    interests = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField()
    last_login = models.DateTimeField(blank=True, null=True)
    profile_image_url = models.CharField(max_length=20, blank=True, null=True)
    provider = models.CharField(unique=True, max_length=20, blank=True, null=True)
    provider_id = models.CharField(unique=True, max_length=50, blank=True, null=True)
    is_active = models.BooleanField(default=False) # 이메일 인증 여부
    email_verification_token = models.CharField(max_length=64, null=True, blank=True) # 이메일 인증 토큰

    class Meta:
        managed = False
        db_table = 'User'
        unique_together = (('provider', 'provider_id', 'nickname'),)


class Usergenre(models.Model):
    user = models.OneToOneField(User, models.DO_NOTHING, primary_key=True)  # The composite primary key (user_id, genre_id) found, that is not supported. The first column is selected.
    genre = models.ForeignKey(Genre, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'UserGenre'
        unique_together = (('user', 'genre'),)


class Userlike(models.Model):
    user = models.OneToOneField(User, models.DO_NOTHING, primary_key=True)  # The composite primary key (user_id, story_id) found, that is not supported. The first column is selected.
    story = models.ForeignKey(Story, models.DO_NOTHING)
    liked_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'UserLike'
        unique_together = (('user', 'story'),)
