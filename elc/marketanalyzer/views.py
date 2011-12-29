import os.path
import csv, glob, sys, string, math, datetime, re, locale, timeit, logging

from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.core.cache import cache
from django.http import HttpResponseRedirect, Http404, HttpResponseBadRequest, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404, redirect, render
from django.contrib import messages
from django.db.models import Q, Avg, Max, Min, Count, StdDev, Variance
from django.core.files.uploadhandler import MemoryFileUploadHandler
from django.utils import simplejson
from django.template import Template, Context
from django.forms.formsets import formset_factory
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

from marketanalyzer.models import *
from marketanalyzer.forms import *
from marketanalyzer.tables import *

logging.basicConfig()

# TO DO: -validate all forms/input
#        -color code stuff!

# How kosher is this? (placement, usage of a global at all, etc)
uploadPath = '/home/django/upload/'

# Convert dumper's timestamp to a python datetime object.
def convTS(ts):
    # dumper TS is the number of 100-nanosecond intervals since Jan. 1, 1600
    # we convert here to a 32-bit representation of seconds since 1-1-1970
    # and then return a datetime object representing that
    return datetime.datetime.fromtimestamp(((int(ts) - 116444736000000000) /
                                             10000000))

#theme = 'base-dark'
#
#def set_theme(request):
#    if request.method == 'POST':
#        theme = request.POST.__getitem__('theme')

# Convert strings representing bools in export files to Python boolean objects
# (for use with CSV exports).
def str2bool(val):
    if ( val == 'True' ):
        return True
    if ( val == 'False' ):
        return False

# Accept an uploaded file that contains market orders in our CSV format.
@login_required
def upload(request):
    if request.method == 'POST':
        print '** POST method determined.'
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            print '** Form validated.'
            handle_uploaded_file(request.FILES['file'])
            messages.add_message(request, messages.SUCCESS,
                                 'File uploaded successfully!')
            return HttpResponseRedirect(reverse('marketanalyzer.views.upload'))
        else:
            messages.add_message(request, messages.ERROR, 'Upload failed!')
            print '!! Invalid form. Errors:', form.errors
    else:
        print '!! No POST'
        form = UploadFileForm()
    
    if 'theme' in request.session:
        selected_theme = request.session['theme']
    else:
        selected_theme = None
        
    # last arg is b/c of CSRF
    return render_to_response('records/upload.html', {'form': form,
                               'selected_theme': selected_theme},
                              context_instance=RequestContext(request))

# !! Multithreading
# View to present upload progress to AJAX in upload view.
def upload_progress(request):
    """
    Return JSON object with information about the progress of an upload.
    """
    print "** IN upload_progress."
    progress_id = None
    if 'X-Progress-ID' in request.GET:
        print "** X-Progress-ID seen in request.GET"
        progress_id = request.GET['X-Progress-ID']
    elif 'X-Progress-ID' in request.META:
        print "** X-Progress-ID seen in request.META"
        progress_id = request.META['X-Progress-ID']
    if progress_id:
        print "** progress_id seen"
        from django.utils import simplejson
        cache_key = "%s_%s" % (request.META['REMOTE_ADDR'], progress_id)
        data = cache.get(cache_key)
        json = simplejson.dumps(data)
        return HttpResponse(json)
    else:
        return HttpResponseBadRequest(
            'Server Error: You must provide X-Progress-ID header or query param.')

# Write contents of an uploaded file to server's disk and then call
# insert_to_db.
# TO DO: -delete uploaded files after X time has passed?
#        -rename new file if filename in use?
#        --tie into uniqueness check on orders?
def handle_uploaded_file(f):
    path = uploadPath + f.name  # uploadPath is defined above as a global
    #if ( not(os.path.isfile(path))):     # if file doesn't exist already
    #   print "** File does not already exist:", path
    destination = open(path, 'wb')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()
    print "** Inserting data to DB."
    insert_to_db(path)
    print "** Done inserting data to DB."
    #else:
    #    print "!! Aborting due to file already existing:", path

