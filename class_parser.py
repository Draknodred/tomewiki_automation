import glob
import os
import collections
import re

class_name_regex = '(?<!,)name = "([^"]*)",'
talent_types_regex = '(?:\["([^\/]*\/[^"]*)"\][^.]*?{(true|false),[^\d]*?(-?\d.\d|-?\d)})'
stats_regex = 'stats = {([^}]*)},'

EXCLUDED_CLASSES = ["Psion"]

class TalentInfo(object):
  def __init__(self,tree_name,unlocked,mastery_addition):
		self.name = tree_name
		self.unlocked = unlocked
		self.mastery_addition = mastery_addition
		self.mastery = 1.0 + float(self.mastery_addition)
	
	@classmethod
	def init_from_regex(cls,regex_result):
		return cls(regex_result[0],regex_result[1],regex_result[2])
	
	def __repr__(self):
		return "<"+self.name+", "+self.unlocked+", "+str(self.mastery)+">"

def check_class_name(class_name,line_str):
	result = re.search(class_name_regex,line_str)
	if result:
		return result.group(1)
	else:
		return class_name

def check_talent(line_str):
	result = re.search(talent_types_regex,line_str)
	if result:
		return result.groups()
	else:
		return None

def check_stats(line_str):
	result = re.search(stats_regex,line_str)
	if result:
		return result.group(1)
	else:
		return None

def process_class_file(class_talent_dict,stat_dict,filename):
	with open(filename,'rb') as fn:
		class_name = None
		for line in fn.readlines():
			class_name = check_class_name(class_name,line)
			if class_name and class_name not in EXCLUDED_CLASSES:
				talent_info = check_talent(line)
				stat_info = check_stats(line)
				if talent_info:
					talent_obj = TalentInfo.init_from_regex(talent_info)
					class_talent_dict[class_name].append(talent_obj)
				elif stat_info:
					stat_dict[class_name] = stat_info

def process_files(file_list):
	class_talent_dict = collections.defaultdict(list)
	stat_dict = {}
	for filename in file_list:
		process_class_file(class_talent_dict,stat_dict,filename)
	return class_talent_dict,stat_dict

def main(filepath):
	os.chdir(filepath)
	filelist = glob.glob("*.lua*")
	class_talents, class_stats = process_files(filelist)
	temp_write_out(filepath,class_talents,class_stats)

def temp_write_out(filepath,class_talents,class_stats):
	with open(filepath+r'\class_output.log','wb') as fn:
		for classname in class_talents:
			fn.write("==Class "+classname+"==\n")
			fn.write("Stats "+str(class_stats[classname])+"\n")
			for talent in class_talents[classname]:
				fn.write(str(talent)+"\n")

if __name__ == "__main__":
	try:
		filepath = r'C:\Stuff\tome4'
		print filepath
		main(filepath)
	except Exception,e:
		print e
		import traceback
		traceback.print_exc()
