# Notes, examples and documentation for factory actions

from libs import command
import json, requests

# NOTE: token is an old dummy account token stored in the JS code. Proper authentication is shown in login()
token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJQdWJsaWNJZCI6IjEyMyIsIkRpc3BsYXlOYW1lIjoiVGVzdCIsIlJvYm9jcmFmdE5hbWUiOiJGYWtlQ1JGVXNlciIsIkZsYWdzIjpbXSwiaXNzIjoiRnJlZWphbSIsInN1YiI6IldlYiIsImlhdCI6MTU0NTIyMzczMiwiZXhwIjoyNTQ1MjIzNzkyfQ.ralLmxdMK9rVKPZxGng8luRIdbTflJ4YMJcd25dKlqg"


class Command(command.Dummy):
    '''Robocraft Community Robot Factory on Discord, WOW!
This is very similar to the fancy new Factory page online:
<https://factory.robocraftgame.com/>

**Usage**
```CRF search [<search term>] [<argument>] [<argument>] [...]```
Where
**`<search term>`** is the term you'd like to search for
**`<argument>`** is an argument like `<keyword>=<value>`
Valid **`<keyword>`**s include:
`movement`: `<value>` is a single word (eg for Mech Leg, use `mech`)
`weapon`: `<value>` is a single word (eg for Chain Shredder, use `chain`)
`maxRR`, `minRR`: `<value>` is an integer
`maxCPU`, `minCPU`: `<value>` is an integer

**NOTE:** items in between `[` and `]` are optional

**Example**
`CRF search NGniusness weapon=rail movement=hover`
'''

    def test(self):
        '''Example query of the Robocraft CRF API'''
        with open('addons/Robocraft/body.json') as f:
            crf_body = json.load(f)
        try:
            crf_list_req = requests.post("https://factory.robocraftgame.com/api/roboShopItems/list", headers={"Authorization":"Web "+token}, json=crf_body)
            crf_json = crf_list_req.json()['response']['roboShopItems']
        except:
            return
        print(json.dumps(crf_json, indent=4))

    def login(self):
        ''' Example login query '''
        email = 'email@domain.com'
        username = 'username'
        password = 'password'
        url = 'https://account.freejamgames.com/api/authenticate/email/web'
        req_json = {'EmailAddress':email, 'Password':password}
        # NOTE: this can also be DisplayName instead of EmailAddress with a request to https://account.freejamgames.com/api/authenticate/displayname/web
        auth_response = requests.post(url, json=req_json)
        return auth_response.json() # you'll need refresh token to refresh, so not just Token is returned

    def refresh(self, token, refresh_token):
        '''JWT tokens need to be refreshed every so often, using the refresh token
        provided on login, the public ID (see https://jwt.io/ - it's decoded from the token) (NOT IMPLEMENTED)

        This part is out of scope for this project, but it is partially implemented here for future reference'''
        url = 'https://account.freejamgames.com/api/authenticate/token/refresh'
        req_json = {'RefreshToken':refresh_token, 'PublicId':'ToBeDecoded', 'Target':'Web'}
        ref_response = requests.post(url, json=req_json) # refresh response is similar to the login response
        return ref_response.json()


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
