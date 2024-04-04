import requests
import time
import io


class ImageClient:
    def __init__(self, timeout: float=0.1):
        self.host = 'http://178.154.220.122:7777/images/'
        self.timeout = timeout

    def get_image(self, image_id: int):
        retry_limit = 5
        while retry_limit > 0:
            try:
                response = requests.get(
                            self.host + str(image_id),
                            timeout=self.timeout
                            )
                status = response.status_code
                if status == 200:
                    im = io.BytesIO(response.content)
                    return im, 200
                # отдельно не обрабатываем 404, т.к. валидируем доступные айдишники внутри эндпоинта
                else:
                    retry_limit -= 1
                    time.sleep(0.1)
                    continue
            except requests.exceptions.Timeout:
                retry_limit -= 1
                time.sleep(0.1)
                continue
        return None, 500
