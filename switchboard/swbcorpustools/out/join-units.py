import sys
import re

infile = sys.argv[1]

full_transcript = ""

with open(infile, 'r') as f:
    for line in f:
        clean = line.replace("\n", "").replace("*","").replace("[","").replace("]","").strip()
        full_transcript = full_transcript + clean + " "

code = re.search(r"_[0-9]{4}-", infile).group(0).replace("_", "").replace("-", "")
method = re.search(r"swbc(.*?)res", infile).group(0)
if "-A.out" in infile:
    speaker = "A"
elif "-B.out" in infile:
    speaker = "B"
outfile = "./joined/" + method + "/sw" + code + "-" + speaker + ".out"

with open(outfile, 'w') as o:
    o.write(full_transcript)