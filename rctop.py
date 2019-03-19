from addons.UIdea.libs import ui as ui_class
import re
import requests
import json
from addons.Robocraft.libs import rc_auth

PLAYERS_PER_PAGE = 16

TOP_PLAYERS_URL = 'https://leaderboards.robocraftgame.com/api/data/player/top'

board_body = {
    'ClanMembersOnly':False, # dummy account, this should never be True
    'FriendsOnly':False, # dummy account, this should never be True
    'Region':False, # True to view only same region as player
    # Player regions: EU, NA, AS, SA, OC ... AF maybe is Africa?
    'WeaponId':None # str representing a weapon; T#{Weapon}
    }

class UI(ui_class.UI):
    def shouldCreate(msg):
        return collect_args(msg.content) is not None

    def onCreate(self, msg, *args, **kwargs):
        args = collect_args(msg.content)
        try:
            # RC API calls
            credentials = rc_auth.fj_login()
            # get leaderboard
            leaderboard_resp = requests.post(TOP_PLAYERS_URL, headers = rc_auth.make_headers(credentials['Token']), json = board_body)
            self.leaderboard = leaderboard_resp.json()['Values']
            # print(json.dumps(leaderboard, indent=4)) # debug
        except:
            self.embed.description = 'Failed to contact Robocraft Leaderboard'
            self.page = -1
            self.update()
            # traceback.print_exc()
            return
        self.page = 0
        self.embed.title = 'Global Leaderboard'
        self.update()

    def onUp(self, reaction, user):
        if self.page > 0:
            self.page -= 1
            self.update()

    def onDown(self, reaction, user):
        if self.page != -1 and self.page+1 < (len(self.leaderboard)/PLAYERS_PER_PAGE):
            # NOTE: Last page may not be full, but that's ok (it's why ^^^ doesn't use // )
            self.page += 1
            self.update()

    def update(self):
        self.embed.description = self.make_description()
        super().update()

    def make_description(self):
        desc = 'Page: %s \n\n**Rank**\n' % self.page
        if len(self.leaderboard) < (self.page+1)*PLAYERS_PER_PAGE:
            page_set = self.leaderboard[self.page*PLAYERS_PER_PAGE:]
        else:
            page_set = self.leaderboard[self.page*PLAYERS_PER_PAGE:(self.page+1)*PLAYERS_PER_PAGE]
        max_len_rank = max([len(str(p['RankNumber'])) for p in page_set])
        max_len_name = max([len(str(p['DisplayName'])) for p in page_set])
        for p in page_set:
            desc += '**`'+('.'*(max_len_rank-len(str(p['RankNumber']))))+str(p['RankNumber'])+'`**'
            desc += ' | ' # seperator
            desc += '`'+p['DisplayName']+'`'
            desc += '\n' # end of player
        return desc


def collect_args(string):
    return re.search(r'(?:view)?\s*(?:robocraft|rc)\s*(?:leader)?board', string, re.I)
