import requests
from pprint import pprint
import os
from dotenv import load_dotenv
import random
from pathvalidate import sanitize_filename

load_dotenv()

params = {
    'group_id': os.getenv('group_id'),
    'access_token': os.getenv('access_token'),
    'v': 5.126
}

proxies = {
    'http': os.getenv('PROXY_HTTP'),
    'https': os.getenv('PROXY_HTTPS')
}


def get_response(url, params=None, proxies=None):
    response = requests.get(url, params=params, proxies=proxies)
    response.raise_for_status()
    answer = response.json()
    return answer


def get_random_comics():
    comics_count = get_response('https://xkcd.com/info.0.json')['num']
    return random.randint(1, comics_count)


def fetch_comics(comics_id):
    comics = get_response(f'https://xkcd.com/{comics_id}/info.0.json')
    return {'image_link': comics['img'], 'image_title': comics['safe_title'], 'image_alt': comics['alt']}

def save_picture(comics):
    file_name = sanitize_filename(f"{comics['image_title']}{os.path.splitext(comics['image_link'])[1]}")
    with open(file_name, 'wb') as file:
            response = requests.get(comics['image_link'])
            file.write(response.content)
    return file_name


def get_upload_url(params, proxies):
    url = 'https://api.vk.com/method/photos.getWallUploadServer'
    return get_response(url, params=params, proxies=proxies)['response']['upload_url']


def post_picture(upload_url, file_path, params=None, proxies=None):
    with open(file_path, 'rb') as file:
        files = {
            'photo': file,
        }
        response = requests.post(upload_url, files=files, params=params, proxies=proxies)
        response.raise_for_status()
        return response.json()


def save_picture_for_the_wall(posted_picture_data, params=None, proxies=None):
    url = 'https://api.vk.com/method/photos.saveWallPhoto'
    upload_param = params.copy()
    upload_param['hash'] = posted_picture_data['hash']
    upload_param['photo'] = posted_picture_data['photo']
    upload_param['server'] = posted_picture_data['server']
    response = requests.post(url, params=upload_param, proxies=proxies)
    return response.json()


def post_picture_on_the_wall(saved_picture_data, params=None, proxies=None):
    photo_id = saved_picture_data['response'][0]['id']
    owner_id = saved_picture_data['response'][0]['owner_id']
    post_params = params.copy()
    post_params['owner_id'] = f"-{post_params['group_id']}"
    post_params['from_group'] = 1
    post_params['message'] = 'test'
    post_params['attachments'] = f'photo{owner_id}_{photo_id}'
    print(post_params)
    url = 'https://api.vk.com/method/wall.post'
    response = requests.post(url, params=post_params, proxies=proxies)
    response.raise_for_status()
    print(response.json())




if __name__ == '__main__':
    comics_id = get_random_comics()
    comics = fetch_comics(comics_id)
    file_name = save_picture(comics)
    upload_url = get_upload_url(params, proxies)
    posted_picture_data = post_picture(upload_url, file_name, params, proxies)
    saved_picture_data = save_picture_for_the_wall(posted_picture_data, params, proxies)
    pprint(saved_picture_data)
    post_picture_on_the_wall(saved_picture_data, params, proxies)
    os.remove(file_name)




