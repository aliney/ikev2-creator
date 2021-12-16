from pydantic import BaseSettings


class Config(BaseSettings):
    mikrotik_ip: str = '10.1.50.254'
    auth_user: str = 'Valkyrie'
    auth_password: str = "vAlh@11@"

    ca: str = 'CA.tmn.vpn.carbery.online'