# Insert a file on the server containing market orders into the database.
# TO DO: handle problem of multiple people uploading data on same order
#        -consider checking orderID, if matches, check order contents,
#          and if they match, then don't add order
def insert_to_db(f):
    print '========== insert_to_db =========='
    # keyList used to zip()
    keyList = ['lastUpdated', 'price', 'volRemaining', 'typeID', 'range',
               'orderID', 'volEntered', 'minVolume', 'bid', 'issueDate',
               'duration', 'stationID', 'jumps']
    expList = []
    types = set()
    timestamp = -1
    
    with open(f, 'rb') as f:
        reader = csv.reader(f)
        # wierd shit can happen here so we should catch errors
        try:
            for row in reader:
                # if this isn't a blank line
                if ( len(row) ):    
                    # if row starts with 'TS:' we know it's a timestamp line
                    if ( string.find(row[0], 'TS:') == 0 ):
                        # extract UTC timestamp (datetime.utcnow())
                        timestamp = row[0][4:]
                    # if this isn't a keys row, it must be data
                    elif ( not(string.find(row[0], 'price') == 0) ):
                        # insert the timestamp at front of the list
                        #  (as per keyList)
                        row.insert(0, timestamp)
                        # add entry to expList
                        expList.append(dict(zip(keyList, row)))
                        
        except csv.Error, e:
            sys.exit('file %s, line %d: %s' % (filename, reader.line_num, e))
            
    f.close()
    lastType = -1
    
    # expList now contains a list of dicts, where each dict is a row from the
    # market dump source
    for i in expList:
        #print '** i:', i
        # print out typeID only when it changes
        if ( lastType != i['typeID'] ):
            lastType = i['typeID']
            print '** inserting typeID:', lastType
        
        # TO DO: consider putting types.add() inside of the try/except block so
        # we don't pass types to compute_price_data that it can't work with
        # (currently, we are checking for the same errors in compute_price_data
        # as we are here)
        
        # add type as seen, so we can limit our market computations to
        # item types that exist in the newly added records
        types.add(i['typeID'])
        
        try:
            r = MarketRecord(typeID=invTypes.objects.get(pk=i['typeID']),
                             volEntered=i['volEntered'],
                             minVolume=i['minVolume'],
                             jumps=i['jumps'],
                             lastUpdated=i['lastUpdated'],
                             price=i['price'],
                             stationID=staStations.objects.get(
                                pk=i['stationID']),
                             range=i['range'],
                             orderID=i['orderID'],
                             issueDate=i['issueDate'],
                             volRemaining=i['volRemaining'],
                             duration=i['duration'],
                             bid=str2bool(i['bid']))
        # haven't ever actually seen this raised yet; ok to remove?
        except MarketRecord.DoesNotExist as detail:
            print '!! MarketRecord does not exist (is it a new item?):', detail
            continue
        except Exception as detail:
            print '!! ERROR in insert_to_db (is it a new item?) [typeID:', \
                i['typeID'], ']:', detail
            continue
        else:
            r.save()

    #print '** types:', types
    compute_price_data(types)

# Accepts a set of typeIDs.
# Computes global price statistics on items passed to it.
def compute_price_data(types):
    print '========== compute_price_data =========='
    
    for t in types:
        print '** Computing for type:', t
        
        buyPriceList = []
        sellPriceList = []
        bLen = -1
        sLen = -1
        
        try:
            # store query results now, in case they change during computation
            item = invTypes.objects.get(typeID=t)
        except invTypes.DoesNotExist as detail:
            print '!! `item` not found in query:', detail
            continue
        else:
            buyOrders = item.marketrecord_set.filter(bid=True)
            sellOrders = item.marketrecord_set.filter(bid=False)
            
            item.meanSellPrice = sellOrders.aggregate(Avg('price')).values()[0]
            item.highSellPrice = sellOrders.aggregate(Max('price')).values()[0]
            item.lowSellPrice = sellOrders.aggregate(Min('price')).values()[0]
            item.stdDevSell = sellOrders.aggregate(StdDev('price')).values()[0]
            item.varianceSell = sellOrders.aggregate(Variance('price')).values()[0]
            
            item.meanBuyPrice = buyOrders.aggregate(Avg('price')).values()[0]
            item.highBuyPrice = buyOrders.aggregate(Max('price')).values()[0]
            item.lowBuyPrice = buyOrders.aggregate(Min('price')).values()[0]
            item.stdDevBuy = buyOrders.aggregate(StdDev('price')).values()[0]
            item.varianceBuy = buyOrders.aggregate(Variance('price')).values()[0]
            
    
            # setup stuff for finding medians
            for rec in buyOrders:
                buyPriceList.append(rec.price)
                
            for rec in sellOrders:
                sellPriceList.append(rec.price)
                
            bLen = len(buyPriceList)
            sLen = len(sellPriceList)
            
            #print '** len(buyPriceList):', bLen
            #print '** len(sellPriceList):', sLen
            
            # calculate medians
            if bLen == 0:
                pass
            elif bLen % 2 != 0:   # odd amt of items
                item.medianBuyPrice = buyPriceList[bLen/2]
            else:   # even amt of items, so avg 2 middle items' values
                item.medianBuyPrice = (buyPriceList[int(math.ceil(bLen)/2)]
                                       + buyPriceList[int(math.floor(bLen)/2)]
                                       / 2)
            if sLen == 0:
                pass
            elif sLen % 2 != 0:
                item.medianSellPrice = sellPriceList[sLen/2]
            else:
                item.medianSellPrice = (sellPriceList[int(math.ceil(sLen)/2)]
                                       + sellPriceList[int(math.floor(sLen)/2)]
                                       / 2)
                
            item.save()
            
            # FOR DEV PURPOSES ONLY, this speeds up db_clear
            x = modified(typeID=item.typeID)
            x.save()

