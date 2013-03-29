import pprint
from wikitools import wiki, api

SITE = wiki.Wiki("http://te4.org/w/api.php")
bot_name = ''
bot_pw = ''
class Wikibot(object):
	def __init__(self,site,name,pw):
		self.site = site
		self.name = name
		self.pw = pw
		self.login_token = None
		
	def login(self):
		self.login_token = self._get_login_auth(self.name,self.pw)
		
	def _get_login_param(self,name,pw,token=None):
		if token:
			param = {'action':'login',
			'lgname':name,
			'lgpassword':pw,
			'lgtoken':token}
		else:
			param = {'action':'login',
			'lgname':name,
			'lgpassword':pw}
		return param

	def _get_login_auth(self,name,pw):
		login_param = self._get_login_param(bot_name,bot_pw)
		result = self.run_request(login_param)
		new_login_param = self._get_login_param(bot_name,bot_pw,result['login']['token'])
		new_result = self.run_request(new_login_param)
		return new_result

	def run_request(self,params):
		#pprint.pprint(params)
		req = api.APIRequest(self.site, params)
		#pprint.pprint(req)
		res = req.query(querycontinue=True)
		#pprint.pprint(res)
		return res
	
	def get_edit_tokens(self,page_list):
		formatted_titles = '|'.join(page_list)
		edit_request_param = {
			'action':'query',
			'titles':formatted_titles,
			'prop':'info',
			'intoken':'edit'
		}
		edit_request = self.run_request(edit_request_param)
		token_dict = {}
		page_dict = edit_request['query']['pages']
		for page_idx in page_dict:
			token_dict[page_dict[page_idx]['title']] = page_dict[page_idx]['edittoken']
		return token_dict
	
	def edit_page(self,title,text,token):
		edit_param = {
			'action':'edit',
			'title':title,
			'text':text,
			#'createonly':'True',
			'token':token
		}
		return self.run_request(edit_param)
	
def main():
	#wm_bot = Wikibot(SITE,bot_name,bot_pw)
	#wm_bot.login()
	#token_dict = wm_bot.get_edit_tokens([title1])
	#pprint.pprint(wm_bot.run_request()
	None

if __name__ == "__main__":
	main()