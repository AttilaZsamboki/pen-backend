from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from dotenv import load_dotenv
from os import environ
import html
load_dotenv()

class TestLogin(APITestCase):
    def test_create_account(self):
        url = reverse('unas_login')
        data = f"""<?xml version="1.0" encoding="UTF-8" ?>
        <Params>
            <ApiKey>Az&amp;rh5$kWYZ%KA7xaDUQ</ApiKey>
        </Params>
"""

        response = self.client.post(url, data, format='json')