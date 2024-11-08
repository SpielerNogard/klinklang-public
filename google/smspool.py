import time

import requests
from pydantic import BaseModel
from typing import List

URL = "https://api.smspool.net"


class Pool(BaseModel):
    ID: int
    name: str


class Country(BaseModel):
    ID: int
    name: str
    short_name: str
    cc: str
    region: str


class Service(BaseModel):
    ID: int
    name: str
    favourite: int


class Pricing(BaseModel):
    service: int
    service_name: str
    country: int
    country_name: str
    short_name: str
    pool: int
    price: float


class OrderResponse(BaseModel):
    success: int
    number: int
    cc: str
    phonenumber: str
    order_id: str
    orderid: str
    country: str
    service: str
    pool: int
    expires_in: int
    expiration: int
    message: str
    cost: str
    current_balance: str


class SMSPool:
    def __init__(self, api_key: str, service_name: str):
        self.api_key = api_key
        self._headers = {"Authorization": f"Bearer {self.api_key}"}

        self._countries = self.country_list()
        self._service = Service(**{"ID": 395, "name": "Google/Gmail", "favourite": 0})

    def order_history(self, phone_number: str = None):
        url = f"{URL}/request/history"
        resp = requests.post(url, params={"key": self.api_key}, headers=self._headers)
        if phone_number:
            return [item for item in resp.json() if item["phonenumber"] == phone_number]
        return resp.json()

    def country_list(self) -> List[Country]:
        url = f"{URL}/country/retrieve_all"
        resp = requests.get(url, headers=self._headers)
        return [Country(**item) for item in resp.json()]

    def service_list(self) -> List[Service]:
        url = f"{URL}/service/retrieve_all"
        resp = requests.get(url, headers=self._headers)
        return [Service(**item) for item in resp.json()]

    def pool_list(self) -> List[Pool]:
        url = f"{URL}/pool/retrieve_all"
        resp = requests.post(url, headers=self._headers)
        return [Pool(**item) for item in resp.json()]

    def order_sms(
        self, service: Service, option: str = "cheapest", ignore_countries: list = None
    ) -> OrderResponse:
        ignore_countries = ignore_countries or []
        best_option = self.best_option(
            service=service, option=option, nr_of_options=100000
        )

        for option in best_option:
            if option.country_name in ignore_countries:
                print(f"{option=} skipped")
                continue
            if option.country in ignore_countries:
                print(f"{option=} skipped")
                continue
            resp = requests.post(
                f"{URL}/purchase/sms",
                headers=self._headers,
                params={
                    "service": option.service,
                    "country": option.country,
                    "pool": option.pool,
                    "pricing_option": 0,
                    "quantity": 1,
                },
            )
            if resp.status_code != 200:
                print("Order failed")
                print(resp.content)
                continue
            print(resp.json())
            return OrderResponse(**resp.json())

    def request_pricing(self, service: Service) -> List[Pricing]:
        url = f"{URL}/request/pricing"
        resp = requests.post(url, headers=self._headers)
        pricings = [Pricing(**item) for item in resp.json()]
        return [pricing for pricing in pricings if pricing.service == service.ID]

    def best_option(
        self, service: Service, option: str = "cheapest", nr_of_options: int = 1
    ) -> List[Pricing]:
        if option == "cheapest":
            return sorted(self.request_pricing(service=service), key=lambda x: x.price)[
                :nr_of_options
            ]
        else:
            pass

    def refund(self, order_id: str):
        url = f"{URL}/sms/cancel"
        resp = requests.post(url, headers=self._headers, params={"orderid": order_id})
        print(resp.json())
        return resp.json()
