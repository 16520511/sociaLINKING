from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from .forms import LoginForm, RegisterForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .models import MyUser, Post, UserAction
import datetime
import json
from django.core import serializers

#Login Page - also default Page
def default_login(request):
    if not request.user.is_authenticated:
        if request.method == 'POST':
            loginForm = LoginForm(request.POST)
            if loginForm.is_valid():
                user = authenticate(username = loginForm.cleaned_data['email'],
                    password = loginForm.cleaned_data['password'])
                if user:
                    login(request, user)
                    return HttpResponseRedirect(reverse(home))
        else:
            loginForm = LoginForm()
        return render(request, 'login.html', {'loginForm': loginForm,})
    else:
        return HttpResponseRedirect(reverse(home))

#Register Page
def new_register(request):
    if not request.user.is_authenticated:
        if request.method == 'POST':
            regForm = RegisterForm(request.POST)
            if regForm.is_valid():
                user = MyUser.objects.create_user(email = regForm.cleaned_data['email'],
                    password = regForm.cleaned_data['password'], firstName = regForm.cleaned_data['firstName'], 
                    lastName = regForm.cleaned_data['lastName'], gender = regForm.cleaned_data['gender'], 
                    age = regForm.cleaned_data['age'])     
                user.save() 
                return HttpResponseRedirect(reverse(default_login))
        else:
            regForm = RegisterForm()
        return render(request, 'register.html', {'regForm': regForm,})
    else:
        return HttpResponseRedirect(reverse(home))

#Logout Request
@login_required(login_url = '/')
def user_logout(request):
    if request.user.is_authenticated:
        logout(request)
        return HttpResponseRedirect(reverse(default_login))


#Home Page
@login_required(login_url = '/')
def home(request):
    #Show user's and people they are following's posts
    Posts = (Post.objects.filter(user = request.user)|Post.objects.filter(user__in = request.user.following.all(),
        privacySetting = 'Public')).order_by('-postedOn').filter(postedOn__gte = datetime.datetime.now()-datetime.timedelta(weeks = 2))
    #Get all the actions with the posts from current user
    userUpActions = UserAction.objects.filter(user = request.user, action = 'Up')
    userDownActions = UserAction.objects.filter(user = request.user, action = 'Down')
    if request.method == 'POST':
        #If new post request
        if 'content' in request.POST:
            content = request.POST.get('content', None)
            Post.objects.create(user = request.user, content = content)

        #Handle an up action from user
        if 'up' in request.POST:
            postId = request.POST.get('up', None)
            post = Post.objects.get(pk = postId)
            if UserAction.objects.filter(user = request.user, post = post, action = 'Up').count() == 0:
                UserAction.objects.create(user = request.user, post = post, action = 'Up')
                userUp = 'True'
            elif UserAction.objects.filter(user = request.user, post = post, action = 'Up').count() > 0:
                UserAction.objects.filter(user = request.user, post = post, action = 'Up').delete()
                userUp = 'False'
            post = Post.objects.get(pk = postId)
            jsonData = {'up': post.upNumber, 'down': post.downNumber, 'userUp': userUp}
            return HttpResponse(json.dumps(jsonData))

        #Handle a down action from user
        if 'down' in request.POST:
            postId = request.POST.get('down', None)
            post = Post.objects.get(pk = postId)
            if UserAction.objects.filter(user = request.user, post = post, action = 'Down').count() == 0:
                UserAction.objects.create(user = request.user, post = post, action = 'Down')
                userDown = 'True'
            elif UserAction.objects.filter(user = request.user, post = post, action = 'Down').count() > 0:
                UserAction.objects.filter(user = request.user, post = post, action = 'Down').delete()
                userDown = 'False'
            post = Post.objects.get(pk = postId)
            jsonData = {'up': post.upNumber, 'down': post.downNumber, 'userDown': userDown}
            return HttpResponse(json.dumps(jsonData))

        #Load More
        if 'numberOfLoad' in request.POST:
            numberOfLoad = int(request.POST.get('numberOfLoad', None))
            #Check the number of posts left
            if Posts.count() >= numberOfLoad*10:
                jsonData = serializers.serialize('json', Posts[((numberOfLoad-1)*10):(numberOfLoad*10-1)])
            elif Posts.count() > (numberOfLoad-1)*10 and Posts.count() < numberOfLoad*10:
                jsonData = serializers.serialize('json', Posts[(numberOfLoad-1)*10:])

            #No more posts
            else:
                jsonData = {'None': 'None'}
            
            #Add additional data for json objects
            if 'None' not in jsonData:
                jsonData = json.loads(jsonData)
                #Get all the post that users interact with to check in the view
                for i in jsonData:
                    user = MyUser.objects.get(pk = i['fields']['user'])
                    i['username'] = user.get_full_name
                    i['avatar'] = user.profile.avatar.url
                    i['slug'] = user.slug

                    #Reformat the datetime for json objects
                    i['fields']['postedOn'] = str(Post.objects.get(pk = i['pk']).postedOn.strftime("%b %d, %Y, %I:%M %p")).replace('AM','a.m').replace('PM', 'p.m')
                    i['up'] = 'False'
                    i['down'] = 'False'
                    #Add current users action with the posts to json
                    post = Post.objects.get(pk = i['pk'])
                    for action in userUpActions:
                        if post == action.post:
                            i['up'] = 'True'
                            break
                    for action in userDownActions:
                        if post == action.post:
                            i['down'] = 'True'
                            break
            return HttpResponse(json.dumps(jsonData))
        
    upPosts = []
    downPosts = []
    for action in userUpActions:
        upPosts.append(action.post)
    for action in userDownActions:
        downPosts.append(action.post)
    
    return render(request, 'home.html', {'Posts': Posts[:10], 'upPosts': upPosts,
                'downPosts': downPosts})

