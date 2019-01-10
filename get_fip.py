import sys


'------------------------------------------'
"process source_file to get fips"
'------------------------------------------'
"neutron floatingip-list > source_file"
"python get_fip.py   source_fil   out_file"
"default out_file name is all_fips"
'-----------------------------------------'

source_file = sys.argv[1]

with open(source_file, "r") as f:
    all_str = f.read()
    f.close()

result = []
all_str_list = all_str.split()
for elm in all_str_list:
    if '186.30' in elm:
        result.append(elm)

final_str = '\n'.join(result)

out_name = 'all_fips'
if len(sys.argv) == 3:
    out_name = sys.argv[2]

with open(out_name, 'w') as f:
    f.write(final_str)
    f.close()



