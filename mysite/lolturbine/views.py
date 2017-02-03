from django.shortcuts import render

# Create your views here.

from .models import OngoingGame,TopographicalDescription,Nation,Continent,Player,NationInGame,Comment
from random import randint#, shuffle
from math import floor
from django.contrib.messages import get_messages
from django.contrib import messages
from django.http import HttpResponse,   HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core import serializers
import simplejson as json
import math,random

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
    game = OngoingGame.objects.filter(pk = pk)
    if request.method == "POST":
        comment = request.POST["chat"]
        player = Player.objects.filter(user = request.user, game = game )[0]
        c = Comment(player = player, comment = comment)
        c.save()
        text = " Comment successfully added! "
        messages.add_message(request, messages.INFO, text)
#        return HttpResponseRedirect(reverse('lolturbine/game/10'))
        return HttpResponseRedirect('/lolturbine/game/' + str(pk) )


    comments = Comment.objects.filter(player__game = game)

    ###### Calculating troops #######
    current_player = Player.objects.filter(user = request.user, game = game[0])
    nations_in_game = NationInGame.objects.filter(owner = current_player[0], ongoing_game = game[0])
    continents = Continent.objects.filter(topographical_description = game[0].current_map)


    # Dette skal bare skje første gangen...
    player = current_player[0]
    if player.nTroops == 0 and current_player[0].index == game[0].current_player and player.new_troops == 0:


        troopsFromArea = max(3, math.floor(len(list(nations_in_game))/3))
        troopsFromContinents = 0
        print("YYYYYYYYYYYYYYOOOOOOOOOOOOOOOOOOOOOOo")

        for continent in continents: 
            nations_in_continent = list(map(int, continent.nations.split(",") ))
            number = 0
            for nation in nations_in_game:    
                if nation.area.index in nations_in_continent:    
                    number += 1
            if number == len(nations_in_continent):
                troopsFromContinents += continent.bonus

        player.nTroops = troopsFromArea + troopsFromContinents
        player.new_troops = 1
        player.save()
        print(player.nTroops)
        print(troopsFromArea + troopsFromContinents)

        #print(troopsFromArea + troopsFromContinents)
        #print(current_player[0].nTroops)

    current_player = Player.objects.filter(user = request.user, game = game[0])
    print(current_player[0].nTroops)
    ###################Getting information#############
    nations = Nation.objects.filter(topographical_description = game[0].current_map)
    nations_in_game = NationInGame.objects.filter(ongoing_game = game[0])
    continents = Continent.objects.filter(topographical_description = game[0].current_map)
    players = Player.objects.filter(game = game[0])
    current_map = TopographicalDescription.objects.filter(name = game[0].current_map.name)

    ######################Makes the information avilable to json#######################
    game = serializers.serialize('json', game)
    nations_in_game = serializers.serialize('json', nations_in_game)
    continents = serializers.serialize('json', continents)
    nations = serializers.serialize('json', nations)
    current_map = serializers.serialize('json', current_map)
    players = serializers.serialize('json', players)
    current_player = serializers.serialize('json', current_player)





    context = {
        'game' : game,
        'nations' : nations,
        'nations_in_game' : nations_in_game,
        'continents' : continents,
        'current_map' : current_map,
        'players' : players,
        'comments' : comments,
        'text' : getMessage(request),
        'current_player' : current_player,

#        'current_player' : 
    }
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
            n = NationInGame(troops = 3, area = nation, ongoing_game = g  )  
            n.save()
    g.current_player = randint(0,players.count()-1)
    g.save()
    ###### SEND MAIL TIL DENNE SPILLEREN ######

@login_required
def index(request):
    current_user = request.user
    current_games = OngoingGame.objects.filter( current_player = 150, player__user = current_user)
    ongoing_games = OngoingGame.objects.filter( player__user = current_user).exclude( current_player = 150 )
    joinable_games = OngoingGame.objects.filter( current_player = 150).exclude(player__user = current_user)
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
            text = " Successfully joined game! "
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
            text = " Successfully removed from game! "

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
            text = " Successfully added a new game! "
        messages.add_message(request, messages.INFO, text)
        return HttpResponseRedirect(reverse('lolturbine:index'))


    context['text'] = getMessage(request)

    return render(request, 'lolturbine/index.html',context = context)


