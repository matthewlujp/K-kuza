# Copyright 2015 IBM Corp. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import sys
from io import StringIO
from flask import Flask, jsonify, request, make_response
from sql import User, Crop
import peewee
import base64
import socket
from io import BytesIO
from PIL import Image
import datetime


app = Flask(__name__)
PORT = 5000
PORT_FOR_PHOTO_SERVER = 80
PHOTO_SERVER_ROOT = '/Applications/XAMPP/htdocs'


@app.route('/')
def Welcome():
    return app.send_static_file('index.html')


@app.route('/crops/<int:crop_id>/check-mature')
def get_crop_check_mature(crop_id):
    crop = Crop.get(Crop.cropId == crop_id)
    return make_response(jsonify({crop}))


@app.route('/crops/', methods=['POST'])
def create_crop():
    data = request.json
    sup = User.get(User.userId == 1)
    # sup = User.get(User.userId == data['supplier'])
    # crop = Crop.create(name=data['name'], latitude=float(data['latitude']),
    #                    longitude=float(data['longitude']), supplier=sup)
    item_id = data['itemId']
    crop = Crop.create(name=data['crop'], supplier=sup)
    if 'image' in data.keys() and data['image'] is not None:
        # print(data['image'], file=sys.stderr)
        saved_file_name = save_base64_img(data['crop'], data['itemId'], data['image'])
        server_url = request.url.split(':' + str(PORT))[0]
        img_url = "%s:%s/" % (server_url, PORT_FOR_PHOTO_SERVER) + saved_file_name

        # Judge maturity
        is_matured = judge_maturity(saved_file_name)

        crop.img_url = img_url
        # if judge_maturity(saved_file_name):
        #     crop.expected_day = datetime.date.today()
        # else:
        #     crop.expected_day = datetime.date.today() + datetime.timedelta(days=2)
        is_matured = judge_maturity(saved_file_name)
        is_matured = False if is_matured is None else is_matured
        crop.save()

    return jsonify({"itemId": item_id, "crop": crop.name, "image": crop.img_url,
                    # "ExpectedMatureDate": crop.expected_day,
                    "mature": is_matured, "supplier": data['supplier']})


@app.route('/test/', methods=['POST'])
def test():
    data = request.json
    # # print(request.json(), file=sys.stderr)
    # # print(request.json)
    # print(request.json)
    # sup = User.get(User.userId == data['supplier'])
    # crop = Crop.create(name=data['name'], latitude=float(data['latitude']),
    #                    longitude=float(data['longitude']), supplier=sup)
    img_url = ""
    if 'img' in data.keys() and data['img'] is not None:
        # print(data['image'], file=sys.stderr)
        saved_file_name = save_base64_img(1, data['img'])
        server_url = request.url.split(':' + str(PORT))[0]
        img_url = "%s:%s" % (server_url, PORT) + saved_file_name
        # crop.img_url = img_url
        # crop.save()

    return jsonify({"Recieved": img_url})


@app.route('/crops/list', methods=['POST'])
def crops_list():
    data = request.json
    lat, long = float(data['latitude']), float(data['longitude'])
    distance = 10
    crops = Crop.select().where((Crop.longitude >= long - distance) & (Crop.longitude <= long + distance) &
                                (Crop.latitude >= lat - distance) & (Crop.latitude <= lat + distance))
    crops_list = [crop for crop in crops]
    return jsonify({"NearCrops": crops_list})


def save_base64_img(crop_name, item_id, base64_img):
    FILE_DIR = 'images'
    dir_name = "%s/%s/%s" % (FILE_DIR, crop_name, item_id)
    actual_dir_name = "%s/%s" % (PHOTO_SERVER_ROOT, dir_name)
    if not os.path.exists(actual_dir_name):
        os.makedirs(actual_dir_name)
    actual_saved_file_name = "%s/crop.png" % (actual_dir_name)
    saved_file_name = "%s/crop.png" % (dir_name)
    with open(actual_saved_file_name, 'wb') as f:
        f.write(base64.b64decode(base64_img))
    return saved_file_name


@app.route('/users/', methods=['POST'])
def add_user():
    data = request.json
    user = User.create(name=data['name'], email=data['email'])
    return jsonify({"Response": "ok"})


def compute_average_image_color(img):
    width, height = img.size

    r_total = 0
    g_total = 0
    b_total = 0

    count = 0
    for x in range(0, width):
        for y in range(0, height):
            r, g, b = img.getpixel((x, y))
            r_total += r
            g_total += g
            b_total += b
            count += 1

    return (r_total // count, g_total // count, b_total // count)


def judge_maturity(img_file):
    # img = Image.open('greenmango.jpg')
    img = Image.open(img_file)

    average_color = compute_average_image_color(img)

    # print(average_color)
    testrgb = []
    testrgb.append(average_color)
    # print(testrgb)
    # defines RGB boundaries based on statistical means
    yupperboundary = [240, 193, 120]
    ylowerboundary = [200, 153, 58]
    gupperboundary = [121, 160, 100]
    glowerboundary = [81, 120, 60]
    riperegioncheck = []
    riperegioncheck = list(map(lambda pair: max(pair), zip(average_color, yupperboundary)))
    tset = set(riperegioncheck)
    # print(tset)
    yupperboundaryset = set(yupperboundary)
    if (tset.union(yupperboundary) == tset):
        test2 = list(map(lambda pair: min(pair), zip(average_color, ylowerboundary)))
        tset2 = set(test2)
        ylowerboundaryset = set(ylowerboundary)
        if (tset2.union(ylowerboundary) == tset2):
            # print("The Image is of a Ripe Mango")
            return True
        else:
            rawregioncheck = []
            rawregioncheck = list(map(lambda pair: max(pair), zip(average_color, gupperboundary)))
            tset = set(rawregioncheck)
            # print(tset)
            gupperbounderyset = set(gupperboundary)
            if(tset.union(gupperboundary) == tset):
                test3 = list(map(lambda pair: min(pair), zip(average_color, glowerboundary)))
                tset3 = set(test3)
                glowerboundaryset = set(glowerboundary)
                if (tset3.union(glowerboundary) == tset3):
                    # print("The Image is a raw Mango")
                    return False
    else:
        # print("The image is too noisy")
        return None


port = os.getenv('PORT', str(PORT))
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(port))
