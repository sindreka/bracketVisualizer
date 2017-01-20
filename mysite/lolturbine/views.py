from django.shortcuts import render

# Create your views here.

from .models import OngoingGame,TopographicalDescription,Nation,Continent,Player,NationInGame
from random import randint#, shuffle
from math import floor
from django.contrib.messages import get_messages
from django.contrib import messages
from django.http import HttpResponse,   HttpResponseRedirect
from django.core.urlresolvers import reverse

from django.contrib.auth.decorators import login_required


colors = ["red","blue","orange", "black", "teal", "cyan", "brown", "violet", "pink" ]


def getMessage(request):
    storage = get_messages(request)
    text = None
    for message in storage:
        return message

def addNations(request,m):
    try:
        i = 0
        while (True):

            index = int(request.POST[str(i) + "index"])
            name = request.POST[str(i) + "name"]
            border = request.POST[str(i) + "border"]
            x = int(request.POST[str(i) + "x"])
            y = int(request.POST[str(i) + "y"])

            n = Nation(name = name,topographical_description = m, border = border, index = index, x = x, y = y)
            n.save()
            i += 1
    except: 
        # not really checking for anything...
        a = 2
    return i

def addContinents(request,m):
    try:
        i = 0
        while (True):
            #index = int(request.POST["c" + str(i) + "index"])
            name = request.POST["c" + str(i) + "name"]
            nations = request.POST["c" + str(i) + "nations"]
            bonus = int(request.POST["c" + str(i) + "bonus"])
            c = Continent(bonus = bonus, topographical_description = m, name = name, nations = nations )
            c.save()
            i += 1
    except: 
        # not really checking for anything...
        a = 2
    return i

@login_required
def addMap(request):
    context = {}
    if request.method == "POST" : 
        ################ Create new map ########################
        name = request.POST.get("map_name")
        image = request.POST.get("imageLoader")
        m = TopographicalDescription(name = name, image = image, created_by = request.user )
        m.save()
        n = addNations(request,m)
        c = addContinents(request,m)
        text = "Map added with %i nations and %i continents." % (n,c)
        messages.add_message(request, messages.INFO, text)
        return HttpResponseRedirect(reverse('lolturbine:addMap'))
    context['text'] = getMessage(request)
    return render(request, 'lolturbine/addMap.html',context = context)

@login_required
def game(request,pk):
    context = {}
    return render(request, 'lolturbine/game.html',context = context)

def unique_color(g):
    while True:
        i = randint(0,len(colors)-1)
        p = Player.objects.filter(game = g, color = colors[i])
        try:
            p[0]
        except:
            return colors[i]

def start_game(g):
    ################ Create game #################
    nations = Nation.objects.filter(topographical_description = g.current_map).order_by("?")
    players = Player.objects.filter(game = g)

    player_index = 0
    i = 0

    player = players[player_index]
    nations_each = floor(nations.count()/players.count())

    for nation in nations[:nations_each*players.count()]:
        player = players[player_index]
        n = NationInGame(troops = 3, owner = player, area = nation, ongoing_game = g )  
        n.save()
        i += 1
        if (i == nations_each):
            i = 0
            player_index += 1
    if nations_each*players.count() < nations.count():
        for nation in nations[nations_each*players.count():]:
            n = NationInGame(troops = 3, area = nation, ongoing_game = g )  
            n.save()
    g.current_player = randint(0,players.count()-1)
    g.save()
    ###### SEND MAIL TIL DENNE SPILLEREN ######

@login_required
def index(request):
    current_user = request.user
    current_games = OngoingGame.objects.filter( current_player = "", player__user = current_user)
    ongoing_games = OngoingGame.objects.filter( player__user = current_user).exclude( current_player = "" )
    joinable_games = OngoingGame.objects.filter( current_player = "").exclude(player__user = current_user)
    m = TopographicalDescription.objects.all()

    context = {
        'maps': m,
        'joinable_games': joinable_games,
        'current_games': current_games,
        'ongoing_games': ongoing_games,
        'user': current_user,
    }


    if request.method == "POST":
        if "join" in request.POST:
            ############# ADD PLAYER ###########
            g = request.POST["j"]
            g = OngoingGame.objects.get(pk = g)
            all_players = Player.objects.filter(game = g).order_by("index")
            i = 0;
            for player in all_players:
                if player.index != i:
                    index = i
                    break
                i += 1
            else: 
                index = i

            color = unique_color(g)
            p = Player( user = current_user, index = index, color = color, game = g )
            p.save()

            # Joined game
            text = "Successfully joined game."
            if int(all_players.count()) + 1 == g.num_players:
                start_game(g)
        elif "leave" in request.POST:
            g = request.POST["l"]
            g = OngoingGame.objects.get(pk = g)
            index = Player.objects.filter(game = g).count()  

            p = Player.objects.filter(user = current_user, game = g)
            p.delete()
            if Player.objects.filter(game = g).count() == 0:
                ############### DELETE GAME ###############
                g.delete()
            text = "Successfully removed from game."

        elif "new" in request.POST:
            ############ ADD NEW GAME ###########
            m = request.POST["map"]
            m = TopographicalDescription.objects.get(name=m)
            num_players = int(request.POST["num_players"])
            time_limit = int(request.POST["time_limit"])*60
            
            o = OngoingGame(current_map = m, time_per_move = time_limit,num_players = num_players)
            o.save()
            
            ############# ADD PLAYER ###########
            i = randint(0,len(colors)-1)
            p = Player( user = current_user, index = 0, game = o, color = colors[i] )
            p.save()

            # New game was added
            text = "Successfully added a new game."
        messages.add_message(request, messages.INFO, text)
        return HttpResponseRedirect(reverse('lolturbine:index'))


    context['text'] = getMessage(request)

    return render(request, 'lolturbine/index.html',context = context)






