from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import AuctionList, User, Comment, Bids, WatchList, Winner



def index(request):
    return render(request, "auctions/index.html")


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


@login_required(login_url="/login")
def createlisting(request):
    if request.method == "POST":
        item = AuctionList()
        item.seller = request.user.username
        item.title = request.POST.get("title")
        item.description = request.POST.get("description")
        item.category = request.POST.get("category")
        item.starting_bid = request.POST.get("starting_bid")
        
        # Submitting data of the image link is optional:
        if request.POST.get("image_link"):
            item.image_link = request.POST.get("image_link")
        else:
            item.image_link = "https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.smk114.net%2F2402.html&psig=AOvVaw21JHD_Noh6Bp5AKplSuwVY&ust=1646708551763000&source=images&cd=vfe&ved=0CAsQjRxqFwoTCNj_2qGks_YCFQAAAAAdAAAAABAD"

        item.save()

        # Get all the products after creating
        products = AuctionList.objects.all()
        empty = False

        if len(products) == 0:
            empty = True

        return render(request, "auctions/activelisting.html", {
            "products": products,
            "empty": empty
        })
    else:
        return render(request, "auctions/createlisting.html")
    

@login_required(login_url="/login")
def activelisting(request):
    products = AuctionList.objects.all()

    empty = False

    if len(products) == 0:
        empty == True

    return render(request, "auctions/activelisting.html", {
        "products": products,
        "empty": empty
    })


@login_required(login_url="/login")
def viewlisting(request, product_id):
    comments= Comment.objects.filter(listingid=product_id)

    if request.method == "POST":
        item = AuctionList.objects.get(id=product_id)
        newbid = int(request.POST.get("newbid"))

        if item.starting_bid >= newbid:
            product = AuctionList.objects.get(id=product_id)
            return render(request, "auctions/viewlisting.html", {
                "product": product,
                "message": "Your Bid should be higher than the Current one.",
                "msg_type": "danger",
                "comments": comments
            })
        
        else:
            item.starting_bid = newbid
            item.save()

            bidobj = Bids.objects.filter(listingid = product_id)
            if bidobj:
                bidobj.delete()

            obj = Bids()
            obj.user = request.user.username
            obj.title = item.title
            obj.listingid = product_id
            obj.bid = newbid
            obj.save()

            product = AuctionList.objects.filter(id = product_id)
            return render(request, "auctions/viewlisting.html", {
                "product": product,
                "message": "Your Bid is added.",
                "msg_type": "success",
                "comments": comments
            })

    else:
        product = AuctionList.objects.get(id=product_id)
        added = WatchList.objects.filter(
        listingid=product_id, user=request.user.username)
        return render(request, "auctions/viewlisting.html", {
            "product": product,
            "added": added,
            "comments": comments
        })


@login_required(login_url='/login')
def addtowatchlist(request, product_id):

    obj = WatchList.objects.filter(
        listingid=product_id, user=request.user.username)
    comments = Comment.objects.filter(listingid=product_id)
    # checking if it is already added to the watchlist
    if obj:
        # if its already there then user wants to remove it from watchlist
        obj.delete()
        # returning the updated content
        product = AuctionList.objects.get(id=product_id)
        added = WatchList.objects.filter(
            listingid=product_id, user=request.user.username)
        return render(request, "auctions/viewlisting.html", {
            "product": product,
            "added": added,
            "comments": comments
        })
    else:
        # if it not present then the user wants to add it to watchlist
        obj = WatchList()
        obj.user = request.user.username
        obj.listingid = product_id
        obj.save()
        # returning the updated content
        product = AuctionList.objects.get(id=product_id)
        added = WatchList.objects.filter(
            listingid=product_id, user=request.user.username)
        return render(request, "auctions/viewlisting.html", {
            "product": product,
            "added": added,
            "comments": comments
        })


# view for comments
@login_required(login_url='/login')
def addcomment(request, product_id):
    obj = Comment()
    obj.comment = request.POST.get("comment")
    obj.user = request.user.username
    obj.listingid = product_id
    obj.save()
    # returning the updated content
    print("displaying comments")
    comments = Comment.objects.filter(listingid=product_id)
    product = AuctionList.objects.get(id=product_id)
    added = WatchList.objects.filter(
        listingid=product_id, user=request.user.username)
    return render(request, "auctions/viewlisting.html", {
        "product": product,
        "added": added,
        "comments": comments
    })


# view when the user wants to close the bid
@login_required(login_url='/login')
def closebid(request, product_id):
    winobj = Winner()
    listobj = AuctionList.objects.get(id=product_id)
    obj = get_object_or_404(Bids, listingid=product_id)

    if not obj:
        message = "Delete Bid"
        msg_type = "danger"

    else: 
        bidobj = Bids.objects.get(listingid=product_id)
        winobj.owner = request.user.username
        winobj.winner = bidobj.user
        winobj.listingid = product_id
        winobj.winprice = bidobj.bid
        winobj.title = bidobj.title
        winobj.save()

        message = "Bid Closed"
        msg_type = "success"

        # Remove from bid
        bidobj.delete()

    # Remove from watchlist
    if WatchList.objects.filter(listingid=product_id):
        watchobj = WatchList.objects.filter(listingid=product_id)
        watchobj.delete()

    # Remove from comments
    if Comment.objects.filter(listingid=product_id):
        commentobj = Comment.objects.filter(listingid=product_id)
        commentobj.delete()

    # Remove from listing
    listobj.delete()

    winners = Winner.objects.all()

    empty = False

    if len(winners) == 0:
        empty = True
    
    return render(request, "auctions/closedlisting.html", {
        "products": winners,
        "empty": empty,
        "message": message,
        "msg_type": msg_type
    })


@login_required(login_url="/login")
def closedlisting(request):
    # List of products available in Winner model
    winners = Winner.objects.all()

    # Check of there are some products
    empty = False

    if len(winners) == 0:
        empty = True

    return render(request, "auctions/closedlisting.html", {
        "products": winners,
        "empty": empty
    })


@login_required(login_url=("/login"))
def dashboard(request):
    winners = Winner.objects.filter(winner=request.user.username)

    # Check for watchlist
    lst = WatchList.objects.filter(user=request.user.username)

    # List of products available in WinnerModel
    present = False
    prodlst = []
    i = 0

    if lst:
        present = True

        for item in lst:
            product = AuctionList.objects.get(id=item.listingid)
            prodlst.append(product)
        
    print(prodlst)

    return render(request, "auctions/dashboard.html", {
        "product_list": prodlst,
        "present": present,
        "products": winners
    })


@login_required(login_url="/login")
def categories(request):
    return render(request, "auctions/categories.html")


@login_required(login_url=("/login"))
def category(request, categ):
    categ_products = AuctionList.objects.filter(catefory=categ)
    empty = False

    if len(categ_products) == 0:
        empty = True

    return render(request, "auctions/category.html", {
        "categ": categ,
        "empty": empty,
        "products": categ_products
    })