# TO DO: for all views using tables
#        -remove some irrelevant columns from tables.
#        -paginate results.
#        -combine the all* views into one.
#        -add total volumes for currently buying/selling.
#        -add movement of units.
#        -filter by age of data, min qty.
#        -color code security rating.
#        -add best price for buy/sell globally, and for jita.
#        -display position of type in market group hierarchy.
#        --allow navigation through group hierarchy.
#        --show meta levels, jita prices, +/-20% jita prices,
#          jita avg qty/day over last 30 days.

# View that provides buy and sell tables of all market orders of a single item
# type, as well as attributes of that item (e.g. duration, hp, etc)
def type_detail(request, type_id):
    try:
        item = invTypes.objects.get(pk=type_id)
    except invTypes.DoesNotExist:
        raise Http404   # perhaps display a more informative page

    # Dict to hold the attributes of the item in question
    attrs = {}
    
    # Fill attr dict with attribute names as keys, and the int/float as values
    # Each attribute should have either an int or a float value, not both
    for x in dgmTypeAttributes.objects.filter(typeID=item.typeID):
        if x.valueInt:
            attrs[x.attributeID.attributeName] = x.valueInt
        else:
            attrs[x.attributeID.attributeName] = x.valueFloat
        
    #print '** attrs:', attrs.items()
        
    buy = None
    sell = None
    
    # by default, sort buy orders by descending price
    if ( request.GET.get('b-sort') ):
        bOrder = request.GET.get('b-sort')
    else:
        bOrder = '-price'
    
    # by default, sort sell by ascending price
    if ( request.GET.get('s-sort') ):
        sOrder = request.GET.get('s-sort')
    else:
        sOrder = 'price'
        
    buy = DetailTable(item.marketrecord_set.filter(bid__exact=1),
                        prefix='b-', order_by=bOrder)
    
    sell = DetailTable(item.marketrecord_set.filter(bid__exact=0),
                        prefix='s-', order_by=sOrder)

    # User wants to apply a selected theme now.
    if request.method == 'POST':
        #print '** typeDetail POST'
        theme = ThemeSelector(request.POST)
        
        if theme.is_valid():
            request.session['theme'] = theme.cleaned_data['themes']
            selected_theme = request.session['theme']
            return render_to_response('records/type_detail.html',
                              { 'buy': buy, 'sell': sell,
                               'attrs': attrs, 'item': item,
                               'theme': theme,
                               'selected_theme': selected_theme},
                              context_instance=RequestContext(request))
            
    # No POST; user isn't selecting a theme to apply now.
    else:
        #print '** typeDetail NO POST'
        # The user has a theme set.
        if 'theme' in request.session:
            #print '** theme exists:', request.session['theme']
            theme = ThemeSelector(initial={'themes': request.session['theme']})
            selected_theme = request.session['theme']
        else:
            # If no theme set in session, then use default.
            selected_theme = 'dark'
        
    
    return render_to_response('records/type_detail.html',
                              { 'buy': buy, 'sell': sell,
                               'attrs': attrs, 'item': item,
                               'theme': theme,
                               'selected_theme': selected_theme},
                              context_instance=RequestContext(request))
    
