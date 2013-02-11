from marketanalyzer.models import *
from django.contrib import admin

# TO DO: change __unicode__() to return names (instead of IDs)
#         OR follow foreign keys to get names (everywhere?)
#
# This is an issue applying to any aspect of the site that
# displays models that use FKs, not just here

class MarketAdmin(admin.ModelAdmin):
    
    # we have to follow a ForeignKey relation to get item name
    def getName(rec):
        return rec.typeID.typeName
    getName.short_description = 'Item'
    
    def getStation(rec):
        return rec.stationID.stationName
    getStation.short_description = 'Station'

    def getRegion(rec):
        return rec.stationID.regionID.regionName
    getRegion.short_description = 'Region'
    
    fieldsets = [
        (None,            {'fields': ['typeID', 'stationID', 'range', 'jumps',
                                      'issueDate', 'duration',
                                      'lastUpdated']}),
        ('Price details', {'fields': ['price', 'volRemaining', 'orderID',
                                      'volEntered', 'minVolume', 'bid']}),
    ]
    list_display = ('typeID', getName, getRegion, getStation, 'price', 'bid',
                    'lastUpdated')
    list_filter = ['lastUpdated', 'bid']
    search_fields = ['typeID__typeName']
    
class invTypesAdmin(admin.ModelAdmin):
    list_display = ('typeID', 'groupID', 'typeName', 'marketGroupID', 'volume',
                    'basePrice', 'medianBuyPrice', 'medianSellPrice',
                    'meanBuyPrice', 'meanSellPrice',
                    'highBuyPrice', 'highSellPrice', 'isLPreward')
    list_filter = ['isLPreward']
    search_fields = ['typeID', 'typeName']
    
class invMarketGroupsAdmin(admin.ModelAdmin):
    list_display = ('marketGroupID', 'marketGroupName', 'parentGroupID', 'description')
    search_fields = ['marketGroupName', 'description']
    
class mapRegionsAdmin(admin.ModelAdmin):
    list_display = ('regionID', 'regionName')
    list_filter = ['regionName']
    search_fields = ['regionName']
    
class mapConstellationsAdmin(admin.ModelAdmin):
    list_display = ('constellationID', 'constellationName', 'regionID')
    list_filter = ['constellationName']
    search_fields = ['constellationName']
    
class mapSolarSystemsAdmin(admin.ModelAdmin):
    list_display = ('solarSystemID', 'solarSystemName', 'constellationID', 'regionID', 'security', 'securityClass')
    list_filter = ['securityClass']
    
class staStationsAdmin(admin.ModelAdmin):
    list_display = ('stationID', 'stationName', 'solarSystemID',)
    
class modifiedAdmin(admin.ModelAdmin):
    pass

class LP_RewardAdmin(admin.ModelAdmin):
    list_display = ('LP_store_id', 'corp_id', 'LP_cost', 'ISK_cost', 'award_type_id', 'award_qty')
    search_fields = ['corp_id', 'award_type_id']

class evenamesAdmin(admin.ModelAdmin):
    list_display = ('itemid', 'itemname', 'categoryid', 'groupid', 'typeid')
    list_filter = ['categoryid', 'groupid']

admin.site.register(MarketRecord, MarketAdmin)
admin.site.register(invTypes, invTypesAdmin)
# Since migrating to pgsql, registering invMarketGroupsAdmin causes no entries
# to appear in that admin section.
admin.site.register(invMarketGroups)#, invMarketGroupsAdmin)
admin.site.register(mapRegions, mapRegionsAdmin)
admin.site.register(mapConstellations, mapConstellationsAdmin)
admin.site.register(mapSolarSystems, mapSolarSystemsAdmin)
admin.site.register(staStations, staStationsAdmin)
admin.site.register(modified, modifiedAdmin)
admin.site.register(LP_Reward, LP_RewardAdmin)
admin.site.register(evenames, evenamesAdmin)
