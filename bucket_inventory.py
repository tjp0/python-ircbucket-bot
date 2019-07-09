#from  bucket_core import listen_command
#import bucket_core
#import bucket_sql
from . import bucket_core
from . import bucket_sql
from . import bucket_factoid
import random
items = []
MAX_ITEMS=20

class Item(bucket_sql.Base):
    from sqlalchemy import Column, Integer, String, Boolean,Text,Sequence, Enum
    __tablename__ = 'bucket_items'
    id = Column(Integer,Sequence('user_id_seq'),primary_key=True,nullable=False)
    item = Column(String(64),nullable=False)
    def __repr__(self):
        return("id: %s, item: %s" % (self.id,self.item))

@bucket_core.listen_command("(puts|throws|gives) (?P<item>.+) (into|in|to) (the )?$bucket")
def add_item(bot, trigger, match):
    item = match.group('item')
    print("Adding item: %s" % (item))
    session = bucket_sql.Session()
    _check_items()
    items.append(item)
    itemRecord = session.query(Item).filter(Item.item == item).first()
    if(not itemRecord):
        session.add(Item(item=item))

    session.commit()
    bot.action("now contains %s." % (item))

@bucket_core.bucket_command("Inventory")
def query_inventory(bot, trigger, match):
    if(len(items) == 0):
        bot.action("contains nothing")
    else:
        string = ' '.join(items)
        bot.action("contains %s" % (string))

def _check_items():
    if(len(items) == MAX_ITEMS):
        discard_item = take_item()
        bot.action("tosses away %s" % (discard_item))

def take_item():
    if(len(items) > 0):
        item = random.choice(items)
        items.remove(item)
        return item
    else:
        return "nothing"

def get_item():
    return random.choice(items)

def add_random_item():
    session = bucket_sql.Session()
    itemRecords = session.query(Item).all()
    item = random.choice(itemRecords).item
    _check_items()
    items.append(item)
    return item

@bucket_factoid.factoid_sub(priority=-10)
def replace_inventory(match,state):
        if(match == "$item"):
            return get_item()
        if(match == "$giveitem"):
            return take_item()
        if(match == "$newitem"):
            return add_random_item()
