#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ==================================
# Nanorm 1.8.5
# ==================================

import sqlite3
import time

__VERSION__ = "1.8.5"

"""
Modify:
1. add execute_sql function
"""


NANO_SETTINGS = {
    "type" : "sqlite3",
    "db_name" : "test.db",
    "auto_commit" : True,
}


def set_db_name(db_name):
    NANO_SETTINGS["db_name"] = db_name
    NANO_SETTINGS["cx"] = sqlite3.connect(db_name, check_same_thread=False)


def get_cursor():
    if not NANO_SETTINGS.get("cx"):
        NANO_SETTINGS["cx"] = sqlite3.connect(NANO_SETTINGS["db_name"], check_same_thread=False)
    cu = NANO_SETTINGS["cx"].cursor()
    return cu


def db_commit():
    if NANO_SETTINGS["auto_commit"]:
        NANO_SETTINGS["cx"].commit()

def auto_commit_close():
    NANO_SETTINGS["auto_commit"] = False


def auto_commit_open():
    NANO_SETTINGS["auto_commit"] = True
    db_commit()


def execute_sql(cu, sql):
    try:
        cu.execute(sql)
    except Exception, e:
        print('---------- sql failed -----------')
        print(sql)
        print('---------------------------------')
        raise e


class Field(object):
    field_type = ""
    field_level = 0
    default = ""

    def field_sql(self, field_name):
        return '"%s" %s' % (field_name, self.field_type)


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


class ForeignKey(Field):
    def __init__(self, model_class):
        self.field_type = "foreignkey"
        self.field_level = 1
        self.model_class = model_class

    def field_sql(self, field_name):
        return '"%s" integer REFERENCES "%s" ("id")' % (field_name, self.model_class.__name__.lower())
        


        
class Model(object):

    def __init__(self, rid=0, **kwargs):
        self.__class__.try_create_table()
        self.table_name = self.__class__.__name__.lower()
        self.id = rid
        for name in self.field_names:
            field = getattr(self.__class__, name.replace("`", ""))
            setattr(self, name.replace("`", ""), field.default)
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
                names.append("`%s`"%name)
        return names


    @property
    def field_values(self):
        values = []
        for name in self.field_names:
            value = getattr(self, name.replace("`", ""))
            if isinstance(value, Model):
                value = value.id
            if isinstance(value, str) or isinstance(value, unicode):
                value = value.replace("'", "''")
                try:
                    value = value.decode("gbk")
                except Exception, e:
                    pass
                try:
                    value = value.decode("utf8")
                except Exception, e:
                    pass
            values.append("'%s'" % value)
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
                    field_sql = field.field_sql(name)
                    fields_sql += ", " + field_sql
            sql = 'create table `%s` ( "id" integer not null primary key %s );' % (table_name, fields_sql)
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

    def __init__(self, model_class):
        model_class.try_create_table()
        self.model_class = model_class
        self.table_name = self.model_class.__name__
        self.where_sql = "1=1"
        self.order_sql = ""



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
                names.append("`%s`"%name)
        return names


    @property
    def query_sql(self):
        sql = "select * from `%s` where %s %s;" % (self.table_name, self.where_sql, self.order_sql)
        return sql


    def filter(self, operator="=", **kwargs):
        where_sql = self.where_sql
        for name, value in kwargs.items():
            if "`%s`"%name in self.field_names + ["`id`"]:
                if isinstance(value, Model):
                    value = value.id
                if isinstance(value, str) or isinstance(value, unicode):
                    value = value.replace("'", "''")
                    try:
                        value = value.decode("gbk")
                    except Exception, e:
                        pass
                    try:
                        value = value.decode("utf8")
                    except Exception, e:
                        pass
                where_sql += " and `%s` %s '%s'" % (name, operator, value)
        query = self.__class__(self.model_class)
        query.order_sql = self.order_sql
        query.where_sql = where_sql
        return query


    def order(self, field_name):
        order_sql = "order by " + field_name.replace("-", "")
        if field_name[0] == "-":
            order_sql += " desc"
        query = self.__class__(self.model_class)
        query.where_sql = self.where_sql
        query.order_sql = order_sql
        return query


    def _r2ob(self, r):
        rid = r[0]
        ob = self.model_class(rid=rid)
        for i in range(1, len(r)):
            name = self.field_names[i-1]
            field = getattr(self.model_class, name.replace("`", ""))
            if field.field_level == 0:
                if field.field_type == "boolean":
                    value = eval(r[i])
                    try:
                        value = bool(value)
                    except Exception as e:
                        pass
                else:
                    value = r[i]
            elif field.field_level ==1:
                if field.field_type == "foreignkey":
                    fid = r[i]
                    value = field.model_class.get(id=fid)
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
        sql = self.query_sql
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
