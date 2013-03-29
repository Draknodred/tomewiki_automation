import pprint
from tome_wikibot import Wikibot, SITE, bot_name, bot_pw
import re
import os
import os.path
from slpp import slpp

IMPORTANT_ITEMS = ["name","guardian","level_range","width","height","max_level","min_material_level","max_material_level"]

EXCLUDED_ZONES = ['TestZone!','Tutorial','Derth (Southeast)','Ambush!','Fearscape',"Unknown Sher'Tul Fortress",'World of Eyal','Void between worlds','Small lumberjack village']

ZONE_SUFFIX = ' (zone)'

class Zone(object):
	def __init__(self,name,floors,min_level,max_level,min_ilevel,max_ilevel,width,height,guardian_name,artifacts):
		self.name = name
		self.floors = floors
		self.min_level = min_level
		self.max_level = max_level
		self.min_ilevel = min_ilevel
		self.max_ilevel = max_ilevel
		self.width = width
		self.height = height
		self.guardian_name = guardian_name
		self.artifacts = artifacts
	
	def formatted_guardian_name(self):
		return self.guardian_name.replace("_"," ").lower().title()
		
	def get_wiki_title(self):
		return self.name.capitalize()
	
	def get_wiki_table(self):
		if self.guardian_name:
			return '{{Zone| name = '+self.name+'| floors = '+self.floors+'| guardian = [['+self.formatted_guardian_name()+']]| min_level = '+str(self.min_level)+'| max_level = '+str(self.max_level)+'| min_ilevel = '+str(self.min_ilevel)+'| max_ilevel = '+str(self.max_ilevel)+'| width = '+str(self.width)+'| height = '+str(self.height)+'}}'
		else:
			return '{{Zone| name = '+self.name+'| floors = '+self.floors+'| min_level = '+str(self.min_level)+'| max_level = '+str(self.max_level)+'| min_ilevel = '+str(self.min_ilevel)+'| max_ilevel = '+str(self.max_ilevel)+'| width = '+str(self.width)+'| height = '+str(self.height)+'}}'
	
	def get_artifact_text(self):
		artifact_wiki_text = ''
		for artifact in self.artifacts:
			artifact_wiki_text += '*[['+artifact+']]\n'
		return artifact_wiki_text
	
	def get_wiki_page(self):
		page_str = ''
		page_str += self.get_wiki_table()
		page_str += '\n'
		page_str += '==Zone Information==\n'
		page_str += 'TBD\n'
		if self.artifacts:
			page_str += '==Zone Specific Artifacts==\n'
			page_str += self.get_artifact_text()
		return page_str

