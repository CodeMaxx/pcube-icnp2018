import sys
import os
import re
from pyparsing import Word, alphas, nums, nestedExpr, Keyword, alphanums, Regex

keywords = {
	'for'	:	'@for',
	'endfor':	'@endfor',
	'compare'	:	'@compare',
	'endcompare':	'@endcompare',
	'case'	:	'@case',
	'endcase':	'@endcase'
}

constants = {}

def roll_out_forloop(content,iter_var,dfile,start,end,step):
	replacement = '$%s' % iter_var

	for i in range(start,end+1,step):
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
						start,end,step = int(res.group(1)),constants[res.group(2)],int(res.group(3))

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
				if j != var_keys[-1]:
					cond += ' and '
		condition[i] = cond

		if i == var_keys[0]:
			final += '%sif(%s) {\n%s\n%s}\n' % (spaces, cond, varlist[i], spaces)
		else:
			final += '%selse if(%s) {\n%s\n%s}\n' % (spaces, cond, varlist[i], spaces)
	
	dfile.write(final)

def expand_compare(src, dest):
	sfile = open(src, 'r')
	dfile = open(dest, 'w')
	compare_format = Keyword('@compare') + '(' + Word(nums)("num") + \
            ')' + '(' + Regex(r'[^\s\(\)]*')('op') + ')' 
	case_var_format = Word(alphas+"_", alphanums+"_"+".")('var')
	case_format = Keyword('@case') + case_var_format + ":"

	for line in sfile:
		if keywords['compare'] in line:
			res = compare_format.parseString(line)
			num = int(res.num)
			op = res.op
			varlist = {}
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


def generate_basic_commands(src, dest):
	sfile = open(src, 'r')
	dfile = open(dest, 'w')




if __name__ == '__main__':
	if len(sys.argv) < 2:
		print("Format: python3 %s <filename>.ip4" % sys.argv[0])
		sys.exit()
	src = sys.argv[1]
	tempfiles = []
	filename = src[:-4]
	destfor = "%s.forp4" % filename
	tempfiles.append(destfor)
	destcmp = "%s.cmpp4" % filename
	# tempfiles.append(destcmp)
	dest = "%s.p4" % filename
	ip4_to_p4(src, destfor)
	expand_compare(destfor, dest)
	for f in tempfiles:
		os.system('rm -f %s' % f)
