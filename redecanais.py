# -*- coding: utf-8 -*-
#
import re
import shutil
import webbrowser

import requests
from bs4 import BeautifulSoup

BASE_URL = 'https://redecanais.rocks'


class Browser:

    def __init__(self):
        self.request = None
        self.response = None

    def headers(self):
        headers = {
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
        }
        return headers

    def open(self, url, referer=None):
        if referer:
            headers = self.headers()
            headers['referer'] = referer
        else:
            headers = self.headers()
        with requests.session() as s:
            self.request = s.get(url, headers=headers)
            self.response = self.request.text
        return self.response


class ChannelsNetwork(Browser):

    def __init__(self):
        super().__init__()

    def search(self):
        film_name = input('Digite o nome do filme que deseja assistir: ')
        url_search = f'{BASE_URL}/search.php?keywords={film_name}'
        return self.films_per_genre(url_search)

    def films(self, url, category, page=None):
        if type(category) is dict:
            list_category = ['legendado', 'dublado', 'nacional']
            if category['category'] in list_category:
                info_category = self.categories(url, category['category'].capitalize() + ' ')[0]
                pages = re.compile(r'videos-(.*?)-date').findall(info_category['url'])[0]
                if category['category'] == 'dublado':
                    print(BASE_URL + info_category['url'].replace('filmes-dublado', category['genre'].capitalize() + '-Filmes').replace(pages, str(category['page']) + '-date'))
                    url_category_films = BASE_URL + info_category['url'].replace('filmes-dublado', category['genre'].capitalize() + '-Filmes').replace(pages, str(category['page']) + '-date')
                    return self.films_per_genre(url_category_films)
                else:
                    print(BASE_URL + info_category['url'].replace('filmes-' + category['category'], category['genre'].capitalize() + '-Filmes-' + category['category'].capitalize()).replace(pages, str(category['page']) + '-date'))
                    url_category_films = BASE_URL + info_category['url'].replace('filmes-' + category['category'], category['genre'].capitalize() + '-Filmes-' + category['category'].capitalize()).replace(pages, str(category['page']) + '-date')
                    return self.films_per_genre(url_category_films)
            else:
                info_category = self.categories(url, category['category'].capitalize() + ' ')[0]
                pages = re.compile(r'videos(.*?)date').findall(info_category['url'])[0]
                url_category_films = BASE_URL + info_category['url'].replace(pages, '-' + str(page) + '-')
                print(url_category_films)
                return self.films_per_category(url_category_films)
        else:
            info_category = self.categories(url, category.capitalize() + ' ')[0]
            pages = re.compile(r'videos(.*?)date').findall(info_category['url'])[0]
            url_category_films = BASE_URL + info_category['url'].replace(pages,  '-' + str(page) + '-')
            print(url_category_films)
            return self.films_per_category(url_category_films)

    def films_per_category(self, url):
        html = self.open(url)
        soup = BeautifulSoup(html, 'html.parser')
        tags = soup.find('ul', {'class': 'row pm-ul-browse-videos list-unstyled'})
        films = tags.find_all('div', {'class': 'pm-video-thumb'})
        films_list = []
        for info in films:
            result = info.find_all('a')[1]
            dict_films = {'title': result.img['alt'], 'url': BASE_URL + result['href'], 'img': result.img['data-echo']}
            films_list.append(dict_films)
        return films_list

    def films_per_genre(self, url, category=None, genre=None):
        url_genre = url
        html = self.open(url_genre)
        soup = BeautifulSoup(html, 'html.parser')
        tags = soup.find('ul', {'class': 'row pm-ul-browse-videos list-unstyled'})
        films = tags.find_all('div', {'class': 'pm-video-thumb'})
        films_list = []
        for info in films:
            result = info.find_all('a')[1]
            dict_films = {'title': result.img['alt'], 'url': BASE_URL + result['href'], 'img': result.img['data-echo']}
            films_list.append(dict_films)
        return films_list

    def categories(self, url, category=None):
        html = self.open(url)
        soup = BeautifulSoup(html, 'html.parser')
        tags = soup.find_all('li', {'class': 'dropdown-submenu'})[0]
        tags.ul.unwrap()
        new_html = str(tags).replace('dropdown-submenu', '').replace('</a>\n', '</a> </li>')
        new_soup = BeautifulSoup(new_html, 'html.parser')
        new_tags = new_soup.find_all('li')
        category_list = []
        for info in new_tags:
            if category is not None:
                if category == info.text:
                    category_dict = {'category': info.text, 'url': info.a['href']}
                    category_list.append(category_dict)
            else:
                category_dict = {'category': info.text, 'url': info.a['href']}
                category_list.append(category_dict)
        return category_list

    def get_player(self, url):
        html = self.open(url)
        iframe = BeautifulSoup(html, 'html.parser')
        url_player = iframe.find('div', {'id': 'video-wrapper'}).iframe['src']
        url_player_dict = {'embed': url_player, 'player': url_player.replace('.php', 'playerfree.php')}
        return url_player_dict

    def get_stream(self, url, referer):
        html = self.open(url, referer)
        source = BeautifulSoup(html, 'html.parser')
        url_stream = source.find('div', {'id': 'instructions'}).source['src']
        return url_stream

    def download(self, url):
        filename = url.split('/')[-1].replace('?attachment=true', '')
        print('Downloading...' + filename)
        with requests.get(url, stream=True) as r:
            with open(filename, 'wb') as f:
                shutil.copyfileobj(r.raw, f)

    def select_film(self, films):
        print('\n')
        for index, film in enumerate(films):
            print(str(index) + ' == ' + film['title'])
        print('\n')
        selected = int(input('Digite o número correspondente ao filme que deseja assistir: '))
        print(films[selected]['url'])
        filme = films[selected]['url']
        player_url = rede.get_player(filme)
        video_url = rede.get_stream(url=player_url['player'], referer=player_url['embed'])
        print(video_url)
        rede.play(video_url)
        return

    def play(self, url):
        start = """
<!DOCTYPE html>
<html lang="en">
<style>
.container {
    width: 100vw;
    height: 100vh;
    background: #6C7A89;
    display: flex;
    flex-direction: row;
    justify-content: center;
    align-items: center
}

.title {
    text-align: center;
}

body {
    margin: 0px;
}
</style>
<head>
    <meta charset="UTF-8">
    <title>afterglow player</title>
    <link rel="stylesheet" href="//cdn.jsdelivr.net/afterglow/latest/afterglow.min.js" type=”text/javascript”>
</head>
<body>
    <div class="title">
        <h3>RedeCanais Player With Python Backend</h3>
    </div>
    <div class="container">
        <div>
            <video class="afterglow" id="myvideo" controls width="1080" height="500" autoplay="autoplay" src="%s"></video>
        </div>
    </div>
</body>
<script>

</script>
</html>
        """ % url

        with open('player.html', 'w') as f:
            f.write(start)
        webbrowser.open('player.html')
        return print('Starting video')


