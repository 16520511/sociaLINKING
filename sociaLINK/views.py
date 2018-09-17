from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from .forms import LoginForm, RegisterForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .models import MyUser, Post, UserAction, Notification
import datetime
import json
from django.core import serializers
from .seach_engine import SearchEngine

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
    #User's notifications
    noti = Notification.objects.filter(user = request.user).order_by('-createdAt')
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

        if 'deletePost' in request.POST:
            postId = request.POST.get('deletePost', None)
            p = Post.objects.get(pk = postId)
            if request.user == p.user:
                p.delete()
                message = 'Success'
            else:
                message = 'Fail'
            jsonData = {"message": message,}
            return HttpResponse(json.dumps(jsonData))

        
    upPosts = []
    downPosts = []
    for action in userUpActions:
        upPosts.append(action.post)
    for action in userDownActions:
        downPosts.append(action.post)
    #Only show 7 notifications    
    if noti.count() >= 2:
        noti = noti[:2]
    return render(request, 'home.html', {'Posts': Posts[:10], 'upPosts': upPosts,
                'downPosts': downPosts, 'noti': noti})

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
                            #Add current user actions with the posts to json
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
                    elif not targetUser in request.user.following.all() and not request.user in targetUser.block.all() and request.user != targetUser:
                        request.user.following.add(targetUser)
                        followed = 'True'

                    followers = 0
                    for u in MyUser.objects.all():
                        if targetUser in u.following.all():
                            followers += 1
                    followings = targetUser.following.all().count()

                    jsonData = {"followed":followed, "followers": followers, "followings": followings}
                    return HttpResponse(json.dumps(jsonData))

                if 'deletePost' in request.POST:
                    postId = request.POST.get('deletePost', None)
                    post = Post.objects.get(pk = postId)
                    if request.user == post.user:
                        post.delete()
                        message = 'Success'
                    else:
                        message = 'Fail'
                    jsonData = {"message": message,}
                    return HttpResponse(json.dumps(jsonData))

            #Put all the informations needed down here
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
                'downPosts': downPosts, 'followers': followers, 'followings': followings})
        else:
            return render(request, 'error.html', {'errorMessage': 'You cannot see this page because this user have private setting or you have been blocked.'})
    elif targetUser.count() == 0:
        return render(request, 'error.html', {'errorMessage': 'User Not Found.'})

def search(request):
    nameSearch = SearchEngine()
    locationSearch = SearchEngine()
    query = location = ""
    openTab = "by-name" #Get the current open search tab when reload the page
    if request.method == 'GET':
        if 'location' not in request.GET:
            query = request.GET.get("q", "")
            if query == "":
                nameSearch.result = MyUser.objects.none()
            else:
                nameSearch.search_by_name(query)
            locationSearch = nameSearch
        if 'location' in request.GET:
            query = request.GET.get("q", "")
            location = request.GET.get("location", "")
            if query == "" and location == "":
                locationSearch.result = MyUser.objects.none()
            else:
                locationSearch.search_by_name(query)
                locationSearch.search_by_location(location)
            openTab = "by-location"
    if request.method == 'POST':
        if 'follow' in request.POST:
            userId = request.POST.get("follow", None)
            targetUser = MyUser.objects.get(pk = userId)
            followed = 'False'
            if targetUser in request.user.following.all():
                request.user.following.remove(targetUser)
            elif targetUser not in request.user.following.all() and request.user not in targetUser.block.all() and request.user != targetUser:
                request.user.following.add(targetUser)
                followed = 'True'
            jsonData = {"followed":followed}
            return HttpResponse(json.dumps(jsonData))

    return render(request, "search.html", {'nameResult': nameSearch.result, 'locationResult': locationSearch.result,
     'query': query, 'location': location, 'openTab': openTab})

@login_required(login_url = '/')
def notifications(request):
    noti = Notification.objects.filter(user = request.user).order_by('-createdAt')
    request.user.newNotificationsNumber = 0 #Set the new notifications number to 0 if the user access the notifications page.
    request.user.save()

    if request.method == 'POST':
        #Handle mark as read a noti
        if 'markRead' in request.POST:
            notiId = request.POST.get('markRead', None)
            readNoti = Notification.objects.get(pk = notiId)
            readNoti.isRead = True
            readNoti.save()
        #Handle mark all as read
        if 'markAllRead' in request.POST:
            allUserNoti = Notification.objects.filter(user = request.user)
            for noti in allUserNoti:
                noti.isRead = True
                noti.save()
        #Stop receing notification
        if 'stopNoti' in request.POST:
            otherEndUserId = request.POST.get('stopNoti', None)
            otherEndUser = MyUser.objects.get(pk = otherEndUserId)
            request.user.blockNoti.add(otherEndUser)
            request.user.save()
    return render(request, 'notifications.html', {'noti': noti})
