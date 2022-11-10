import os, json
from utils import portalContentFolder, scrub_unicode

id = "636c926661b743e4af86ab68757a8f98" # File known to be bad
input_file = os.path.join(portalContentFolder, id, id)
clean_output = os.path.join("C:/Temp", id + '.json')

# read the string with its nonbreak space and its annoying A
with open(input_file, "r", encoding="utf-8") as fp:
    raw = fp.read()

# convert to json
#j = json.loads(raw)
# minify
#mini = json.dumps(j,separators=(',',':'))

# This replaces actual honest to god unicode characters
clean = raw.replace('\u00c2','').replace('\u00a0',' ')

# This replaces the string representation of unicode, huh? Well yeah.
clean = clean.replace('\\u00c2','').replace('\\u00a0',' ')

if raw == clean:
    print("Nothing changed.")

with open(clean_output, 'w', encoding='utf-8') as fp:
    fp.write(clean)

print("We're so done here.")

#j = json.loads(raw) # pull into a dict
#cleaned = json.dumps(j, indent=2) # make dict back into a string
#stripped = raw.replace('\u00c2', '') # strip out A/circumflex
#print(len(raw), len(stripped))

