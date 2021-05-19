import re
import requests.exceptions
import json
import logging
import concurrent.futures
import tldextract
import traceback

from urllib.parse import urlparse

import hypercane.errors

module_logger = logging.getLogger('hypercane.score.dsa1_ranking')

blog_sources = [
    'blogger.com',
    'blogspot.com',
    'wordpress.com',
    'typepad.com'
]

# image sharing websites as per https://en.wikipedia.org/wiki/List_of_image-sharing_websites
wikipedia_imagesharing_sources = [
    '500px.com',
    'album2.com',
    'bilddagboken.se',
    'myphotodiary.com',
    'kuvapaivakirja.fi',
    'bildedagboka.no',
    'billeddagbog.dk',
    'deviantart.com',
    'dronestagr.am',
    'flickr.com',
    'fotki.com',
    'fotolog.com',
    'fotolog.net',
    'geograph.org.uk',
    'photos.google.com',
    'instagram.com',
    'imgur.com',
    'ipernity.com',
    'jalbum.net',
    'photobucket.com',
    'pinterest.com',
    'pixabay.com',
    'securetribeapp.com',
    'shutterflyinc.com',
    'smugmug.com',
    'snapfish.com',
    'unsplash.com'
]

# video domains as per https://en.wikipedia.org/wiki/List_of_video_hosting_services#Specifically_dedicated_video_hosting_websites
wikipedia_video_sources = [
    'acfun.cn',
    'afreecatv.com',
    'aparat.com',
    'bigo.tv',
    'bilibili.com',
    'bitchute.com',
    'dailymotion.com',
    'godtube.com',
    'iqiyi.com',
    'liveleak.com',
    'metacafe.com',
    'mixer.com',
    'nicovideo.jp',
    'periscope.tv',
    'rutube.ru',
    'schooltube.com',
    'smashcast.tv',
    'trilulilu.ro',
    'tudou.com',
    'tune.pk',
    'twitch.tv',
    'vbox7.com',
    'veoh.com',
    'vimeo.com',
    'youku.com',
    'younow.com',
    'youtube.com'
]

