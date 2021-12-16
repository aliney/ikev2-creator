import routeros_api
import pprint

from routeros_api.resource import RouterOsResource

from config import Config

config = Config()

connection = routeros_api.RouterOsApiPool(host=config.mikrotik_ip, username=config.auth_user,
                                          password=config.auth_password,
                                          plaintext_login=True)
api = connection.get_api()

certificate_template = {
    'name': '',
    'common-name': '',
    'country': 'RU',
    'state': "Tyumen Oblast",
    'locality': 'Tyumen',
    'organization': 'Carbery',
    'subject-alt-name': "",
    'key-size': '2048',
    'days-valid': '1825',
    'key-usage': 'tls-client'
}

certificate_identity = {
    'auth-method': 'digital-signature',
    'certificate': 'vpn.ike2.xyz',
    'remote-certificate': 'alex@nsc.ru',
    'generate-policy': 'port-strict',
    'match-by': 'certificate',
    'mode-config': "modeconfvpn.ike2.xyz",
    'peer': "peer 123.45.67.8",
    'policy-template-group': "group vpn.ike2.xyz",
    'remote-id': 'user-fqdn:alex@nsc.ru'
}

user_list = [['EmelanovaA', '89080088424']]

certificates = api.get_resource('/certificate')  # type: RouterOsResource
identities = api.get_resource('/ip/ipsec/identity')


class Certificate(object):

    def __init__(self, name: str, password: str):
        self.name = name.lower()
        self.common_name = f"{self.name}@tmn.vpn.carbery.online"
        self.status = certificates.get(name=self.common_name)
        self.config = certificate_template
        self.config['name'] = self.common_name
        self.config['common-name'] = self.common_name
        self.config['subject-alt-name'] = f"email:{self.common_name}"
        self.issued = None

    def if_exist(self):
        if not self.status:
            return False
        else:
            return True

    def create(self):
        if self.if_exist():
            print(f"Certificate {self.common_name} exist")
        else:
            certificates.add(**self.config)
            self.status = certificates.get(name=self.common_name)
            print(f"Certificate {self.common_name} created")
        self.issued = self.status[0].get('issued')

    def signed(self):
        if self.issued:
            return True
        else:
            return False

    def sign(self):
        if self.signed():
            print('Certificate issued')
        else:
            result = certificates.call('sign', {'.id': self.common_name, 'ca': config.ca})
            pprint.pprint(result)

    def export(self):
        if self.signed():
            result = certificates.call('export-certificate',
                                       {'.id': self.common_name,
                                        'type': 'pkcs12',
                                        'export-passphrase': 'keepinsecret'})
            print(result)
        else:
            print('Not signed certificate')


class Identity(object):
    def show(self):
        result = identities.get()
        pprint.pprint(result)


if __name__ == '__main__':
    # identity = Identity()
    # identity.show()

    for user in user_list:
        cerificate = Certificate(user[0], user[1])
        cerificate.create()
        cerificate.sign()
        cerificate.export()