def set_theme(request):
    print '** in set_theme...'
    if request.method == 'POST':
        theme_form = ThemeSelector(request.POST)
        print '** set_theme POST:', request.POST
        
        if theme_form.is_valid():
            from_url = request.POST['from_url']
            theme = theme_form.cleaned_data['themes']
            
            print '** form is valid:', from_url, ',', theme
            
            request.session['theme'] = theme
            
            return redirect(from_url)
        else:
            print '!! set_theme: form INVALID. "theme" not set.'
            return redirect(from_url)
    else:
        print '!! set_theme: NO POST.'
        return redirect('/records')
        

# View to show every buy order in the database.
def all_buy(request):
    # by default, sort by descending price
    if ( request.GET.get('sort') ):
        order = request.GET.get('sort')
    else:
        order = '-price'
    # get just the BUY orders
    table = RecordTable(MarketRecord.objects.filter(bid__exact=1),
                        order_by=order)
    return render_to_response('records/all_buy.html', {'table': table},
                              context_instance=RequestContext(request))

# View to show every sell order in the database.
def all_sell(request):
    # by default, sort by ascending price
    if ( request.GET.get('sort') ):
        order = request.GET.get('sort')
    else:
        order = 'price'
    
    # get just the SELL orders
    table = RecordTable(MarketRecord.objects.filter(bid__exact=0),
                        order_by=order)
    return render_to_response('records/all_sell.html', {'table': table},
                              context_instance=RequestContext(request))

# probably won't regularly use the "all" view, and paginating requires more work
# with multiple tables so hold off?

# View to show all market orders in the database.
def all(request):
    # by default, sort buy orders by descending price
    if ( request.GET.get('b-sort') ):
        bOrder = request.GET.get('b-sort')
    else:
        bOrder = '-price'
    
    # by default, sort sell by ascending price
    if ( request.GET.get('s-sort') ):
        sOrder = request.GET.get('s-sort')
    else:
        sOrder = 'price'
        
    buy = RecordTable(MarketRecord.objects.filter(bid__exact=1),
                      prefix='b-', order_by=bOrder)
    sell = RecordTable(MarketRecord.objects.filter(bid__exact=0),
                       prefix='s-', order_by=sOrder)
        
    return render_to_response('records/all.html', {'buy': buy, 'sell': sell},
                              context_instance=RequestContext(request))

# Remove all marketrecords from DB and clear associated invType statistics
# regarding price.
# TO DO: This is slow b/c of the invType work, consider tracking types that
#        have had their *price fields edited.
#        May be a waste of time since this will rarely be run in production env.

# View to allow the clearing of market orders database.
@login_required
def clear_db(request):
    if request.method == 'POST':
        MarketRecord.objects.all().delete()
        
        # only have to reset stats for types that we've modified
        for type in modified.objects.all():
            item = invTypes.objects.get(typeID=type.typeID)
            print '** Clearing stats for:', item.typeName
            
            #for i in query:
            item.medianSellPrice = None
            item.medianBuyPrice = None
            item.meanSellPrice = None
            item.meanBuyPrice = None
            item.lowSellPrice = None
            item.highSellPrice = None
            item.lowBuyPrice = None
            item.highBuyPrice = None
            item.stdDev = None
            item.variance = None
            item.save()
                
        modified.objects.all().delete()
        messages.add_message(request, messages.SUCCESS,
                             'All orders and associated stats have been erased!')
    return render_to_response('records/clear_db.html',
                              context_instance=RequestContext(request))

# View to allow the clearing of the LP store database.
@login_required
def clear_lp_db(request):
    if request.method == 'POST':
        LPReward.objects.all().delete()
        
        # reset isLPreward for all invTypes
        for type in invTypes.objects.all():
            
            #value = type.typeName
            #try:
            #    unicode(value, "utf-8")
            #except UnicodeError:
            #    value = unicode(value, "utf-8")
            #else:
            #    # value was valid ASCII data
            #    pass
            
            try:
                print '** Clearing isLPreward for:', type.typeName
            except UnicodeEncodeError as e:
                print '!! Weird character(s) in name: ', e
            type.isLPreward = False
            type.save()
                
        messages.add_message(request, messages.SUCCESS,
                             'All LP rewards and isLPreward attrs have been cleared!')
    return render_to_response('records/clear_lp_db.html',
                              context_instance=RequestContext(request))