# social media domains as per https://helpx.adobe.com/analytics/kb/list-social-networks.html
adobe_socialmedia_sources = [
    '12seconds.tv',
    '4travel.jp',
    'advogato.org',
    'ameba.jp',
    'anobii.com',
    'answers.yahoo.com',
    'asmallworld.net',
    'avforums.com',
    'backtype.com',
    'badoo.com',
    'bebo.com',
    'bigadda.com',
    'bigtent.com',
    'biip.no',
    'blackplanet.com',
    'blog.seesaa.jp',
    'blogspot.com',
    'blogster.com',
    'blomotion.jp',
    'bolt.com',
    'brightkite.com',
    'buzznet.com',
    'cafemom.com',
    'care2.com',
    'classmates.com',
    'cloob.com',
    'collegeblender.com',
    'cyworld.co.kr',
    'cyworld.com.cn',
    'dailymotion.com',
    'delicious.com',
    'deviantart.com',
    'digg.com',
    'diigo.com',
    'disqus.com',
    'draugiem.lv',
    'facebook.com',
    'faceparty.com',
    'fc2.com',
    'flickr.com',
    'flixster.com',
    'fotolog.com',
    'foursquare.com',
    'friendfeed.com',
    'friendsreunited.co.uk',
    'friendsreunited.com',
    'friendster.com',
    'fubar.com',
    'gaiaonline.com',
    'geni.com',
    'goodreads.com',
    'grono.net',
    'habbo.com',
    'hatena.ne.jp',
    'hi5.com',
    'hotnews.infoseek.co.jp',
    'hyves.nl',
    'ibibo.com',
    'identi.ca',
    'imeem.com',
    'instagram.com',
    'intensedebate.com',
    'irc-galleria.net',
    'iwiw.hu',
    'jaiku.com',
    'jp.myspace.com',
    'kaixin001.com',
    'kaixin002.com',
    'kakaku.com',
    'kanshin.com',
    'kozocom.com',
    'last.fm',
    'linkedin.com',
    'livejournal.com',
    'lnkd.in',
    'matome.naver.jp',
    'me2day.net',
    'meetup.com',
    'mister-wong.com',
    'mixi.jp',
    'mixx.com',
    'mouthshut.com',
    'mp.weixin.qq.com',
    'multiply.com',
    'mumsnet.com',
    'myheritage.com',
    'mylife.com',
    'myspace.com',
    'myyearbook.com',
    'nasza-klasa.pl',
    'netlog.com',
    'nettby.no',
    'netvibes.com',
    'nextdoor.com',
    'nicovideo.jp',
    'ning.com',
    'odnoklassniki.ru',
    'ok.ru',
    'orkut.com',
    'pakila.jp',
    'photobucket.com',
    'pinterest.at',
    'pinterest.be',
    'pinterest.ca',
    'pinterest.ch',
    'pinterest.cl',
    'pinterest.co',
    'pinterest.co.kr',
    'pinterest.co.uk',
    'pinterest.com',
    'pinterest.de',
    'pinterest.dk',
    'pinterest.es',
    'pinterest.fr',
    'pinterest.hu',
    'pinterest.ie',
    'pinterest.in',
    'pinterest.jp',
    'pinterest.nz',
    'pinterest.ph',
    'pinterest.pt',
    'pinterest.se',
    'plaxo.com',
    'plurk.com',
    'plus.google.com',
    'plus.url.google.com',
    'po.st',
    'reddit.com',
    'renren.com',
    'skyrock.com',
    'slideshare.net',
    'smcb.jp',
    'smugmug.com',
    'sonico.com',
    'studivz.net',
    'stumbleupon.com',
    't.163.com',
    't.co',
    't.hexun.com',
    't.ifeng.com',
    't.people.com.cn',
    't.qq.com',
    't.sina.com.cn',
    't.sohu.com',
    'tabelog.com',
    'tagged.com',
    'taringa.net',
    'thefancy.com',
    'toutiao.com',
    'tripit.com',
    'trombi.com',
    'trytrend.jp',
    'tuenti.com',
    'tumblr.com',
    'twine.com',
    'twitter.com',
    'uhuru.jp',
    'viadeo.com',
    'vimeo.com',
    'vk.com',
    'wayn.com',
    'weibo.com',
    'weourfamily.com',
    'wer-kennt-wen.de',
    'wordpress.com',
    'xanga.com',
    'xing.com',
    'yammer.com',
    'yaplog.jp',
    'yelp.co.uk',
    'yelp.com',
    'youku.com',
    'youtube.com',
    'yozm.daum.net',
    'yuku.com',
    'zhihu.com',
    'zooomr.com'
]

# news domains from https://pewresearch-org-preprod.go-vip.co/journalism/2019/07/23/state-of-the-news-media-methodology/#digital-native-news-outlet-audit
pew_news_sources = [
    '12UP.COM',
    '247SPORTS.COM',
    '90MIN.COM',
    'APLUS.COM',
    'BGR.COM',
    'BLEACHERREPORT.COM',
    'BREITBART.COM',
    'BUSINESSINSIDER.COM',
    'BUSTLE.COM',
    'BUZZFEED.COM',
    'BUZZFEEDNEWS.COM',
    'CHEATSHEET.COM',
    'CINEMABLEND.COM',
    'CNET.COM',
    'COMICBOOK.COM',
    'DAILYDOT.COM',
    'DEADSPIN.COM',
    'DIGITALTRENDS.COM',
    'EATER.COM',
    'ELITEDAILY.COM',
    'ENGADGET.COM',
    'FIVETHIRTYEIGHT.COM',
    'GAMESPOT.COM',
    'GIZMODO.COM',
    'HELLOGIGGLES.COM',
    'HOLLYWOODLIFE.COM',
    'HUFFINGTONPOST.COM',
    'IBTIMES.COM',
    'IFLSCIENCE.COM',
    'IGN.COM',
    'IJR.COM',
    'IJREVIEW.COM',
    'INVESTOPEDIA.COM',
    'JEZEBEL.COM',
    'MARKETWATCH.COM',
    'MASHABLE.COM',
    'MAXPREPS.COM',
    'MIC.COM',
    'OPPOSINGVIEWS.COM',
    'POLITICO.COM',
    'POLYGON.COM',
    'QZ.COM',
    'RARE.US',
    'RAWSTORY.COM',
    'REFINERY29.COM',
    'SALON.COM',
    'SBNATION.COM',
    'SLATE.COM',
    'TECHRADAR.COM',
    'THEBLAZE.COM',
    'THEDAILYBEAST.COM',
    'THEROOT.COM',
    'THEVERGE.COM',
    'THISISINSIDER.COM',
    'THRILLIST.COM',
    'TMZ.COM',
    'TOPIX.COM',
    'TOPIX.NET',
    'UPROXX.COM',
    'UPWORTHY.COM',
    'VOX.COM'
]

