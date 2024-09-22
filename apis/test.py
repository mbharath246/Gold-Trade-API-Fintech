# import requests

# url = 'https://api.metalpriceapi.com/v1/latest'

# json = {
#     'api_key':'fd4e20f161566a39fc8ce1ac15c8372d',
#     'base':'USD',
#     'currencies':'XAU'
# }

# res = requests.get(url, params=json)
# data = res.json()
# print(data)


toknn = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzI3MDI4OTQ1LCJpYXQiOjE3MjY5NDI1NDUsImp0aSI6IjQ1MjJkMGRiYjY5YzRkM2M4MWE4ZjE4N2U1ZmY4YTY0IiwidXNlcl9pZCI6IjE0Y2UwNTU0LWUwZGYtNDk5MS1iYjQ3LWI0MzAyNDU4YzNjNyIsIm5hbWUiOiJiaGFyYXRoIiwiZW1haWwiOiJiaGFyYXRoQGdtYWlsLmNvbSJ9.Dd2BucJNnM-GjZiyxsZ8FkC-DY_JkTIrERxkQTvFSYg'


import redis
import redis.exceptions
try:
    redis_client = redis.Redis(host='localhost', port=6379, db=1)
    print(redis_client.ping())
except redis.exceptions.ConnectionError as e:
    print(e)