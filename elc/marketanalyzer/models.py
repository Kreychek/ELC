import datetime

from django.db import models

# Shown before CCP-sourced models are the SQL statements to make the src table

#############################################################################
#CREATE TABLE "mapRegions" (
#  "regionID" int(11) NOT NULL,
#  "regionName" varchar(100) default NULL,
#  "x" double default NULL,
#  "y" double default NULL,
#  "z" double default NULL,
#  "xMin" double default NULL,
#  "xMax" double default NULL,
#  "yMin" double default NULL,
#  "yMax" double default NULL,
#  "zMin" double default NULL,
#  "zMax" double default NULL,
#  "factionID" int(11) default NULL,
#  "radius" double default NULL,
#  PRIMARY KEY  ("regionID")
#);
#
#CREATE INDEX "mapRegions_IX_factionID" ON "mapRegions" ("factionID");

class mapRegions(models.Model):
    """A table containing region data. Primarily used for regionID lookups."""
    regionID = models.IntegerField('Region ID', primary_key=True, db_column='regionID')
    regionName = models.CharField('Region Name', max_length=100)
    
    def __unicode__(self):
        return str(self.regionID)
        
    #class Meta:
    #    db_table = u'marketanalyzer_mapregions'

#############################################################################
#CREATE TABLE "mapConstellations" (
#  "regionID" int(11) default NULL,
#  "constellationID" int(11) NOT NULL,
#  "constellationName" varchar(100) default NULL,
#  "x" double default NULL,
#  "y" double default NULL,
#  "z" double default NULL,
#  "xMin" double default NULL,
#  "xMax" double default NULL,
#  "yMin" double default NULL,
#  "yMax" double default NULL,
#  "zMin" double default NULL,
#  "zMax" double default NULL,
#  "factionID" int(11) default NULL,
#  "radius" double default NULL,
#  PRIMARY KEY  ("constellationID")
#);
#
#CREATE UNIQUE INDEX "mapConstellations_IX_constellationID" ON "mapConstellations" ("constellationID","regionID");
#CREATE INDEX "mapConstellations_IX_factionID" ON "mapConstellations" ("factionID");
#CREATE INDEX "mapConstellations_IX_region" ON "mapConstellations" ("regionID");

class mapConstellations(models.Model):
    """A table containing constellation data. Primarily used for constellationID lookups."""
    regionID = models.ForeignKey(mapRegions, to_field='regionID',
                                 verbose_name='Region ID', db_index=True,
                                 db_column='regionID')
    constellationID = models.IntegerField('Constellation ID', primary_key=True)
    constellationName = models.CharField('Constellation name', max_length=100)
    
    def __unicode__(self):
        return str(self.constellationID)
    
    class Meta:
        unique_together = ('constellationID', 'regionID')

#############################################################################
#CREATE TABLE "mapSolarSystems" (
#  "regionID" int(11) default NULL,
#  "constellationID" int(11) default NULL,
#  "solarSystemID" int(11) NOT NULL,
#  "solarSystemName" varchar(100) default NULL,
#  "x" double default NULL,
#  "y" double default NULL,
#  "z" double default NULL,
#  "xMin" double default NULL,
#  "xMax" double default NULL,
#  "yMin" double default NULL,
#  "yMax" double default NULL,
#  "zMin" double default NULL,
#  "zMax" double default NULL,
#  "luminosity" double default NULL,
#  "border" tinyint(1) default NULL,
#  "fringe" tinyint(1) default NULL,
#  "corridor" tinyint(1) default NULL,
#  "hub" tinyint(1) default NULL,
#  "international" tinyint(1) default NULL,
#  "regional" tinyint(1) default NULL,
#  "constellation" tinyint(1) default NULL,
#  "security" double default NULL,
#  "factionID" int(11) default NULL,
#  "radius" double default NULL,
#  "sunTypeID" int(11) default NULL,
#  "securityClass" varchar(2) default NULL,
#  PRIMARY KEY  ("solarSystemID")
#);
#
#CREATE INDEX "mapSolarSystems_IX_constellation" ON "mapSolarSystems" ("constellationID");
#CREATE INDEX "mapSolarSystems_IX_region" ON "mapSolarSystems" ("regionID");
#CREATE INDEX "mapSolarSystems_IX_security" ON "mapSolarSystems" ("security");
#CREATE UNIQUE INDEX "mapSolarSystems_IX_solarSystemID" ON "mapSolarSystems" ("solarSystemID","constellationID","regionID");
#CREATE INDEX "mapSolarSystems_IX_sunTypeID" ON "mapSolarSystems" ("sunTypeID");

