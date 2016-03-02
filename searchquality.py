import urllib2
import base64
import json
import os
import sys
from scipy.stats import norm
from urlparse import urlparse

googleapikey = 'PLACEHOLDER'
googlesearchengineid = 'PLACEHOLDER'
azureaccountkey = 'PLACEHOLDER'

class Search(object):
    def __init__(self, name, maxquerylimit, apikey, nresults, keyword):
        self.name = name
        self.maxquerylimit = maxquerylimit
        self.apikey = apikey
        self.nresults = nresults
        self.keyword = keyword
        self.cachefolder = 'cache/'
        self.checkcachefiles()

    def getcachefilename(self, index):
        return '%s%s-%s-%d.json' \
               % (self.cachefolder, self.name, self.keyword, index)

    def checkcachefiles(self):
        self.cachefiles = []
        i = 1
        exists = True
        while exists:
            filepath = self.getcachefilename(i)
            exists = os.path.isfile(filepath)
            if exists:
                self.cachefiles += [filepath]
            i += 1

    def download(self):
        self.cachefiles = []
        self.results = []
        i = 0
        batchleft = self.nresults
        while batchleft > 0:
            batchsize = min(self.maxquerylimit, batchleft)
            pair = self.singlequery(i, batchsize)
            if pair[0] == 0:
                cachefile = self.getcachefilename(i + 1)
                with open(cachefile, 'w') as outfile:
                    outfile.write(pair[1])
                self.cachefiles += [cachefile]
                self.results += self.parseresult(pair[1])
                batchleft -= batchsize
                i += 1
            else:
                sys.stderr.write('Download error - %d\n' % pair[0])
                break

    def loadcache(self):
        self.results = []
        for cache in self.cachefiles:
            with open(cache, 'r') as infile:
                s = infile.read()
            self.results += self.parseresult(s)

    def run(self):
        if len(self.cachefiles) == 0:
            self.download()
        else:
            self.loadcache()

    def updatescores(self, rankscores, evalpage):
        for i in xrange(0, len(self.results)):
            o = urlparse(self.results[i][1])
            score_url = evalpage(self.keyword, self.results[i])
            self.results[i][2] = score_url \
                * (rankscores[i] if i < len(rankscores) else 0)

    @staticmethod
    def getvaluesafely(dict, key):
        return dict[key] if key in dict.keys() else ''

class Bing(Search):
    def __init__(self, apikey, nresults, keyword):
        super(Bing, self).__init__('bing', 50, apikey, nresults, keyword)

    def singlequery(self, index, batchsize):
        q = "https://api.datamarket.azure.com/Bing/Search/v1/Web" \
            "?Query='%s'&Adult='Off'&$format=json&$skip=%d&$top=%d" \
            % (self.keyword,
               index * self.maxquerylimit,
               batchsize)
        passmgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
        passmgr.add_password(None, q, self.apikey, self.apikey)
        authhandler = urllib2.HTTPBasicAuthHandler(passmgr)
        requestor = urllib2.build_opener(authhandler)
        urllib2.install_opener(requestor)
        status = 0
        try:
            response = requestor.open(q).read()
        except urllib2.HTTPError as e:
            status = e.code
            response = e.read()
        return (status, response)

    def parseresult(self, result):
        jsondata = json.loads(result)
        results = jsondata['d']['results']
        return [[Search.getvaluesafely(result, 'Title'),
                 Search.getvaluesafely(result, 'Url'),
                 .0] for result in results]

class Google(Search):
    def __init__(self, apikey, searchengineid, nresults, keyword):
        super(Google, self).__init__('google', 10, apikey, nresults, keyword)
        self.searchengineid = searchengineid

    def singlequery(self, index, batchsize):
        q = 'https://www.googleapis.com/customsearch/v1' \
            '?key=%s&cx=%s&safe=off&start=%d&num=%d&q=%s' \
            % (self.apikey,
               self.searchengineid,
               index * self.maxquerylimit + 1,
               batchsize,
               self.keyword)
        request = urllib2.Request(q)
        requestor = urllib2.build_opener()
        status = 0
        try:
            response = requestor.open(request).read()
        except urllib2.HTTPError as e:
            status = e.code
            response = e.read()
        return (status, response)

    def parseresult(self, result):
        jsondata = json.loads(result)
        results = jsondata['items']
        return [[Search.getvaluesafely(result, 'title'),
                 Search.getvaluesafely(result, 'link'),
                 .0] for result in results]

class RankScore:
    def __init__(self, sd_page, sd_inpagerank, pagesize, nresults):
        self.sd_page = sd_page
        self.sd_inpagerank = sd_inpagerank
        self.pagesize = pagesize
        self.array = []
        page = 0
        pos = 0
        while nresults > 0:
            if pos % self.pagesize == 0:
                pos = 0
                page += 1
                score_page = (norm.cdf(page, scale = self.sd_page)
                              - norm.cdf(page - 1, scale = self.sd_page)) * 2
            score_pos = ((norm.cdf(pos + 1, scale = self.sd_inpagerank)
                          - norm.cdf(pos, scale = self.sd_inpagerank))
                        / (norm.cdf(pagesize, scale = self.sd_inpagerank) - .5))
            self.array += [score_page * score_pos]
            nresults -= 1
            pos += 1

def EvaluateSearchResultForMSDN(keyword, pair):
    o = urlparse(pair[1])
    titlelow = pair[0].lower()
    return 1.0 if (o.hostname == 'msdn.microsoft.com') \
                   and (titlelow.startswith(keyword.lower())) \
                   and ('(windows)' in titlelow) \
               else .0

def EvaluateSingleKeyword(n, keyword):
    scores = RankScore(sd_page = .5,
                       sd_inpagerank = 10,
                       pagesize = 10,
                       nresults = n)
    engines = [
        Google(googleapikey, googlesearchengineid, n, keyword),
        Bing(azureaccountkey, n, keyword)
    ]
    for engine in engines:
        engine.run()
        engine.updatescores(scores.array, EvaluateSearchResultForMSDN)
        print '\t'.join([
            engine.name[0],
            keyword,
            str(sum([result[2] for result in engine.results]))
        ])

if __name__ == '__main__':
    for line in sys.stdin:
        if len(line) > 1 and not line.startswith('#'):
            EvaluateSingleKeyword(100, line[:-1])
