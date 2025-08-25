from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("categories/", views.categories_view, name="categories"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path("create/", views.create_listing, name="create-listing"),
    path("listing/<int:pk>", views.listing_view, name="listing"),
    path("close/<int:pk>", views.close_listing, name="close"),
    path("mylistings/", views.my_listings, name="my-listings"),
    path("watchlist/", views.watchlist, name="watchlist"),
    path("set_watchlist/<int:listing_id>",
         views.watchlist_item, name="set-watchlist"),
]
