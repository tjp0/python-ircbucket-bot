from . import bucket_core
from . import bucket_factoid
from . import bucket_sql

class Gender(bucket_sql.Base):
    from sqlalchemy import Column, Integer, String, Boolean,Text,Sequence, Enum
    __tablename__ = 'bucket_genders'
    id = Column(Integer,Sequence('user_id_seq'),primary_key=True,nullable=False)
    nick = Column(String(64),nullable=False)
    gender = Column(Enum("male","female","androgynous","inanimate","full name"))
    def __repr__(self):
        return("id: %s, nick: %s, gender: %s" %(self.id,self.nick,self.gender))

@bucket_core.bucket_command("I am (?P<gender>.*)")
def set_gender(bot, trigger, match):
    gender = match.group('gender').lower()
    genders = ['male','female','inanimate','full name']
    if(gender not in genders):
        bot.say("Recognized grammatical genders: male, female, androgynous, inanimate, full name")
        return
    session = bucket_sql.Session()

    nick = session.query(Gender).filter(Gender.nick == trigger.nick).first()
    if(nick):
        nick.gender = gender
    else:
        session.add(Gender(nick=trigger.nick,gender=gender))
    session.commit()
    bot.say("Okay, %s" % (trigger.nick))

@bucket_core.bucket_command("What gender is (?P<nick>.+)")
def query_gender(bot, trigger, match):
    print("Querying gender")
    nick = match.group("nick")
    session = bucket_sql.Session()
    gender = session.query(Gender).filter(Gender.nick == nick).first()
    if(gender):
        gender = gender.gender
    else:
        gender = "androgynous"
    bot.reply("%s is %s"% (nick,gender))

@bucket_factoid.factoid_sub(priority=10)
def replace_gender(match,state):

        if('person' in state):
            person = state['person']
        else:
            person = "bucket"

        session = bucket_sql.Session()
        nickRecord = session.query(Gender).filter(Gender.nick == person).first()
        gender = "androgynous"
        if(nickRecord):
            gender = nickRecord.gender

        subjective = {
                'male': 'he',
                'female': 'she',
                'androgynous': 'they',
                'inanimate': 'it',
                'full name': "%s" % (person)
                }
        objective = {
                'male': 'him',
                'female': 'her',
                'androgynous': 'them',
                'inanimate': 'it',
                'full name': "%s" % (person)
                }
        reflexive = {
                'male': 'himself',
                'female': 'herself',
                'androgynous': 'themself',
                'inanimate': 'itself',
                'full name': "%s" % (person)
                }
        possessive = {
                'male': 'his',
                'female': 'hers',
                'androgynous': 'theirs',
                'inanimate': 'its',
                'full name': "%s's" % (person)
                }
        determiner = {
                'male': 'his',
                'female': 'her',
                'androgynous': 'their',
                'inanimate': 'its',
                'full name': "%s's" % (person)
                }
        variables = {
                '$subjective':subjective,
                '$shehe':subjective,
                '$heshe':subjective,
                '$he':subjective,
                '$she':subjective,
                '$they':subjective,
                '$it':subjective,

                '$objective':objective,
                '$him':objective,
                '$her':objective,
                '$them':objective,
                '$himher':objective,
                '$herhim':objective,

                '$reflexive':reflexive,
                '$himselfherself':reflexive,
                '$herselfhimself':reflexive,
                '$himself':reflexive,
                '$herself':reflexive,
                '$themself':reflexive,
                '$itself':reflexive,

                '$possessive':possessive,
                '$hishers':possessive,
                '$hershis':possessive,
                '$hers':possessive,
                '$theirs':possessive,

                '$determiner':determiner,
                '$hisher':determiner,
                '$herhis':determiner,
                '$their':determiner
                }

        if(match in variables):
            return variables[match][gender]
