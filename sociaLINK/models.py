from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.exceptions import ValidationError

class MyUserManager(BaseUserManager):
    def create_user(self, email, password, firstName, lastName, age, gender = 'Male'):
        if not email:
            raise ValueError('Email address is required!')

        user = self.model(
            email = self.normalize_email(email),
            firstName = firstName,
            lastName = lastName,
            gender = gender,
            age = age,
        )

        user.set_password(password)
        user.save(using =  self._db)
        return user

    def create_superuser(self, email, password, firstName, lastName, age, gender = 'Mr'):
        user = self.create_user(
            email,
            firstName = firstName,
            lastName = lastName,
            gender = gender,
            age = age,
            password = password,
        )

        user.is_admin = True
        user.save(using = self._db)
        return user

class MyUser(AbstractBaseUser):
    
    GENDER = (
        ('Male', 'Male'),
        ('Female', 'Female'),
    )

    #Basic Sign Up Fields
    email = models.EmailField('Email Address', max_length = 50, unique = True)
    firstName = models.CharField('First Name', max_length = 50)
    lastName = models.CharField('Last Name', max_length = 50)
    gender = models.CharField(max_length = 6, choices = GENDER, default = 'Male')
    age = models.IntegerField()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['firstName', 'lastName', 'gender', 'age']

    #For User Admin Page
    objects = MyUserManager()
    is_active = models.BooleanField(default = True)
    is_admin = models.BooleanField(default = False)

    #Customize fields go here:
    slug = models.SlugField(max_length = 50, blank = True)
    following = models.ManyToManyField('self', symmetrical = False)
    block = models.ManyToManyField('self', symmetrical = False, related_name = 'blocks')


    def __str__(self):
        return self.email

    #Functions that are required to create a customized User Model
    @property
    def get_full_name(self):
        return f'{self.firstName} {self.lastName}'

    @property
    def is_staff(self):
        return self.is_admin

    def has_perm(self, perm, obj = None):
        return self.is_staff

    def has_perms(self, perm, obj = None):
        return self.is_staff

    def has_module_perms(self, app_label):
        return self.is_staff

#Unique auto slug and profile for new users
def auto_user_slug_and_profile(*args, **kwargs):
    instance = kwargs['instance']
    if kwargs['created']:
        #Take user email as slug
        slug = instance.email.split('@')[0]
        originalSlug = slug

        #Check if slug is already taken, then adds numbers until it is available
        takenSlug = []
        for i in MyUser.objects.all():
            takenSlug.append(i.slug)

        counter = 1
        while slug in takenSlug:
            slug = f'{originalSlug}-{str(counter)}'
            counter += 1
        instance.slug = slug
        instance.save()

        #Create a new profile
        Profile.objects.create(user = instance, avatar = "/avatar/default.png",
            cover = "/cover/default-cover.jpg")

models.signals.post_save.connect(auto_user_slug_and_profile, sender = MyUser)

#Send a notification for a user when someone follow them
def follow_notification(*args, **kwargs):
    instance = kwargs['instance']
    action = kwargs['action']
    if kwargs['pk_set']:
        if action == 'post_add':
            notificationUser = MyUser.objects.filter(pk__in = kwargs['pk_set'])[0]
            message = f'{ instance.get_full_name } followed you.'
            Notification.objects.create(user = notificationUser, message = message, url = instance.slug)

models.signals.m2m_changed.connect(follow_notification, sender = MyUser.following.through)

class Profile(models.Model):
    user = models.OneToOneField(MyUser, on_delete = models.CASCADE)
    location = models.CharField(max_length = 100, blank = True, null = True)
    job = models.CharField(max_length = 100, blank = True, null = True)
    education = models.CharField(max_length = 100, blank = True, null = True)

    avatar = models.ImageField(upload_to='avatar', max_length = 100, blank = True, null = True)
    cover = models.ImageField(upload_to='cover', max_length = 100, blank = True, null = True)

    def __str__(self):
        return f'{self.user.email} Profile'

class Post(models.Model):

    PRIVACY = (
        ('Public', 'Public'),
        ('Private', 'Private'),
    )
    user = models.ForeignKey(MyUser, on_delete = models.CASCADE)
    userAction = models.ManyToManyField(MyUser, through = 'UserAction', related_name = 'action')

    content = models.TextField(max_length = 500)
    postedOn = models.DateTimeField(auto_now_add = True)
    upNumber = models.IntegerField(default = 0)
    downNumber = models.IntegerField(default = 0)
    repostNumber = models.IntegerField(default = 0)
    privacySetting = models.CharField(max_length = 7, choices = PRIVACY, default = 'Public')

    def __str__(self):
        return f'Post {self.id} by {self.user}'

class UserAction(models.Model):
    ACTION = (
        ('Post', 'Post'),
        ('Up', 'Up'),
        ('Down', 'Down'),
        ('Repost', 'Repost'),
    )
    user = models.ForeignKey(MyUser, on_delete = models.CASCADE)
    post = models.ForeignKey(Post, on_delete = models.CASCADE)
    action = models.CharField(max_length = 6, choices = ACTION)
    createdOn = models.DateTimeField(auto_now_add = True)

#Create a connection between Post and UserAction when a new post is created, and send a
#notification to tagged users if any
def post_created(*args, **kwargs):
    instance = kwargs['instance']
    if kwargs['created']:
        UserAction.objects.create(user = instance.user, post = instance, action = 'Post')
        for user in MyUser.objects.all():
            message = f'{instance.user.get_full_name} mentioned you in a post.'
            if instance.content.find(f'@{user.slug}') != -1:
                Notification.objects.create(user = user, message = message)

models.signals.post_save.connect(post_created, sender = Post)

#Update the action number in the post model when a user action is created...
def action_created(*args, **kwargs):
    instance = kwargs['instance']
    if kwargs['created']:
        if instance.action == 'Up':
            instance.post.upNumber += 1
            #Delete the down vote from user with this post
            down = UserAction.objects.filter(user = instance.user, post = instance.post, action = 'Down')
            if down.count() > 0:
                down.delete()
                instance.post.downNumber -= 1
        if instance.action == 'Down':
            instance.post.downNumber += 1
            #Delete the up vote from user with this post
            up = UserAction.objects.filter(user = instance.user, post = instance.post, action = 'Up')
            if up.count() > 0:
                up.delete()
                instance.post.upNumber -= 1
        if instance.action == 'Repost':
            instance.post.repostNumber += 1
        instance.post.save()

#...And when it is deleted
def action_delete(*args, **kwargs):
    instance = kwargs['instance']
    if instance.action == 'Up':
        instance.post.upNumber -= 1
    if instance.action == 'Down':
        instance.post.downNumber -= 1
    if instance.action == 'Repost':
        instance.post.repostNumber -= 1
    instance.post.save()

models.signals.post_save.connect(action_created, sender = UserAction)
models.signals.post_delete.connect(action_delete, sender = UserAction)

class Notification(models.Model):
    user = models.ForeignKey(MyUser, on_delete = models.CASCADE)
    message = models.CharField(max_length = 100)
    url = models.CharField(max_length = 100, blank = True, null = True)
    isRead = models.BooleanField(default = False)

    def __str__(self):
        return f'Notification for {self.user.slug}'
