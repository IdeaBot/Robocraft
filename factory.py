from addons.UIdea.libs import ui as ui_lib
import json, requests, re
import traceback

with open('addons/Robocraft/body.json') as f:
    crf_body = json.load(f)

avatar_url = "http://images-pull.freejam.netdna-cdn.com/customavatar/Live/" # username goes at end
robot_url = "https://factory.robocraftgame.com/robot?id=%s&src=discord"

# maps user terms to API movement constants
movement_dict = {
    'wheel':100000,
    'hover':200000,
    'wing':300000,
    'thruster':400000,
    'rudder':500000,
    'insect':600000,
    'mech':700000, 'leg':700000,
    'ski':800000,
    'tread':900000, 'tank':900000,
    'rotor':1000000,
    'sprinter':1100000,
    'propeller':1200000, 'prop':1200000
}

# maps user terms to API weapon constants
weapon_dict = {
    'laser':10000000, 'smg':10000000, 'lasor':10000000,
    'plasma':20000000,
    'mortar':25000000,
    'rail':30000000,
    'nano':40000000, 'medic':40000000,
    'tesla':50000000,
    'flak':60000000,
    'ion':65000000,
    'protoseeker':70100000, 'ps':70100000,
    'chain':75000000, 'csh':75000000,
}

# NOTE: This is a burner account, with no items unlocked
USERNAME = 'FJAPIC00L'
EMAIL = 'melon.spoik@gmail.com'
PASSWORD = 'P4$$w0rd'

class UI(ui_lib.UI):

    def shouldCreate(message):
        return collect_args(message)!=None

    def onCreate(self, message):
        self.page = 0
        args = collect_args(message)
        self.body = dict(crf_body) # copy of crf_body
        # assemble body
        if args.group(1).lower()=='search':
            if args.group(2):
                kwargs, term = parse_searchquery(args.group(2).strip())
                self.body=make_body(term, **kwargs)
                # self.body['textFilter']=term
        else: # browse chosen
            self.body['prependFeaturedRobot']=True

        # get items
        try:
            # do login
            credentials = fj_login(USERNAME, PASSWORD)
            # print(credentials)  # debug
            # query robocraft factory list API
            crf_list_req = requests.post("https://factory.robocraftgame.com/api/roboShopItems/list", headers={"Authorization":"Web "+credentials['Token']}, json=self.body)
            # store results
            self.crf_json = crf_list_req.json()['response']['roboShopItems']
            remove_duplicate_robots(self.crf_json)
        except:
            # Change UI to reflect failure
            self.embed.description = 'Failed to contact Robocraft Factory'
            self.update()
            self.page = -1
            traceback.print_exc()
            return
        if len(self.crf_json)>0:
            item = self.crf_json[self.page]
            self.embed.title = '%s of %s: %s'%(self.page+1, len(self.crf_json),item['itemName'])
            # NOTE: I have no idea what the difference is between addedBy and addedByDisplayName
            # I have a leading supsicion that is has something to do with renames, where addedBy is their original name
            # and addedByDisplayName is their current name
            self.embed.set_author(name=item['addedByDisplayName'], icon_url=avatar_url+item['addedBy'], url=robot_url % item['itemId'])
            self.embed.description = item['itemDescription']
            self.embed.set_image(url=item['thumbnail'])
            # self.embed.set_footer(text='Robocraft Factory')
            self.embed.colour=0x3e8ac9
            # info stuff
            self.embed.add_field(name='Info', value='CPU: %s\nRanking: %s\nID:`%s`'%(item['cpu'], item['totalRobotRanking'], item['itemId']))

            self.update()
        else:
            self.embed.description = 'No results found'
            self.update()
            self.page = -1
            return

    def onLeft(self, reaction, user):
        if self.page>0:
            self.page-=1
            item = self.crf_json[self.page]
            self.embed.title = '%s of %s: %s'%(self.page+1, len(self.crf_json),item['itemName'])
            self.embed.set_author(name=item['addedByDisplayName'], icon_url=avatar_url+item['addedBy'], url=robot_url % item['itemId'])
            self.embed.description = item['itemDescription']
            self.embed.set_image(url=item['thumbnail'])
            # self.embed.set_footer(text='Robocraft Factory')
            self.embed.colour=0x3e8ac9
            # info stuff
            self.embed.set_field_at(0, name='Info', value='CPU: %s\nRanking: %s\nID:`%s`'%(item['cpu'], item['totalRobotRanking'], item['itemId']))
            self.update()

    def onRight(self, reaction, user):
        if self.page!=-1 and self.page+1<len(self.crf_json):
            self.page+=1
            item = self.crf_json[self.page]
            self.embed.title = '%s of %s: %s'%(self.page+1, len(self.crf_json),item['itemName'])
            self.embed.set_author(name=item['addedByDisplayName'], icon_url=avatar_url+item['addedBy'], url=robot_url % item['itemId'])
            self.embed.description = item['itemDescription']
            self.embed.set_image(url=item['thumbnail'])
            # self.embed.set_footer(text='Robocraft Factory')
            self.embed.colour=0x3e8ac9
            # info stuff
            self.embed.set_field_at(0, name='Info', value='CPU: %s\nRanking: %s\nID:`%s`'%(item['cpu'], item['totalRobotRanking'], item['itemId']))
            self.update()

