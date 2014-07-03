import sqlite3


DB_NAME = "test.db"
cx = sqlite3.connect(DB_NAME)



class Field(object):
    field_type = ""
    default = None

    def field_sql(self, field_name):
        return "%s %s" % (field_name, self.field_type)


class CharField(Field):
    def __init__(self, max_length=255, default=""):
        self.field_type = "varchar(%d)" % max_length
        self.default = default
        self.max_length = max_length


class IntegerField(Field):
    def __init__(self, default=0):
        self.field_type = "integer"
        self.default = default


class BooleanField(Field):
    def __init__(self, default=True):
        self.field_type = "boolean"
        self.default = default

        
        
class Model(object):

    def __init__(self, rid=0, **kwargs):
        self.table_name = self.__class__.__name__.lower()
        self.try_create_table()
        self.id = rid
        for name in self.field_names:
            field = getattr(self.__class__, name)
            setattr(self, name, field.default)
        for key, value in kwargs.items():
            setattr(self, key, value)


    def __str__(self):
        return "%s_%d" % (self.__class__.__name__, self.id)


    def __unicode__(self):
        return self.__str__()


    def __repr__(self):
        return self.__str__()


    @property
    def field_names(self):
        field_names = []
        for name in dir(self.__class__):
            var = getattr(self.__class__, name)
            if isinstance(var, Field):
                field_names.append(name)
        return field_names


    @property
    def field_values(self):
        return ["'%s'" % getattr(self, name) for name in self.field_names]



    def try_create_table(self):
        cu = cx.cursor()

        sql = "select * from sqlite_master where type='table' AND name='%s';" % self.table_name
        cu.execute(sql)
        if cu.fetchall():
            return

        sql = "drop table if exists %s;" % self.table_name
        cu.execute(sql)

        fields_sql = "" 
        for name in self.field_names:
            field = self.__class__
            field = getattr(self.__class__, name)
            field_sql = field.field_sql(name)
            fields_sql += ", " + field_sql
        sql = "create table %s ( id integer not null primary key %s );" % (self.table_name, fields_sql)
      
        cu.execute(sql)
        cx.commit()


    def insert(self):
        cu = cx.cursor()

        field_names_sql = ", ".join(self.field_names)
        field_values_sql = ", ".join(self.field_values)

        sql = "insert into %s(%s) values(%s)" % (self.table_name, field_names_sql, field_values_sql)
        cu.execute(sql)
        cx.commit()

        sql = "select id from %s order by id desc;" % self.table_name
        cu.execute(sql)
        self.id = cu.fetchone()[0]


    def update(self):
        cu = cx.cursor()

        name_value = []
        for name, value in zip(self.field_names, self.field_values):
            name_value.append("%s=%s" % (name, value))
        name_value_sql = ", ".join(name_value)

        sql = "update %s set %s where id = %d" % (self.table_name, name_value_sql, self.id)
        cu.execute(sql)
        cx.commit()


    def save(self):
        if self.id:
            self.update()
        else:
            self.insert()
            

    def delete(self):
        cu = cx.cursor()
        sql = "delete from %s where id = %d" % (self.table_name, self.id)
        cu.execute(sql)
        cx.commit()


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
        self.model_class = model_class
        self.table_name = self.model_class.__name__
        self.where_sql = "1=1"
        self.order_sql = ""



    def __str__(self):
        return "%s_%s_%s" % (self.__class__.__name__, self.table_name, self.sql)


    def __unicode__(self):
        return self.__str__()


    def __repr__(self):
        return self.__str__()


    @property
    def field_names(self):
        field_names = []
        for name in dir(self.model_class):
            var = getattr(self.model_class, name)
            if isinstance(var, Field):
                field_names.append(name)
        return field_names


    @property
    def sql(self):
        sql = "select * from %s where %s %s;" % (self.table_name, self.where_sql, self.order_sql)
        return sql


    def filter(self, **kwargs):
        where_sql = self.where_sql
        for name, value in kwargs.items():
            where_sql += " and %s='%s'" % (name, value)
        query = self.__class__(self.model_class)
        query.where_sql = where_sql
        return query


    def order(self, field_name):
        order_sql = field_name.replace("-", "")
        if field_name[0] == "-":
            order_sql += " desc"
        return order_sql


    def all(self):
        cu = cx.cursor()
        cu.execute(self.sql)
        rows = cu.fetchall()
        obs = []
        for r in rows:
            rid = r[0]
            ob = self.model_class(rid=rid)
            for i in range(1, len(r)):
                name = self.field_names[i-1]
                value = r[i]
                setattr(ob, name, value)
            obs.append(ob)
        return obs


    def first(self):
        obs = self.all()
        if obs:
            return obs[0]


    def delete(self):
        cu = cx.cursor()
        sql = "delete from %s where %s" % (self.table_name, self.where_sql)
        cu.execute(sql)
        cx.commit()



def test():

    class Student(Model):
        name = CharField(128)
        age = IntegerField(default=20)
        sex = BooleanField()

        def __str__(self):
            return "%s_%s_%s_%s_%s" % (self.__class__.__name__, self.id, self.name, self.age, self.sex)

    Student.query().delete()

    s1 = Student()
    s1.name = "Joe"
    s1.age = 45
    s1.sex = True
    s1.save()

    s2 = Student(name="Motive")
    s2.age = 40
    s2.save()

    s3 = Student(name="Sandy", sex=False)
    s3.save()


    sandy = Student.query().filter(name="Sandy").first()
    sandy.age = 32
    sandy.save()

    print sandy

    print Student.gets(name="Joe")

    print "ok"



if __name__ == "__main__":
    test()




