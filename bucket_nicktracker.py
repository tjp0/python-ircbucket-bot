import sopel
from . import bucket_core
from . import bucket_sql
from . import bucket_factoid
import time
@sopel.module.rule(".*")
def _handle_message(bot, trigger):
        handle_nicktracker(bot, trigger)

channels = {}
def handle_nicktracker(bot, trigger):
    if(trigger.nick == bot.nick):
        return

    if(trigger.is_privmsg):
        return

    if(trigger.sender not in channels):
        channels[trigger.sender] = {}

    channels[trigger.sender][trigger.nick] = time.monotonic()
    print("%s spoke" % (trigger.nick))

def get_recent_nicks(channel):
    RECENT_SECONDS = 60*10 # Ten minutes
    current_time = time.monotonic()
    recent_nicks = list()
    if(channel not in channels):
        return recent_nicks

    expired_nicks = list()

    for nick,timestamp in channels[channel].items():
        if(current_time - timestamp > RECENT_SECONDS):
            expired_nicks.append(nick)
        else:
            recent_nicks.append(nick)

    for nick in expired_nicks:
        del channels[channel][nick]

    return recent_nicks

@bucket_factoid.factoid_sub_setup(priority=-10)
def setup_sub(bot, trigger, state):
    state['who'] = trigger.nick
    state['people'] = get_recent_nicks(trigger.sender)
    return
@bucket_factoid.factoid_sub(priority=-10)
def replace_person(match,state):
    if(match == "$someone"):
        person = pick_person(state['people'])
        state['person'] = person
        return person
    if(match == "$who"):
        state['person'] = state['who']
        return state['who']
    return None

def pick_person(people):
    print(people)
    if(len(people) == 0):
        people += ["Garrus","Tali","Obama","Background Pony #7","A ninja"]

    person = random.choice(people)
    people.remove(person)
    return person
