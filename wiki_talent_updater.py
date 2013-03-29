import pprint
from talent_parser import TalentParser, CAT_TYPE_SUFFIX, CATEGORY_SUFFIX, TALENT_SUFFIX, exclude_categories, exclude_categories_trees
from tome_wikibot import Wikibot, SITE, bot_name, bot_pw
talents_directory=r"D:\Files\tome4 source\t-engine4\game\modules\tome\data\talents"

def format_category_page(cat_to_talent_obj_dict, category):
	category_str = ''
	for talent in cat_to_talent_obj_dict[category]:
		category_str += '{{:'+talent.get_wiki_title()+'}}'
	category_str += '<noinclude>[[Category:Category]]</noinclude>'
	return category_str

def format_category_type_page(type_to_cat_dict,cat_type):
	type_str = ''
	for category in sorted(type_to_cat_dict[cat_type]):
		type_str += '=='+category[:-len(CATEGORY_SUFFIX)]+'==\n'
		type_str += '{{:'+category+'}}\n'
	type_str += '<noinclude>[[Category:Category Type]]</noinclude>'
	return type_str

def chunks(l, n):
    return [l[i:i+n] for i in range(0, len(l), n)]

def main():
	talent_parse = TalentParser(talents_directory)
	talent_parse.process()
	type_to_cat,cat_to_talent_obj = talent_parse.get_mapping_dicts()
	wm_bot = Wikibot(SITE,bot_name,bot_pw)
	wm_bot.login()
	
	type_list = [type for type in type_to_cat]
	cat_list = [cat for cat in cat_to_talent_obj]
	talent_list = []
	for cat_t,talents in cat_to_talent_obj.iteritems():
		talent_list += talents
	talent_title_list = [talent.get_wiki_title() for talent in talent_list]
	
	title_list = type_list + cat_list + talent_title_list
	token_dict = {}
	for list_chunk in chunks(title_list,500):
		token_dict.update(wm_bot.get_edit_tokens(list_chunk))

	#for talent in talent_list:
	#	pprint.pprint(wm_bot.edit_page(talent.get_wiki_title(),talent.get_wiki_table(),token_dict[talent.get_wiki_title()]))
	#for category in cat_list:
	#	pprint.pprint(wm_bot.edit_page(category,format_category_page(cat_to_talent_obj,category),token_dict[category]))
	#for cat_type in type_list:
	#	pprint.pprint(wm_bot.edit_page(cat_type,format_category_type_page(type_to_cat,cat_type),token_dict[cat_type]))
	print "Done!"
	
if __name__ == "__main__":
	main()