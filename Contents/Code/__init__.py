NAME = 'Star Trek New Voyages'
ART = 'art-default.jpg'
ICON = 'icon-default.png'
YT_USER = 'startrekphase2DE'

YT_API_UPLOADS   = 'http://gdata.youtube.com/feeds/api/users/%s/uploads?orderby=published&start-index=%%d&max-results=%%d&v=2&alt=json'
YT_API_PLAYLISTS = 'http://gdata.youtube.com/feeds/api/users/%s/playlists?start-index=%%d&max-results=%%d&v=2&alt=json'
YT_API_PLAYLIST  = 'http://gdata.youtube.com/feeds/api/playlists/%s?start-index=%%d&max-results=%%d&v=2&alt=json'
#YT_API_SEARCH    = 'http://gdata.youtube.com/feeds/api/videos?q=%s&author=%s&orderby=relevance&start-index=%%d&max-results=%%d&v=2&alt=json'
YT_VIDEO_PAGE    = 'http://www.youtube.com/watch?v=%s'

###################################################################################################
def Start():
    
	Plugin.AddPrefixHandler('/video/startrekphase2DE', MainMenu, NAME, ICON, ART)
	Plugin.AddViewGroup('List', viewMode='List', mediaType='items')
	Plugin.AddViewGroup('InfoList', viewMode='InfoList', mediaType='items')
    
	ObjectContainer.art = R(ART)
	ObjectContainer.title1 = NAME
	ObjectContainer.view_group = 'InfoList'
	DirectoryObject.thumb = R(ICON)
    
	HTTP.CacheTime = CACHE_1HOUR
	HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:15.0) Gecko/20100101 Firefox/15.0.1'

###################################################################################################
def MainMenu():
    
	oc = ObjectContainer(view_group='List')
    
	oc.add(DirectoryObject(key=Callback(Uploads), title='Videos'))
	oc.add(DirectoryObject(key=Callback(Playlists), title='Playlists'))
    
	return oc

###################################################################################################
def Uploads():
    
	oc = ObjectContainer(title2='Videos', http_cookies=HTTP.CookiesForURL('http://www.youtube.com/'))
	url = YT_API_UPLOADS % YT_USER
    
	for video in GetVideos(url, loop_next=False):
		(video_id, title, summary, originally_available_at, duration, rating, thumb) = video
        
		oc.add(VideoClipObject(
                               url = YT_VIDEO_PAGE % video_id,
                               title = title,
                               summary = summary,
                               originally_available_at = originally_available_at,
                               duration = duration,
                               rating= rating,
                               thumb = Callback(GetThumb, url=thumb)
                               ))
    
	return oc

###################################################################################################
def Playlists():
    
	oc = ObjectContainer(title2='Playlists')
	url = YT_API_PLAYLISTS % YT_USER
    
	for playlist in GetPlaylists(url):
		(playlist_id, title, summary) = playlist
        
		oc.add(DirectoryObject(key=Callback(Playlist, playlist_id=playlist_id, title=title), title=title, summary=summary))
    
	return oc

###################################################################################################
def GetPlaylists(url, start_index=1, max_results=50):
    
	playlists = []
	json = JSON.ObjectFromURL( url % (start_index, max_results) )
    
	if 'feed' in json:
		if 'entry' in json['feed']:
			for playlist in json['feed']['entry']:
				playlist_id = playlist['yt$playlistId']['$t']
				title = playlist['title']['$t']
				summary = playlist['summary']['$t']
                
				playlists.append([playlist_id, title, summary])
        
		if 'openSearch$totalResults' in json['feed']:
			if json['feed']['openSearch$totalResults']['$t'] > start_index + max_results:
				playlists.extend( GetPlaylists(url, start_index = start_index + max_results) )
    
	return playlists

###################################################################################################
def Playlist(playlist_id, title):
    
	oc = ObjectContainer(title2=title, http_cookies=HTTP.CookiesForURL('http://www.youtube.com/'))
	url = YT_API_PLAYLIST % playlist_id
    
	for video in GetVideos(url):
		(video_id, title, summary, originally_available_at, duration, rating, thumb) = video
        
		oc.add(VideoClipObject(
                               url = YT_VIDEO_PAGE % video_id,
                               title = title,
                               summary = summary,
                               originally_available_at = originally_available_at,
                               duration = duration,
                               rating= rating,
                               thumb = Callback(GetThumb, url=thumb)
                               ))
    
	return oc

###################################################################################################
def GetVideos(url, loop_next=True, start_index=1, max_results=50):
    
	videos = []
	json = JSON.ObjectFromURL( url % (start_index, max_results) )
    
	if 'feed' in json:
		if 'entry' in json['feed']:
			for video in json['feed']['entry']:
				video_id = video['media$group']['yt$videoid']['$t']
				title = video['title']['$t']
				summary = video['media$group']['media$description']['$t']
				try:
					published = video['published']['$t']
					originally_available_at = Datetime.ParseDate(published).date()
				except:
					originally_available_at = None
				duration = int(video['media$group']['yt$duration']['seconds']) * 1000
				try:
					rating = float(video['gd$rating']['average']) * 2
				except:
					rating = None
				thumb = video['media$group']['media$thumbnail'][1]['url']
                
				videos.append([video_id, title, summary, originally_available_at, duration, rating, thumb])
        
		if 'openSearch$totalResults' in json['feed']:
			if json['feed']['openSearch$totalResults']['$t'] > start_index + max_results:
				if loop_next:
					videos.extend( GetVideos(url, start_index = start_index + max_results) )
    
	return videos

###################################################################################################
def GetThumb(url):
    
	try:
		data = HTTP.Request(url, cacheTime=CACHE_1MONTH).content
		return DataObject(data, 'image/jpeg')
 	except:
		return Redirect(R(ICON))
