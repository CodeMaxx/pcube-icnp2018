#!/usr/bin/env python3

# Copyright 2018-present Akash Trehan Aniket Shirke
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

########################################################
# 1. Convert ip4 format to p4
########################################################

import sys
import os
import re
from collections import OrderedDict
# For recognising the 
from pyparsing import Word, alphas, nums, nestedExpr, Keyword, alphanums, Regex, White, Optional

# Kept a global for clarity on what all features are present
# and also prevent hardcoding of tokens in the code

keywords = {
	'for'	:	'@for',
	'endfor':	'@endfor',
	'compare'	:	'@compare',
	'endcompare':	'@endcompare',
	'case'	:	'@case',
	'endcase':	'@endcase',
	'sum'	:	'@sum'
}

# TODO: Wrap code into a class

# Can read in any #define constant and replaces them if present as a parameter for `for` loop
# For e.g. Number of servers
# TODO: Do an initial pass for constants so that they can be used in all features not just loops
constants = {}

# Replaces the ip4 for loop format by sequential p4 code
def roll_out_forloop(content,iter_var,dfile,start,end,step):
	# For replacing all occurances of the loop variable in the code.
	replacement = '$%s' % iter_var

	for i in range(start,end,step):
		dfile.write(content.replace(replacement,str(i)))

# Recognises all for loops present in the code along with their parameters
# Nesting of loops not supported since it's not a common feature required in P4 programming
# TODO: Can use pyparsing code just like in all other functions
def expand_for(src,dest):
	# Recognises if we are in a for loop
	active_for = False
	# The iteration variable
	iter_var = None
	# range(start, end, step)
	start,end,step = None,None,None
	# Content of the loop
	content = ""

	with open(dest,'w') as dfile:
		with open(src,'r') as sfile:
			# Loop through ip4 source
			for row in sfile:
				# Collect constants
				if '#define' in row:
					tokens = row.split()
					constants[tokens[1]] = int(tokens[2])
				# If we are entering a for loop or already in one
				if active_for or keywords['for'] in row:
					# If starting a for loop
					if keywords['for'] in row:
						active_for = True
						tokens = row.split()
						# Get the lexeme used as iteration variable
						iter_var = re.search(r'\((.*)\)',tokens[1]).group(1)
						# 
						res = re.search(r'\[(.*),(.*),(.*)\]',tokens[2].rstrip('\n'))
						try:
							start, end, step = int(res.group(1)), int(res.group(2)), int(res.group(3))
						except:
							start, end, step = int(res.group(1)), constants[res.group(2)], int(res.group(3))

					elif keywords['endfor'] in row:
						# print(content)
						roll_out_forloop(content,iter_var,dfile,start,end,step)
						active_for = False
						content = ""
					else:
						content += row
				else:
					dfile.write(row)


def roll_out_compare(varlist, op, dfile):
	var_keys = list(varlist.keys())
	condition = {}
	final = ''
	a = varlist[var_keys[0]]
	spaces = ' '*(len(a) - len(a.lstrip(' ')) - 4)

	for i in var_keys:
		cond = ''
		for j in var_keys:
			if j != i:
				cond += "%s %s %s" % (i, op, j)
				if (i != var_keys[-1] and j != var_keys[-1]) or (i == var_keys[-1] and j != var_keys[-2]):
					cond += ' and '
		condition[i] = cond

		if i == var_keys[0]:
			final += '%sif(%s) {\n%s\n%s}\n' % (spaces, cond, varlist[i].rstrip('\n'), spaces)
		else:
			final += '%selse if(%s) {\n%s\n%s}\n' % (spaces, cond, varlist[i].rstrip('\n'), spaces)
	
	dfile.write(final)

def expand_compare(src, dest):
	sfile = open(src, 'r')
	dfile = open(dest, 'w')
	compare_format = Keyword(keywords['compare']) + '(' + Word(nums)("num") + \
            ')' + '(' + Regex(r'[^\s\(\)]*')('op') + ')' 
	case_var_format = Word(alphas+"_", alphanums+"_"+".")('var')
	case_format = Keyword(keywords['case']) + case_var_format + ":"

	for line in sfile:
		if keywords['compare'] in line:
			res = compare_format.parseString(line)
			num = int(res.num)
			op = res.op
			varlist = OrderedDict()
			while num:
				l = sfile.readline()
				# import pdb; pdb.set_trace()
				# try:
				res = case_format.parseString(l)
				var = res.var
				varlist[var] = ''
				lcase = sfile.readline()
				content = ''
				while keywords['endcase'] not in lcase:
					content += lcase
					lcase = sfile.readline()
				varlist[var] = content
				num -= 1
				# except:
				# 	# import pdb; pdb.set_trace()
				# 	l = sfile.readline()
			lcompare = sfile.readline()
			while keywords['endcompare'] not in lcompare:
				lcompare = sfile.readline()
			roll_out_compare(varlist, op, dfile)
		else:
			dfile.write(line)
		
	sfile.close()
	dfile.close()


def generate_basic_commands(src):
	sfile = open(src, 'r')
	dfile = open('basic_commands.txt', 'w')
	open_brac = Optional(White()) + "{" + Optional(White())
	close_brac = Optional(White()) + "}" + Optional(White())
	actions_format = Keyword('actions') + open_brac + Word(alphas + "_", alphanums+"_")('default_action') \
            + ";" + Regex(r'[^\}\{]*') + close_brac
	reads_format = Keyword('reads') + open_brac + Regex(r'[^\}\{]*') + close_brac
	table_format = Keyword('table') + Word(alphas+"_", alphanums+"_")('table_name') + open_brac \
            + Optional(reads_format) + actions_format + \
            Optional(reads_format) + Regex(r'[^\}\{]*') + close_brac
	sfile_str = sfile.read()
	res = table_format.searchString(sfile_str)
	
	for table in res:
		dfile.write('table_set_default %s %s\n' % (table.table_name, table.default_action))
	
	sfile.close()
	dfile.close()


def expand_sum(src, dest):
	sfile = open(src, 'r')
	dfile = open(dest, 'w')

	sum_format = Keyword(keywords['sum']) + '(' + Word(nums)("start") + "," + Word(nums)("end") + ')' \
					+ '(' + Regex(r'[^\s\(\)]*')("var") + ')'
	line_sum_format = Regex(r'[^\@]*')("before") + sum_format + Regex(r'[^\@]*')("after")
	
	for line in sfile:
		if keywords['sum'] in line:
			# import pdb; pdb.set_trace()
			res = line_sum_format.parseString(line)
			start = int(res.start)
			end = int(res.end)
			var = res.var

			replacement = res.before
			for i in range(start, end):
				replacement += var.replace("$i", str(i)) + " + "
			replacement = replacement[:-3] + res.after
			dfile.write(replacement)
		else:
			dfile.write(line)
	
	sfile.close()
	dfile.close()


if __name__ == '__main__':
	if len(sys.argv) < 2:
		print("Format: python3 %s <filename>.ip4" % sys.argv[0])
		sys.exit()
	src = sys.argv[1]
	tempfiles = []
	filename = src[:-4]
	destfor = "%s.forp4" % filename
	destcmp = "%s.cmpp4" % filename
	dest = "%s.p4" % filename

	tempfiles.append(destfor)
	tempfiles.append(destcmp)

	expand_for(src, destfor)
	expand_compare(destfor, destcmp)
	expand_sum(destcmp, dest)
	generate_basic_commands(dest)

	for f in tempfiles:
		os.system('rm -f %s' % f)