# sources from https://www.w3newspapers.com/newssites/
w3newspapers_sources = [
    'aljazeera.com',
    'nytimes.com',
    'wsj.com',
    'huffpost.com',
    'washingtonpost.com',
    'latimes.com',
    'reuters.com',
    'abcnews.go.com',
    'usatoday.com',
    'bloomberg.com',
    'nbcnews.com',
    'dailymail.co.uk',
    'theguardian.com',
    'thesun.co.uk',
    'mirror.co.uk',
    'telegraph.co.uk',
    'bbc.com',
    'thestar.com',
    'theglobeandmail.com',
    'news.com.au',
    'forbes.com',
    'cnbc.com',
    'chinadaily.com.cn',
    'chron.com',
    'nypost.com',
    'usnews.com',
    'dw.com',
    'indiatimes.com',
    'thehindu.com',
    'indianexpress.com',
    'hindustantimes.com',
    'cbsnews.com',
    'time.com',
    'sfgate.com',
    'thehill.com',
    'thedailybeast.com',
    'newsweek.com',
    'theatlantic.com',
    'nzherald.co.nz',
    'herald.co.zw',
    'vanguardngr.com',
    'dailysun.co.za',
    'thejakartapost.com',
    'thestar.com.my',
    'straitstimes.com',
    'bangkokpost.com',
    'japantimes.co.jp',
    'thedailystar.net',
    'dawn.com',
    'alarabiya.net',
    'hollywoodreporter.com',
    'scmp.com',
    'aljazeera.com',
    'voanews.com'
]

# Borrowed from: https://github.com/yasmina85/DSA-stories/blob/181d2453a7931bbbe8b56d46575a4d8491d736c2/src/memento_picker.py#L13
# Credit goes to Yasmin AlNoamany
def get_memento_uri_category_score(memento_uri, session):