if __name__ == '__main__':
    rede = ChannelsNetwork()
    #categorias = rede.categories(BASE_URL + '/browse.html')
    #print(categorias)
    #filmes = rede.films(BASE_URL + '/browse.html', category='filmes 2018', page=3)
    #search_film = rede.search()
    #print(search_film)
    filmes = rede.films(BASE_URL, category={'category': 'dublado', 'genre': 'terror', 'page': 2})
    print(filmes)
    """print('\n')
    for index, film in enumerate(filmes):
        print(str(index) + ' == ' + film['title'])
    print('\n')
    select = int(input('Digite o número correspondente ao filme que deseja assistir: '))
    print(filmes[select]['url'])
    filme = filmes[select]['url']
    player_url = rede.get_player(filme)
    video_url = rede.get_stream(url=player_url['player'], referer=player_url['embed'])
    print(video_url)
    rede.play(video_url)
    """
    #player_url = rede.get_player('https://redecanais.rocks/doutor-estranho-dublado-2016-1080p_55218911d.html')
    #print(player_url)
    #video_url = rede.get_stream(url='https://cometa.top/player3/serverfplayerfree.php?vid=VNGDRSULTMTO4K', referer='https://cometa.top/player3/serverf.php?vid=VNGDRSULTMTO4K')
    #video_url = rede.get_stream(url=player_url['player'], referer=player_url['embed'])
    #print(video_url)
    #search_film = rede.search()
    #print(search_film)
    #rede.download(video_url)
    #rede.play(video_url)
    #select_film = rede.select_film(filmes)
