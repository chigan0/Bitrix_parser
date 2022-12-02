from typing import List
import asyncio
import re
import csv
import os

from bs4 import BeautifulSoup
from aiohttp.client_exceptions import InvalidURL
import aiohttp


valid_url = 0
os_name = os.name


def csv_write(phone, mail, title, header, domain):
	with open('result.csv', 'a', newline='\n') as csvfile:
		fieldnames = ['Title','Header', 'Mail', 'Phone', 'Сыллка']
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
		#writer.writeheader()

		phone = set(i for i in phone)
		mail = set(i for i in mail)

		writer.writerow({
			'Title': title.string if title is not None else 'Не Найденно',
			'Header': header.string if header is not None else 'Не Найденно',
			'Mail': ','.join(mail) if len(mail) > 0 else 'Не Найденно',
			'Phone': ','.join(phone) if len(phone) > 0 else 'Не Найденно',
			'Сыллка': domain
		})


async def search_bitrix(values: List[str], domain: str, html, soup):
	global valid_url

	for i in values:
		if re.search(r'\bbitrix24\b', str(i)) is not None:
			if re.search(r'\bsite_button\b', str(i)) is not None:
				mail = []
				phone = []
				title = soup.title
				src = soup.find_all('a')
				header = soup.find('h1')

				for i in src:
					try:
						data = i.get('href').split(':')
						
						if data[0] == 'mailto':
							mail.append(data[-1])

						elif data[0] == 'tel':
							phone.append(data[-1])

					except AttributeError:
						continue

				csv_write(phone, mail, title, header, domain)
				valid_url += 1


async def main():
	global valid_url

	session = aiohttp.ClientSession()
	url_count = 0

	with open('ru.txt') as domens:
		for domen in domens.read().split('\n'):
			try:
				d = f'http://{domen}'
				async with session.get(d, timeout=3) as resp:
					html = await resp.text()
					soup = BeautifulSoup(html, 'html.parser')
					scripts = soup.find_all('script')
					asyncio.create_task(search_bitrix(scripts, d, html, soup))

			except Exception as e:
				continue

			url_count+=1
			os.system('clear' if os_name == 'posix' else 'cls')

			print(f"Проверено: {url_count}")
			print(f'Найдено: {valid_url}')

	await session.close()

if __name__ == '__main__':
	asyncio.run(main())