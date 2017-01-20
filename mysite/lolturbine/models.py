from django.db import models
from django.utils import timezone


from django.contrib.auth.models import User


class TopographicalDescription(models.Model):
    name = models.CharField(max_length = 200)
    image = models.FileField(upload_to='lolturbine/static/maps')
    created_by = models.ForeignKey(User, blank = True)
    pub_date = models.DateTimeField(default = timezone.now)
    def __str__(self):
        return self.name
    class Meta:
        ordering = ['name']

class Continent(models.Model):
    bonus = models.IntegerField()
    topographical_description = models.ForeignKey(TopographicalDescription, blank = True)
    name = models.CharField(max_length = 200)
    nations = models.CharField(max_length = 200)
    def __str__(self):
        return self.name


class Nation(models.Model):
    name = models.CharField(max_length = 200)
    topographical_description = models.ForeignKey(TopographicalDescription, blank = True)
    border = models.CharField(max_length = 200)

    index = models.IntegerField()
    x = models.IntegerField()
    y = models.IntegerField()

    def __str__(self):
        return self.name

class OngoingGame(models.Model):

    current_map = models.ForeignKey(TopographicalDescription, blank = True)
    num_players = models.IntegerField()
    current_player = models.CharField(max_length = 200,default = "")
    time_per_move = models.IntegerField()
    time_since_last_move = models.DateTimeField(default = timezone.now)
    pub_date = models.DateTimeField(default = timezone.now)

    def __str__(self):
        return "map: %s, number of players: %d, timelimit: %d seconds" % (self.current_map.name,self.num_players,self.time_per_move)
    class Meta:
        ordering = ['pub_date']

class PlayerStats(models.Model):
    user = models.ForeignKey(User)
    games_won = models.IntegerField(default = 0)
    games_lost = models.IntegerField(default = 0)
    score = models.IntegerField(default = 0)
    total_games_played = models.IntegerField(default = 0)
    turns_skipped = models.IntegerField(default = 0)
    current_games = models.IntegerField(default = 0)
    def __str__(self):
        return self.user

class Player(models.Model):
    color = models.CharField(max_length = 200)
    user = models.ForeignKey(User)
    index = models.IntegerField()
    spoils = models.CharField(max_length = 200, blank = True) # Skal inn etter hvert, hvordan fikser man dette?
    game = models.ForeignKey(OngoingGame)
    mission = models.CharField(max_length = 200, blank = True) # Skal inn etter hvert, men usikker på hvordan
    def __str__(self):
        return "User %s in %s" % (self.user,self.game)

class Comment(models.Model):
    player = models.ForeignKey(Player)
    comment = models.CharField(max_length = 200)
    pub_date = models.DateTimeField(default = timezone.now)
    def __str__(self):
        return "%s's comment: %s" % (self.user,self.comment)    

class NationInGame(models.Model):
    troops = models.IntegerField()
    owner = models.ForeignKey(Player, blank = True)
    area = models.ForeignKey(Nation)
    ongoing_game = models.ForeignKey(OngoingGame)

    def __str__(self):
        return "%s's area %s has %i troops" % (self.owner,self.area.name,self.troops)
 
    











