from html.parser import HTMLParser  
from urllib.request import urlopen  
from urllib import parse
from concurrent import futures	
from urllib import robotparser
import threading
import sys
# We are going to create a class called LinkParser that inherits some
# methods from HTMLParser which is why it is passed into the definition
class LinkParser(HTMLParser):
	visited = []
	numVisited = 0
	# This is a function that HTMLParser normally has
	# but we are adding some functionality to it
	def handle_starttag(self, tag, attrs):
		# We are looking for the begining of a link. Links normally look
		# like <a href="www.someurl.com"></a>
		if tag == 'a':
			for (key, value) in attrs:
				if key =='href':
					# We are grabbing the new URL. We are also adding the
					# base URL to it. For example:
					# www.netinstructions.com is the base and
					# somepage.html is the new URL (a relative URL)
					#
					# We combine a relative URL with the base URL to create
					newUrl = parse.urljoin(self.baseUrl, value)
					# And add it to our colection of links:
					self.links = self.links + [newUrl]

	# This is a new function that we are creating to get links
	# that our spider() function will call
	def getLinks(self, url):
		self.links = []
		# Remember the base URL which will be important when creating
		# absolute URLs
		self.baseUrl = url
		# Use the urlopen function from the standard Python 3 library
		response = urlopen(url)
		# Make sure that we are looking at HTML and not other things that
		# are floating around on the internet (such as
		# JavaScript files, CSS, or .PDFs for example)
		if response.getheader('Content-Type')=='text/html':
			htmlBytes = response.read()
			# Note that feed() handles Strings well, but not bytes
			# (A change from Python 2.x to Python 3.x)
			htmlString = htmlBytes.decode("utf-8")
			self.feed(htmlString)
			return htmlString, self.links
		else:
			return "",[]

# And finally here is our spider. It takes in an URL, a word to find,
# and the number of pages to search through before giving up
def spider(url,superMaxPages):
	print(threading.current_thread())
	lock = threading.Lock()
	writeLock = threading.Lock()
	mydata = threading.local()
	mydata.numberVisited = 0  

	# Start from the beginning of our collection of pages to visit:
	# frequency of visitingg the URL, we chose it to be based on the domain (to be easier for us)
	while url != [] and LinkParser.numVisited < int(maxPages):

		# lock the vistied list, since more than one thread reads and writes to it.
		lock.acquire()
		try:
			mydata.link = url[0]
			del url[0]
		finally:
			lock.release() # this won't block

		# In case we are not allowed to read the page -> delete url -> continue.
		rp = robotparser.RobotFileParser()
		rp.set_url(mydata.link+'/robots.txt')
		rp.read()
		if not(rp.can_fetch("*", mydata.link)):
			continue

		LinkParser.visited.append(mydata.link)

		LinkParser.numVisited += 1

		writeLock.acquire()
		try:
			f.write(mydata.link+'\n')
		finally:
			writeLock.release()

		try:
			parser = LinkParser()
			data, links = parser.getLinks(mydata.link)		
			# Add the pages that we visited to the end of our collection
			# of pages to visit:
			url = url + links
			print("One more page added from &i",threading.get_ident())
		except:
			print(" **Failed!**")

class myThread (threading.Thread):
	def __init__(self, url, maxPages):
		threading.Thread.__init__(self)
		self.maxPages = maxPages
	def run(self):
		spider (url, maxPages)


def file_len(fname):
	with open(fname) as f:
		return(sum(1 for _ in f))


if __name__ == '__main__':
# Retirve previously made list.
	length = 0
	try:
		length = file_len("urls.txt")
	except:
		print("file doesnt exist yet")
	if length > 1:
		f = open('urls.txt','r+')		
		print(length)
		for x in range(length):
			LinkParser.visited.append(f.readline().strip('\n'))
			print(LinkParser.visited)

	else:
		f = open('urls.txt','w+')					

	threads = []
	url = []
	url.append("https://docs.python.org/3/py-modindex.html")
	# url.append("https://docs.python.org/3/py-modindex.html")
	# url.append("https://docs.python.org/3/library/threading.html")
	numberOfThreads = sys.argv[1]

	maxPages = sys.argv[2]	# This value is overriden in the function Spider #
	for i in range(0,int(numberOfThreads)):
		threads.append(myThread( spider, (url,maxPages) ))	# This value is overriden in the function Spider #

	print("Number of created threads is ", threading.active_count(), "threads len is" , len(threads))

	for i in range(0,int(numberOfThreads)):
		threads[i].start()

	print("Number of created threads is ", threading.active_count(), "threads len is" , len(threads))

	for j in range(0,int(numberOfThreads)):
		threads[j].join()

	# This zero should be overriden after we know the number of acual urls crawled.
	#f.write('0')		# This '0' means the Indexer was here, -the indexer sets the '0'-,	// Fares.
										# if it is 'x', then, 'x' pages have been added to the list, since last time the indexer has indexed.
										# This is done to save the indexer from re indexing indexed pages.
	f.close()
