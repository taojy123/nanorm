#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ==================================
# Nanorm - Nano ORM
# ==================================

import sqlite3
import time
import datetime
try:
    import thread
except ImportError as e:
    # Compatible with python3
    import _thread as thread
    unicode = str


__VERSION__ = "1.9.14"

"""
History 

1.9.14:
fix BooleanField

1.9.13:
add default value of datetime -- by yangtianyan

1.9.12:
fix filter for datetime 

1.9.11:
add limit count in query

1.9.10:
add mutex timeout_seconds

1.9.9:
add DateTimeField and DateField

1.9.8:
add SelfForeignKey field

1.9.7:
add thread lock
"""

NANO_SETTINGS = {
    "type": "sqlite3",
    "db_name": "test.db",
    "auto_commit": True,
    "mutex_seconds": 1,
    "timeout_seconds": 10,
}

lock = thread.allocate_lock()


def mutex(func):
    def wrapper(*arg, **kwargs):
        global lock, NANO_SETTINGS
        mutex_seconds = NANO_SETTINGS["mutex_seconds"]
        timeout_seconds = NANO_SETTINGS["timeout_seconds"]
        t = 0
        while not lock.acquire(False):
            print('mutex wait...')
            t += mutex_seconds
            if timeout_seconds and t > timeout_seconds:
                raise IOError('mutex lock timeout!')
            time.sleep(mutex_seconds)
        r = func(*arg, **kwargs)
        lock.release()
        return r

    return wrapper


@mutex
def set_db_name(db_name):
    NANO_SETTINGS["db_name"] = db_name
    NANO_SETTINGS["cx"] = sqlite3.connect(db_name, check_same_thread=False)


@mutex
def get_cursor():
    if not NANO_SETTINGS.get("cx"):
        NANO_SETTINGS["cx"] = sqlite3.connect(NANO_SETTINGS["db_name"], check_same_thread=False)
    cu = NANO_SETTINGS["cx"].cursor()
    return cu


@mutex
def db_commit():
    if NANO_SETTINGS["auto_commit"]:
        NANO_SETTINGS["cx"].commit()


def auto_commit_close():
    NANO_SETTINGS["auto_commit"] = False


def auto_commit_open():
    NANO_SETTINGS["auto_commit"] = True
    db_commit()


@mutex
def execute_sql(cu, sql):
    try:
        cu.execute(sql)
    except Exception as e:
        print('---------- sql failed -----------')
        print(sql)
        print('---------------------------------')
        raise e


class Field(object):
    field_type = ""
    field_level = 0
    default = None

    def field_sql(self, field_name):
        return '"%s" %s null' % (field_name, self.field_type)


class CharField(Field):
    def __init__(self, max_length=255, default=""):
        self.field_type = "varchar(%d)" % max_length
        self.default = default
        self.max_length = max_length


class IntegerField(Field):
    def __init__(self, default=0):
        self.field_type = "integer"
        self.default = default


class FloatField(Field):
    def __init__(self, default=0.0):
        self.field_type = "real"
        self.default = default


class BooleanField(Field):
    def __init__(self, default=True):
        self.field_type = "boolean"
        self.default = default


class DateField(Field):
    def __init__(self, default=None, auto_now_add=False, auto_now=False):
        self.field_type = "date"
        self.default = default
        self.auto_now_add = auto_now_add
        self.auto_now = auto_now


class DateTimeField(Field):
    def __init__(self, default=None, auto_now_add=False, auto_now=False):
        self.field_type = "datetime"
        self.default = default
        self.auto_now_add = auto_now_add
        self.auto_now = auto_now


class ForeignKey(Field):
    def __init__(self, model_class):
        self.field_type = "foreignkey"
        self.field_level = 1
        self.model_class = model_class

    def field_sql(self, field_name):
        foreign_to = self.model_class.__name__.lower()
        return '"%s" integer NULL REFERENCES "%s" ("id")' % (field_name, foreign_to)


class SelfForeignKey(Field):
    def __init__(self):
        self.field_type = "selfforeignkey"
        self.field_level = 1

    def field_sql(self, field_name, model_class):
        foreign_to = model_class.__name__.lower()
        return '"%s" integer NULL REFERENCES "%s" ("id")' % (field_name, foreign_to)