class mapSolarSystems(models.Model):
    """A table containing solar system data. Primarily used for solarStationID lookups"""
    regionID = models.ForeignKey(mapRegions, to_field='regionID',
                                 verbose_name='Region ID',
                                 db_index=True, db_column='regionID')
    constellationID = models.ForeignKey(mapConstellations,
                                        to_field='constellationID',
                                        db_column='constellationID')
    solarSystemID = models.IntegerField('Solar system ID', primary_key=True)
    solarSystemName = models.CharField('Solar system name', max_length=100)
    security = models.FloatField('Security', db_index=True)
    securityClass = models.CharField('Security class', max_length=2, null=True)
    
    def __unicode__(self):
        return str(self.solarSystemID)
    
    class Meta:
        unique_together = ('solarSystemID', 'constellationID', 'regionID')

#############################################################################
#CREATE TABLE "staStations" (
#  "stationID" int(11) NOT NULL,
#  "security" smallint(6) default NULL,
#  "dockingCostPerVolume" double default NULL,
#  "maxShipVolumeDockable" double default NULL,
#  "officeRentalCost" int(11) default NULL,
#  "operationID" tinyint(3) default NULL,
#  "stationTypeID" int(11) default NULL,
#  "corporationID" int(11) default NULL,
#  "solarSystemID" int(11) default NULL,
#  "constellationID" int(11) default NULL,
#  "regionID" int(11) default NULL,
#  "stationName" varchar(100) default NULL,
#  "x" double default NULL,
#  "y" double default NULL,
#  "z" double default NULL,
#  "reprocessingEfficiency" double default NULL,
#  "reprocessingStationsTake" double default NULL,
#  "reprocessingHangarFlag" tinyint(4) default NULL,
#  PRIMARY KEY  ("stationID")
#);
#
#CREATE INDEX "staStations_IX_constellation" ON "staStations" ("constellationID");
#CREATE INDEX "staStations_IX_corporation" ON "staStations" ("corporationID");
#CREATE INDEX "staStations_IX_operation" ON "staStations" ("operationID");
#CREATE INDEX "staStations_IX_region" ON "staStations" ("regionID");
#CREATE INDEX "staStations_IX_solarSystemID" ON "staStations" ("solarSystemID","constellationID","regionID");
#CREATE INDEX "staStations_IX_system" ON "staStations" ("solarSystemID");
#CREATE INDEX "staStations_IX_type" ON "staStations" ("stationTypeID");

class staStations(models.Model):
    """A table containing station data. Primarily used for stationID lookups."""
    stationID = models.IntegerField(primary_key=True)
    #operationID = models.IntegerField(blank=True)   # what is this?
    corporationID = models.IntegerField(blank=True) # potentially useful?
    solarSystemID = models.ForeignKey(mapSolarSystems, to_field='solarSystemID', db_column='solarSystemID')
    constellationID = models.ForeignKey(mapConstellations, to_field='constellationID', db_column='constellationID')
    regionID = models.ForeignKey(mapRegions, to_field='regionID', db_column='regionID')
    stationName = models.CharField(max_length=100, blank=True, db_index=True)
    reprocessingEfficiency = models.FloatField(blank=True)
    reprocessingStationsTake = models.FloatField(blank=True)

