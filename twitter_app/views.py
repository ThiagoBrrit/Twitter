from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Profile, Tweet
from .forms import TweetForm, SignUpForm, ProfilePicForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms



def home(request):
    if request.user.is_authenticated:
        form = TweetForm(request.POST or None)
        if request.method == "POST":
            if form.is_valid():
                tweet = form.save(commit=False)
                tweet.user = request.user
                tweet.save()
                messages.success(request, ("Seu tweet foi postado."))
                return redirect('home')

        tweets = Tweet.objects.all().order_by("-created_at")
        return render(request, 'home.html', {"tweets":tweets, "form":form})
    else:
        tweets = Tweet.objects.all().order_by("-created_at")
        return render(request, 'home.html', {"tweets":tweets})


def profile_list(request):
    if request.user.is_authenticated:
        profiles = Profile.objects.exclude(user=request.user)
        return render(request, 'profile_list.html', {"profiles":profiles})
    else:
        messages.success(request, ("Você deve estar logado para visualizar esta página."))
        return redirect('home')


def unfollow(request, pk):
    if request.user.is_authenticated:
        # Obtendo o perfil para deixar de seguir
        profile = Profile.objects.get(user__id=pk)
        # Deixando de seguir o perfil
        request.user.profile.follows.remove(profile)
        # Salvando o nosso perfil
        request.user.profile.save()
        # Retornando uma messagem
        messages.success(request, (f"Você deixou de seguir com sucesso {profile.user.username}"))
        return redirect(request.META.get("HTTP_REFERER"))
    else:
        messages.success(request, ("Você deve estar logado para visualizar esta página."))
        return redirect('home')


def follow(request, pk):
    if request.user.is_authenticated:
        # Obtendo o perfil para seguir de volta
        profile = Profile.objects.get(user__id=pk)
        # seguindo o perfil
        request.user.profile.follows.add(profile)
        # Salvando o nosso perfil
        request.user.profile.save()
        # Retornando uma messagem
        messages.success(request, (f"Você seguiu com sucesso {profile.user.username}"))
        return redirect(request.META.get("HTTP_REFERER"))
    else:
        messages.success(request, ("Você deve estar logado para visualizar esta página."))
        return redirect('home')


def profile(request, pk):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user_id=pk)
        tweets = Tweet.objects.filter(user_id=pk)

        if request.method == "POST":
            current_user_profile = request.user.profile
            action = request.POST['follow']
            if action == "unfollow":
                current_user_profile.follows.remove(profile)
            elif action == "follow":
                current_user_profile.follows.add(profile)
            current_user_profile.save()

        return render(request, 'profile.html', {'profile':profile, "tweets":tweets})
    else:
        messages.success(request, ("Você deve estar logado para visualizar esta página."))
        return redirect('home')


def followers(request, pk):
    if request.user.is_authenticated:
        if request.user.id == pk:
            profiles = Profile.objects.get(user_id=pk)
            return render(request, 'followers.html', {"profiles":profiles})
        else:
            messages.success(request, ("Essa não é a sua página de perfil"))
            return redirect('home')
    else:
        messages.success(request, ("Você deve estar logado para visualizar esta página."))
        return redirect('home')


def follows(request, pk):
    if request.user.is_authenticated:
        if request.user.id == pk:
            profiles = Profile.objects.get(user_id=pk)
            return render(request, 'follows.html', {"profiles":profiles})
        else:
            messages.success(request, ("Essa não é a sua página de perfil."))
            return redirect('home')
    else:
        messages.success(request, ("Você deve estar logado para visualizar esta página."))
        return redirect('home')


def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, ("Você está logado!."))
            return redirect('home')
        else:
            messages.success(request, ("Ocorreu um erro ao fazer login. Tente novamente!"))
            return redirect('login')

    else:
        return render(request, 'login.html', {})


def logout_user(request):
    logout(request)
    messages.success(request, ("Você foi desconectado."))
    return redirect('home')


