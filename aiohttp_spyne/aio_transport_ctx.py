from spyne.server.http import HttpTransportContext


class AioTransportContext(HttpTransportContext):
    def __init__(self, parent, transport, req_env, content_type):
        super(AioTransportContext, self).__init__(parent, transport, req_env, content_type)
        self.req_env = req_env
        self.content_type = content_type

    def get_path(self):
        return self.req_env.path

    def get_path_and_qs(self):
        return self.req_env.path_qs

    def get_cookie(self, key):
        return self.req_env.cookies[key]

    def get_request_method(self):
        return self.req_env.method

    def get_request_content_type(self):
        return self.content_type

