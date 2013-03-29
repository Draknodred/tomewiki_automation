import pprint
import os,glob
from tome_wikibot import Wikibot, SITE, bot_name, bot_pw
from wikitools import wikifile
talent_gfx_directory=r"D:\Files\tome4 source\t-engine4\game\modules\tome\data\gfx\talents"

def main():
	os.chdir(talent_gfx_directory)
	image_list = glob.glob("*.png")
	wm_bot = Wikibot(SITE,bot_name,bot_pw)
	wm_bot.login()
	#fname = 'Aether_avatar.png'
	#token_dict = wm_bot.get_edit_tokens([title1])
	#statuskey = ''
	for fname in image_list:
		clean_name = fname.replace('_',' ')
		title1='File:'+clean_name
		with open(talent_gfx_directory+'\\'+fname,'rb') as fn:
			wf_obj = wikifile.File(SITE,title1)
			pprint.pprint(wf_obj.upload(fn))

if __name__ == "__main__":
	main()