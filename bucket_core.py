import re
from operator import itemgetter
from sopel import module
bucket_commands = []
listen_commands = []
class bucket_command:
    def __init__(self,regex,priority=0):
        self.regex = regex
        self.priority = priority
    def __call__(self, f):
        global bucket_commands
        bucket_commands.append((f,self.regex,self.priority))
        bucket_commands = sorted(bucket_commands, key=itemgetter(2))
        print("Registered %s for bucket_command" % f)
        return f

class listen_command:
    def __init__(self,regex,priority=0):
        self.regex  = regex
        self.priority = priority
    def __call__(self, f):
        global listen_commands
        listen_commands.append((f,self.regex,self.priority))
        listen_commands = sorted(listen_commands, key=itemgetter(2))
        print("Registered %s for listen_command" % f)
        return f

@module.rule(".*")
def handle_message(bot, trigger):
    match = re.match(r'^bucket[:, ]\s*',trigger.group(0),re.I)
    if(match):
        for f, regex, priority in bucket_commands:
            match = re.match(r'^bucket[:, ]\s*'+regex.replace("$bucket",bot.nick),trigger.group(0),re.I)
            if(match):
                log("Passing to function: %s" % f)
                f(bot, trigger, match)
                return

    for f, regex, priority in listen_commands:
        match = re.match(regex.replace("$bucket",bot.nick),trigger.group(0),re.I)
        if(match):
            log("Passing to function: %s" % f)
            f(bot, trigger, match)
            return

def log(message):
    print(message)

def isAdmin(bot, trigger):
    if(trigger.sender in bot.privileges):
        if(trigger.nick in bot.privileges[trigger.sender]):
            perm = bot.privileges[trigger.sender][trigger.nick]
            if(perm == module.ADMIN):
                return True
            if(perm == module.OP):
                return True
            if(perm == module.OWNER):
                return True
    return False
print("Bucket core initialized")