def register_user(request):
    form = SignUpForm()
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            # first_name = form.cleaned_data['first_name']
            # last_name = form.cleaned_data['last_name']
            # email= form.cleaned_data['email']

            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, ("Você se registrou com sucesso. BEM-VINDO"))
            return redirect('home')
    return render(request, 'register.html', {'form':form})


def update_user(request):
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        profile_user = Profile.objects.get(user__id=request.user.id)

        user_form = SignUpForm(request.POST or None, request.FILES or None, instance=current_user)
        profile_form = ProfilePicForm(request.POST or None, request.FILES or None, instance=profile_user)
        if user_form.is_valid() and profile_form.is_valid:
            user_form.save()
            profile_form.save()
            login(request, current_user)
            messages.success(request, ("Seu perfil foi atualizado"))
            return redirect('home')
    

        return render(request, 'update_user.html', {'user_form':user_form, 'profile_form':profile_form})
    else:
        messages.success(request, ("Você deve estar logado para visualizar essa página"))
        return redirect('home')
    

def tweet_like(request, pk):
    if request.user.is_authenticated:
        tweet = get_object_or_404(Tweet, id=pk)
        if tweet.likes.filter(id=request.user.id):
            tweet.likes.remove(request.user)
        else:
            tweet.likes.add(request.user)
        return redirect(request.META.get("HTTP_REFERER"))
    else:
        messages.success(request, ("Você deve estar logado para visualizar essa página"))
        return redirect('home')
    
def tweet_show(request, pk):
    tweet = get_object_or_404(Tweet, id=pk)
    if tweet:
        return render(request, 'show_tweet.html', {'tweet':tweet})

    else:
        messages.success(request, ("Esse tweet não existe."))
        return redirect('home')


def delete_tweet(request, pk):
    if request.user.is_authenticated:
        tweet = get_object_or_404(Tweet, id=pk)
        # verifica se você está vendo o tweet
        if request.user.username == tweet.user.username:
            # removendo o tweet
            tweet.delete()
            messages.success(request, ("O Tweet foi excluído"))
            return redirect(request.META.get("HTTP_REFERER"))
        else:
            messages.success(request, ("Você não é o dono desse tweet"))
            return redirect('home')
    else:
        messages.success(request, ("Por favor faça o login para continuar"))
        return redirect(request.META.get("HTTP_REFERER"))


def edit_tweet(request, pk):
    if request.user.is_authenticated:
        # pegando o tweet
        tweet = get_object_or_404(Tweet, id=pk)
        # verifica se você está vendo o tweet
        if request.user.username == tweet.user.username:
            form = TweetForm(request.POST or None, instance=tweet)
            if request.method == "POST":
                if form.is_valid():
                    tweet = form.save(commit=False)
                    tweet.user = request.user
                    tweet.save()
                    messages.success(request, ("Seu Tweet foi atualizado."))
                    return redirect('home')
            else:
                return render(request, 'edit_tweet.html', {'form':form, 'tweet':tweet})
            
        else:
            messages.success(request, ("Você não é o dono desse tweet"))
            return redirect('home')
    else:
        messages.success(request, ("Por favor faça o login para continuar"))
        return redirect('home')


def search(request):
    if request.method == "POST":
        # Pegando o campo do formulario para procurar
        search = request.POST['search']
        # Procurando no banco de dados
        searched = Tweet.objects.filter(body__contains =search)
        return render(request, 'search.html', {'search':search, 'searched':searched})
    else:
        return render(request, 'search.html', {})


def search_user(request):
    if request.method == "POST":
        # Pegando o campo do formulario para procurar
        search = request.POST['search']
        # Procurando no banco de dados
        searched = User.objects.filter(username__contains = search)
        return render(request, 'search_user.html', {'search':search, 'searched':searched})
    else:
        return render(request, 'search_user.html', {})