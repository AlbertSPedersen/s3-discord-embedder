from flask import Flask, request, redirect, jsonify, abort
from pathlib import Path
import requests
import json


app = Flask(__name__)
app.url_map.strict_slashes = False
with open(str(Path(__file__).parent) + '/config.json', 'r') as file:
    config = json.load(file)


def size_string(size):
    if size < 1024:
        return str(size) + 'B'
    elif size < 1048576:
        return str(round(size / 1024, 2)) + 'KiB'
    elif size < 1073741824:
        return str(round(size / 1048576, 2)) + 'MiB'
    else:
        return str(round(size / 1073741824, 2)) + 'GiB'


@app.route('/<path:object_path>')
def index(object_path):
    response = requests.head(config['s3_endpoint'] + object_path)
    if response.status_code != 403:
        if request.headers.get('user-agent') == 'Mozilla/5.0 (compatible; Discordbot/2.0; +https://discordapp.com)':
            return f'''<!DOCTYPE html>
            <html>
                <head>
                    <meta name="theme-color" content="#00FF00">
                    <meta property="og:title" content="{object_path.split('/')[-1]}">
                    <meta content="{config['s3_endpoint'] + object_path}" property="og:image">
                    <meta name="twitter:card" content="summary_large_image">
                    <link type="application/json+oembed" href="https://cdn.asp.gg/oembed/{object_path}" />
                    <meta content="```py
                        def test():
                            print('hello')
                    ```" property="og:description">
                </head>
            </html>'''
        else:
            return redirect(config['s3_endpoint'] + object_path)
    else:
        abort(404)


@app.route('/oembed/<path:object_path>')
def oembed(object_path):
    response = requests.head(config['s3_endpoint'] + object_path)
    if response.status_code != 403:
        if request.headers.get('user-agent') == 'Mozilla/5.0 (compatible; Discordbot/2.0; +https://discordapp.com)':
            return jsonify(
                {
                    'author_name': size_string(int(response.headers.get('content-length'))) + ' | ' + response.headers.get('content-type'),
                    'provider_name': response.headers.get('last-modified')
                }
            )
        else:
            return redirect(config['s3_endpoint'] + object_path)
    else:
        abort(404)


if __name__ == '__main__':
    app.run(host=config['bind_address'], port=config['bind_port'])
