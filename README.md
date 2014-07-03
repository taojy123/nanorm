Nanorm:Simple ORM framework of Python
=========================================
version 0.1


这是一个精简的Python ORM框架。旨在于用一个文件写出ORM，提供开发小型或微型项目时的一些基本功能。


为什么要使用nanorm？
-------------------
当你的项目足够小，以至于不想与其他的多余库产生依赖关系，但是你又需要使用一些简单的ORM功能（SQLAlchemy对你来说过于庞大），这时你就可以选择Nanorm。它只有一个py文件，直接把它放在你的项目目录下就行，你甚至可以把它嵌入在你的源代码中。


为什么只支持sqlite3？
--------------------
这个ORM的目的只在于解决一些小微项目的需求，sqlite3对于小微项目来说是很好的选择。因为在Python标准库中就有对sqlite3的支持，不需要像使用mysql时那样另外安装mysqldb库。另一方面，你也不用在你的电脑或服务器上安装数据库服务，大多数windows和unix的操作系统都自带了sqlite3的支持。我们的目的就是精简，极简。


如何使用？
---------
直接上示例代码：
```python
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
```
