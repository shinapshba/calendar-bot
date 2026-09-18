from urllib.parse import urljoin
from requests import Request, Response, request as send_request
from requests.exceptions import Timeout as RequestTimeoutException

ROOT_HOST = 'https://production-calendar.ru'
ROOT_URL = ROOT_HOST + '/v2/'
TIMEOUT = 5


class ProductionCalendar:
    def __init__(self, token):
        self.token = token

    @staticmethod
    def __build_info_log(request: Request, response: Response):
        return f'\tURL: {request.url}\n' \
               f'\tResponse code: {response.status_code}'

    def __process_current_period(self, period):
        request = Request(method='GET', headers={'Authorization': f'Bearer {self.token}'},
                          url=urljoin(ROOT_URL, f'ru/{period}/days'))
        try:
            response = send_request(method=request.method, headers=request.headers, url=request.url, timeout=TIMEOUT)
        except RequestTimeoutException:
            raise Exception(f'Timeout while processing with production-calendar resource. URL - {request.url}')
        return response

    def get_current_week(self):
        return self.__process_current_period('current-week')

    def get_current_month(self):
        return self.__process_current_period('current-month')

    def get_current_quarter(self):
        return self.__process_current_period('current-quarter')

    def get_current_year(self):
        return self.__process_current_period('current-year')

    def get_current_day(self):
        return self.__process_current_period('today')