# Original code below
#    base_ait_idx_end = memento_uri.find('http',10)
#    original_uri = memento_uri[ base_ait_idx_end:]
#
#    o = urlparse(original_uri)
#    hostname = o.hostname
#    if hostname == None:
#        return -1
#    if  bool(re.search('.*twitter.*', hostname)) or bool(re.search('.*t.co.*', hostname)) or \
#        bool(re.search('.*redd.it.*', hostname)) or bool(re.search('.*twitter.*', hostname)) or \
#        bool(re.search('.*facebook.*', hostname)) or bool(re.search('.*fb.me.*', hostname)) or \
#        bool(re.search('.*plus.google.*', hostname))  or   bool(re.search('.*wiki.*', hostname)) or \
#        bool(re.search('.*globalvoicesonline.*', hostname))  or  bool(re.search('.*fbcdn.*', hostname)):
#        return 0.5
#    elif  bool(re.search('.*cnn.*', hostname)) or  bool(re.search('.*bbc.*', hostname)) or \
#        bool(re.search('news', hostname)) or  bool(re.search('.*news.*', hostname)) or  \
#        bool(re.search('.*rosaonline.*', hostname))or  bool(re.search('.*aljazeera.*', hostname)) or  \
#        bool(re.search('.*guardian.*', hostname)) or  bool(re.search('.*USATODAY.*', hostname)) or  \
#        bool(re.search('.*nytimes.*', hostname))or  bool(re.search('.*abc.*', hostname))or  \
#        bool(re.search('.*foxnews.*', hostname)) or  bool(re.search('.*allvoices.*', hostname)) or \
#        bool(re.search('.*huffingtonpost.*', hostname)) :
#        return 0.7
#    elif  bool(re.search('.*dailymotion.*', hostname)) or  \
#        bool(re.search('.*youtube.*', hostname)) or \
#        bool(re.search('.*youtu.be.*', hostname)):
#        return 0.7
#    elif bool(re.search('.*wordpress.*', hostname)) or  bool(re.search('.*blog.*', hostname)):
#        return 0.4
#    elif  bool(re.search('.*flickr.*', hostname)) or bool(re.search('.*flic.kr.*', hostname)) or  \
#        bool(re.search('.*instagram.*', hostname)) or  bool(re.search('.*twitpic.*', hostname)):
#        return 0.6
#    else:
#        return 0

    # Updated code starts here
    r = session.get(memento_uri)
    urir = r.links['original']['url']
    domain = tldextract.extract(urir).registered_domain

    if domain in blog_sources:
        return 0.4

    elif domain in wikipedia_imagesharing_sources:
        return 0.6

    elif domain.upper() in pew_news_sources:
        return 0.7

    elif domain in w3newspapers_sources:
        return 0.7

    elif 'news' in domain:
        return 0.7

    elif domain in wikipedia_video_sources:
        return 0.7

    elif domain in adobe_socialmedia_sources:
        return 0.5

    else:
        return 0

def get_path_depth(urim, session):
    """
        Calculate path depth for URI-R of urim based on method from https://arxiv.org/abs/cs/0511077
    """

    from urllib.parse import urlparse

    r = session.get(urim)
    urir = r.links['original']['url']

    o = urlparse(urir)
    
    if o.path[0] == '/':
        depth = len([ p for p in o.path.split('/') if len(p) > 0])
    elif o.path[0] == '':
        depth = 0

    if '?' in urir:
        depth += 1

    return depth

# Borrowed from https://github.com/yasmina85/DSA-stories/blob/181d2453a7931bbbe8b56d46575a4d8491d736c2/src/memento_picker.py#L5
# Credit goes to Yasmin AlNoamany
def get_memento_depth(mem_uri, session):

# Original code below
#    if mem_uri.endswith('/'):
#        mem_uri = mem_uri[0:-1]
#    original_uri_idx = mem_uri.find('http',10)
#    original_uri = mem_uri[original_uri_idx+7:-1]
#    level = original_uri.count('/')

    # updated code starts here:
    r = session.get(urim)
    urir = r.links['original']['url']
    level = urir.count('/')

    # TODO: how does it break the DSA1 scoring function if we apply get_path_depth instead?

    return level/10.0

def get_memento_damage(memento_uri, memento_damage_url, session):
    if memento_damage_url == None:
        return 0

    if memento_damage_url.endswith('/'):
        api_endpoint = "{}api/damage/{}".format(
            memento_damage_url, memento_uri)
    else:
        api_endpoint = "{}/api/damage/{}".format(
            memento_damage_url, memento_uri)

    try:
        r = session.get(api_endpoint)
    except requests.exceptions.RequestException:
        module_logger.warning("Failed to download Memento Damage data for URI-M {} "
            "using endpoint {}".format(memento_uri, api_endpoint))
        return 0

    try:
        damagedata = r.json()
    except json.decoder.JSONDecodeError:
        module_logger.warning("Failed to extract Memento Damage data for URI-M {} "
            "using endpoint {}".format(memento_uri, api_endpoint))
        return 0

    if 'total_damage' in damagedata:
        return damagedata['total_damage']
    else:
        return 0

