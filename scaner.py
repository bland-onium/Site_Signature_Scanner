import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import sys

#Signature site scanner on python
class SignatureScanner:
	def __init__(self, base_url, signatures):
		self.base_url = base_url 				# First URL
		self.domain = urlparse(base_url).netloc # Domain Url
		self.signatures = signatures 			# List of signatures
		self.visited = []					# List of visited links
		self.session = requests.Session()		# Our session
		self.logname = ''
		
	def get_page_content(self, url): 			# Function to load page
		try:
			response = self.session.get(url, timeout=5)
			response.raise_for_status()
			return response.text 				# Text of page
		except Exception as e:
			print(f"Ошибка при загрузке {url}: {e}")
			return None

	def find_signatures(self, text, url, logfile):		# Module to find signatures
		#print(text)
		print(f"Analysis: {url}")
		logfile.write(f"\n{"="*40}\nAnalysis: {url}")
		logbuff = ''
		for signature in self.signatures:
			#matches = re.finditer(re.escape(signature), text) # ПЕРЕПИСАТЬ. СДЕЛАТЬ АЛЬТЕРНАТИВУ ИЛИ СВОЙ ДВИЖОК
			matches = self.findsign(text, signature)
			for match in matches:
				start = max(0, match) 					# Point of start
				end = min(len(text), match + 100) 	# Point at end
				context = text[start:end]				# Text to write
				print(f"\nFound ▻'{signature}'◅ →→→→→ {context}")
				logbuff+=f"\nFound ▻'{signature}'◅   →→→→→ {context}"
		logfile.write(logbuff)

	def findsign(self, text, sign):
		positions = []
		i = 0
		while i < len(text)-len(sign):
			if text[i:i+len(sign)] == sign:
				print(f"sign->{sign}, txt->{text[i:i+len(sign)]}, i->{i}")
				positions.append(i)
				i += len(sign)
			else:
				i += 1
		return positions
			

	def extract_links(self, html, base_url):
		soup = BeautifulSoup(html, 'html.parser') # ИЗУЧИТЬ ЧТО ЭТО. ПЕРЕПИСАТЬ НА CURL ИЛИ ТИПО ТОГО
		links = []
		for a_tag in soup.find_all('a', href=True):
			href = a_tag['href']
			full_url = urljoin(base_url, href)
			if self.is_same_domain(full_url):
				links.append(full_url)
		return links

	def is_same_domain(self, url):
		return urlparse(url).netloc == self.domain

	def crawl(self, url, depth=0):
		if url in self.visited or depth > 2:  # Ограничение глубины
			return
		self.visited.append(url)
		
		
		logfile, self.logname = self.log_create(url)
		print(f"Анализ: {url}")
		html = self.get_page_content(url)
		if not html:
			return

		self.find_signatures(html, url, logfile)
		links = self.extract_links(html, url)
		
		
		for link in links:
			self.crawl(link, depth + 1)
	def log_create(self, url):
		marker = False; name = ''
		for i in range(1,len(url)):
			if url[i]+url[i-1]=='//':
				marker = True
				continue
			elif marker == True:
				if url[i] == '/':
					break
				name += url[i]
		logfile = open(f"{name}_log.txt", "a", encoding='utf-8')
		return logfile, f"{name}_log.txt"


if __name__ == "__main__":
	print("Usage: py scaner.py https://example/url\t\t(or u can not use any args)")
	if len(sys.argv) > 1:
		target_url = sys.argv[1]
	else:
		target_url = str(input("URL: "))
	if target_url == '':
		quit()
	print(f"Looking at {target_url}")
	signatures = ["телефон", "e-mail", "почта", "мясник", "Директор"]
	
	scanner = SignatureScanner(target_url, signatures)
	scanner.crawl(target_url)
	print(f"Data were placed into {scanner.logname}")
