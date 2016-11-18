# coding=utf-8
import six
from yuntool.db.error import *
from yuntool.db.field import (
    Prikey, Field)
from yuntool.db.handler import DbHandler
from yuntool.db.sql import QuerySet


class MetaModel(type):
    db_table = None
    fields = {}
    db_config = {}

    def __init__(cls, name, bases, attrs):
        super(MetaModel, cls).__init__(name, bases, attrs)
        fields = {}
        pri_field = 'id'
        fields['id'] = Prikey()
        for key, val in cls.__dict__.items():
            if isinstance(val, Prikey):
                fields.pop(pri_field)
                fields[key] = val
                pri_field = key

            elif isinstance(val, Field):
                fields[key] = val
            else:
                pass
        cls.fields = fields
        cls.pri_field = pri_field
        cls.attrs = attrs
        cls.objects = cls()
        if 'meta' in dir(cls):
            cls.db_table = cls.meta.db_table
            cls.db_config = cls.meta.db_config
            DbHandler.connect(**cls.db_config)


@six.add_metaclass(MetaModel)
class Model(object):

    @classmethod
    def create(self, **kwargs):
        '''
        function:
            create one or more data
        params:
            dict
        '''
        for key, val in kwargs.items():
            if val is None or key not in self.fields:
                raise Exception(NORIGHTERROR.format(key))
        for key, val in self.fields.items():
            if isinstance(val, Field):
                if key not in kwargs:
                    if val.default:
                        kwargs[key] = val.default
                    else:
                        raise Exception(FEILDNULLRROR.format(key))
        sql = 'insert ignore into {0}({1}) values ("{2}");'.format(
            self.db_table, ', '.join(kwargs.keys()),
            '","'.join([
                str(kwargs[key]).replace('"', '\'') for key in kwargs.keys()]))
        result = DbHandler.execute(sql)
        if not result._info:
            setattr(result, 'success', True)
        return result

    def update(self, **kwargs):
        '''
        function:
            update data
        params:
            dict
        '''
        for key, val in kwargs.items():
            if val is None or key not in self.fields:
                raise Exception(NORIGHTERROR.format(key))
        where = 'where {0} = {1}'.format(
            self.pri_field, self.__dict__[self.pri_field])
        sql = 'update {0} set {1} {2};'.format(self.db_table, ','.join(
            [key + ' = "{0}"'.format(str(
                kwargs[key]).replace('"', '\'')) for key in kwargs.keys()]),
            where)
        return DbHandler.execute(sql)

    def delete(self, **kwargs):
        for key, val in kwargs.items():
            if val is None or key not in self.fields:
                raise Exception(NORIGHTERROR.format(key))
        where = 'where {0} = {1}'.format(
            self.pri_field, self.__dict__[self.pri_field])
        sql = 'delete from {0} {1};'.format(self.db_table, where)
        try:
            result = DbHandler.execute(sql)
            if not result._info:
                setattr(result, 'success', True)
        except:
            result = object()
            setattr(result, 'success', True)
        return result

    def filter(self, **kwargs):
        '''
        function:
            add filter conditions
        '''
        return QuerySet(self, kwargs)


def execute_raw_sql(sql, params=None):
    return DbHandler.execute(sql, params) if params else DbHandler.execute(sql)
