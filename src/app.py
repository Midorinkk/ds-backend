from flask import Flask, request
import requests
import logging

from models.plate_reader import PlateReader
from client import ImageClient

import io
from PIL import UnidentifiedImageError


app = Flask(__name__)

plate_reader = PlateReader.load_from_file('/app/model_weights/plate_reader_model.pth')
image_provider_client = ImageClient()

VALID_IDS = ['10022', '9965']
ERRORS = {422: {'error': 'Invalid image id'},
          500: {'error': 'Internal server error while downloading image'}}


@app.route('/read_plate', methods=['GET'])
def read_plate():
    image_id = request.args.get('image_id')

    # сразу выбрасываем невалидные id
    if image_id not in VALID_IDS:
        return ERRORS[422], 422

    im, status = image_provider_client.get_image(image_id)

    if status == 200:
        res = plate_reader.read_text(im)
        return {'plate_number': res}
    else:
        return ERRORS[500], 500


@app.route('/read_plates', methods=['POST'])
def read_plates():
    image_ids = request.form.getlist('image_ids')

    plates = []
    for image_id in image_ids:
        plate = {'image_id': image_id}

        if image_id not in VALID_IDS:
            plate['result'] = ERRORS[422]
            plates.append(plate)
            continue

        im, status = image_provider_client.get_image(image_id)

        if status == 200:
            res = plate_reader.read_text(im)
            plate['result'] = {'plate_number': res}
        else:
            plate['result'] = ERRORS[500]
        plates.append(plate)

    return plates



if __name__ == '__main__':
    logging.basicConfig(
        format='[%(levelname)s] [%(asctime)s] %(message)s',
        level=logging.INFO,
    )

    # помогает печатать кириллицу
    app.json.ensure_ascii = False
    app.run(host='0.0.0.0', port=8080, debug=True)