def user_page(request, slug):
    targetUser = MyUser.objects.filter(slug = slug)
    if targetUser.count() == 1:
        targetUser = targetUser[0]
        userUpActions = UserAction.objects.filter(user = targetUser, action = 'Up')
        userDownActions = UserAction.objects.filter(user = targetUser, action = 'Down')
        Posts = Post.objects.filter(user = targetUser).order_by("-postedOn")
        if request.user not in targetUser.block.all():    
            if request.method == 'POST':
                #Handle an up action from user
                if 'up' in request.POST:
                    postId = request.POST.get('up', None)
                    post = Post.objects.get(pk = postId)
                    if UserAction.objects.filter(user = request.user, post = post, action = 'Up').count() == 0:
                        UserAction.objects.create(user = request.user, post = post, action = 'Up')
                        userUp = 'True'
                    elif UserAction.objects.filter(user = request.user, post = post, action = 'Up').count() > 0:
                        UserAction.objects.filter(user = request.user, post = post, action = 'Up').delete()
                        userUp = 'False'
                    post = Post.objects.get(pk = postId)
                    jsonData = {'up': post.upNumber, 'down': post.downNumber, 'userUp': userUp}
                    return HttpResponse(json.dumps(jsonData))

                #Handle a down action from user
                if 'down' in request.POST:
                    postId = request.POST.get('down', None)
                    post = Post.objects.get(pk = postId)
                    if UserAction.objects.filter(user = request.user, post = post, action = 'Down').count() == 0:
                        UserAction.objects.create(user = request.user, post = post, action = 'Down')
                        userDown = 'True'
                    elif UserAction.objects.filter(user = request.user, post = post, action = 'Down').count() > 0:
                        UserAction.objects.filter(user = request.user, post = post, action = 'Down').delete()
                        userDown = 'False'
                    post = Post.objects.get(pk = postId)
                    jsonData = {'up': post.upNumber, 'down': post.downNumber, 'userDown': userDown}
                    return HttpResponse(json.dumps(jsonData))

                #Load More
                if 'numberOfLoad' in request.POST:
                    numberOfLoad = int(request.POST.get('numberOfLoad', None))

                    #Check the number of posts left
                    if Posts.count() >= numberOfLoad*10:
                        jsonData = serializers.serialize('json', Posts[((numberOfLoad-1)*10):(numberOfLoad*10-1)])
                    elif Posts.count() > (numberOfLoad-1)*10 and Posts.count() < numberOfLoad*10:
                        jsonData = serializers.serialize('json', Posts[(numberOfLoad-1)*10:])

                    #No more posts
                    else:
                        jsonData = {'None': 'None'}
                    
                    #Add additional data for json objects
                    if 'None' not in jsonData:
                        jsonData = json.loads(jsonData)
                        #Get all the post that users interact with to check in the view
                        for i in jsonData:
                            i['username'] = targetUser.get_full_name
                            i['avatar'] = targetUser.profile.avatar.url
                            i['slug'] = targetUser.slug

                            #Reformat the datetime for json objects
                            i['fields']['postedOn'] = str(Post.objects.get(pk = i['pk']).postedOn.strftime("%b %d, %Y, %I:%M %p")).replace('AM','a.m').replace('PM', 'p.m')
                            i['up'] = 'False'
                            i['down'] = 'False'
                            #Add current users action with the posts to json
                            post = Post.objects.get(pk = i['pk'])
                            for action in userUpActions:
                                if post == action.post:
                                    i['up'] = 'True'
                                    break
                            for action in userDownActions:
                                if post == action.post:
                                    i['down'] = 'True'
                                    break
                    return HttpResponse(json.dumps(jsonData))

                #Handle follow action from user
                if 'follow' in request.POST:
                    followed = 'False'
                    if targetUser in request.user.following.all():
                        request.user.following.remove(targetUser)
                    elif targetUser not in request.user.following.all() and request.user not in targetUser.block.all() and request.user != targetUser:
                        request.user.following.add(targetUser)
                        followed = 'True'

                    followers = 0
                    for u in MyUser.objects.all():
                        if targetUser in u.following.all():
                            followers += 1
                    followings = targetUser.following.all().count()

                    jsonData = {"followed":followed, "followers": followers, "followings": followings}
                    return HttpResponse(json.dumps(jsonData))

            #Put all the informations needed here
            followers = 0
            for u in MyUser.objects.all():
                if targetUser in u.following.all():
                    followers += 1
            followings = targetUser.following.all().count()

            iHaveFollowed = False
            if targetUser in request.user.following.all():
                iHaveFollowed = True

            upPosts = []
            downPosts = []
            for action in userUpActions:
                upPosts.append(action.post)
            for action in userDownActions:
                downPosts.append(action.post)
            return render(request, 'user_page.html', {'targetUser': targetUser, 'Posts': Posts[:10], 'upPosts': upPosts,
                'downPosts': downPosts, 'followers': followers, 'followings': followings, 'iHaveFollowed': iHaveFollowed})
        else:
            return render(request, 'error.html', {'errorMessage': 'You cannot see this page because this user have private setting or you have been blocked.'})
    elif targetUser.count() == 0:
        return render(request, 'error.html', {'errorMessage': 'User Not Found.'})
