from nanorm import *


class Area(Model):
    name = CharField()


class User(Model):
    name = CharField(128)
    age = IntegerField(default=20)
    sex = BooleanField()
    area = ForeignKey(Area)

    def __str__(self):
        return "%s_%s_%s_%s_%s" % (self.__class__.__name__, self.id, self.name, self.age, self.sex)



# ==============================================

set_db_name("nanorm.db")

Area.try_create_table()
User.try_create_table()

Area.query().delete()
User.query().delete()

# ==============================================


mainland = Area(name="mainland").save()
taiwan = Area(name="taiwan").save()

assert len(Area.gets()) == 2

# ==============================================

s1 = User()
s1.name = "Joe"
s1.age = 45
s1.sex = True
s1.area = taiwan
s1.save()

joe = User.get(age=45)

assert joe.name == "Joe"


# ==============================================


s2 = User(name="Motive")
s2.age = 40
s2.area = mainland
s2.save()
s2.area = taiwan
s2.save()

motive = User.query().filter(id=2).all()[0]

assert motive.area.name == "taiwan"


# ==============================================


s3 = User(name="Sandy", sex=False, area=mainland)
s3.save()

sandy = User.query().filter(name="Sandy").first()
sandy.age = 32
sandy.save()

sandy = User.gets(age=32)[0]

assert sandy.sex == False


# ==============================================

s = User.query().order("age").all()

assert s[0].name == "Sandy"

# ==============================================

s = User.query().filter(sex=True).order("-name").all()

assert s[1].name == "Joe"

# ==============================================

s = User.get(age="32", operator="<=")

assert s.name == "Sandy"

# ==============================================

s = User.get(name="J%", operator="like")

assert s.name == "Joe"

# ==============================================

s = User.get(area=mainland)

assert s.name == "Sandy"

# ==============================================

s1 = User.get(name="Sandy")
s2 = User.get(name="Sandy")

assert  s1 == s2

# ==============================================

s1 = User.get(name="Joe")
s2 = User.get(name="Sandy")

assert  s1 != s2

# ==============================================

s1 = User.get(id=1)
s2 = Area.get(id=1)

assert  s1 != s2

# ==============================================







# ==============================================

print User.gets()
print "Success!"
