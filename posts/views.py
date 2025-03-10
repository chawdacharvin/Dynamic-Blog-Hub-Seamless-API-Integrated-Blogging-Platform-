from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from django.contrib.auth.models import User
from django.contrib import messages, auth
from django.db.models import Q
from .form import *
from .serializer import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.decorators import login_required


from django.http import JsonResponse

def health_check(request):
    return JsonResponse({"status": "ok"})

class Detailview(APIView):
    def get(self, request, id):
        blog= get_object_or_404(Post, id=id)
        serial = PostSerializer(blog)
        return Response(serial.data, status=status.HTTP_200_OK)


class BlogListView(APIView):
    def get(self, request):
        blogs = Post.objects.all()
        serial = PostSerializer(blogs, many=True)
        return Response(serial.data, status=status.HTTP_200_OK)


def home(request):
    posts = Post.objects.all()
    context = {
        "posts" : posts
    }
    return render(request, "index.html", context)


def singlepost(request, pk):
    post = Post.objects.get(id=pk)
    likes = post.likes()
    dislikes = post.dislikes()
    comments = post.comments.all()
    if request.method == "POST":
        if request.user.is_authenticated:
            form = commentform(request.POST)
            if form.is_valid():
                new_comment = form.save(commit=False)
                new_comment.post = post
                new_comment.user = request.user 
                new_comment.save()
                messages.success(request, "Comment added successfully.")
                return redirect("singlepost", pk)
        else:
            messages.error(request, "you must be logged in to add comment.")
            return redirect("login")
    else:
        form = commentform()
    context = {
        "post" : post,
        "id" : pk,
        "likes" : likes,
        "dislikes" : dislikes,
        "comments": comments,
        "form" : form,
    }
    return render(request, "singlepost.html", context)


@login_required(login_url="login")
def addpost(request):
    if request.method == "POST":
        title = request.POST["title"]
        body = request.POST["body"]
        creator = request.user
        post = Post.objects.create(title=title, body=body, creator=creator)
        return redirect ("home")
    return render(request, "addpost.html")


def login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            messages.success(request, "Login Successfull!")
            return redirect("home")
        else:
            messages.error(request, "Invalid username or password.")
            return redirect("login")
    else:
        return render(request, "login.html")




def register(request):
    if request.method == "POST":
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password1"]
        conf_password = request.POST["password2"]

        if password == conf_password:
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already taken!")
                return redirect("register")
            
            else:
                user = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                password=password,)
                user.save()
                messages.success(request, "Registration successful! You are now logged in.")
                auth.login(request , user)
                return redirect ("home")
        else:
            messages.error(request, "Password not matching...")
    else:
        return render(request, "register.html")
    

def logout(request):
    auth.logout(request)
    messages.success(request, "Successfully logged out!")
    return redirect("home")

@login_required(login_url="login")
def delpost(request, post_id):
    post = Post.objects.get(id = post_id)
    if post.creator == request.user:
        post.delete()
        print("deleting post...")
        print(request.user)
        messages.success(request, "Post deleted successfully.")
        return  redirect("home")
    else:
        print(request.user)
        messages.error(request, "You can't delete it you are not owner of this post.")
    return  redirect("singlepost", post_id)


@login_required(login_url="login")
def editpost(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    print(f"post.creator.id: {post.creator.id}, request.user.id: {getattr(request.user, 'id', 'No ID')}")
    # if not request.user.is_authenticated:
    #     messages.error(request, "You must be logged in to edit a post.")
    #     return redirect("singlepost", post_id)
    if post.creator.id != request.user.id:
        messages.error(request, "You can't edit it you are not owner of this post.")
        return redirect("singlepost", post_id)
    
    if request.method == "POST":
        new_title = request.POST.get('title', post.title)
        new_body = request.POST.get('body', post.body)
        post.title = new_title
        post.body = new_body
        post.save()
        messages.success(request, "Post updated...")
        return  redirect("singlepost", post_id)
    return render(request, "edit.html", {"post" : post})
        

@login_required(login_url="login")
def like_post(request, post_id):
    post = Post.objects.get(id = post_id)

    if request.user.is_authenticated:
        if request.user in post.like.all():
            post.like.remove(request.user)
        else:
            post.like.add(request.user)
        post.dislike.remove(request.user)
        return redirect("singlepost", post_id)
    else:
        return redirect("login")

@login_required(login_url="login")
def dislike_post(request, post_id):
    post = Post.objects.get(id=post_id)
    if request.user.is_authenticated:
        if request.user in post.dislike.all():
            post.dislike.remove(request.user)
        else:
            post.dislike.add(request.user)
        post.like.remove(request.user)
        return redirect("singlepost", post_id)
    else:
        redirect("login")


def search_posts(request):
    # Initialize variables
    query = request.GET.get("q", "").strip()  # Get the query from GET parameters, default to empty string
    posts = Post.objects.none()  # Start with no posts

    # If there's a query, perform the search
    if query:
        posts = Post.objects.filter(
            Q(title__icontains=query) | 
            Q(body__icontains=query)
        )
        print(posts)  # Debugging: Print the queryset to the console

    # Render the search results page
    return render(request, "search.html", {"query": query, "posts": posts})

def editcomment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    post_id = comment.post.id
    if request.method == "POST":
        form = commentform(request.POST, instance=comment)#here instance = is used for changing any value in any object predefined
        if form.is_valid():
            form.save()
            messages.success(request, "Comment edited successfully")
            return redirect("singlepost", post_id)
    else:
        form = commentform(instance=comment)

    return render(request, "commentedit.html", {"id":post_id, "form": form})


def delcomment(request, comment_id):
    comment=Comment.objects.get(id=comment_id)
    id = comment.post.id 
    comment.delete()
    messages.success(request, "Comment deleted successfully.")
    return redirect("singlepost", id)
