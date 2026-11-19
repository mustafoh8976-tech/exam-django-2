from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from .models import *


def home_view(request):
    return render(request, "home.html")


def register_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")
        photo = request.FILES.get("photo")

        error = None
        if not username or not email or not password or not password2:
            error = "Заполните все поля"
        elif password != password2:
            error = "Пароли не совпадают"
        elif CustomUser.objects.filter(username=username).exists():
            error = "Такой username уже есть"
        elif CustomUser.objects.filter(email=email).exists():
            error = "Такой email уже есть"

        if error:
            return render(request, "register.html",{"error": error, "username": username, "email": email})
        user = CustomUser.objects.create_user(username=username, email=email, password=password)
        if photo:
            user.photo = photo
            user.save()
        return redirect("login")

    return render(request, "register.html")


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if not username or not password:
            return render(request, "login.html", {"error": "Заполните все поля"})

        user = authenticate(request, username=username, password=password)
        if user is None:
            return render(request, "login.html", {"error": "Неверный username или пароль"})

        login(request, user)
        return redirect("stadions")

    return render(request, "login.html")


def logout_view(request):
    if request.method == "POST":
        logout(request)
    return redirect("login")



@login_required
def stadions_view(request):
    stadions = Stadion.objects.all()

    category = request.GET.get("category")
    q = request.GET.get("q")

    if category and category.isdigit():
        category = int(category)
        stadions = stadions.filter(category=category)
    else:
        category = None

    if q:
        stadions = stadions.filter(Q(name_s__icontains=q) | Q(addres__icontains=q))

    return render(request, "stadions_list.html", {"stadions": stadions,
        "categories": S_Category.objects.all(),
        "category": category,
        "q": q})


@login_required
def stadion_detail_view(request, pk):
    stadion = get_object_or_404(Stadion, pk=pk)
    return render(request, "stadion_detail.html", {"stadion": stadion})


def team_error(has_team, playrs_need):
    if has_team not in ("yes", "no"):
        return "Выберите, есть ли у вас команда"
    if has_team == "no":
        if not playrs_need or not playrs_need.isdigit() or int(playrs_need) < 1:
            return "Укажите, сколько игроков не хватает"
        return None


@login_required
def order_create_view(request, pk):
    stadion = get_object_or_404(Stadion, pk=pk)
    if not stadion.is_free:
        return render(request, "stadion_detail.html",{"stadion": stadion, "error": "Это поле уже занято"})

    if request.method == "POST":
        has_team = request.POST.get("has_team")
        playrs_need = request.POST.get("playrs_need")

        error = team_error(has_team, playrs_need)
        if error:
            return render(request, "order_form.html", {
                "stadion": stadion, "error": error,
                "has_team": has_team, "playrs_need": playrs_need
            })

        if has_team == "yes":
            Order.objects.create(user=request.user, stadion=stadion,has_team=True, playrs_need=0, status="active")
        else:
            Order.objects.create(user=request.user, stadion=stadion,has_team=False, playrs_need=int(playrs_need), status="active")

        stadion.is_free = False          
        return redirect("my_orders")

    return render(request, "order_form.html", {"stadion": stadion, "has_team": "yes"})


@login_required
def my_orders_view(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, "my_orders.html", {
        "active": orders.filter(status="active"),
        "history": orders.exclude(status="active"),
    })