#############################################################################
#CREATE TABLE "invMarketGroups" (
#  "marketGroupID" smallint(6) NOT NULL,
#  "parentGroupID" smallint(6) default NULL,
#  "marketGroupName" varchar(100) default NULL,
#  "description" varchar(3000) default NULL,
#  "iconID" smallint(6) default NULL,
#  "hasTypes" tinyint(1) default NULL,
#  PRIMARY KEY  ("marketGroupID")
#);
#
#CREATE INDEX "invMarketGroups_IX_iconID" ON "invMarketGroups" ("iconID");
#CREATE INDEX "invMarketGroups_IX_parentGroupID" ON "invMarketGroups" ("parentGroupID");

class invMarketGroups(models.Model):
    """A table containing market group data. An item must have a foreign key
    relation to an instance of this model for it to be placeable on the market.
    """
    marketGroupID = models.SmallIntegerField('Market group ID', primary_key=True)
    parentGroupID = models.ForeignKey('self', db_column='parentGroupID',
                                      verbose_name='Parent group ID')
    marketGroupName = models.CharField('Market group name', max_length=100)
    description = models.CharField('Description', max_length=3000)
    #iconid = models.ForeignKey(Eveicons, db_column='iconid')
    #hastypes = models.SmallIntegerField()
    
    def __unicode__(self):
        return str(self.marketGroupID)
    
#############################################################################
#CREATE TABLE "invTypes" (
#  "typeID" int(11) NOT NULL,
#  "groupID" smallint(6) default NULL,
#  "typeName" varchar(100) default NULL,
#  "description" varchar(3000) default NULL,
#  "graphicID" smallint(6) default NULL,
#  "radius" double default NULL,
#  "mass" double default NULL,
#  "volume" double default NULL,
#  "capacity" double default NULL,
#  "portionSize" int(11) default NULL,
#  "raceID" tinyint(3) default NULL,
#  "basePrice" double default NULL,
#  "published" tinyint(1) default NULL,
#  "marketGroupID" smallint(6) default NULL,
#  "chanceOfDuplicating" double default NULL,
#  "iconID" smallint(6) default NULL,
#  PRIMARY KEY  ("typeID")
#);
#
#CREATE INDEX "invTypes_IX_Group" ON "invTypes" ("groupID");
#CREATE INDEX "invTypes_IX_graphicID" ON "invTypes" ("graphicID");
#CREATE INDEX "invTypes_IX_iconID" ON "invTypes" ("iconID");
#CREATE INDEX "invTypes_IX_marketGroupID" ON "invTypes" ("marketGroupID");
#CREATE INDEX "invTypes_IX_raceID" ON "invTypes" ("raceID");

class invTypes(models.Model):
    """A table containing data on items that are able to be stored in one's inventory. Primarily used for typeID lookups.
    """
    typeID = models.IntegerField(primary_key=True, unique=True,
                                 verbose_name='Type ID')
    groupID = models.SmallIntegerField(null=True, blank=True,
                                       verbose_name='Group ID')
    typeName = models.CharField(max_length=100, verbose_name='Item Name', db_index=True)
    description = models.CharField(max_length=3000)
    graphicID = models.SmallIntegerField(null=True, blank=True,
                                         verbose_name='Graphic ID')
    radius = models.FloatField()
    mass = models.FloatField()
    volume = models.FloatField()
    capacity = models.FloatField()
    portionSize = models.IntegerField(verbose_name='Portion size')
    raceID = models.SmallIntegerField(null=True, blank=True,
                                      verbose_name='Race ID')
    basePrice = models.FloatField(verbose_name='Base Price')
    published = models.SmallIntegerField(null=True, blank=True,
                                         verbose_name='Published?')
    
    # TO DO: this might be better off as a ForeignKey to invMarketGroups
    marketGroupID = models.IntegerField(null=True, blank=True,
                                        verbose_name='Market Group ID')
    chanceOfDuplicating = models.FloatField(
        verbose_name='Chance of duplicating')
    iconID = models.IntegerField(null=True, blank=True, verbose_name='Icon ID')
    medianSellPrice = models.FloatField('Median sell price', null=True,
                                          blank=True)
    medianBuyPrice = models.FloatField('Median buy price', null=True,
                                          blank=True)
    meanSellPrice = models.FloatField('Mean sell price', null=True,
                                          blank=True)
    meanBuyPrice = models.FloatField('Mean buy price', null=True,
                                          blank=True)
    highBuyPrice = models.FloatField('High buy price', null=True,
                                          blank=True)
    lowBuyPrice = models.FloatField('Low buy price', null=True,
                                          blank=True)
    highSellPrice = models.FloatField('High sell price', null=True,
                                          blank=True)
    lowSellPrice = models.FloatField('Low sell price', null=True,
                                          blank=True)
    stdDevBuy = models.FloatField('Standard deviation of buy', null=True,
                                          blank=True)
    stdDevSell = models.FloatField('Standard deviation of sell', null=True,
                                          blank=True)
    varianceBuy = models.FloatField('Variance of buy', null=True,
                                          blank=True)
    varianceSell = models.FloatField('Variance of sell', null=True,
                                          blank=True)
    isLPreward = models.BooleanField('Is an LP reward?')
    
    def __unicode__(self):
        return str(self.typeID)