# Related to search view.
def normalize_query(query_string,
                    findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
                    normspace=re.compile(r'\s{2,}').sub):
    ''' Splits the query string in invidual keywords, getting rid of \
        unecessary spaces and grouping quoted words together.
        Example:
        
        >>> normalize_query('  some random  words "with   quotes  " and   spaces')
        ['some', 'random', 'words', 'with quotes', 'and', 'spaces']
    '''
    return [normspace(' ', (t[0] or t[1]).strip()) for t in
            findterms(query_string)] 

# Related to search view.
def get_query(query_string, search_fields):
    ''' Returns a query, that is a combination of Q objects. That combination
        aims to search keywords within a model by testing the given search fields.
    '''
    query = None # Query to search for every search term        
    terms = normalize_query(query_string)
    for term in terms:
        or_query = None # Query to search for a given term in each field
        for field_name in search_fields:
            q = Q(**{"%s__icontains" % field_name: term})
            if or_query is None:
                or_query = q
            else:
                or_query = or_query | q
        if query is None:
            query = or_query
        else:
            query = query & or_query
    return query

# View to search market orders by item name.
def search(request):
    query_string = ''
    found_entries = None
    if ('q' in request.GET) and request.GET['q'].strip():
        query_string = request.GET['q']
        
        # pick what field to search here
        entry_query = get_query(query_string, ['typeName',])
        
        found_entries=invTypes.objects.filter(entry_query).exclude(
            marketGroupID=None).order_by('typeName')

    if 'theme' in request.session:
        selected_theme = request.session['theme']
    else:
        selected_theme = None

    return render_to_response('records/search.html',
                              { 'query_string': query_string,
                               'found_entries': found_entries,
                               'selected_theme': selected_theme},
                              context_instance=RequestContext(request))

# View to search LP store rewards.
def lp_search(request):
    query_string = ''
    found_entries = None
    results = ''
    
    print request.GET
    
    if ('typeid' in request.GET) and request.GET['typeid'].strip():
        filter_form = LPSearchFilter(request.GET)
        
        if filter_form.is_valid():
            query_string = filter_form.cleaned_data['typeid']
            corp_filter = filter_form.cleaned_data['corp']
            
            # pick what field to search here
            entry_query = get_query(query_string, ['itemName',])
            
            if corp_filter == 'All':
                found_entries = LPReward.objects.filter(entry_query).order_by('itemName')
            else:
                found_entries = LPReward.objects.filter(corp__exact=corp_filter).filter(entry_query).order_by('itemName')
            
            # by default, sort sell by ascending price
            if ( request.GET.get('sort') ):
                order = request.GET.get('sort')
            else:
                order = 'itemName'
            
            results = LPResults(found_entries, order_by=order)
            
            # Broken for 1.4: https://github.com/bradleyayers/django-tables2/issues/42
            #results.paginate(page=request.GET.get('page', 1))
    else:
        filter_form = LPSearchFilter()
        
    if 'theme' in request.session:
        selected_theme = request.session['theme']
    else:
        selected_theme = None

    return render_to_response('records/lp_search.html',
                              { 'query_string': query_string,
                               'results': results,
                               'filter_form': filter_form,
                               'selected_theme': selected_theme },
                              context_instance=RequestContext(request))

# LP Calculator:
# Multi-step form currently. Should be converted to AJAX.
#
# per item formula:
#
# profit[x] = ( sellPrice[x, (region, stat)] - store_fee[x] - other_fee[x] )
#             --------------------------------------------------------------
#                                       LP_cost[x]
#
# Where...
# x: item type (e.g. typeID)
# store_fee: -the ISK cost of the item from the LP store
# other_fee: -could assume a stat + region. If not, requires region/stat.
#            (e.g. cost of buying T1 ammo to convert to faction ammo)
# sellPrice: -determined by region & price stat (e.g. mean buy price)

# Accepts iterable of typeID, regionID, and __priceStats.
# Returns a dict containing table data each type, to fill an LPCalcResultsTable.
#
# TO DO: -figure out other_fee (currently set to 0)
#        -make sure prices/fees/etc are PER UNIT or PER PURCHASE SIZE and calc
#         profits accordingly! (ex. faction ammo uses multiples of 5k)

