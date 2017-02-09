from django.shortcuts import render

# Create your views here.

from .models import OngoingGame,TopographicalDescription,Nation,Continent,Player,NationInGame,Comment,PlayerStats
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
            name = request.POST[str(i) + "name"]
            border = request.POST[str(i) + "border"]
            x = int(request.POST[str(i) + "x"])
            y = int(request.POST[str(i) + "y"])
            n = Nation(name = name,topographical_description = m, border = border, index = i, x = x, y = y)
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
def endturn(u,game):
    nations = NationInGame.objects.filter(ongoing_game = game)
    current_player = Player.objects.get(game = game, index = game.current_player)
    playersNations = NationInGame.objects.filter(ongoing_game = game, owner = current_player)
    players = Player.objects.filter(game = game)

    ps = PlayerStats.objects.get(user = u.user) 

    ps.total_turns += 1
    if current_player.stage > 4:
        ps.turns_skipped += 1
    
    current_player.stage = 0
    # Sjekk om spillet er ferdig
    if len(list(playersNations)) == len(list(nations)):
        # Da er spillet ferdig
        ps.games_won += 1
        current_player.stage = 10
        
        # Her må også score oppdateres!
        # De andre skal tape!

    # Vi sjekker om en spiller blir slått ut hver gang et område blir tatt over.
    ps.save()
    

    current_player.save()
    loop = True
    candidate = game.current_player
    while loop:
        candidate = (candidate + 1) % game.num_players
        p = Player.objects.get(game = game, index = candidate)
        if p.stage > -1:
            loop = False
    game.current_player = candidate
    game.save()

@login_required
def game(request,pk):
    game = OngoingGame.objects.get(pk = pk)
    u = request.user
    current_player = Player.objects.get(user = u, game = game)
    if "chat" in request.POST:
        comment = request.POST["c"]
        player = Player.objects.filter(user = u, game = game )[0]
        c = Comment(player = player, comment = comment)
        c.save()
        text = " Comment successfully added! "
        messages.add_message(request, messages.INFO, text)
        return HttpResponseRedirect('/lolturbine/game/' + str(pk) )
    elif "endturn" in request.POST:
        if game.current_player == current_player.index:
            endturn(request,game)
        return HttpResponseRedirect('/lolturbine/game/' + str(pk) )
    elif "leave" in request.POST:
        
        current_player.stage = -2
        nations = NationInGame.objects.filter(ongoing_game = game, owner = current_player)
        for nation in nations:
            nation.owner = None
            nation.save()
        ####################ADD things to player stats#######################################
        current_player.save()
        counter = 0;
        players = Player.objects.filter(game = game)
        for player in players: 
            if player.stage > -1:
                play = player
                counter += 1
        if counter < 1:
            game.delete()
        elif counter == 1:
            #############Sett en vinner######################
           
            print(play)
            play.stage = 10
            play.save()
        elif game.current_player == current_player.index:
            candidate = game.current_player
            loop = True
            while loop:
                candidate = (candidate + 1) % game.num_players
                p = Player.objects.get(game = game, index = candidate)
                if p.stage > -1:
                    loop = False
            game.current_player = candidate
            game.save()


        return HttpResponseRedirect(reverse('lolturbine:index'))
        
    comments = Comment.objects.filter(player__game = game)
    ###### Calculating troops #######

    nations_in_game = NationInGame.objects.filter(owner = current_player, ongoing_game = game)
    continents = Continent.objects.filter(topographical_description = game.current_map)

    player = current_player
    if current_player.index == game.current_player and player.stage == 0:


        troopsFromArea = max(3, math.floor(len(list(nations_in_game))/3))
        troopsFromContinents = 0

        for continent in continents: 
            nations_in_continent = list(map(int, continent.nations.split(",") ))
            number = 0
            for nation in nations_in_game:    
                if nation.area.index in nations_in_continent:    
                    number += 1
            if number == len(nations_in_continent):
                troopsFromContinents += continent.bonus

        player.nTroops = troopsFromArea + troopsFromContinents
        player.stage = 1
        player.save()

    game = OngoingGame.objects.filter(pk = pk)
    current_player = Player.objects.filter(user = u, game = game[0])
    ###################Getting information#############
    nations = Nation.objects.filter(topographical_description = game[0].current_map)
    nations_in_game = NationInGame.objects.filter(ongoing_game = game[0])
    continents = Continent.objects.filter(topographical_description = game[0].current_map)
    players = Player.objects.filter(game = game[0])
    users = [player.user.username for player in players]
    #print(users)
    current_map = TopographicalDescription.objects.filter(name = game[0].current_map.name)
