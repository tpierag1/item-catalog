from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base, User, Category, Item
import time

engine = create_engine('sqlite:///catalog.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()

print "[*]Deleting old databases..."
session.query(Category).delete()
session.query(Item).delete()
session.query(User).delete()

print '\n'
print '[*] Creating Database...'
print 'Stand By...'
time.sleep(.5)

user1 = User(name='Whatever Whatever',
             email='test@test.com',
             picture='https://images.google.com/something')
session.add(user1)
session.commit()

user2 = User(name='Me',
             email='tpierag1@gmail.com',
             picture='http://i0.kym-cdn.com/entries/icons/original/000/021/807/4d7.png')

#Add categories
meat = Category(id=1, name='Meat')
session.add(meat)
session.commit()

veggies = Category(id=2, name='Veggies')
session.add(veggies)
session.commit()

fruit = Category(id=3, name='Fruit')
session.add(fruit)
session.commit()

grains = Category(id=4, name='Grains')
session.add(grains)
session.commit()

other = Category(id=5, name='Other')
session.add(other)
session.commit()

#add items
#meat
steak = Item(name='Steak',
             description='Tasty Meaty Treats',
             price='7.99',
             category_id=1,
             user_id=1)
session.add(steak)
session.commit()

chicken = Item(name='Chicken',
               description='Everything tastes like it',
               price='5.99',
               category_id=1,
               user_id=1)
session.add(chicken)
session.commit()

pork = Item(name='Pork',
            description='The other white meat',
            price='6.99',
            category_id=1,
            user_id=1)
session.add(pork)
session.commit()
#veggies
carrots = Item(name='Carrots',
               description='Good for your eyes',
               price='2.99',
               category_id=2,
               user_id=1)
session.add(carrots)
session.commit()

asparagus = Item(name='Asparagus',
                 description='Super good for you',
                 price='3.99',
                 category_id=2,
                 user_id=1)
session.add(asparagus)
session.commit()

kale = Item(name='Kale',
            description='Green Super Food!',
            price='3.99',
            category_id=2,
            user_id=1)
session.add(kale)
session.commit()
#fruit
apple = Item(name='Apple',
             description='Sweet and crunchy',
             price='0.99',
             category_id=3,
             user_id=1)
session.add(apple)
session.commit()

banana = Item(name='Banana',
              description='Gooey and Awesome',
              price='0.50',
              category_id=3,
              user_id=1)
session.add(banana)
session.commit()

cherry = Item(name='Cherry',
              description='Watch for the pit',
              price='3.99',
              category_id=3,
              user_id=1)
session.add(cherry)
session.commit()
#grains
oats = Item(name='Oats',
            description='Great in the morning',
            price='1.99',
            category_id=4,
            user_id=1)
session.add(oats)
session.commit()

quinoa = Item(name='Quinoa',
              description='Tasty and good for you',
              price='4.99',
              category_id=4,
              user_id=1)
session.add(quinoa)
session.commit()

rice = Item(name='Rice',
            description='Most Common Grain',
            price='1.99',
            category_id=4,
            user_id=1)
session.add(rice)
session.commit()
#other
olive_oil = Item(name='Olive Oil',
                 description='Heart-healthy',
                 price='7.99',
                 category_id=5,
                 user_id=1)
session.add(olive_oil)
session.commit()

ketchup = Item(name='Ketchup',
               description='Not Catsup',
               price='2.99',
               category_id=5,
               user_id=1)
session.add(ketchup)
session.commit()

soy_sauce = Item(name='Soy Sauce',
                 description='Salty and Awesome',
                 price='6.99',
                 category_id=5,
                 user_id=1)
session.add(soy_sauce)
session.commit()

print '\n'
print "[*]Database Test Data Created!"