def get_memento_score(urim, session, memento_damage_url=None, damage_weight=-0.40, category_weight=0.15, path_depth_weight=0.45):

    category_score = get_memento_uri_category_score(urim, session)
    path_depth_score = get_memento_depth(urim, session)
    damage_score = get_memento_damage(urim, memento_damage_url, session)

    score = ( 1 -  damage_weight * damage_score ) + \
        ( path_depth_weight * path_depth_score ) + \
        ( category_weight * category_score )

    return score

def rank_by_dsa1_score(urimdata, session, memento_damage_url=None, damage_weight=-0.40, category_weight=0.15, path_depth_weight=0.45):

    # urim_to_cluster = {}
    # clusters_to_urims = {}

    urims = list(urimdata.keys())

    # for urim in urims:
    #     cluster = urimdata[urim]['Cluster']
    #     urim_to_cluster[urim] = cluster
    #     clusters_to_urims.setdefault(cluster, []).append(urim)

    urim_to_score = {}

    total_urims = len(urims)
    completed_urims = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:

        future_to_urim = { executor.submit(get_memento_score, urim, session, memento_damage_url, damage_weight, category_weight, path_depth_weight): urim for urim in urims }

        for future in concurrent.futures.as_completed(future_to_urim):

            completed_urims += 1
            module_logger.info("extracting score result for {}/{}".format(completed_urims, total_urims))

            try:
                urim = future_to_urim[future]
                urim_to_score[urim] = future.result()
            except Exception as exc:
                module_logger.exception("Error: {}, failed to compute score for {}, skipping...".format(repr(exc), urim))
                hypercane.errors.errorstore.add(urim, traceback.format_exc())

    for urim in urim_to_score:
        urimdata[urim]['Score---DSA1-Score'] = urim_to_score[urim]

    return urimdata

def score_by_path_depth(urimdata, session):

    # urim_to_cluster = {}
    # clusters_to_urims = {}

    urims = list(urimdata.keys())

    # for urim in urims:
    #     cluster = urimdata[urim]['Cluster']
    #     urim_to_cluster[urim] = cluster
    #     clusters_to_urims.setdefault(cluster, []).append(urim)

    urim_to_score = {}

    total_urims = len(urims)
    completed_urims = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:

        future_to_urim = { executor.submit(get_path_depth, urim, session): urim for urim in urims }

        for future in concurrent.futures.as_completed(future_to_urim):

            completed_urims += 1
            module_logger.info("extracting score result for {}/{}".format(completed_urims, total_urims))

            try:
                urim = future_to_urim[future]
                urim_to_score[urim] = future.result()
            except Exception as exc:
                module_logger.exception("Error: {}, failed to compute score for {}, skipping...".format(repr(exc), urim))
                hypercane.errors.errorstore.add(urim, traceback.format_exc())

    for urim in urim_to_score:
        urimdata[urim]['Score---PathDepth'] = urim_to_score[urim]

    return urimdata

def score_by_category(urimdata, session):

    # urim_to_cluster = {}
    # clusters_to_urims = {}

    urims = list(urimdata.keys())

    # for urim in urims:
    #     cluster = urimdata[urim]['Cluster']
    #     urim_to_cluster[urim] = cluster
    #     clusters_to_urims.setdefault(cluster, []).append(urim)

    urim_to_score = {}

    total_urims = len(urims)
    completed_urims = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:

        future_to_urim = { executor.submit(get_memento_uri_category_score, urim, session): urim for urim in urims }

        for future in concurrent.futures.as_completed(future_to_urim):

            completed_urims += 1
            module_logger.info("extracting score result for {}/{}".format(completed_urims, total_urims))

            try:
                urim = future_to_urim[future]
                urim_to_score[urim] = future.result()
            except Exception as exc:
                module_logger.exception("Error: {}, failed to compute score for {}, skipping...".format(repr(exc), urim))
                hypercane.errors.errorstore.add(urim, traceback.format_exc())

    for urim in urim_to_score:
        urimdata[urim]['Score---PathDepth'] = urim_to_score[urim]

    return urimdata
