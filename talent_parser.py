from collections import defaultdict
import pprint
import os
import re
import fnmatch
file_directory=r"D:\Files\tome4 source\t-engine4\game\modules\tome\data\talents"

exclude_categories = ['base','golem','uber',"sher'tul",'misc','tutorial']
exclude_categories_trees = ['malleable-body','other','objects','horror','traveler','traps','poisons-effects','possession','anomalies','dark-figure','unarmed-other','archery - base','keepsake','temporal-archery']

short_name_map = {

}

CAT_TYPE_SUFFIX = ' (category type)'
CATEGORY_SUFFIX = ' (category)'
TALENT_SUFFIX = ' (talent)'

class Talent(object):
	def __init__(self,name,raw_category,desc,readable_category = None):
		self.name = name.capitalize()
		self.raw_category = raw_category
		self.category_type = self.raw_category.split("/")[0].capitalize()
		self.raw_category_tree = self.raw_category.split("/")[-1].capitalize()
		self.desc = desc
		self.readable_category = readable_category
	
	def __eq__(self,other):
		return self.name == other
	
	def __repr(self):
		return "<Talent "+self.raw_category+" "+self.name+">"
	
	@property
	def cat_tree(self):
		if self.readable_category:
			return self.readable_category.capitalize()
		else:
			return self.raw_category_tree.capitalize()
	
	@property
	def formatted_category(self):
		if self.readable_category:
			frmt_category = self.category_type+"/"+self.readable_category
		else:
			frmt_category = self.raw_category
		return frmt_category
	
	@property
	def clean_desc(self):
		if self.desc:
			return self.desc.replace('%d','X').replace('%0.2f','X').replace('%%','%')
		else:
			return self.desc
	
	def csv_self(self):
		result_list = [self.name,self.formatted_category,self.desc]
		return ",".join('"'+item+'"' for item in result_list)
	
	def get_wiki_title(self):
		return self.name+TALENT_SUFFIX
	
	def get_image_name(self):
		return self.name.replace("'",'_').replace("-",'_')
	
	def get_wiki_table(self):
		return '{{Ability_box|image='+self.get_image_name()+'.png|name='+self.name+'|category_type=[['+self.category_type+CAT_TYPE_SUFFIX+'|'+self.category_type+']]|category=[['+str(self.cat_tree)+CATEGORY_SUFFIX+'|'+str(self.cat_tree)+']]|desc='+str(self.clean_desc)+'}}'
	
class TalentParser(object):
	def __init__(self,starting_dir):
		self.file_directory = starting_dir
		self.talent_pattern = re.compile('(?:newTalent{[^.]*?(?<!short_)name[^.]=[^.]["])([^"]*)"[\s\S]*?type[^"]*"([^"]*)[\s\S]*?(?:info[\s\S]*?return[^\[]*?)(?:\[){2}([^\]]*)[^}]*')
		self.category_pattern = re.compile('newTalentType{[^.]*type[^"]*"([^"]*)[^.]*name[^"]*"([^"]*)[^.]*description[^"]*"([^"]*)')
		self.talent_matches = []
		self.category_dict = {}
		self.talent_objs = []
	
	def get_talents(self):
		top_dirnames = os.listdir(self.file_directory)
		for root, dirnames, filenames in os.walk(file_directory):
			for filename in fnmatch.filter(filenames, '*.lua'):
				with open(os.path.join(root, filename),'r') as fn:
					file_contents = fn.read()
					if filename.split('.')[0] in top_dirnames:
						for cat,name,desc in self.clean_regex_result(self.run_regex(self.category_pattern,file_contents)):
							self.category_dict[cat] = (name,desc)
					else:
						self.talent_matches += self.clean_regex_result(self.run_regex(self.talent_pattern,file_contents))
	#classmethod
	def run_regex(cls,pattern,blob):
		matches = []
		for t in pattern.finditer(blob):
			matches.append(t.groups())
		return matches
				
	def clean_regex_result(self,list_val):
		clean_list = []
		for cat,name,desc in list_val:
			clean_list.append((self.clean_string(cat),self.clean_string(name),self.clean_string(desc)))
		return clean_list
			
	def clean_string(self,str_val):
		return re.sub('\s+',' ',str_val)
	
	def setup_objects(self):
		for name,cat,desc in self.talent_matches:
			nice_cat_tuple = self.category_dict.get(cat,0)
			if nice_cat_tuple:
				self.talent_objs.append(Talent(name,cat,desc,nice_cat_tuple[0]))
			else:
				self.talent_objs.append(Talent(name,cat,desc))
			
	def process(self):
		self.get_talents()
		self.setup_objects()
	
	def get_mapping_dicts(self):
		type_to_cat = defaultdict(set)
		cat_to_talent_obj = defaultdict(set)
		format_exclude_cat_type = [cat_type.capitalize() for cat_type in exclude_categories]
		format_exclude_cat_tree = [cat_tree.capitalize() for cat_tree in exclude_categories_trees]
		for obj in self.talent_objs:
			if obj.category_type not in format_exclude_cat_type and obj.raw_category_tree not in format_exclude_cat_tree:
				type_to_cat[obj.category_type+CAT_TYPE_SUFFIX].add(obj.cat_tree+CATEGORY_SUFFIX)
				cat_to_talent_obj[obj.cat_tree+CATEGORY_SUFFIX].add(obj)
		return type_to_cat,cat_to_talent_obj

if __name__ == "__main__":
	talent_parse = TalentParser(file_directory)
	#with open(file_directory+'\spells\explosives.lua','r') as fn:
	#	for t in  talent_parse.run_regex(talent_parse.talent_pattern,fn.read()):
	#		print t
	talent_parse.process()
	type_to_cat = defaultdict(set)
	cat_to_talent = defaultdict(set)
	for obj in talent_parse.talent_objs:
		print obj.clean_desc
		if 0 and obj.category_type not in exclude_categories and obj.raw_category_tree not in exclude_categories_trees:
			#full_talent_dict[obj.category_type][obj.cat_tree].add(obj.name)
			type_to_cat[obj.category_type].add(obj.cat_tree)
			cat_to_talent[obj.cat_tree].add(obj.name)
	if 0:
		for type, cat_list in type_to_cat.iteritems():
			print "=",type
			for cat in cat_list:
				if len(cat_to_talent[cat]) != 4:
					print "===",cat
					for talent in cat_to_talent[cat]:
						print "======",talent