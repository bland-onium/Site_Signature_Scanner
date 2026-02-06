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

	# Function of moving at pages
	def crawl(self, url, depth=0):
		# Check if we've visited page
		if depth > self.maxdepth: return
		if url in self.visited:  return # Ограничение глубины
		self.visited.append(url)
		print(f"Depth right now: {depth}")
		
		print(f"Analysis: {url}")
		html = str(self.get_page_content(url)).lower()			 # Call to get data from page
		if not html: return

		self.find_signatures(html, url, logfile)	# Call parser to get all info
		links = self.extract_links(html, url)		# Try to find links at page
		#print(links)

		for link in links:
			if link not in self.visited:
				self.crawl(link, depth + 1)				# Continue an recursion

	def get_page_content(self, url): 			# Function to load page
		try:
			response = self.session.get(url, timeout=5)
			response.raise_for_status()
			return response.text 				# Text of page
		except Exception as e:
			print(f"Ошибка при загрузке {url}: {e}")
			return None
	
	def find_signatures(self, text, url, logfile):
		logfile.write(f"\n{'='*40}\nAnalysis: {url}")
		logbuff = ''

		parser = HTMLParser(text)
		for tag in parser.css('script, style, noscript, iframe'):
			tag.decompose()
		
		visible_text = parser.body.text(separator=' ', strip=True)
		for signature in self.signatures:
			signature_lower = signature.lower()
			text_lower = visible_text.lower()
			pos = text_lower.find(signature_lower)
			while pos != -1:
				start = max(0, pos - 80)
				end = min(len(visible_text), pos + 100)
				context = visible_text[start:end]

				print(f"\n ☢\t Found ▻'{signature}'◅ → {context}")
				logbuff += f"\n ☢\t Found ▻'{signature}'◅ → {context}"

				pos = text_lower.find(signature_lower, pos + 1)
		logfile.write(logbuff)

	def extract_links(self, html, base_url): 	# Module which returns links from site
		links = []								# It uses Selectolax but if you need one page - you can turn of function
		#return links
		if not html: return links

		parser = HTMLParser(html)
		href_tags = parser.css('a[href]')#, link[href], area[href]')					# href parse
		#src_tags = parser.css('img[src], script[src], iframe[src], frame[src]')		# src parse

		for tag in href_tags:														# loop to extract from hrefs
			href = tag.attributes.get('href')
			if href:
				href = href.strip()
				if (href.startswith("#") or											# list of skipping hrefs
					href.startswith("javascript:") or
					href.startswith("mailto:") or
					href.startswith("tel:") or
					href.endswith("mp4") or
					href.endswith("mp3") or
					href.endswith("pdf") or
					not href): #href.strip() == ''):
					continue
				abs_url = urljoin(base_url, href)
				
				if self.is_same_domain (abs_url):
					clean_url = abs_url.split('#')[0].rstrip('/')
					if clean_url:
						links.append(clean_url) #abs_url)												# add to list
		#for tag in src_tags:														# loop to extract from srcs
		#	src = tag.attributes.get('src')
		#	if src:
		#		if src.startswith('data:') or src.strip() == '':
		#			continue
		#		abs_url = urljoin(base_url, src)#href)#src)#href)
		#		links.append(abs_url)
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
					signatures.append(buff.lower())
					#print(f"|{buff}|")
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

def get_links():
	print("Links stay in file <links.txt>")
	links = []
	try:
		file = open('links.txt', "r").read()
		if file == '' or file == ' ':
			print("No links to parse :(")
		else:
			buff = ''
			for i in range(len(file)):
				if file[i] == ' ' or file[i] == '\n':
					links.append(buff.lower())
					#print(f"|{buff}|")
					buff = ''
				else:
					buff += file[i]
		return links
	except:
		print("broken file or it doesn't exists!")
		try: file = open("links.txt", "r").read()
		except FileExistsError: open('links.txt', 'w'); print('created file links.txt')  
		except FileNotFoundError: open('links.txt', 'w'); print('created file links.txt')
	return None	

# ======================_____________________======================
# Эта программа создана для извлечения полезных данных с выбранных сайтов методом рекурсивного древовидного прохода
# Почти все инструменты и библиотеки вшиты в Python (кроме Selectolax)
# This program made to extract useful data from sites using method of recursive tree-walking
# Most of instuments uses basical Python libs (instead of Selectolax)
# ======================_____________________======================

if __name__ == "__main__":
	#lnk = False
	#while True:
		#print("Usage: python3 scaner.py https://example/url\t(or u can not use any args)")
		#if lnk == False:
		#	if len(sys.argv) > 1:
		#		target_url = sys.argv[1]
		#	else:
		#		target_url = str(input("URL: "))
		#	if target_url == '':
		#		quit()
		#else:
		#	target_url = str(input("URL: "))
		#lnk = True
	links = get_links()
	for i in range(len(links)):
		target_url = links[i]
		print(f"Looking at {target_url}")
		#signatures = ["телефон", "e-mail", "почта", "мясник", "Директор"]
		signatures = get_signatures()
		dpt = 2
		#dpt = int(input("Depth -> "))

		scanner = SignatureScanner(base_url=target_url, signatures=signatures, maxdepth=dpt)
		logfile, scanner.logname = scanner.log_create(target_url) # Yes, create log
		scanner.crawl(target_url)
		print(f"Data were placed into {scanner.logname}")