#    users = User.objects.filter(game = game)

    ######################Makes the information avilable to json#######################
    game = serializers.serialize('json', game)
    nations_in_game = serializers.serialize('json', nations_in_game)
    continents = serializers.serialize('json', continents)
    nations = serializers.serialize('json', nations)
    current_map = serializers.serialize('json', current_map)
    players = serializers.serialize('json', players)
    current_player = serializers.serialize('json', current_player)
    users = json.dumps(users)





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
        'users' : users,

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
    players = Player.objects.filter(game = g).order_by("index")

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
    random.seed()
    g.current_player = randint(0,players.count()-1)
    g.save()
    player = players[g.current_player]
    player.stage = 0
    player.save()
    ###### SEND MAIL TIL DENNE SPILLEREN ######

def makePS(current_user):
    try:
        ps = PlayerStats.objects.get(user = current_user)
    except:
        ps = PlayerStats(user = current_user)
        ps.save()

@login_required
def index(request):
    current_user = request.user
    current_games = OngoingGame.objects.filter( current_player = 150, player__user = current_user).exclude(player__stage = -2)
    ongoing_games = OngoingGame.objects.filter( player__user = current_user).exclude( current_player = 150 ).exclude(player__stage = -2)
    joinable_games = OngoingGame.objects.filter( current_player = 150).exclude(player__user = current_user).exclude(player__stage = -2)
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
            makePS(current_user)
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
            makePS(current_user)
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

@login_required
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


@login_required
def attack(request,pk,a,v):
    aa = 0

    user = request.user
    game = OngoingGame.objects.get(pk = int(pk))
    player = Player.objects.get(game = game, user = user)

    attack = Nation.objects.get(index = int(a), topographical_description = game.current_map)
    victim = Nation.objects.get(index = int(v), topographical_description = game.current_map)

    attack = NationInGame.objects.get(ongoing_game = game, area = attack)
    victim = NationInGame.objects.get(ongoing_game = game, area = victim)
    defender = Player.objects.get(game = game, user = victim.owner.user)
    adice = []
    vdice = []
    b = list(map(int,attack.area.border.split(",")))
    if attack.owner == player and victim.owner != player and attack.troops > 1 and victim.area.index in b:
        player.stage = 2
        player.save()
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
            v = NationInGame.objects.filter(ongoing_game = game, owner = defender)
            a = NationInGame.objects.filter(ongoing_game = game, owner = player)
            al = NationInGame.objects.filter(ongoing_game = game)
            if v.count() == 0:
                victim.stage = -1
            if a.count() == al.count():
                attack.stage = 10
            ################Sjekk om denne spilleren har tapt!######################
        attack.save()
        victim.save()

    aa = 1
    d = json.dumps([aa,adice,vdice])
    return HttpResponse(d)


def blob(game,f,t, player):
    nodes = []
    index = []
    index.append(int(f.area.index))
    nodes.append(int(f.area.index))

    nations = NationInGame.objects.filter(ongoing_game = game).order_by("area_id")
    while len(nodes) > 0:
        element = nodes.pop()
        if nations[element].owner == player:
            b = list(map(int,nations[element].area.border.split(",")))
            for border in b:
                if border not in index:
                    index.append(int(border))
                    nodes.append(int(border))
        if t.area.index in index:
            return 1
    return 0

@login_required
def move_forces(request,pk,f,t):
    a = 0
    game = OngoingGame.objects.get(pk = int(pk))
    player = Player.objects.get(game = game, user = request.user)
    fo = Nation.objects.get(index = int(f), topographical_description = game.current_map)
    to = Nation.objects.get(index = int(t), topographical_description = game.current_map)
    fo = NationInGame.objects.get(ongoing_game = game, area = fo)
    to = NationInGame.objects.get(ongoing_game = game, area = to)
    if (fo.owner == player and to.owner == player and fo.troops > 1 and blob(game,fo,to,player)):
        fo.troops -= 1
        to.troops += 1
        fo.save()
        to.save()
        a = 1
    return a


@login_required
def reinforce_battle(request,pk,f,t):
    a = move_forces(request,pk,f,t)
    return HttpResponse(a)

@login_required
def reinforce(request,pk,f,t):
    a = move_forces(request,pk,f,t)
    game = OngoingGame.objects.get(pk = int(pk))
    player = Player.objects.get(game = game, user = request.user)
    player.stage = 3
    player.save()
    return HttpResponse(a)




