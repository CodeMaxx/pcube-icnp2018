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
import json
from collections import OrderedDict
# For recognising the ???
from pyparsing import Word, alphas, nums, nestedExpr, Keyword, alphanums, Regex, White, Optional

import fileinput

# Kept a global for clarity on what all features are present
# and also prevent hardcoding of tokens in the code

KEYWORDS = {
    'for'		:	'@for',
    'endfor'	:	'@endfor',
    'compare'	:	'@compare',
    'endcompare':	'@endcompare',
    'case'		:	'@case',
    'endcase'	:	'@endcase',
    'sum'		:	'@sum',
    'bool'      :   '@bool'
}

TOPO_DATA = None

class p4_code_generator():

    def __init__(self, switch_id, src, dest):
        self.switch_id = switch_id
        self.string_id = 's%d'%switch_id
        self.src = src
        self.destfor = dest + ".for"
        self.destcmp = dest + ".cmp"
        self.destsum = dest + ".sum"
        self.tempfiles = [self.destfor, self.destfor + ".bak", self.destcmp, self.destsum]
        self.dest = dest
        self.constants = {
            "MCAST_GRP": switch_id
        }
    
    def expand(self):
        self.expand_for()
        self.replace_constants()
        self.expand_compare()
        self.expand_sum()
        self.expand_bool()
        self.generate_commands_template()
        for f in self.tempfiles:
            os.system('rm -f %s' % f)

    # Replaces the ip4 for loop format by sequential p4 code
    def roll_out_forloop(self,content,iter_var,dfile,start,end,step):
        # For replacing all occurances of the loop variable in the code.
        replacement = '$%s' % iter_var

        for i in range(start,end,step):
            dfile.write(content.replace(replacement,str(i)))

    # Recognises all for loops present in the code along with their parameters
    # Nesting of loops not supported since it's not a common feature required in P4 programming
    # TODO: Can use pyparsing code just like in all other functions
    def expand_for(self):
        # Recognises if we are in a for loop
        active_for = False
        # The iteration variable
        iter_var = None
        # range(start, end, step)
        start,end,step = None,None,None
        # Content of the loop
        content = ""

        sfile = open(self.src,'r')
        dfile = open(self.destfor,'w')
        
        # Can read in any #define constant and replaces them if present as a parameter for `for` loop
        # For e.g. Number of servers

        # Loop through ip4 source
        for row in sfile:
            # Collect CONSTANTS
            if '#define' in row:
                _, var_name, val = row.split()
                # if var_name in self.constants :
                #     val = self.constants[var_name]
                # elif var_name in TOPO_DATA["topo_stats"][self.string_id]:
                #     val = TOPO_DATA["topo_stats"][self.string_id][var_name]

                self.constants[var_name] = int(val)
                define_string = "#define %s %d\n"
                dfile.write(define_string%(var_name,int(val)))

            # If we are entering a for loop or already in one
            elif active_for or KEYWORDS['for'] in row:
                # If starting a for loop
                if KEYWORDS['for'] in row:
                    active_for = True
                    tokens = row.split()
                    # Get the lexeme used as iteration variable
                    iter_var = re.search(r'\((.*)\)',tokens[1]).group(1)
                    # 
                    res = re.search(r'\[(.*),(.*),(.*)\]',tokens[2].rstrip('\n'))
                    try:
                        start, end, step = int(res.group(1)), int(res.group(2)), int(res.group(3))
                    except:
                        start, end, step = int(res.group(1)), self.constants[res.group(2)], int(res.group(3))

                elif KEYWORDS['endfor'] in row:
                    # print(content)
                    self.roll_out_forloop(content,iter_var,dfile,start,end,step)
                    active_for = False
                    content = ""
                else:
                    content += row
            else:
                dfile.write(row)

        sfile.close()
        dfile.close()
        self.replace_constants()

    def replace_constants(self):
        for key, value in self.constants.items():
            with fileinput.FileInput(self.destfor, inplace=True, backup='.bak') as file:
                for line in file:
                    print(line.replace(key, str(value)), end='')


    def roll_out_compare(self,varlist, op, dfile):
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

    def expand_compare(self):
        sfile = open(self.destfor, 'r')
        dfile = open(self.destcmp, 'w')

        compare_format = Keyword(KEYWORDS['compare']) + '(' + Word(nums)("num") + \
                ')' + '(' + Regex(r'[^\s\(\)]*')('op') + ')' 
        case_var_format = Word(alphas+"_", alphanums+"_"+".")('var')
        case_format = Keyword(KEYWORDS['case']) + case_var_format + ":"

        for line in sfile:
            if KEYWORDS['compare'] in line:
                # import pdb; pdb.set_trace()
                res = compare_format.parseString(line)
                num = int(res.num)
                op = res.op
                varlist = OrderedDict()
                while num:
                    l = sfile.readline()
                    # import pdb; pdb.set_trace()
                    res = case_format.parseString(l)
                    var = res.var
                    varlist[var] = ''
                    lcase = sfile.readline()
                    content = ''
                    while KEYWORDS['endcase'] not in lcase:
                        content += lcase
                        lcase = sfile.readline()
                    varlist[var] = content
                    num -= 1
                    # except:
                    # 	# import pdb; pdb.set_trace()
                    # 	l = sfile.readline()
                lcompare = sfile.readline()
                while KEYWORDS['endcompare'] not in lcompare:
                    lcompare = sfile.readline()
                self.roll_out_compare(varlist, op, dfile)
            else:
                dfile.write(line)
            
        sfile.close()
        dfile.close()

    def expand_sum(self):
        sfile = open(self.destcmp, 'r')
        dfile = open(self.destsum, 'w')

        sum_format = Keyword(KEYWORDS['sum']) + '(' + Word(nums)("start") + "," + Word(nums)("end") + ')' \
                        + '(' + Regex(r'[^\s\(\)]*')("var") + ')'
        line_sum_format = Regex(r'[^\@]*')("before") + sum_format + Regex(r'[^\@]*')("after")
        
        for line in sfile:
            if KEYWORDS['sum'] in line:
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
    
    def expand_bool(self):
        sfile = open(self.destsum, 'r')
        dfile = open(self.dest, 'w')

        bool_format = Keyword(KEYWORDS['bool']) + '(' + Word(nums)("start") + "," + Word(nums)("end") + ","      + Word(nums)("jump") + ')' + '(' + Regex(r'[^\s\(\)]*')('op') + ')' + '(' + Regex(r'[^\s\(\),]*')("var") + "," + Regex(r'[^\s\(\),]*')("operand") + ')'
        line_bool_format = Regex(r'[^\@]*')("before") + \
            bool_format + Regex(r'[^\@]*')("after")

        for line in sfile:
            if KEYWORDS['bool'] in line:
                # import pdb; pdb.set_trace()
                res = line_bool_format.parseString(line)
                start = int(res.start)
                end = int(res.end)
                jump = int(res.jump)
                var = res.var
                operand = res.operand
                op = res.op

                replacement = res.before
                for i in range(start, end, jump):
                    replacement +=  "%s %s %s and " % (var.replace("$i", str(i)), op, operand)
                replacement = replacement[:-5] + res.after
                dfile.write(replacement)
            else:
                dfile.write(line)

        sfile.close()
        dfile.close()

    def generate_commands_template(self):
        sfile = open(self.dest, 'r')
        dfile = open('commands_template_merged_%s.txt'%self.string_id, 'w')
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

def get_topo_data():
    with open('topo.json','r') as f:
        data = json.load(f)
    return data

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Format: python3 %s <filename>.ip4" % sys.argv[0])
        sys.exit()

    TOPO_DATA = get_topo_data()
    num_switches = TOPO_DATA["nb_switches"]

    src = sys.argv[1]
    
    filename = src[:-4]

    for i in range(1, num_switches + 1):
        dest = "%s_s%d.p4" % (filename,i)
        code_gen = p4_code_generator(i,src,dest)
        code_gen.expand()
