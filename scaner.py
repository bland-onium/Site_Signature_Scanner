import requests
from selectolax.parser import HTMLParser
from urllib.parse import urljoin, urlparse
import sys

#Signature site scanner on python
class SignatureScanner:
	def __init__(self, base_url, signatures, maxdepth):
		self.base_url = base_url 				# First URL
		self.domain = urlparse(base_url).netloc # Domain Url
		self.signatures = signatures 			# List of signatures
		self.visited = []					# List of visited links
		self.session = requests.Session()		# Our session
		self.logname = ''
		self.maxdepth = maxdepth
		self.depth = 0

	# Function of moving at pages
	def crawl(self, url, depth):
		# Check if we've visited page
		if url in self.visited or depth > self.maxdepth:  # Ограничение глубины
			return
		self.visited.append(url)
		
		print(f"Analysis: {url}")
		html = self.get_page_content(url)			 # Call to get data from page
		if not html:
			return

		self.find_signatures(html, url, logfile)	# Call parser to get all info
		links = self.extract_links(html, url)		# Try to find links at page
		
		for link in links:
			self.crawl(link, self.depth + 1)				# Continue an recursion

	def get_page_content(self, url): 			# Function to load page
		try:
			response = self.session.get(url, timeout=5)
			response.raise_for_status()
			return response.text 				# Text of page
		except Exception as e:
			print(f"Ошибка при загрузке {url}: {e}")
			return None

	def find_signatures(self, text, url, logfile):		# Module to find signatures
		logfile.write(f"\n{"="*40}\nAnalysis: {url}")
		logbuff = ''
		for signature in self.signatures:
			matches = self.findsign(text, signature)
			for match in matches:
				start = max(0, match) 					# Point of start
				end = min(len(text), match + 100) 	# Point at end
				context = text[start:end]				# Text to write
				print(f"\n☢ Found ▻'{signature}'◅ →→→→→ {context}")
				logbuff+=f"\n☢ Found ▻'{signature}'◅   →→→→→ {context}" # Writing to log
		logfile.write(logbuff)

	def findsign(self, text, sign):			# Module to find one signature in text
		positions = []
		i = 0
		while i < len(text)-len(sign):
			if text[i:i+len(sign)] == sign: # Found, let's write it to position list
				print(f"sign->{sign}, txt->{text[i:i+len(sign)]}, i->{i}")
				positions.append(i)
				i += len(sign)
			else: 							# Continue parsing
				i += 1
		return positions
			

	def extract_links(self, html, base_url): 	# Module which returns links from site
		links = []								# It uses Selectolax but if you need one page - you can turn of function
		#return links
		parser = HTMLParser(html)
		href_tags = parser.css('a[href], link[href], area[href]')					# href parse
		src_tags = parser.css('img[src], script[src], iframe[src], frame[src]')		# src parse

		for tag in href_tags:														# loop to extract from hrefs
			href = tag.attributes.get('href')
			if href:
				if (href.startswith("#") or											# list of skipping hrefs
					href.startswith("javascript:") or
					href.startswith("mailto:") or
					href.strip() == ''):
					continue
				abs_url = urljoin(base_url, href)
				links.append(abs_url)												# add to list
		for tag in src_tags:														# loop to extract from srcs
			src = tag.attributes.get('src')
			if src:
				if src.startswith('data:') or src.strip() == '':
					continue
				abs_url = urljoin(base_url, href)
				links.append(abs_url)
		return links

	def is_same_domain(self, url):
		return urlparse(url).netloc == self.domain

	def log_create(self, url):				# Module whict creates log file for site
		marker = False; name = ''
		for i in range(1,len(url)):
			if url[i]+url[i-1]=='//': marker = True; continue
			elif marker == True: 
				if url[i] == '/': break
				name += url[i]
		logfile = open(f"{name}_log.txt", "w", encoding='utf-8')
		for i in self.signatures:			# write signatures in the beginning
			logfile.write(i + ' ')
		logfile = open(f"{name}_log.txt", "a", encoding='utf-8')
		return logfile, f"{name}_log.txt"

def get_signatures(): 						# Module whict extract signatures from file or creates them
	print("Signatures stay in file <signs.txt>")
	signatures = []
	var = False
	try:
		file = open('signs.txt', "r").read()
		var = True
	except:
		#print ('VAR _____ 2 _ file not exist, create new')
		var = False
	if var == True:
		#print("VAR ______ 1 _ file exist, we read")
		file = str(open('signs.txt', 'r').read())
		if file == '' or file == ' ':
		#	print("VAR ______ 3 _ file is bullshit, create new")
			signatures = ['email ', 'phone ', 'почта ', 'телефон ', 'Директор ']
			file = open('signs.txt', 'w', encoding='utf-8')
			file = open('signs.txt', 'a', encoding='utf-8')
			for i in signatures: file.write(i)
		else:
			buff = ''
			for i in range(len(file)):
				if file[i] == ' ' or file[i] == '\n':
					signatures.append(buff)
					buff = ''
				else:
					buff += file[i]
	else:
		signatures = ['email ', 'phone ', 'почта ', 'телефон ', 'Директор ']
		file = open('signs.txt', 'w', encoding='utf-8')
		file = open('signs.txt', 'a', encoding='utf-8')
		for i in signatures: file.write(i)

	print(f"seeking signatures: {', '.join(signatures)}")
	return signatures						# Returns list of signatures which we seek on sites
# ======================_____________________======================
# Эта программа создана для извлечения полезных данных с выбранных сайтов методом рекурсивного древовидного прохода
# Требования: Selectolax, requests, urllib
# This program made to extract useful data from sites using method of recursive tree-walking
# Requirements: Selectolax, requests, urllib
# ======================_____________________======================

if __name__ == "__main__":
	print("Usage: python3 scaner.py https://example/url\t(or u can not use any args)")
	if len(sys.argv) > 1:
		target_url = sys.argv[1]
	else:
		target_url = str(input("URL: "))
	if target_url == '':
		quit()
	print(f"Looking at {target_url}")
	#signatures = ["телефон", "e-mail", "почта", "мясник", "Директор"]
	signatures = get_signatures()
	dpt = 1

	scanner = SignatureScanner(base_url=target_url, signatures=signatures, maxdepth=dpt)
	logfile, scanner.logname = scanner.log_create(target_url) # Yes, create log
	scanner.crawl(target_url, dpt)
	print(f"Data were placed into {scanner.logname}")
