from base64 import b64decode


class API:

    def __init__(self, config_vars=None, config_vars_prefix='', password='',
                 production=None, regions=None, requires=None, sso_salt='',
                 test=None, version=1):
        self.config_vars = [] if config_vars is None else list(config_vars)
        self.config_vars_prefix = config_vars_prefix
        self.password = password
        self.production = Production() if production is None else production
        self.regions = [] if regions is None else list(regions)
        self.requires = [] if requires is None else list(requires)
        self.sso_salt = sso_salt
        self.test = Test() if test is None else test
        self.version = version

    @classmethod
    def decode(cls, schema):
        production = schema.pop('production', {})
        test = schema.pop('test', {})
        return cls(production=Production(production), test=Test(test), **schema)


class Manifest:

    def __init__(self, api=None, cli_plugin_name='', id='', name=''):
        self.api = API() if None else api
        self.cli_plugin_name = cli_plugin_name
        self.id = id
        self.name = name

    def accept(self, visitor):
        visitor.visit_manifest(self)

    @classmethod
    def decode(cls, schema):
        api = schema.pop('api', {})
        return cls(api=API.decode(api), **schema)

    def validate(self, encoded):
        decoded = b64decode(encoded).decode('UTF-8')
        identifier, password = decoded.split(':')
        return identifier == self.id and password == self.api.password


class Production:

    def __init__(self, base_url='', sso_url=''):
        self.base_url = base_url
        self.sso_url = sso_url


class Test:

    def __init__(self, base_url='', sso_url=''):
        self.base_url = base_url
        self.sso_url = sso_url