class Model(object):

    def __init__(self, rid=0, **kwargs):
        self.__class__.try_create_table()
        self.table_name = self.__class__.__name__.lower()
        self.id = rid
        for name in self.field_names:
            assert name.lower() not in ('op', 'id', 'key', 'in', 'is', 'like'), 'field name should not be `%s`' % name
            field = getattr(self.__class__, name.replace("`", ""))
            value = field.default
            if isinstance(field, DateTimeField) and field.auto_now_add:
                value = datetime.datetime.now()
            elif isinstance(field, DateField) and field.auto_now_add:
                value = datetime.date.today()
            if callable(value):
                value = value()
            setattr(self, name.replace("`", ""), value)
        for key, value in kwargs.items():
            setattr(self, key.replace("`", ""), value)

    def __str__(self):
        return "%s_%d" % (self.__class__.__name__, self.id)

    def __unicode__(self):
        return self.__str__()

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def field_names(self):
        names = []
        for name in dir(self.__class__):
            var = getattr(self.__class__, name.replace("`", ""))
            if isinstance(var, Field):
                names.append("`%s`" % name)
        return names

    @property
    def field_values(self):
        values = []
        for name in self.field_names:
            name = name.replace("`", "")
            value = getattr(self, name)
            field = getattr(self.__class__, name)

            is_string = True

            if isinstance(value, (str, unicode)):
                value = value.replace("'", "''")
                try:
                    value = value.decode("gbk")
                except Exception as e:
                    pass
                try:
                    value = value.decode("utf8")
                except Exception as e:
                    pass

            if isinstance(value, Model):
                value = value.id
                is_string = False
            
            if isinstance(field, DateTimeField) and field.auto_now:
                value = datetime.datetime.now()
                setattr(self, name.replace("`", ""), value)
            
            if isinstance(field, DateField) and field.auto_now:
                value = datetime.date.today()
                setattr(self, name.replace("`", ""), value)
            
            if isinstance(field, BooleanField):
                value = 'true' if value else 'false'
                is_string = False

            if isinstance(field, (IntegerField,FloatField)):
                is_string = False 

            if field.field_type == 'datetime' and value:
                value = value.strftime('%Y-%m-%d %H:%M:%S.%f')

            if field.field_type == 'date' and value:
                value = value.strftime('%Y-%m-%d')
            
            if field.field_type == 'selfforeignkey' and value:
                assert self.id != value, 'SelfForeignKey can not set the self instance!'

            if is_string:
                values.append("'%s'" % value)
            else:
                values.append(str(value))

        return values

    def insert(self):
        cu = get_cursor()

        field_names_sql = ", ".join(self.field_names)
        field_values_sql = ", ".join(self.field_values)

        sql = "insert into `%s`(%s) values(%s)" % (self.table_name, field_names_sql, field_values_sql)
        execute_sql(cu, sql)
        db_commit()

        sql = "select id from `%s` order by id desc;" % self.table_name
        execute_sql(cu, sql)
        self.id = cu.fetchone()[0]

    def update(self):
        cu = get_cursor()

        name_value = []
        for name, value in zip(self.field_names, self.field_values):
            name_value.append("%s=%s" % (name, value))
        name_value_sql = ", ".join(name_value)

        sql = "update `%s` set %s where id = %d" % (self.table_name, name_value_sql, self.id)
        execute_sql(cu, sql)
        db_commit()

    def save(self):
        if self.id:
            self.update()
        else:
            self.insert()
        return self

    def delete(self):
        cu = get_cursor()
        sql = "delete from `%s` where id = %d" % (self.table_name, self.id)
        execute_sql(cu, sql)
        db_commit()

    def refresh(self):
        assert self.id, 'only saved instance can be refreshed'
        return self.__class__.get(id=self.id)

    @classmethod
    def try_create_table(cls):
        table_name = cls.__name__.lower()

        cu = get_cursor()
        sql = "select * from sqlite_master where type='table' AND name='%s';" % table_name
        execute_sql(cu, sql)
        if not cu.fetchall():
            sql = "drop table if exists `%s`;" % table_name
            execute_sql(cu, sql)

            fields_sql = ""
            for name in dir(cls):
                var = getattr(cls, name.replace("`", ""))
                if isinstance(var, Field):
                    field = var
                    if isinstance(field, SelfForeignKey):
                        field_sql = field.field_sql(name, cls)
                    else:
                        field_sql = field.field_sql(name)
                    fields_sql += ", " + field_sql
            sql = 'create table `%s` ( "id" integer not null primary key autoincrement %s );' % (table_name, fields_sql)
            execute_sql(cu, sql)

            db_commit()

    @classmethod
    def query(cls):
        query = Query(cls)
        return query

    @classmethod
    def gets(cls, **kwargs):
        query = Query(cls)
        return query.filter(**kwargs).all()

    @classmethod
    def get(cls, **kwargs):
        query = Query(cls)
        return query.filter(**kwargs).first()


