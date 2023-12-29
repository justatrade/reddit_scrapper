from decouple import config

SERVER_ADDRESS = '127.0.0.1'
SERVER_PORT = 8080
REDIRECT_URL = 'http://' + SERVER_ADDRESS+':' + str(SERVER_PORT)+'/reddit_app'
TIME_DEPTH_DAYS = 1

client_id = config('client_id')
client_secret = config('client_secret')
user_agent = config('user_agent')
redirect_uri = config('redirect_uri')
refresh_token = config('refresh_token')