#############################################################################
# partial paste from http://wiki.eve-id.net/APIv2_Char_MarketOrders_XML
# orderID 	int 	Unique order ID for this order. Note that these are not
#                       guaranteed to be unique forever, they can recycle.
#                       But they are unique for the purpose of one data pull.
# stationID 	int 	ID of the station the order was placed in.
# volEntered 	int 	Quantity of items required/offered to begin with.
# volRemaining 	int 	Quantity of items still for sale or still desired.
# minVolume 	int 	For bids (buy orders), the minimum quantity that must
#                       be sold in one sale in order to be accepted by this
#                       order.
# typeID 	short 	ID of the type (references the invTypes table) of the
#                       items this order is buying/selling.
# range 	short 	The range this order is good for. For sell orders, this
#                       is always 32767. For buy orders, allowed values are:
#                       -1 = station, 0 = solar system, 5/10/20/40 Jumps,
#                       32767 = region.
# duration 	short 	How many days this order is good for. Expiration is
#                       issued + duration in days.
# price 	decimal The cost per unit for this order.
# bid   	bool 	If true, this order is a bid (buy order). Else, sell
#                       order.
# issued 	datetime    When this order was issued. 

# some fields will probably be removed
# ?(keep region, system, station, price, qty, expires, reported time)?
# TO DO: correct field types to match official EVE documentation

class MarketRecord(models.Model):
    """A table containing market order data."""
    price = models.FloatField("Price")
    volRemaining = models.FloatField("Volume remaining")
    range = models.IntegerField("Range")
    orderID = models.IntegerField("Order ID")   # bigint on the backend
    volEntered = models.IntegerField("Vol entered")
    minVolume = models.IntegerField("Minimum vol")
    bid = models.BooleanField("Buy?")
    issueDate = models.DateTimeField("Issue date")
    duration = models.IntegerField("Duration")
    typeID = models.ForeignKey(invTypes, to_field="typeID",
                               verbose_name="Type ID")
    # db_column is req'd otherwise django would append _id and that would
    # screw shit up
    stationID = models.ForeignKey(staStations, to_field='stationID',
                                  verbose_name='Station ID',
                                  db_column='stationID')
    #regionID = models.ForeignKey(mapRegions,
    #                             to_field='regionID',
    #                             verbose_name='Region ID',
    #                             db_column='regionID')
    #solarSystemID = models.ForeignKey(mapSolarSystems,
    #                                  to_field='solarSystemID',
    #                                  verbose_name='Solar system ID',
    #                                  db_column='solarSystemID')
    jumps = models.IntegerField("Jumps")
    lastUpdated = models.DateTimeField("Entry updated")
    
    def __unicode__(self):
        return self.typeID.typeName
    
    def was_updated_today(self):
        return self.lastUpdated == datetime.date.today()
        
    was_updated_today.short_description = 'Updated today?'