def calculate_profits(items, region, stat, spendable):
    count = len(items)
    data = list()
    for x in range(0, count):
        item = invTypes.objects.get(pk=items[x])
        item_name = item.typeName
        region_name = mapRegions.objects.get(regionID=region[x]).regionName
        isk_per_lp = None
        profit = None
        
        # start limiting our query to typeID, regionID
        q = MarketRecord.objects.filter(typeID__exact=item).filter(stationID__regionID__exact=region[x])
        try:
            if stat[x] == 'meanbp':
                sell_price = q.filter(bid__exact=True).aggregate(tmp=Avg('price'))['tmp']
            elif stat[x] == 'hbp':
                sell_price = q.filter(bid__exact=True).aggregate(tmp=Max('price'))['tmp']
            elif stat[x] == 'lbp':
                sell_price = q.filter(bid__exact=True).aggregate(tmp=Min('price'))['tmp']
            elif stat[x] == 'meansp':
                sell_price = q.filter(bid__exact=False).aggregate(tmp=Avg('price'))['tmp']
            elif stat[x] == 'hsp':
                sell_price = q.filter(bid__exact=False).aggregate(tmp=Max('price'))['tmp']
            elif stat[x] == 'lsp':
                sell_price = q.filter(bid__exact=False).aggregate(tmp=Min('price'))['tmp']
            
            # We assume each LP-bought item will cost the same ISK, LP, and other_fee
            lp_reward = LPReward.objects.filter(itemName__exact=item_name)[0]
            store_fee = int(lp_reward.ISKcost)
            other_fee = int(0)
            lp_cost = int(lp_reward.LPcost)
            
            isk_per_lp = ((sell_price * lp_reward.qty) - store_fee - other_fee) / float(lp_cost)
            buyable = int(int(spendable) / lp_cost)
            profit = isk_per_lp * buyable * lp_cost
            
            # isk_per_lp = (isk/lp) for a each unit
            # total profit (isk) = isk_per_lp (isk/lp) * buyable (n/a) * lp_cost (1/lp)
        
        except TypeError as e:
            print '!! Error in calculate_profits (sell_price assignment):', e
        
        if not isk_per_lp:
            isk_per_lp = 'ERROR'
        if not profit:
            profit = 'ERROR'
        
        data.append({'itemName': item_name, 'regionName': region_name,
                   'sellPrice': sell_price, 'storeFee': store_fee,
                   'otherFee': other_fee, 'lpCost': lp_cost,
                   'isk_per_lp': isk_per_lp, 'profit': profit,
                   'qty': lp_reward.qty})
        
    return data

# TO DO: -lp_calc validation + display errors when submitting invalid form
#        -consider storing state as a hash, like Django form wizard
#        -consider storing state entirely in querystring, so each step can be
#         bookmarked/pasted to people.
#        -should ask for corp that the LP is for and narrow calcs based on such
    
