from django.contrib import admin

# Register your models here.

from .models import OngoingGame, Continent, TopographicalDescription, NationInGame, Nation, Player,PlayerStats, Comment,gameLog

class ContinentAdmin(admin.TabularInline):
    model = Continent
    
class NationAdmin(admin.TabularInline):
    model = Nation

class TopographicalDescriptionAdmin(admin.ModelAdmin):
    fieldset = [ 
        ("Map name", {'fields': ['name']}),
    ]
    inlines = [ContinentAdmin,NationAdmin]


admin.site.register(OngoingGame)
admin.site.register(Player)
admin.site.register(PlayerStats)
admin.site.register(Comment)
admin.site.register(NationInGame)
admin.site.register(TopographicalDescription,TopographicalDescriptionAdmin)
admin.site.register(Continent)
admin.site.register(Nation)
admin.site.register(gameLog)
