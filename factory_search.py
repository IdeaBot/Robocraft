from libs import command, embed
import json, requests, re

with open('addons/Robocraft/body.json') as f:
    crf_body = json.load(f)

token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJQdWJsaWNJZCI6IjEyMyIsIkRpc3BsYXlOYW1lIjoiVGVzdCIsIlJvYm9jcmFmdE5hbWUiOiJGYWtlQ1JGVXNlciIsIkZsYWdzIjpbXSwiaXNzIjoiRnJlZWphbSIsInN1YiI6IldlYiIsImlhdCI6MTU0NTIyMzczMiwiZXhwIjoyNTQ1MjIzNzkyfQ.ralLmxdMK9rVKPZxGng8luRIdbTflJ4YMJcd25dKlqg"

class Command(command.DirectOnlyCommand):
    def matches(self, message):
        return False and self.collect_args(message)!=None

    def action(self, message):
        args = self.collect_args(message)
        body = dict(crf_body) # copy of crf_body
        # assemble body
        if args.group(1).lower()=='search':
            if args.group(2):
                body['textFilter']=args.group(2).strip()
        else: # browse chosen
            body['prependFeaturedRobot']=True

        # get items
        yield from self.send_typing(message.channel)
        try:
            crf_list_req = requests.post("https://factory.robocraftgame.com/api/roboShopItems/list", headers={"Authorization":"Web "+token}, json=body)
            crf_json = crf_list_req.json()['response']['roboShopItems']
        except:
            yield from self.send_message(message.channel, 'Failed to contact Robocraft Factory')
            return
        if len(crf_json)>0:
            item = crf_json[0]
            em = embed.create_embed(title='%s of %s: %s'%(crf_json.index(item)+1, len(crf_json),item['itemName']), author={'name':item['addedByDisplayName'], 'icon_url':None, 'url':None}, description=item['itemDescription'], image={'url':item['thumbnail']}, footer={'text':'Robocraft Factory', 'icon_url':None}, colour=0x3e8ac9)
            yield from self.send_message(message.channel, embed=em)
        else:
            yield from self.send_message(message.channel, 'No results found')

    def collect_args(self, message):
        return re.search(r'CRF\s+(search|browse)(?:\s+(.+))?', message.content, re.I)

''' Notes
{
		"page": 1, No idea how this applies to anything
		"pageSize": 10, No idea how this applies to anything
		"order": 0, Orders are: "Suggested": 0,
	                            "CombatRating": 1,
	                            "CosmeticRating": 2,
	                            "Added": 3,
	                            "CPU": 4,
	                            "MostBought": 5
		"playerFilter": false, I'd assume this only matches usernames or something similar
		"movementFilter": "100000,200000,300000,400000,500000,600000,700000,800000,900000,1000000,1100000,1200000",
		"movementCategoryFilter": "100000,200000,300000,400000,500000,600000,700000,800000,900000,1000000,1100000,1200000",
        movementCategoryFilter constants:
        100000 WHEELS
        200000 HOVERS
        300000 WINGS
        400000 THRUSTERS (?)
        500000 ??? RUDDERS?
        600000 INSECT LEGS
        700000 MECH LEGS
        800000 SKIS
        900000 TANK TREADS
        1000000 ROTOR BLADES
        1100000 SPRINTER LEGS
        1200000 PROPELLERS (?)

		"weaponFilter": "10000000,20000000,25000000,30000000,40000000,50000000,60000000,65000000,70100000,75000000",
		"weaponCategoryFilter": "10000000,20000000,25000000,30000000,40000000,50000000,60000000,65000000,70100000,75000000",
        weaponCategoryFilter constants
        10000000 Lasers
        20000000 Plasma
        25000000 Mortar
        30000000 Rail
        40000000 Nano (?)
        50000000 Tesla
        60000000 Flak
        65000000 Ion
        70100000 Protoseeker (?)
        75000000 Chain

		"minimumCpu": 100,
		"maximumCpu": 2000,
		"minimumRobotRanking": 0,
		"maximumRobotRanking": 100000000,
		"textFilter": "", Search field, matches usernames and robots (titles & descriptions)
		"textSearchField": "", No idea what this does
		"buyable": true, I'd assumed this hides bots with parts you don't have unlocked. Probably actually works if you're logged in
        If you're not logged in, leave this set to true otherwise the server will throw a 500 error
		"prependFeaturedRobot": false, (Show/hide feature bot at start of results)
		"featuredOnly": false, Only show featured bots (like the checkbox in-game)
		"defaultPage": false No idea what this does
}

token is hilariously dumb (not to mention long), was found in a JS file
There are other api endpoints, but they have not been investigated.
A good file to look at to understand CRF API functionality https://factory.robocraftgame.com//js/roboshop.js
Thanks for not minifying that :)

'''
