from libs import command
import re
import requests

TMP_FILE = 'addons/Robocraft/tmp.jpg'

player_url = r'http://images-pull.freejam.netdna-cdn.com/customavatar/Live/'
clan_url = r'http://images-pull.freejam.netdna-cdn.com/clanavatar/Live/'


class Command(command.DirectOnlyCommand):
    '''Retrieve an avatar from Robocraft

**Usage**
```@Idea get avatar for <name>```
Where
**`<name>`** is the name of the clan/player

**Example**
`@Idea get avatar for NGniusness` 
'''
    def matches(self, message):
        return self.collect_args(message) is not None
    
    def action(self, message):
        yield from self.send_typing(message.channel)
        args = self.collect_args(message)
        has_clan_tag = re.search(r'(?:\s|^)-%s\b' % 'c', message.content, re.I) is not None
        has_player_tag = re.search(r'(?:\s|^)-%s\b' % 'p', message.content, re.I) is not None
        has_no_tag = not (has_clan_tag or has_player_tag)
        
        # download img
        mode = None
        # query player avatars
        if has_player_tag or (has_no_tag and mode is None):
            resp = requests.get(player_url+args.group(1))
            if resp.status_code == 200:
                mode = 'Player'
        
        # query clan avatars
        if has_clan_tag or (has_no_tag and mode is None):
            resp = requests.get(clan_url+args.group(1).lower())
            if resp.status_code == 200:
                mode = 'Clan'
                
        # both requests failed to find anything
        if mode is None:
            yield from self.send_message(message.channel, 'Unable to find player/clan avatar, perhaps they\'re not using a custom avatar?')
            return
            
        # save img to TMP_FILE
        with open(TMP_FILE, 'wb') as f:
            f.write(resp.content)
        content = '%s\'s %s avatar' % (args.group(1), mode)
        yield from self.send_file(message.channel, fp=TMP_FILE, content=content)
    
    def collect_args(self, message):
        return re.search(r'(?:get|find|search)(?:\s*for)?\s*avatar\s+(\S+)', message.content, re.I)
