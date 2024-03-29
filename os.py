import argparse
import os
import datetime as dt
import sys
import re

parser = argparse.ArgumentParser()

# Vault is required or at least has a default
# todo is optional and defaults to false
# recent is optional and defaults to 7 days and lookback is optional

parser.add_argument("-v","--vault", help="Name of the vault", default="homeGyaan")
parser.add_argument("--todo", help="Write todos to file", action="store_true")
parser.add_argument("--recent", help="Write recent files to file", action="store_true")
parser.add_argument("-d","--days", help="Number of days to look back", default=7)

args = parser.parse_args()

home = os.path.expanduser("~")
BASE_DIR = home+"/Vaults/"+args.vault+"/"
print('Using the vault ',BASE_DIR)


def convert_path_to_links(_path):
    # Return None if not a valid link
    if _path.endswith('todos.md') or _path.endswith('recent_files.md') or _path.endswith('unlinked.md'):
        return None
    if not _path.endswith('.md'):
        return None
    _link = _path.split('/')[-1]
    _link = _link.replace('.md','')
    return "[[" + _link + "]]"

def get_recent_files(num_days_lookback):
    now = dt.datetime.now()
    ago = now-dt.timedelta(days=num_days_lookback)
    modified_files_list = []
    for root, dirs,files in os.walk(BASE_DIR):
        for fname in files:
            path = os.path.join(root, fname)
            st = os.stat(path)
            mtime = dt.datetime.fromtimestamp(st.st_mtime)
            if mtime > ago:
                modified_files_list.append(path)
    return modified_files_list


def write_recent_files(num_days_lookback):
    f = open(BASE_DIR + 'recent_files.md','w')
    print('Writing recent files with a',str(num_days_lookback),'day lookback to file : ',BASE_DIR + 'recent_files.md')
    modified_files_list = get_recent_files(num_days_lookback)
    for file in modified_files_list:
        link = convert_path_to_links(file)
        if link is not None:
            f.write(link + '\n')


def write_todos():
    todos = []
    for root, dirs,files in os.walk(BASE_DIR):
        for fname in files:
            path = os.path.join(root, fname)
            link = convert_path_to_links(path)
            if link is None:
                continue
            with open(path,'r') as in_file:
                for line in in_file:
                    line = line.strip()
                    if line.find('- [ ]') != -1 :
                        todos.append(line + '\t' + link)
    f = open(BASE_DIR + 'todos.md','w')
    todos.sort()
    print('Writing todos to file : ',BASE_DIR + 'todos.md')
    for todo in todos:
        f.write(todo + '\n')


def get_links_in_file(_path):
    _links = [] 
    with open(_path,'r') as in_file:
        for line in in_file:
            line = line.strip()
            r1 = re.findall(r"\[\[(.*?)\]\]",line)
            if len(r1) > 0:
                for tok in r1:
                    _links.append('[['+tok+']]')
    return _links


def write_orphan_files():
    zero_length_files, non_zero_length_files, links = [], [], []
    backlinks = set()

    for root, dirs,files in os.walk(BASE_DIR):  
        for fname in files:
            path = os.path.join(root, fname)
            link = convert_path_to_links(path)
            if link is None:
                continue
            if os.path.getsize(path) == 0:
                zero_length_files.append(link)
            else:
                non_zero_length_files.append(link)
                links = get_links_in_file(path)
                for link in links: 
                    backlinks.add(link)

    with open(BASE_DIR + 'unlinked.md','w') as out_file:
        out_file.write('### Zero-Length Files\n\n')
        zero_length_files.sort()
        non_zero_length_files.sort()
        for _f in zero_length_files:
            out_file.write(_f+'\n')
        out_file.write('\n\n### Unlinked Files\n\n')
        for _f in non_zero_length_files:
            if _f not in backlinks:
                out_file.write(_f + '\n')


if '__main__' == __name__:
    if args.todo:
        write_todos()
    if args.recent:
        write_recent_files(int(args.days))
    if not args.todo and not args.recent:
        print('Please specific action to take on vault. Use --help for more info')

#if mode == "recent":
#    write_recent_files(lookback)
#elif mode == "todo":
#    write_todos()
#elif mode == "clean":
#    write_orphan_files()
