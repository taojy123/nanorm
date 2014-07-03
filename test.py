from nanorm import *

class Student(Model):
    name = CharField(128)
    age = IntegerField(default=20)
    sex = BooleanField()

    def __str__(self):
        return "%s_%s_%s_%s_%s" % (self.__class__.__name__, self.id, self.name, self.age, self.sex)

s = Student()
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

print "Finish!"