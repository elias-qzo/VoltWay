from spyne import Application, rpc, ServiceBase, Iterable, Integer, Unicode, ComplexModel, Float
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from dotenv import load_dotenv
import os

class TimeCostType(ComplexModel):
    time = Integer
    cost = Float

class VotlwaySoapService(ServiceBase):
    @rpc(Float, Float, Integer, Integer, _returns=TimeCostType)
    def get_time_cost(ctx, distance, baseTime, loadTime, autonomy):
        PRICE_PER_MIN = 1.50
        autonomy = autonomy * 1000
        nb_charges = distance // autonomy
        total_load_time = (nb_charges * loadTime)
        time = baseTime + total_load_time
        cost = PRICE_PER_MIN * total_load_time
        return TimeCostType(time=int(time), cost=float(cost))

application = Application([VotlwaySoapService], 'voltway.soap',
                          in_protocol=Soap11(validator='lxml'),
                          out_protocol=Soap11())

wsgi_application = WsgiApplication(application)

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    load_dotenv()
    PORT = os.getenv("PORT", 7000)

    print(f'Server running on http://127.0.0.1:{PORT}')

    server = make_server('127.0.0.1', int(PORT), wsgi_application)
    server.serve_forever()