def place_troops(request,pk,n):
    a = 0

    user = request.user
    game = OngoingGame.objects.get(pk = int(pk))
    player = Player.objects.get(game = game, user = user)
    nation = Nation.objects.get(index = int(n), topographical_description = game.current_map)
    nation = NationInGame.objects.get(ongoing_game = game, area = nation)

    if player.nTroops > 0 and nation.owner == player: 
        nation.troops += 1
        nation.save()
        player.nTroops -= 1
        player.save()
        a = 1
    return HttpResponse(a)

def attack(request,pk,a,v):
    aa = 0
    #a,v = v,a

    user = request.user
    game = OngoingGame.objects.get(pk = int(pk))
    player = Player.objects.get(game = game, user = user)
    attack = Nation.objects.get(index = int(a), topographical_description = game.current_map)
    victim = Nation.objects.get(index = int(v), topographical_description = game.current_map)
    attack = NationInGame.objects.get(ongoing_game = game, area = attack)
    victim = NationInGame.objects.get(ongoing_game = game, area = victim)
    adice = []
    vdice = []
    b = list(map(int,attack.area.border.split(",")))
    print(player)
    print("attack")
    print(attack)
    print(attack.troops)
    print(attack.owner)
    print(attack.area)
    print(attack.area.index)
    print("victim")
    print(victim)
    print(victim.troops)
    print(victim.owner)
    print(victim.area)
    print(victim.area.index)
    print("!!!!!!!Slutt!!!!!!!")
    if attack.owner == player and victim.owner != player and attack.troops > 1 and victim.area.index in b:
        random.seed()
        for i in range(min(3,attack.troops-1)):
            adice.append(random.randint(1, 6))
        for j in range(min(2,victim.troops)):
            vdice.append(random.randint(1, 6))
        adice.sort(reverse = True)
        vdice.sort(reverse = True)
        if adice[0] > vdice[0]:
            victim.troops -= 1
        else:
            attack.troops -= 1
        if len(adice) > 1 and len(vdice) > 1:   
            if adice[1] > vdice[1]:
                victim.troops -= 1
            else:
                attack.troops -= 1
        if victim.troops == 0:
            victim.owner = player
            victim.troops = 1
            attack.troops -= 1
        attack.save()
        victim.save()

    aa = 1
    d = json.dumps([aa,adice,vdice])
    return HttpResponse(d)

def blob(game,f,t,player):
    nodes = list(map(int,f.area.border.split(",")))
    index = list(map(int,f.area.border.split(",")))
    #nodes = f.area.border
    #index = f.area.border
    nations = NationInGame.objects.filter(ongoing_game = game).order_by("area_id") # OBS, funker ikke generelt!!!
    while len(nodes) > 0:
        element = nodes.pop()
        if nations[element].owner == player:
            b = nations[element].area.border
            for border in b:
                if border not in index:
                    index.append(border)
                    nodes.append(border)
        if t.area.index in index:
            return 1
    return 0

def reinforce(request,pk,f,t):
    a = 0

    user = request.user
    game = OngoingGame.objects.get(pk = int(pk))
    player = Player.objects.get(game = game, user = user)
    fo = Nation.objects.get(index = int(f), topographical_description = game.current_map)
    to = Nation.objects.get(index = int(t), topographical_description = game.current_map)
    fo = NationInGame.objects.get(ongoing_game = game, area = fo)
    to = NationInGame.objects.get(ongoing_game = game, area = to)
    print("masse Stuff")
    print(blob(game,fo,to,player))
    print(fo.owner == player)
    print(to.owner == player)
    print(fo.troops > 1)
    if (fo.owner == player and to.owner == player and blob(game,fo,to,player) and fo.troops > 1): 
        print("Yooooooo")
        fo.troops -= 1
        to.troops += 1
        fo.save()
        to.save()
        a = 1
        

    return HttpResponse(a)




