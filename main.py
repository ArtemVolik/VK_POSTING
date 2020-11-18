import requests
from pprint import pprint
import os
from dotenv import load_dotenv

load_dotenv()
params = {
    'group_id': 200405671,
    'access_token': os.getenv('access_token'),
    'v': 5.126

}

proxies = {
    'http': os.getenv('PROXY_HTTP'),
    'https': os.getenv('PROXY_HTTPS')
}



def fetch_comics(url):
    comics = get_response(url)
    image_link = comics['img']
    image_title = comics['safe_title']
    print(comics['alt'])
    response = requests.get(image_link)
    response.raise_for_status()
    with open(f'{image_title}.{os.path.splitext(image_link)[1]}', 'wb') as file:
        file.write(response.content)


# pprint(get_response('http://xkcd.com/353/info.0.json'))
# fetch_comics('http://xkcd.com/353/info.0.json')



# upload_params = {'group_id': '200405671'}
# upload_url = response.json()['upload_url']


def get_upload_url(params, proxies):
    url = 'https://api.vk.com/method/photos.getWallUploadServer'
    response = requests.get(url, params=params, proxies=proxies)
    response.raise_for_status()
    return response.json()['response']['upload_url']


def post_picture(upload_url, params, file_path, proxies=None):
    with open(file_path, 'rb') as file:
        files = {
            'photo': file,
        }
        response = requests.post(upload_url, files=files, params=params, proxies=proxies)
        response.raise_for_status()
        return response.json()


def save_picture_on_the_wall(params, posted_picture_data):
    url = 'https://api.vk.com/method/photos.saveWallPhoto'
    upload_param = params.copy()
    upload_param['hash'] = posted_picture_data['hash']
    upload_param['photo'] = posted_picture_data['photo']
    upload_param['server'] = posted_picture_data['server']
    response = requests.get(url, params=upload_param, proxies=proxies)
    pprint(response.json())

print(params)
upload_url = get_upload_url(params, proxies)
print(params)
# print(upload_url)
# print(os.listdir())
posted_picture_data = post_picture(upload_url, params, 'Python.png', proxies=proxies)
print(params)
save_picture_on_the_wall(params, posted_picture_data)

