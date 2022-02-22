from flask_tools import flaskappdecorator
from flask import Flask
from threading import Thread


class RenameFunction(object):
    def __init__(self, func, funcname):
        self.funcname = funcname
        self.func = func

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    @property
    def __name__(self):
        return self.funcname


class StartServer(object):
    def __init__(self, ports=None, portstart=None, portend=None, tag='test', funcnames=None):
        """
        :param ports: if not None, the range of ports will be aligned.
        :param portstart, portend: if ports is None, ports will be range(portstart, portend)
        :param tag: ‘test' by default.
        :param funcnames: None: the funcnames of each port will be "f_portstart", ..., "f_portend".
                                    in type str: the funcnames of each port will be the same as funcnames.
                                    in list str: the funcnames of each port will be every item in funcnames.
        """
        if ports is None:
            if portstart is None or portend is None:
                raise ValueError(f"invalid input ports {ports}")
            else:
                ports = range(int(portstart), int(portend))
        self.ports = ports
        self.tag = tag
        if funcnames is None:
            self.Server = type('Server', (object,), {f"f{k}": RenameFunction(lambda x, k=k: f"p_{k}", f"f{k}") for k in ports})
        elif isinstance(funcnames, str):
            self.Server = type('Server', (object,), {f"f{k}": RenameFunction(lambda x, k=k: f"p_{k}", funcnames) for k in ports})
        else:
            funcnames = list(funcnames) + [str(p) for p in ports[len(funcnames):]]
            self.Server = type('Server', (object,), {f"f{k}": RenameFunction(lambda x, k=k: f"p_{k}", f"f{funcname}") for k, funcname in zip(ports, funcnames)})

    def start(self):
        for port in self.ports:
            class ServerThread(Thread):
                def __init__(this, port_):
                    super(ServerThread, this).__init__()
                    this.port = port_

                def run(this):
                    flaskappdecorator.app = Flask(f"{__name__}{this.port}")
                    flaskappdecorator.auto_route_func_list([getattr(self.Server(), f"f{this.port}")], tag=self.tag)
                    flaskappdecorator.run(host="0.0.0.0", port=this.port)

            ServerThread(port_=port).start()


def start_on_same_port(funcnum=5, port=8000, tag='test'):
    Server = type('Server', (object,), {f"f{k}": RenameFunction(lambda x, k=k: f"port{k}", f"f{k}") for k in range(funcnum)})
    flaskappdecorator.auto_route_class(Server(), tag=tag)
    flaskappdecorator.run(host='0.0.0.0', port=port)


if __name__ == '__main__':
    StartServer(ports=[8001, 8002, 8003], funcnames='sameport').start()