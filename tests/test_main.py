import hmac, hashlib
import random
import string

from unittest import TestCase
from parameterized import parameterized
from fastapi.testclient import TestClient

from app.main import app
from app.config import SECRET_KEY


def prepare_data() -> tuple[list[list], list[list], list[list]]:
    """Generation data for testing:
        - data_with_right_sig: list with right signature and all params
        - data_without_params: list with right signature and without params (appId, sessionId, accountId)
        - data_with_wrong_sig: list with wrong signature and all params
    Returns:
        tuple[list[list], list[list], list[list]]: data_with_right_sig, data_without_params, 
                                                   data_with_wrong_sig respectively
    """
    
    def _generation_data(secret_key: bytes, 
                         all_params = True, 
                         wrong_sig = False) -> list:
        """Method for generation random data and calculation signature

        Args:
            secret_key (bytes): secret key for (d)encryption
            all_params (bool): If true then send all params in message. Defaults to True.
            wrong_sig (bool): If true then generate wrong signature. Defaults to False.

        Returns:
            list[dict, dict]: params and json respectively
        """
        
        params = {
            'signature': None
        }

        json = {
            "event": None, 
            "character_id": "58483181", 
            "utc_timestap": "2022-01-05T01:26:09"
        }

        # generation random string
        letters = string.ascii_lowercase
        random_str = ''.join(random.choice(letters) for i in range(15))
        json["event"] = random_str
        if not wrong_sig:
            signature = hmac.new(
                secret_key, 
                bytes(str(json), encoding='ascii'), 
                hashlib.sha512).hexdigest()
            
            params['signature'] = signature
        else:
            params['signature'] = random_str
            
        if all_params:
            params.update({'appId': 'casino'})
            params.update({'accountId': '58483181'})
            params.update({'sessionId': 1})
            
        return [params, json]
    
    shared_secret = bytes(SECRET_KEY, encoding='ascii')
    data_with_right_sig = [_generation_data(shared_secret) for _ in range(5)]
    data_without_params = [_generation_data(shared_secret, all_params=False) for _ in range(5)]
    data_with_wrong_sig = [_generation_data(shared_secret, wrong_sig=True) for _ in range(5)]
    
    return data_with_right_sig, data_without_params, data_with_wrong_sig


class MainTestCase(TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.test_data = prepare_data()
    
    def test_data_with_right_sig(self):
        for sample in self.test_data[0]:
            print(sample)
            response = self.client.post("/test", params=sample[0], json=sample[1])
            assert response.status_code == 201
            assert response.json() == sample[1]
    
    def test_data_without_params(self):
        for sample in self.test_data[1]:
            print(sample)
            response = self.client.post("/test", params=sample[0], json=sample[1])
            assert response.status_code == 201
            assert response.json() == sample[1]
    
    def test_data_with_wrong_sig(self):
        for sample in self.test_data[2]:
            print(sample)
            response = self.client.post("/test", params=sample[0], json=sample[1])
            assert response.status_code == 400