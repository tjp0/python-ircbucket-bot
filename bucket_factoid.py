from . import bucket_core
from . import bucket_sql

import random
import re
from operator import itemgetter
class Factoid(bucket_sql.Base):
    from sqlalchemy import Column, Integer, String, Boolean,Text,Sequence
    __tablename__ = 'bucket_facts'
    id = Column(Integer,Sequence('user_id_seq'),primary_key=True,nullable=False)
    fact = Column(String(128),nullable=False)
    tidbit = Column(Text,nullable=False)
    verb = Column(String(16),nullable=False)
    RE = Column(Boolean,nullable=False)
    protected = Column(Boolean,nullable=False)

    def __repr__(self):
        return("id: %s, fact: %s, tidbit: %s, verb: %s, RE: %s, protected: %s" %(self.id,self.fact,self.tidbit,self.verb,self.RE,self.protected))
    def toLiteral(self,admin):
        if(admin):
            return("(#%s) %s %s" % (self.id,self.verb,self.tidbit))
        else:
            return("%s %s" % (self.verb,self.tidbit))

@bucket_core.bucket_command("(?P<fact>.+) (?P<verb>is|are|(\<.+\>)) (?P<tidbit>.+)")
def add_factoid(bot, trigger, match):
    global last_added_id
    fact = match.group("fact").lower()
    verb = match.group("verb")
    tidbit = match.group("tidbit")
    session = bucket_sql.Session()

    newFact = Factoid(fact=fact,verb=verb,tidbit=tidbit,RE=False,protected=False)
    session.add(newFact)
    session.commit()
    last_added_id = newFact.id
    bot.say("Okay, %s" % trigger.nick)

last_added_id = -1
last_used_id = -1

@bucket_core.bucket_command("literal(\[(?P<index>\d+)\])? (?P<factoid>.+)")
def literal_factoid(bot, trigger, match):
    session = bucket_sql.Session()
    try:
        start_index = int(match.group('index'))
    except:
        start_index = 0
    ELEMENTS = 5
    factoids = session.query(Factoid).filter(Factoid.fact == match.group('factoid')).order_by(Factoid.id)[start_index*ELEMENTS:start_index*ELEMENTS+ELEMENTS]
    factoid_parsed = []
    op = bucket_core.isAdmin(bot,trigger)
    for fact in factoids:
        factoid_parsed.append(fact.toLiteral(op))
    if(len(factoid_parsed) == 0):
        bot.action("shrugs")
    else:
        bot.say('|'.join(factoid_parsed))

@bucket_core.bucket_command("what was that")
def what_factoid(bot, trigger, match):
    session = bucket_sql.Session()
    factoid = session.query(Factoid).filter(Factoid.id == last_used_id).one()
    bot.say(factoid.fact+" "+factoid.toLiteral(bucket_core.isAdmin(bot,trigger)))
    return

@bucket_core.listen_command(".*",999)
def trigger_factoid(bot, trigger, match):
    bucket_core.log("--- Message: \"%s\"" % (trigger.group(0)))
    session = bucket_sql.Session()
    #Slow, but this shouldn't matter for the number of rows we're working with
    factoids = session.query(Factoid).filter(Factoid.fact == trigger.group(0).lower()).all()
    if(factoids):
        factoid = random.choice(factoids)
        handle_factoid(bot, trigger, factoid)
    bucket_core.log("---")

def handle_factoid(bot, trigger, factoid):
    global last_used_id
    last_used_id = factoid.id
    bucket_core.log("Handling factoid: %s" % (factoid.toLiteral(True)))
    fact = factoid.fact
    verb = factoid.verb
    tidbit = factoid.tidbit
    tidbit = re.sub("\$[0-9A-Za-z\-_]+",Sub_Factoid(bot, trigger),tidbit)
    verbln = verb.lower()
    bucket_core.log("Final factoid: %s %s %s" % (fact,verb,tidbit))
    if (verbln == "is" or verbln == "are"):
        bot.say("%s %s %s" % (fact, verb, tidbit))
    elif(verbln == "<reply>"):
        bot.say("%s" % (tidbit))
    elif(verbln == "<action>"):
        bot.action("%s" % (tidbit))
    else:
        bot.say("%s %s %s",(fact, verb[1:-1], tidbit))


subs_parsers = []
class factoid_sub:
    def __init__(self,priority):
        self.priority = priority
    def __call__(self, f):
        global subs_parsers
        subs_parsers.append((f,self.priority))
        subs_parsers = sorted(subs_parsers, key=itemgetter(1))
        bucket_core.log("Registered %s for factoid parser" % f)
        return f

subs_setup = []
class factoid_sub_setup:
    def __init__(self,priority):
        self.priority = priority
    def __call__(self, f):
        global subs_setup
        subs_setup.append((f,self.priority))
        subs_setup = sorted(subs_setup, key=itemgetter(1))
        bucket_core.log("Registered %s for factoid parser setup" % f)
        return f

class Sub_Factoid:
    def __init__(self, bot, trigger):
        self.state = dict()
        for f,priority in subs_setup:
            f(bot, trigger, self.state)

    def __call__(self, match):
        repl = None
        for f,priority in subs_parsers:
            repl = f(match.group(0),self.state)
            if(repl):
                break
        if(not repl):
            repl = "<INVALID>"
        bucket_core.log("Replacing \"%s\" with \"%s\"" %(match.group(0),repl))
        return repl