@login_required
def order_detail_view(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    players = Participant.objects.filter(order=order)
    return render(request, "order_detail.html", {"order": order, "players": players})


@login_required
def order_edit_view(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)

    if order.status != "active":        
        return redirect("order_detail", pk=pk)

    if request.method == "POST":
        has_team = request.POST.get("has_team")
        playrs_need = request.POST.get("playrs_need")

        error = team_error(has_team, playrs_need)
        if error:
            return render(request, "order_form.html", {"stadion": order.stadion, "order": order, "error": error,"has_team": has_team, "playrs_need": playrs_need})

        if has_team == "yes":
            order.has_team = True
            order.playrs_need = 0
        else:
            order.has_team = False
            order.playrs_need = int(playrs_need)
        order.save()
        return redirect("order_detail", pk=pk)

    if order.has_team:
        context = {"has_team": "yes"}
    else:
        context = {"has_team": "no", "playrs_need": order.playrs_need}
    context["stadion"] = order.stadion
    context["order"] = order
    return render(request, "order_form.html", context)


@login_required
def order_delete_view(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)

    if request.method == "POST":
        if order.status == "active":     
            order.stadion.is_free = True
            order.stadion.save()
        order.delete()
        return redirect("my_orders")

    return render(request, "order_confirm_delete.html", {"order": order})



@login_required
def order_cancel_view(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    if request.method == "POST" and order.status == "active":
        order.status = "cancelled"
        order.save()
        order.stadion.is_free = True     
        order.stadion.save()
    return redirect("my_orders")


@login_required
def order_finish_view(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    if request.method == "POST" and order.status == "active":
        order.status = "completed"
        order.save()
        order.stadion.is_free = True   
        order.stadion.save()
    return redirect("my_orders")



@login_required
def play_together_view(request, error=None):
    orders = Order.objects.filter(status="active", has_team=False)
    cards = []
    for order in orders:
        players = Participant.objects.filter(order=order)
        cards.append({
            "order": order,
            "players": players,
            "is_own": order.user == request.user,
            "joined": Participant.objects.filter(order=order, user=request.user),
            "is_full": len(players) >= order.playrs_need
        })
    return render(request, "play_together.html", {"cards": cards, "error": error})


@login_required
def join_order_view(request, pk):
    if request.method != "POST":
        return redirect("play_together")

    order = get_object_or_404(Order, pk=pk, status="active", has_team=False)
    players = Participant.objects.filter(order=order)

    if order.user == request.user:
        return play_together_view(request, error="Нельзя вступить в свой же заказ")
    if Participant.objects.filter(order=order, user=request.user):
        return play_together_view(request, error="Вы уже в этой команде")
    if len(players) >= order.playrs_need:
        return play_together_view(request, error="Команда уже набрана")

    Participant.objects.create(order=order, user=request.user)
    return redirect("play_together")


@login_required
def leave_order_view(request, pk):
    if request.method == "POST":
        Participant.objects.filter(order_id=pk, user=request.user).delete()
    return redirect("play_together")


@login_required
def profile_view(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, "profile.html",{"profile_user": request.user, "orders": orders, "is_own": True})


@login_required
def user_profile_view(request, pk):
    if pk == request.user.pk:
        return redirect("profile")
    profile_user = get_object_or_404(CustomUser, pk=pk)
    orders = Order.objects.filter(user=profile_user)
    return render(request, "profile.html",{"profile_user": profile_user, "orders": orders, "is_own": False})


@login_required
def profile_edit_view(request):
    user = request.user

    if request.method == "POST":
        email = request.POST.get("email")
        phone = request.POST.get("phone", "")
        about = request.POST.get("about", "")
        photo = request.FILES.get("photo")

        error = None
        if not email:
            error = "Укажите email"
        elif CustomUser.objects.filter(email=email).exclude(pk=user.pk).exists():
            error = "Этот email уже занят"
        elif len(phone) > 13:
            error = "Телефон не длиннее 13 символов"

        if error:
            return render(request, "profile_edit.html", {"error": error})

        user.email = email
        user.phone = phone
        user.about = about
        if photo:
            user.photo = photo
        user.save()
        return redirect("profile")

    return render(request, "profile_edit.html")


@login_required
def stadion_create_view(request):
    if request.method == "POST":
        name_s = request.POST.get("name_s")
        addres = request.POST.get("addres")
        disc = request.POST.get("disc")
        category = request.POST.get("category")
        price = request.POST.get("price")
        photo_s = request.FILES.get("photo_s")

        if not name_s or not addres or not disc or not category or not price:
            return render(request, "stadion_form.html", context={"error": "Заполните все поля", "categories": S_Category.objects.all(), "name_s": name_s, "addres": addres, "disc": disc, "category": category, "price": price},)
        if not category.isdigit() or not S_Category.objects.filter(pk=category).exists():
            return render(request, "stadion_form.html", context={"error": "Выберите формат поля", "categories": S_Category.objects.all(), "name_s": name_s, "addres": addres, "disc": disc, "category": category, "price": price},)
        try:
            float(price)
        except ValueError:
            return render(request, "stadion_form.html", context={"error": "Цена должна быть числом", "categories": S_Category.objects.all(), "name_s": name_s, "addres": addres, "disc": disc, "category": category, "price": price},)

        stadion = Stadion.objects.create(name_s=name_s, addres=addres, disc=disc, category_id=category, price=price, is_free=True)
        if photo_s:
            stadion.photo_s = photo_s
            stadion.save()
        return redirect("stadion_detail", pk=stadion.pk)

    return render(request, "stadion_form.html", context={"categories": S_Category.objects.all()},)


@login_required
def stadion_edit_view(request, pk):
    stadion = get_object_or_404(Stadion, pk=pk)

    if request.method == "POST":
        name_s = request.POST.get("name_s")
        addres = request.POST.get("addres")
        disc = request.POST.get("disc")
        category = request.POST.get("category")
        price = request.POST.get("price")
        photo_s = request.FILES.get("photo_s")

        if not name_s or not addres or not disc or not category or not price:
            return render(request, "stadion_form.html", context={"error": "Заполните все поля", "stadion": stadion, "categories": S_Category.objects.all(), "name_s": name_s, "addres": addres, "disc": disc, "category": category, "price": price},)
        if not category.isdigit() or not S_Category.objects.filter(pk=category).exists():
            return render(request, "stadion_form.html", context={"error": "Выберите формат поля", "stadion": stadion, "categories": S_Category.objects.all(), "name_s": name_s, "addres": addres, "disc": disc, "category": category, "price": price},)
        try:
            float(price)
        except ValueError:
            return render(request, "stadion_form.html", context={"error": "Цена должна быть числом", "stadion": stadion, "categories": S_Category.objects.all(), "name_s": name_s, "addres": addres, "disc": disc, "category": category, "price": price},)

        stadion.name_s = name_s
        stadion.addres = addres
        stadion.disc = disc
        stadion.category_id = category
        stadion.price = price
        if photo_s:
            stadion.photo_s = photo_s
        stadion.save()
        return redirect("stadion_detail", pk=pk)

    return render(request, "stadion_form.html", context={"stadion": stadion, "categories": S_Category.objects.all(), "name_s": stadion.name_s, "addres": stadion.addres, "disc": stadion.disc, "category": str(stadion.category_id), "price": stadion.price},)


@login_required
def stadion_delete_view(request, pk):
    stadion = get_object_or_404(Stadion, pk=pk)

    if request.method == "POST":
        stadion.delete()
        return redirect("stadions")

    return render(request, "stadion_confirm_delete.html", context={"stadion": stadion},)