# TO DO: Add FK for itemName and/or typeID, so we can easily resolve those from templates, etc
class LPReward(models.Model):
    """LP Store entries for each item, containing Corporation, Reward Name, QTY, LP Cost, ISK Cost, Req'd Items"""
    corp = models.CharField('Corporation', max_length=100)
    itemName = models.CharField('Item Name', max_length=100)
    qty = models.IntegerField('Qty')
    LPcost = models.IntegerField('LP Cost')
    ISKcost = models.IntegerField('ISK Cost')
    
    # this field will hold a list of the items required and their assoc'd qty
    # format: typeID_of_n0, qty_of_n0, typeID_of_n1, qty_of_n1, ...
    # (should always be an even amt of entries b/c of pairing)
    requiredItems = models.CommaSeparatedIntegerField('Required Items', max_length = 100)
    
    def __unicode__(self):
        return self.corp + ' - ' + self.itemName

# FOR TESTING PURPOSES ONLY
class modified(models.Model):
    """A table containing a list of typeIDs that have had their statistics set to a value other than "None".
    This speeds up database resets by allowing us to ignore untouched invType instances."""
    typeID = models.IntegerField('type', blank=False, primary_key=True)
    
    def __unicode__(self):
        return str(self.typeID)

##############################################################################    
# TO DO: this should probably go elsewhere b/c it can cause an error when we
# modify the invTypes model by hand. For example, when adding a new column, but
# before populating it, we run a 'manage.py syncdb' just to add the tables to
# the DB, which would work fine if there wasn't any code in here being executed
# that relies on invTypes being fully valid
# WORKAROUND: comment out sellable code during such work
#
# should this go into the DB?
# make a list of sellable typeIDs at server start
# this should only be set once per invType update (basically, each EVE patch)
# comment out when MaxChildPerRequest = 1 in apache config
#
#sellable = set()
#q = invTypes.objects.exclude(marketGroupID__exact=None)
#print '** sellable count:', len(q)
#
#for type in q:
#    sellable.add(type.typeID)
#    print ' {0},'.format(type.typeName)
##############################################################################

class dgmAttributeCategories(models.Model):
    categoryID = models.SmallIntegerField('categoryID', primary_key=True)
    categoryName = models.CharField(verbose_name='categoryName', max_length=50)
    categoryDescription = models.CharField(verbose_name='categoryDescription', max_length=200)
    
class dgmTypeAttributes(models.Model):
    typeID = models.ForeignKey(invTypes, to_field='typeID', verbose_name='typeID', primary_key=True, db_column='typeID')
    attributeID = models.ForeignKey('dgmAttributeTypes', to_field='attributeID', verbose_name='attributeID', db_index=True, db_column='attributeID')
    valueInt = models.IntegerField('valueInt')
    valueFloat = models.FloatField('valueFloat')
    
class dgmAttributeTypes(models.Model):
    attributeID = models.IntegerField(verbose_name='attributeID', primary_key=True)
    attributeName = models.CharField(verbose_name='attributeName', max_length=100)
    description = models.CharField(verbose_name='description', max_length=1000)
    #iconID = models.IntegerField('iconID')  # FK originally
    defaultValue = models.FloatField('defaultValue')
    published = models.SmallIntegerField('published')
    displayName = models.CharField(verbose_name='displayName', max_length=100)
    #unitID = models.SmallIntegerField('unitID') # FK originally
    stackable = models.SmallIntegerField('stackable')
    highIsGood = models.SmallIntegerField('highIsGood')
    categoryID = models.ForeignKey(dgmAttributeCategories, to_field='categoryID', db_index=True, db_column='categoryID')

# create a list of invTypes which are purchaseable with LP
LPitems = []

for x in invTypes.objects.filter(isLPreward__exact=True).order_by('typeName'):
    if len(MarketRecord.objects.filter(typeID__exact=x.typeID)) != 0:
        LPitems.append((x.typeID, x.typeName + ' [' + str(x.typeID) + ']' + ' (' + str(len(MarketRecord.objects.filter(typeID__exact=x.typeID))) + ')'))

#LPitems_with_stats = LPitems
#
#for x in LPitems_with_stats:
#    print x[1][len(x[1])-3:]
#    if x[1][len(x[1])-3:] == u'(0)':
#        print 'removing', x[1]
#        LPitems_with_stats.remove(x)