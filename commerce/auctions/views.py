from datetime import datetime

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Max, OuterRef, Subquery
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse

from .models import User, Listing, Bid, Comment, Category
from .forms import CreateListingForm


def index(request):
    cat = request.GET.get('cat')
    if cat is not None:
        listings = Listing.objects.annotate(
            max_bid=Max("bids__ammount")).order_by('-created_at').filter(category=cat)
    else:
        listings = Listing.objects.annotate(
            max_bid=Max("bids__ammount")).order_by('-created_at')
    return render(request, "auctions/index.html", {
        "listings": listings
    })

# LISTINGS


@login_required(login_url="login")
def create_listing(request):
    if request.method == "POST":
        form = CreateListingForm(request.POST)
        if form.is_valid():
            # Get the current time
            now = datetime.now()
            # Save Listing object
            new_listing = Listing(
                active=True,
                author=request.user,
                created_at=now,
                title=form.cleaned_data["title"],
                description=form.cleaned_data["description"],
                img_url=form.cleaned_data["img_url"],
                category=form.cleaned_data["category"],
            )
            new_listing.save()
            # Save Bid object
            initial_bid = Bid(
                user=request.user,
                listing=new_listing,
                ammount=form.cleaned_data["base_bid"],
                created_at=now
            )
            initial_bid.save()
            # Redirect to listing page - TODO
            return HttpResponseRedirect(reverse("listing", kwargs={"pk": new_listing.id}))
        # Else error message
        else:
            return render(request, "auctions/create.html", {
                "message": "Please check all required fields.",
                "form": form,
            })

    form = CreateListingForm()
    return render(request, "auctions/create.html", {
        "form": form,
    })


def listing_view(request, pk):
    listing = Listing.objects.get(pk=pk)
    comments = Comment.objects.filter(listing=listing).order_by('-created_at')
    current_bid = Bid.objects.filter(
        listing=listing).order_by('-ammount').first()
    total_bids = len(Bid.objects.filter(
        listing=listing))
    in_watchlist = True if request.user in listing.watchers.all() else False
    if request.user.is_authenticated:
        has_user_bid = True if Bid.objects.filter(
            listing=listing).filter(user=request.user).exists() else False
    else:
        has_user_bid = False

    if request.method == "POST":
        # Check if the user is authenticated
        if not request.user.is_authenticated:
            return redirect(reverse('login'))
        # Bid
        if 'add_bid' in request.POST:
            # Check if the bid is higher than the current
            bid_ammount = request.POST["bid_ammount"]
            if float(bid_ammount) <= current_bid.ammount:
                return render(request, "auctions/listing.html", {
                    "listing": listing,
                    "current_bid": current_bid,
                    "total_bids": total_bids,
                    "has_user_bid": has_user_bid,
                    "in_watchlist": in_watchlist,
                    "comments": comments,
                    "message": "Your bid has to be higher than the current bid."
                })
            # Create a bid with the new ammount
            else:
                now = datetime.now()
                new_bid = Bid(
                    user=request.user,
                    listing=listing,
                    ammount=float(bid_ammount),
                    created_at=now
                )
                new_bid.save()
            # Redirect to listing page
                return HttpResponseRedirect(reverse('listing', kwargs={"pk": pk}))
        # Comment
        elif 'send_comment' in request.POST:
            comment_body = request.POST["comment_body"]
            new_comment = Comment(
                author=request.user,
                listing=listing,
                body=comment_body,
                created_at=datetime.now()
            )
            new_comment.save()
            return HttpResponseRedirect(reverse('listing', kwargs={"pk": pk}))

    # GET
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "current_bid": current_bid,
        "total_bids": total_bids,
        "has_user_bid": has_user_bid,
        "in_watchlist": in_watchlist,
        "comments": comments,
    })


def categories_view(request):
    categories = Category.objects.all()
    return render(request, 'auctions/categories.html', {
        "categories": categories,
    })


@login_required(login_url="login")
def my_listings(request):
    listings = Listing.objects.annotate(
        max_bid=Max("bids__ammount")).order_by('-created_at').filter(author=request.user)
    won_listings = []  # TODO

    print(f"DEBUG: Won listings: {won_listings}")
    return render(request, "auctions/mylistings.html", {
        "listings": listings,
        "won_listings": won_listings,
    })


@login_required(login_url="login")
def close_listing(request, pk):
    listing = Listing.objects.get(pk=pk)
    if request.method == "POST" and request.user == listing.author:
        listing.active = False
        listing.save()
        return HttpResponseRedirect(reverse('listing', kwargs={"pk": pk}))
    return render(request, 'auctions/close.html', {
        "listing": listing
    })

# WATCHLIST


def watchlist_item(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    if request.user in listing.watchers.all():
        request.user.watchlist.remove(listing)
    else:
        request.user.watchlist.add(listing)
    print(f"Watchlist: {request.user.watchlist}")

    return HttpResponseRedirect(reverse('listing', args=(listing_id, )))


def watchlist(request):
    watched_listings = request.user.watchlist.all()
    print(f"DEBUG: {watched_listings}")
    return render(request, 'auctions/watchlist.html', {
        'watched_listings': watched_listings
    })


# LOGIN


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