class Query(object):

    def __init__(self, model_class, where_sql='1=1', order_sql='', limit_sql=''):
        model_class.try_create_table()
        self.model_class = model_class
        self.table_name = self.model_class.__name__
        self.where_sql = where_sql
        self.order_sql = order_sql
        self.limit_sql = limit_sql

    def __str__(self):
        return "%s_%s_%s" % (self.__class__.__name__, self.table_name, self.query_sql)

    def __unicode__(self):
        return self.__str__()

    def __repr__(self):
        return self.__str__()

    @property
    def field_names(self):
        names = []
        for name in dir(self.model_class):
            var = getattr(self.model_class, name.replace("`", ""))
            if isinstance(var, Field):
                names.append("`%s`" % name)
        return names

    @property
    def query_sql(self):
        sql = "select * from `%s` where %s %s %s;" % (self.table_name, self.where_sql, self.order_sql, self.limit_sql)
        return sql

    def filter(self, op="=", **kwargs):
        where_sql = self.where_sql
        for name, value in kwargs.items():
            if "`%s`" % name in self.field_names + ["`id`"]:
                is_string = True

                if isinstance(value, Model):
                    value = value.id
                    is_string = False

                if isinstance(value, (int, float)):
                    is_string = False

                if isinstance(value, bool):
                    value = 'true' if value else 'false'
                    is_string = False
                
                if isinstance(value, datetime.datetime):
                    value = value.strftime('%Y-%m-%d %H:%M:%S.%f')
                
                if isinstance(value, (str, unicode)):
                    value = value.replace("'", "''")
                    try:
                        value = value.decode("gbk")
                    except Exception as e:
                        pass
                    try:
                        value = value.decode("utf8")
                    except Exception as e:
                        pass

                if is_string:
                    where_sql += " and `%s` %s '%s'" % (name, op, value)
                else:
                    where_sql += " and `%s` %s %s" % (name, op, value)

        query = self.__class__(self.model_class, where_sql, self.order_sql, self.limit_sql)
        return query

    def order(self, field_name):
        order_sql = "order by " + field_name.replace("-", "")
        if field_name[0] == "-":
            order_sql += " desc"
        query = self.__class__(self.model_class, self.where_sql, order_sql, self.limit_sql)
        return query

    def order_by(self, field_name):
        return self.order(field_name)

    def limit(self, count=1):
        limit_sql = 'limit %d' % count
        query = self.__class__(self.model_class, self.where_sql, self.order_sql, limit_sql)
        return query

    def _r2ob(self, r):
        # 数据库查得的一行记录转为 Model 对象
        rid = r[0]
        ob = self.model_class(rid=rid)
        for i in range(1, len(r)):
            name = self.field_names[i - 1]
            field = getattr(self.model_class, name.replace("`", ""))

            if field.field_level == 0:
                value = r[i]
                value = None if value == 'None' else value

                if field.field_type == "boolean":
                    if value in ['True', 'False']:
                        # 兼容老版本
                        value = eval(value)
                    else:
                        value = bool(value == 1)

                if field.field_type == "datetime" and value:
                    value = datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S.%f') if value else None
                
                if field.field_type == "date" and value:
                    value = datetime.datetime.strptime(value, '%Y-%m-%d').date() if value else None

            elif field.field_level == 1:
                if field.field_type == "selfforeignkey":
                    field.model_class = self.model_class
                fid = r[i]
                if fid:
                    value = field.model_class.get(id=fid)
                else:
                    value = None

            setattr(ob, name.replace("`", ""), value)
        return ob

    def all(self):
        cu = get_cursor()
        sql = self.query_sql
        execute_sql(cu, sql)
        rows = cu.fetchall()
        obs = []
        for r in rows:
            ob = self._r2ob(r)
            obs.append(ob)
        return obs

    def first(self):
        cu = get_cursor()
        sql = self.limit(1).query_sql
        execute_sql(cu, sql)
        rows = cu.fetchall()
        if rows:
            r = rows[0]
            ob = self._r2ob(r)
            return ob
        else:
            return None

    def last(self):
        cu = get_cursor()
        sql = self.query_sql
        execute_sql(cu, sql)
        rows = cu.fetchall()
        if rows:
            r = rows[-1]
            ob = self._r2ob(r)
            return ob
        else:
            return None

    def delete(self):
        cu = get_cursor()
        sql = "delete from `%s` where %s" % (self.table_name, self.where_sql)
        execute_sql(cu, sql)
        db_commit()

# THE END
