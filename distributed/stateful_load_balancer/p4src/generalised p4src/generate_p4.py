import sys
import re

keywords = {
	'for'	:	'@for',
	'endfor':	'@endfor'	
}

def roll_out_forloop(content,iter_var,dfile,start,end,step):
	replacement = '$%s'%iter_var

	for i in range(start,end+1,step):
		dfile.write(content.replace(replacement,str(i)))

def ip4_to_p4(src,dest):

	active_for = False 
	iter_var = None
	start,end,step = None,None,None
	content = ""
	constants = {}

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
						iter_var = re.search('\((.*)\)',tokens[1]).group(1)
						res = re.search('\[(.*),(.*),(.*)\]',tokens[2].rstrip('\n'))
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



if __name__ == '__main__':
	if len(sys.argv) < 2:
		print("Format: python3 generate_p4 <filename>.ip4")
		exit()
	source_file = sys.argv[1]
	filename = source_file.split('.')[0]
	dest_file = "%s.p4"%filename
	ip4_to_p4(source_file,dest_file)