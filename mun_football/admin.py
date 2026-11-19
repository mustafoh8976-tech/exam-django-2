from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, Order, Participant, S_Category, Stadion


# через UserAdmin, чтобы пароли хэшировались
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("Профиль", {"fields": ("photo", "phone", "about")}),)
    add_fieldsets = UserAdmin.add_fieldsets + (("Профиль", {"fields": ("email",)}),)
    list_display = ("username", "email", "phone", "is_staff")
    list_filter = ("is_staff", "is_active")
    search_fields = ("username", "email", "phone")


class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name_c", "count_playrs")
    search_fields = ("name_c",)


class StadionAdmin(admin.ModelAdmin):
    list_display = ("name_s", "category", "addres", "price", "is_free")
    list_filter = ("category", "is_free")
    search_fields = ("name_s", "addres")


class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "stadion", "has_team", "playrs_need", "status")
    list_filter = ("status", "has_team")
    search_fields = ("user__username", "stadion__name_s")


class ParticipantAdmin(admin.ModelAdmin):
    list_display = ("order", "user")
    search_fields = ("user__username",)


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(S_Category, CategoryAdmin)
admin.site.register(Stadion, StadionAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Participant, ParticipantAdmin)
