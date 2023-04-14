from config.sqlalchemy.connection_handler import ConnectionHandler
from repository.mappers.tta036_j_cod_prov_cotacao_mes import Tta036JCodProvCotacaoMes
from sqlalchemy import text

class Repository:
    
    def sequence_value(self, sequence):
        with ConnectionHandler() as db:
            result = db.session.execute(text(f'SELECT {sequence}.nextval from dual'))
            if result is None: return None
            for res in result:
                return res[0]

    def get(self, mapper, filter=None):
        with ConnectionHandler() as db:
            data = db.session.query(mapper)
            if filter:
                return data.where(*filter).one_or_none()
            return data.one_or_none()
        
    def insert(self, object):
        with ConnectionHandler() as db:
            try:
                db.session.merge(object)
                db.session.commit()
            except Exception as e:
                print('teste', str(e))
                db.session.rollback()
                raise Exception(e)
            
    def update(self, object):
        with ConnectionHandler() as db:
            try:
                db.session.merge(object)
                db.session.commit()
            except Exception as e:
                print('teste', str(e))
                db.session.rollback()
                raise Exception(e)

    def filter(self, mapper, filter=None, order_by=None):
        with ConnectionHandler() as db:
            data = db.session.query(mapper)
            if not order_by is None:
                if len(order_by) == 1: data = data.order_by(order_by[0]) 
                else: data = data.order_by(*order_by)
            if not filter is None:
                return data.filter(*filter).all()
            return data.all()
        