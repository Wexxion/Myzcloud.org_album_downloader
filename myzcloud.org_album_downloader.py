import os
import requests
import argparse
from bs4 import BeautifulSoup

HOST = 'https://myzcloud.org'


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--link', type=str, help='link to album on myzcloud.org')
    parser.add_argument('-f', '--file', type=str, help='path to file with links to albums on myzcloud.org')
    parser.add_argument('-o', '--output', type=str, help='path to save album')

    args = parser.parse_args()
    return args.link, args.file, args.output


def get_output_path(output, album_name):
    output_path = os.path.join(output, album_name)
    if not os.path.isdir(output_path):
        os.mkdir(output_path)
    return output_path


def download_album(link, output):
    if not link.startswith('https://myzcloud.org/album/'):
        print("link should start with 'https://myzcloud.org/album/', but yours '{}'".format(link))
    album_page = requests.get(link).text
    soup = BeautifulSoup(album_page, 'html.parser')
    album_name = soup.find("header", {"class": "content__title"}).contents[1].string

    output_path = get_output_path(output, album_name)
    print(album_name)

    song_tags = soup.find_all("div", {"class": "playlist__actions"})
    for i in range(len(song_tags)):
        song_tag = song_tags[i]
        song_link = HOST + song_tag.find('a')['href']

        try:
            song_filename, song = download_song(song_link, i + 1)
            print('\t{}'.format(song_filename))

            save_song(output_path, song_filename, song)
        except:
            print("Can't download song '{}'".format(song_link))


def download_song(link, number):
    song_page = requests.get(link).text
    soup = BeautifulSoup(song_page, 'html.parser')
    song_name = soup.find("li", {"class": "breadcrumb-item active"}).string
    song_filename = "{}. {}.mp3".format(number, song_name)

    download_link = HOST + soup.find("div", {"class": "playlist__actions"}).find('a')['href']
    song = requests.get(download_link).content
    return song_filename, song


def save_song(output_path, song_filename, song):
    with open(os.path.join(output_path, song_filename), 'wb') as file:
        file.write(song)


if __name__ == '__main__':
    link, filename, output = parse_args()
    if not output:
        output = os.getcwd()
    if link:
        download_album(link, output)
    elif filename:
        with open(filename) as file:
            for album_link in file.readlines():
                download_album(album_link.strip(), output)