# View to calculate profits from selling various LP store rewards in any
# location given prevailing market conditions.
#
# State is maintained via hidden input fields. There are 3 steps (0-2), which
# are split up into 3 templates, each holding a hidden input denoting which
# step it corresponds to. Item(s) and spendable LP are written to the HTML upon
# render and stuck into 'items' and 'spendable' hidden inputs, respectively.
# 'items' are stored with a semi-colon following each typeID in the HTML.
def lp_calc(request):
    if request.method == 'GET':
        #print '** lp_calc: GET:', request.GET

        form = LPCalcItem(request.GET)
        
        # No 'step' param, so user must've just gotten here and hasn't
        # inputted anything yet.
        if 'step' not in request.GET:
            print '** No STEP in GET.'
        else:
            # We're on step 1, so we're getting regions and price stats for
            # each item selected in step 0.
            if request.GET.get('step') == '1':
                print '** On STEP 1...'
                
                #print 'cleaned_data:', form.cleaned_data
                
                if form.is_valid():
                    print '** Form validated.'
                    
                    item_list = request.GET.getlist('item')
                    #print '** item_list:', item_list
                    
                    LPCalcDetailsFormSet = formset_factory(LPCalcDetails,
                                              extra=len(item_list))
                    
                    formset = LPCalcDetailsFormSet()
                    count = 0
                    
                    spendable = int(request.GET.get('spendable'))
                    
                    # Get the item name into each form; use as label on render.
                    for form in formset:
                        form.item_name = invTypes.objects.get(pk=item_list[count]).typeName
                        count = count + 1
                        
                    if 'theme' in request.session:
                        selected_theme = request.session['theme']
                    else:
                        selected_theme = None
                    
                    return render_to_response('records/lp_calc2.html',
                                              {'formset': formset,
                                               'items': item_list,
                                               'spendable': spendable,
                               'selected_theme': selected_theme},
                                              context_instance=RequestContext(request))
                # if form doesn't validate
                else:
                    print 'step 1 didnt validate:'
                    for field in form:
                        print field.errors
                    
            # We have the item list and associated region-stat combos,
            # so perform the required calculations and display the result.
            elif request.GET.get('step') == '2':
                print '** ON STEP 2...'
                #print '** GET:', request.GET
                
                # Recreate the formset as it was made for this particular query
                LPCalcDetailsFormSet = formset_factory(LPCalcDetails,
                                          extra=request.GET.get('TOTAL_FORMS'))
                formset = LPCalcDetailsFormSet(request.GET)
                
                if formset.is_valid():
                    print '** Formset is valid:', formset.data
                    
                    items = request.GET.get('items')
                    # -1 b/c last semi-colon adds an empty element
                    item_count = len(items.split(';')) - 1
                    item_list = items.split(';')[0:item_count]
                    
                    form_count = int(request.GET.get('form-TOTAL_FORMS'))
                    
                    region = dict()
                    stat = dict()
                    for x in range(0, form_count):
                        region[x] = request.GET.get('form-' + str(x)
                                                    + '-region')
                        stat[x] = request.GET.get('form-' + str(x)
                                                  + '-stat')
                        
                    spendable = request.GET.get('spendable')
                    
                    table_data = calculate_profits(item_list, region, stat,
                                                   spendable)
                    
                    # by default, sort by descending profit
                    if ( request.GET.get('sort') ):
                        order = request.GET.get('sort')
                    else:
                        order = '-profit'
                    
                    table = LPCalcResultsTable(table_data, order_by=order)
                    
                    #print 'table_data:'
                    #for k in range(0, len(table_data)):
                    #    print str(k) + ':', table_data[k]
                    
                    if 'theme' in request.session:
                        selected_theme = request.session['theme']
                    else:
                        selected_theme = None
                    
                    return render_to_response('records/lp_calc3.html',
                                              {'table': table,
                               'selected_theme': selected_theme},
                                              context_instance=RequestContext(request))
                    
    else:
        print '** NO GET.'
        form = LPCalcItem()
        
    if 'theme' in request.session:
        selected_theme = request.session['theme']
    else:
        selected_theme = None
        
    return render_to_response('records/lp_calc.html', {'form': form,
                               'selected_theme': selected_theme},
                              context_instance=RequestContext(request))

# TO DO: consider combining autocomplete views (add param for filter).

# Hidden view for typeName autocompletion.
def type_lookup(request):
    # Default return list
    results = []
    if request.method == "GET":
        if request.GET.has_key(u'query'):
            value = request.GET[u'query']
            # Ignore queries shorter than length 2
            if len(value) > 2:
                model_results = invTypes.objects.filter(
                    typeName__icontains=value)
                results = [ x.typeName for x in model_results ]
    json = simplejson.dumps(results)
    return HttpResponse(json, mimetype='application/json')
    
# Hidden view for typeName autocompletion, filtered to return LP rewards only.
def lp_lookup(request):
    # Default return list
    results2 = []
    if request.method == "GET":
        if request.GET.has_key(u'query'):
            value = request.GET[u'query']
            # Ignore queries shorter than length 2
            if len(value) > 2:
                model_results2 = invTypes.objects.filter(
                    isLPreward__exact=True).filter(
                    typeName__icontains=value).order_by('typeName')
                results2 = [ x.typeName for x in model_results2 ]
    json = simplejson.dumps(results2)
    return HttpResponse(json, mimetype='application/json')
    
