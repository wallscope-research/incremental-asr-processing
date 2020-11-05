import sys
import re
import json

directory = sys.argv[1]
code = re.search(r"[0-9]{4}", directory).group(0)

full_transcript = []
a_transcript = []
b_transcript = []

file_a = directory + "sw" + code + "A-ms98-a-word.text"
file_b = directory + "sw" + code + "B-ms98-a-word.text"

with open(file_a, 'r') as a:
    for row in a:
        line = row.split()
        ws_time = float(line[1])
        we_time = float(line[2])
        if line[3].startswith("["):
            if line[3].startswith("[laughter-"):
                word = re.search(r"(?<=\[laughter-)(.*?)(?=\])", line[3]).group(0).lower()
                full_transcript.append({'ws':ws_time, 'we':we_time, 'Word':word})
                a_transcript.append({'ws':ws_time, 'we':we_time, 'Word':word})
        else:
            word = line[3].replace("[", "").replace("]", "").replace("{", "").replace("}", "").replace("-", "").replace("_", "").lower()
            # word = ''.join([i for i in word if not i.isdigit()])
            full_transcript.append({'ws':ws_time, 'we':we_time, 'Word':word})
            a_transcript.append({'ws':ws_time, 'we':we_time, 'Word':word})

with open(file_b, 'r') as b:
    for row in b:
        line = row.split()
        ws_time = float(line[1])
        we_time = float(line[2])
        if line[3].startswith("["):
            if line[3].startswith("[laughter-"):
                word = re.search(r"(?<=\[laughter-)(.*?)(?=\])", line[3]).group(0).lower()
                full_transcript.append({'ws':ws_time, 'we':we_time, 'Word':word})
                b_transcript.append({'ws':ws_time, 'we':we_time, 'Word':word})
        else:
            word = line[3].replace("[", "").replace("]", "").replace("{", "").replace("}", "").replace("-", "").replace("_", "").lower()
            # word = ''.join([i for i in word if not i.isdigit()])
            full_transcript.append({'ws':ws_time, 'we':we_time, 'Word':word})
            b_transcript.append({'ws':ws_time, 'we':we_time, 'Word':word})

ordered = sorted(full_transcript, key=lambda k: k['ws'])

joined_transcript = ""
a_joined = ""
b_joined = ""

for item in ordered:
    joined_transcript = joined_transcript + item['Word'] + " "

for aword in a_transcript:
    a_joined = a_joined + aword['Word'] + " "

for bword in b_transcript:
    b_joined = b_joined + bword['Word'] + " "

full_outfile = "./joined/full/" + code + "-full-joined-transcript.txt"
a_outfile = "./joined/a/" + code + "-A-joined-transcript.txt"
b_outfile = "./joined/b/" + code + "-B-joined-transcript.txt"
timings_outfile = "./joined/timings/" + code + "-full-transcript.json"

with open(full_outfile, 'w') as fo:
    fo.write(joined_transcript)

with open(a_outfile, 'w') as ao:
    ao.write(a_joined)

with open(b_outfile, 'w') as bo:
    bo.write(b_joined)

with open(timings_outfile, 'w') as tof:
    json.dump(ordered, tof)