class ZoneReader(object):
	def __init__(self,filepath):
		self.zone_dict = {}
		self.artifact_list = []
		self.get_zone_info(filepath)
		self.get_object_info(filepath)
	
	def get_zone_info(self,filepath):
		zone_path = filepath+"/zone.lua"
		with open(zone_path, "rb") as fn:
			self.process_lua_file(fn)

	def process_lua_file(self,zone_file):
		v_str = ""
		for item in zone_file.readlines():
			clean_str = item.strip()
			if not item.strip().startswith("--"):
				if item.startswith("return"):
					v_str += "{"
				elif clean_str.startswith("min_material_level"):
					v_str += clean_str[:21]+str(self.get_lowest_num_in_str(clean_str))+", "
				elif clean_str.startswith("max_material_level"):
					v_str += clean_str[:21]+str(self.get_highest_num_in_str(clean_str))+", "
				else:
					v_str += str(item)
		v_str = " ".join(v_str.split())
		data = slpp.decode(v_str)
		self.process_dict(data,0)
			
	def get_lowest_num_in_str(self,input_str):
		str_list = re.findall(r"\d+", input_str)
		if str_list:
			digit_list = sorted([int(item) for item in str_list])
			return digit_list[0]
		else:
			return None
		
	def get_highest_num_in_str(self,input_str):
		str_list = re.findall(r"\d+", input_str)
		if str_list:
			digit_list = sorted([int(item) for item in str_list], reverse= True)
			return digit_list[0]
		else:
			return None
	
	def process_dict(self,inp_dict,cnt):
		cnt += 1
		for k,v in inp_dict.iteritems():
			if not isinstance(k,int):
				if isinstance(v,dict):
					self.process_dict(v,cnt)
				else:
					if k in IMPORTANT_ITEMS:
						self.zone_dict[k] = v

	def get_object_info(self,filepath):
		object_path = filepath+"/objects.lua"
		with open(object_path, "r") as fn:
			self.read_object(fn)
			
	def read_object(self,object_file):
		v_str = ""
		for item in object_file.readlines():
			clean_str = item.strip()
			if not item.strip().startswith("--"):
				if item.startswith("load") or item.startswith("for") or item.startswith("local"):
					None
				elif item.startswith("return"):
					v_str += "{"
				else:
					v_str += str(item).replace("newEntity","|")
		v_str = " ".join(v_str.split())
		obj_list = v_str.split("|")
		artifact_list = []
		for object in obj_list:
			data = slpp.decode(object)
			#print data
			if data:
				if "base" in data:
					if data["base"] != "BASE_LORE":
						self.artifact_list.append(str(data["name"]))
				else:
					self.artifact_list.append(str(data["name"]))

		
	def get_zone_object(self):
		name = str(self.zone_dict["name"])
		floors = str(self.zone_dict["max_level"])
		lvl_range = self.zone_dict["level_range"]
		min_level = str(lvl_range[0])
		max_level = str(lvl_range[1])
		min_ilevel = str(self.zone_dict.get("min_material_level",1))
		max_ilevel = str(self.zone_dict.get("max_material_level",5))
		if "guardian" in self.zone_dict:
			guardian_name = str(self.zone_dict["guardian"])
		else:
			guardian_name = None
		width = str(self.zone_dict["width"])
		height = str(self.zone_dict["height"])
		
		return Zone(name,floors,min_level,max_level,min_ilevel,max_ilevel,width,height,guardian_name,self.artifact_list)

def process_zone_file(filepath):
	zone_reader = ZoneReader(filepath)
	zone_obj = zone_reader.get_zone_object()
	return zone_obj
	#for k,v in zone_obj.__dict__.iteritems():
		#print "!",k,v

def main():
	fp = r"D:\Files\tome4 source\t-engine4\game\modules\tome\data\zones"
	fplist = [fp+"/"+o for o in os.listdir(fp) if os.path.isdir(fp+"/"+o)]
	success_zones = []
	failed_zones = []
	for zone in fplist:
		try:
			new_zone_obj = process_zone_file(zone)
			if new_zone_obj:
				success_zones.append(new_zone_obj)
		except Exception, e:
			failed_zones.append(zone)
			#import traceback
			#traceback.print_exc()
			#print "!!!ERROR!!! ",zone, "!!",e
			#raise
	load_zones(success_zones)

def chunks(l, n):
    return [l[i:i+n] for i in range(0, len(l), n)]

def load_zones(zone_obj_list):
	wm_bot = Wikibot(SITE,bot_name,bot_pw)
	wm_bot.login()
	title_list = [zone.get_wiki_title() for zone in zone_obj_list]
	token_dict = {}
	for list_chunk in chunks(title_list,500):
		token_dict.update(wm_bot.get_edit_tokens(list_chunk))
	for zone in zone_obj_list:
		if zone.name not in EXCLUDED_ZONES:
			#print zone.get_wiki_title(),zone.get_wiki_page(),token_dict[zone.get_wiki_title()]
			pprint.pprint(wm_bot.edit_page(zone.get_wiki_title(),zone.get_wiki_page(),token_dict[zone.get_wiki_title()]))
	print "Done!"
	
if __name__ == "__main__":
	try:
		main()

	except Exception, e:
		import traceback
		print traceback.print_exc()