from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import * 


def home_view(request):
    return render(request, "home.html")


def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")

        if not username or not email or not password or not password2:
            return render(request, "register.html", context={"error": "Заполните все поля"},)
        if password != password2:
            return render(request, "register.html", context={"error": "Пароли не совпадают"},)
        if CustomUser.objects.filter(username=username).exists():
            return render(request, "register.html", context={"error": "Такой username уже есть"},)
        if CustomUser.objects.filter(email=email).exists():
            return render(request, "register.html", context={"error": "Такой email уже есть"},)

        CustomUser.objects.create_user(username=username, email=email, password=password)
        return redirect("login")
    return render(request, "register.html")




def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        if not email or not password:
            return render(request, "login.html", context={"error": "Заполните все поля"},)

        user = authenticate(request, username=email, password=password)
        if user is None:
            return render(request, "login.html", context={"error": "Неверный username или пароль"},)

        login(request, user)
        return redirect("home.html")
    return render(request, "login.html")



def logout_view(request):
    logout(request,'logaut.html')
    return redirect("login.html")






