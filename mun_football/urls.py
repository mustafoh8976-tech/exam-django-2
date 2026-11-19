from django.urls import path

from . import views

urlpatterns = [
    path("", views.home_view, name="home"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    # CRUD стадионов
    path("fields/", views.stadions_view, name="stadions"),                                   # Read (список)
    path("fields/add/", views.stadion_create_view, name="stadion_create"),                   # Create
    path("fields/<int:pk>/", views.stadion_detail_view, name="stadion_detail"),              # Read (один)
    path("fields/<int:pk>/edit/", views.stadion_edit_view, name="stadion_edit"),             # Update
    path("fields/<int:pk>/delete/", views.stadion_delete_view, name="stadion_delete"),       # Delete

    # CRUD заказов
    path("fields/<int:pk>/book/", views.order_create_view, name="order_create"),      # Create
    path("my-fields/", views.my_orders_view, name="my_orders"),                       # Read (список)
    path("bookings/<int:pk>/", views.order_detail_view, name="order_detail"),         # Read (один)
    path("bookings/<int:pk>/edit/", views.order_edit_view, name="order_edit"),        # Update
    path("bookings/<int:pk>/delete/", views.order_delete_view, name="order_delete"),  # Delete
    path("bookings/<int:pk>/cancel/", views.order_cancel_view, name="order_cancel"),
    path("bookings/<int:pk>/finish/", views.order_finish_view, name="order_finish"),

    # играем вместе
    path("play-together/", views.play_together_view, name="play_together"),
    path("bookings/<int:pk>/join/", views.join_order_view, name="join_order"),
    path("bookings/<int:pk>/leave/", views.leave_order_view, name="leave_order"),

    # профиль
    path("profile/", views.profile_view, name="profile"),
    path("profile/edit/", views.profile_edit_view, name="profile_edit"),
    path("users/<int:pk>/", views.user_profile_view, name="user_profile"),
]
