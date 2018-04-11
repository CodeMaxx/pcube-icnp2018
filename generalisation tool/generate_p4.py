import sys
import os
import re
from collections import OrderedDict
from pyparsing import Word, alphas, nums, nestedExpr, Keyword, alphanums, Regex, White, Optional

keywords = {
	'for'	:	'@for',
	'endfor':	'@endfor',
	'compare'	:	'@compare',
	'endcompare':	'@endcompare',
	'case'	:	'@case',
	'endcase':	'@endcase',
	'sum'	:	'@sum'
}

constants = {}

def roll_out_forloop(content,iter_var,dfile,start,end,step):
	replacement = '$%s' % iter_var

	for i in range(start,end,step):
		dfile.write(content.replace(replacement,str(i)))

def ip4_to_p4(src,dest):

	active_for = False 
	iter_var = None
	start,end,step = None,None,None
	content = ""

	with open(dest,'w') as dfile:
		with open(src,'r') as sfile:
			for row in sfile:
				if '#define' in row:
					tokens = row.split()
					constants[tokens[1]] = int(tokens[2])
				if active_for or keywords['for'] in row:
					if keywords['for'] in row:
						active_for = True
						tokens = row.split()
						iter_var = re.search(r'\((.*)\)',tokens[1]).group(1)
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

	ip4_to_p4(src, destfor)
	expand_compare(destfor, destcmp)
	expand_sum(destcmp, dest)
	generate_basic_commands(dest)

	for f in tempfiles:
		os.system('rm -f %s' % f)
