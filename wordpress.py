import json
import base64

from bs4 import BeautifulSoup
from urllib.parse import urljoin
from image import generate_image
from request import get_session

WP_URL = ''  # 자신의 워드프레스 주소
WP_USERNAME = ''  # 워드프레스 사용자이름
WP_PASSWORD = ''  # 어플리케이션 비밀번호


def get_header(user, password):
    credentials = user + ':' + password
    token = base64.b64encode(credentials.encode())
    header_json = {'Authorization': 'Basic ' + token.decode('utf-8')}
    return header_json

def post(title, description, keywords, html):
    media_id = None

    if keywords:
        image_url = generate_image(keywords)
        if image_url:
            media = {'file': open(image_url, "rb"), 'caption': keywords}
            res = get_session().post(
                urljoin(WP_URL, "wp-json/wp/v2/media"),
                files=media,
                headers=get_header(WP_USERNAME, WP_PASSWORD),
                auth=(WP_USERNAME, WP_PASSWORD)
            )
            
            if res.ok:
                media_id = res.json()['id']


    status = 'publish'  # 즉시발행：publish, 임시저장：draft

    category_ids = []
    tag_ids = []

    tags_response = get_session().get(urljoin(WP_URL, "wp-json/wp/v2/tags"))
    tags = tags_response.json()
    print(tags)

    keywords_array = [x.strip() for x in keywords.split(',')]

    for keyword in keywords_array:
        tag_id = None

        # 태그가 존재하는지 확인하고 ID 가져오기
        for tag in tags:
            if tag['name'] == keyword:
                tag_id = tag['id']
                break

        # 태그가 존재하지 않으면 추가하고 ID 가져오기
        print(keyword + ' is not exists in tag')
        if tag_id is None:
            new_tag_response = get_session().post(
                urljoin(WP_URL, "wp-json/wp/v2/tags"),
                data=json.dumps({'name': keyword}),
                headers={'Content-type': "application/json"},
                auth=(WP_USERNAME, WP_PASSWORD)
            )
            new_tag = new_tag_response.json()
            print(new_tag)
            tag_id = new_tag['id'] if 'id' in new_tag else None

        if tag_id:
            print(f'Tag ID: {tag_id}')
            tag_ids.append(tag_id)
        else:
            print('Failed to get or create tag.')

    print(tag_ids)

    meta = {
        "title": title,
        "description": description,
    }

    soup = BeautifulSoup(html, 'html.parser')

    payload = {"status": status,
            "title": title,
            "content": str(soup.body),
            "categories": category_ids,
            "lang": 'en',
            "tags": tag_ids,
            "excerpt": description,
            "meta": meta}
    
    if media_id is not None:
        payload['featured_media'] = media_id

    res = get_session().post(urljoin(WP_URL, "wp-json/wp/v2/posts"),
                            data=json.dumps(payload),
                            headers={'Content-type': "application/json"},
                            auth=(WP_USERNAME, WP_PASSWORD))

    if res.ok:
        print(f"성공 code:{res.text}")
    else:
        print(f"실패 code:{res.status_code} reason:{res.reason} msg:{res.text}")