from nanorm import *


class Area(Model):
    name = CharField()


class Employee(Model):
    name = CharField(128)
    age = IntegerField(default=20)
    sex = BooleanField()
    area = ForeignKey(Area)

    def __str__(self):
        return "%s_%s_%s_%s_%s" % (self.__class__.__name__, self.id, self.name, self.age, self.sex)



# ==============================================

set_db_name("nanorm.db")

Area.try_create_table()
Employee.try_create_table()

Area.query().delete()
Employee.query().delete()

# ==============================================


mainland = Area(name="mainland").save()
taiwan = Area(name="taiwan").save()

assert len(Area.gets()) == 2

# ==============================================

s1 = Employee()
s1.name = "Joe"
s1.age = 45
s1.sex = True
s1.area = taiwan
s1.save()

joe = Employee.get(age=45)

assert joe.name == "Joe"


# ==============================================


s2 = Employee(name="Motive")
s2.age = 40
s2.area = mainland
s2.save()
s2.area = taiwan
s2.save()

motive = Employee.query().filter(id=2).all()[0]

assert motive.area.name == "taiwan"


# ==============================================


s3 = Employee(name="Sandy", sex=False, area=mainland)
s3.save()

sandy = Employee.query().filter(name="Sandy").first()
sandy.age = 32
sandy.save()

sandy = Employee.gets(age=32)[0]

assert sandy.sex == False


# ==============================================

s = Employee.query().order("age").all()

assert s[0].name == "Sandy"

# ==============================================

s = Employee.query().filter(sex=True).order("-name").all()

assert s[1].name == "Joe"

# ==============================================

s = Employee.get(age="32", operator="<=")

assert s.name == "Sandy"

# ==============================================

s = Employee.get(name="J%", operator="like")

assert s.name == "Joe"

# ==============================================

s = Employee.get(area=mainland)

assert s.name == "Sandy"

# ==============================================







# ==============================================

print Employee.gets()
print "Success!"