def fj_login(name, password, email_mode=False):
    if email_mode:
        url = 'https://account.freejamgames.com/api/authenticate/email/web'
        body_json = {'EmailAddress':name, 'Password':password}
        response = requests.post(url, json=body_json)
    else:
        url = 'https://account.freejamgames.com/api/authenticate/displayname/web'
        body_json = {'DisplayName':name, 'Password':password}
        response = requests.post(url, json=body_json)
    if response.status_code != 200:
        print('FJ Auth returned error', response.status_code)
    return response.json()


def collect_args(message):
    return re.search(r'CRF\s+(search|browse)(?:\s+(.+))?', message.content, re.I)

def remove_duplicate_robots(robots):
    '''Remove duplicate robots from the API response
    No idea why duplicates are received in the first place... '''
    i = 0
    seen_IDs = list()
    while (i<len(robots)):
        if robots[i]['itemId'] in seen_IDs:
            del(robots[i])
        else:
            seen_IDs.append(robots[i]['itemId'])
            i += 1
    return robots

def parse_searchquery(query):
    kwargs = dict()
    for match in re.finditer(r'(\S+)\s*[\=\:]\s*(\S+)', query):
        kwargs[match.group(1).lower()]=match.group(2).lower()
    term = re.sub(r'(\S+)\s*[\=\:]\s*(\S+)', '', query).strip()
    kwargs = convert2constants(kwargs)
    return kwargs, term

def convert2constants(kwargs):
    result = dict()
    for key in kwargs:
        if key in ["movement", "move"]: # movement filter
            result['movementCategoryFilter']=to_movement_int(kwargs[key])
            print(result['movementCategoryFilter'])
        elif key in ["weapon", "gun"]: # weapon filter
            result['weaponCategoryFilter']=to_weapon_int(kwargs[key])
            print(result['weaponCategoryFilter'])
        elif key in ["mincpu", "minimumcpu"]: # min cpu
            result["minimumCPU"]=int(kwargs[key])
        elif key in ["maxcpu", "maximumcpu"]: # max cpu
            result["maximumCPU"]=int(kwargs[key])
        elif key in ["minrr", "maximumrr", "maxr"]: # min RR
            result["minimumRobotRanking"]=int(kwargs[key])
        elif key in ["maxrr", "maximumrr", "maxr"]: # max RR
            result["maximumRobotRanking"]=int(kwargs[key])
        else:
            result[key] = kwargs[key]
    return result

def make_body(term, **kwargs):
    body = dict(crf_body) # copy of original
    body['textFilter']=term.strip()
    for key in kwargs:
        if key in body:
            body[key]=kwargs[key]
    return body

def to_movement_int(string):
    try:
        return int(string)
    except:
        pass
    if string.lower().rstrip('s') in movement_dict:
        return movement_dict[string.lower().rstrip('s')]
    return 1000000 # default; wheels

def to_weapon_int(string):
    try:
        return int(string)
    except:
        pass
    if string.lower().rstrip('s') in weapon_dict:
        return weapon_dict[string.lower().rstrip('s')]
    return 10000000 # default; lasers
