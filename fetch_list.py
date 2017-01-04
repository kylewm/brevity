import pprint
import requests
import json

r = requests.get('http://data.iana.org/TLD/tlds-alpha-by-domain.txt')
lines = r.text.splitlines()
tlds = ["'" + line.lower() + "'" for line in lines if not line.startswith('#')]

print('[' + ', '.join(tlds) + ']')

# make a prefix tree

tree = {}

for tld in tlds:
    branch = tree
    for letter in tld:
        branch = branch.setdefault(letter, {})
    branch['$'] = {}

#with(open('tree.json', 'w')) as f:
#    json.dump(tree, f, indent=True)

# build a regex

def build_regex(branch):
    choices = []
    suffix = ''

    if '$' in branch:
        suffix = '?'

    for letter in sorted(branch):
        if letter != '$':
            choice = letter + build_regex(branch[letter])
            choices.append(choice)

    if not choices:
        return ''
    if len(choices) == 1 and not suffix:
        return choices[0]
    return '(?:' + '|'.join(choices) + ')' + suffix


re = build_regex(tree)
print(re)
