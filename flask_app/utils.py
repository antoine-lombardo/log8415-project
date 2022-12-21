from flask import request


def base_url() -> str:
    return request.scheme + '://' + request.host

def client_ip() -> str:
    client_ip = request.headers.get('cf-connecting-ip')
    if client_ip is None:
        client_ip = request.remote_addr
    return client_ip