# View to handle the importing of LP store data.
@login_required
def import_lp_data(request):
    print '** IN import_lp_data...'
    
    path = '/home/django/elc/eve_lp_store.csv'
    firstLine = True
    seen = set()
    
    if request.method == 'POST':        
        with open(path, 'rb') as f:
            reader = csv.reader(f)
            
            try:
                for row in reader:
                    
                    if firstLine == False:
                        toAdd = LPReward()
                        need = dict()
                        index = 1
                        reqItems = ''
                        
                        toAdd.corp = row[0]
                        toAdd.itemName = row[1]
                        toAdd.qty = row[2]
                        toAdd.LPcost = row[3]
                        toAdd.ISKcost = row[4]
                        
                        #print '** RAW row:', row
                        
                        # Parse required items list
                        if (row[5] != '') & (row[5] != 'Reqired Items'):
                            splitd = re.split(' x ', row[5])
                            reqdCount = len(splitd) - 1
                            #print '** splitd:', splitd
                            
                            # Get first requirement; key = item name, val = qty.
                            if index == 1:
                                need[splitd[index][0:splitd[index].rfind(' ')]] = splitd[index-1]
                            
                            # Loop through each of the remaining elements.
                            while index < len(splitd) - 1:
                                index = index + 1
                                if ( index == len(splitd) - 1): # non-first/last items will have item name followed by qty of NEXT item
                                    need[splitd[index]] = int(splitd[index-1][splitd[index-1].rfind(' '):len(splitd[index-1])])
                                else:   # last item will be just the item name
                                    need[splitd[index][0:splitd[index].rfind(' ')]] = int(splitd[index-1][splitd[index-1].rfind(' '):len(splitd[index-1])])
                                    
                            # Store req'd items' typeID followed by comma,
                            # followed by qty of typeID, followed by comma.
                            for key in need:
                                reqItems = reqItems + str(invTypes.objects.get(typeName = key).typeID) + ','
                                reqItems = reqItems + str(need[key]) + ','
                            
                            reqItems = reqItems[0:len(reqItems)-1]    
                            toAdd.requiredItems = reqItems
                                                    
                            #print '** reqItems:', reqItems
                        else:
                            #print '** No required items found.'
                            reqItems = ''
                        
                        #print '** toAdd: corp:%s, itemName:%s, qty:%s, LPcost:%s, ISKcost:%s, requiredItems:%s' % (toAdd.corp, toAdd.itemName, toAdd.qty, toAdd.LPcost, toAdd.ISKcost, toAdd.requiredItems)
                        toAdd.save()
                        
                        if toAdd.itemName not in seen:
                            seen.add(toAdd.itemName)
                            
                            try:
                                x = invTypes.objects.get(typeName = toAdd.itemName)
                                x.isLPreward = True
                                x.save()
                            except Exception as detail:
                                print '!! ERROR in import_lp_data (typeName: "' + toAdd.itemName + '"):', detail
                                continue
                    
                    firstLine = False
                    
            except csv.Error, e:
                print '!! import_lp_data: CSV error in file %s, line %d: %s' % (path, reader.line_num, e)
                
            f.close()
    
    if 'theme' in request.session:
        selected_theme = request.session['theme']
    else:
        selected_theme = None
        
    return render_to_response('records/import_lp.html',
                              {'selected_theme': selected_theme},
                              context_instance=RequestContext(request))

# View to display LP store-related details on a particular item.
def lp_detail(request, type_id):
    try:
        item = LPReward.objects.get(pk=type_id)
    except invTypes.DoesNotExist:
        raise Http404   # perhaps display a more informative page
    
    # dict to hold the attributes of the item in question
    attrs = {}
    
    # fill dict with attribute names as keys, and the int/float as values
    for x in dgmTypeAttributes.objects.filter(typeID=item.typeID):
        if x.valueInt:
            attrs[x.attributeID.attributeName] = x.valueInt
        else:
            attrs[x.attributeID.attributeName] = x.valueFloat
        
    #print '** attrs:', attrs.items()
        
    buy = None
    sell = None
    
    # by default, sort buy orders by descending price
    if ( request.GET.get('b-sort') ):
        bOrder = request.GET.get('b-sort')
    else:
        bOrder = '-price'
    
    # by default, sort sell by ascending price
    if ( request.GET.get('s-sort') ):
        sOrder = request.GET.get('s-sort')
    else:
        sOrder = 'price'
        
    buy = DetailTable(item.marketrecord_set.filter(bid__exact=1),
                        prefix='b-', order_by=bOrder)
    
    sell = DetailTable(item.marketrecord_set.filter(bid__exact=0),
                        prefix='s-', order_by=sOrder)
    
    if 'theme' in request.session:
        selected_theme = request.session['theme']
    else:
        selected_theme = None
        
    return render_to_response('records/type_detail.html',
                              { 'buy': buy, 'sell': sell, 'item': item,
                               'attrs': attrs,
                               'selected_theme': selected_theme },
                              context_instance=RequestContext(request))

# Hidden view to log user out, throws no errors if user isn't logged in.    
def logout_view(request):
    logout(request)
    
    print request.META
    
    return redirect(request.META['HTTP_REFERER'])