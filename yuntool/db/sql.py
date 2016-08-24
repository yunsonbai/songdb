# coding=utf-8
from yuntool.db.handler import DbHandler


class QuerySet(object):

    operator = {
        'lt': '<',
        'gt': '>',
        'une': '!=',
        'lte': '<=',
        'gte': '>=',
        'eq': '=',
        'in': ' in ',
    }

    def __init__(self, model, kwargs):
        self.first_line = False
        self.model = model
        self.params = kwargs.values()
        equations = []
        i = 0
        for key in kwargs.keys():
            key_spl = key.split('__')
            try:
                equations.append(
                    key_spl[-2] + self.operator[key_spl[-1]] + '%s')
            except:
                equations.append(key_spl[-1] + '=%s')
            i += 1
        self.where_expr = 'where ' + ' and '.join(
            equations) if len(equations) > 0 else ''

    def _make_sql(self):
        if self.model.fields.keys():
            sql = 'select {0} from {1} {2};'.format(
                ', '.join(self.model.fields.keys()),
                self.model.db_table, self.where_expr)
        else:
            sql = 'select * from {0} {1};'.format(
                self.model.db_table, self.where_expr)
        return sql

    def _datas(self, sql):
        try:
            for row in DbHandler.execute(sql, self.params).fetchall():
                inst = self.model
                for idx, f in enumerate(row):
                    setattr(inst, list(self.model.fields.keys())[idx], f)
                yield inst
        except Exception as e:
            raise e

    def order_by(self, *rows):
        self.where_expr += ' order by {0}'.format('{0}'.format(','.join(rows)))
        return self

    def desc_order_by(self, *rows):
        self.where_expr += ' order by {0} desc'.format(
            '{0}'.format(','.join(rows)))
        return self

    def group_by(self, *rows):
        self.where_expr += ' group by {0}'.format('{0}'.format(','.join(rows)))
        return self

    def limit(self, *rows):
        '''
        function:
            limit the result number
        parameter:
            *rows:
                1
                1, 2
        return:
            object QuerySet

        '''
        if len(rows) == 1:
            self.where_expr = self.where_expr + ' limit {0}'.format(rows)
        elif len(rows) == 2:
            self.where_expr = self.where_expr + \
                ' limit {0},{1}'.format(rows[0], rows[1])
        return self

    def first(self):
        '''
        function:
            get the first result
        return:
            object QuerySet
        '''
        self.first_line = True
        return self

    def all(self, sql=None):
        '''
        function:
            get the all result
        return:
            object QuerySet
        '''
        return self

    def data(self):
        '''
        function:
            get the result
        return:
            if one result:
                return orm
            if more result:
                return generator
        '''
        sql = self._make_sql()
        try:
            if self.first_line:
                row = DbHandler.execute(sql, self.params).fetchone()
                inst = self.model
                for idx, f in enumerate(row):
                    setattr(inst, self.model.fields.keys()[idx], f)
                return inst
            else:
                return self._datas(sql)
        except Exception as e:
            raise e

    def count(self):
        '''
        function:
            get the result num
        return:
            int num
        '''
        sql = 'select count(*) from {0} {1};'.format(self.model.db_table,
                                                     self.where_expr)
        (row_cnt, ) = DbHandler.execute(sql, self.params).fetchone()
        return row_cnt