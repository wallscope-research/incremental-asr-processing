import re
import sys
from os import listdir, mkdir,path,walk
from os.path import isfile, join

regexF = 'regexes.txt'
corpus_folder = 'swbda-corpus'
out_folder = 'out'
regexes = {}
params = ['-res', '-fp', '-ns']


def init():
    load_regexes()


def turns(file_name, speaker):
    """Returns a generator over all turns from speaker in file. speaker is either A or B"""
    with open(file_name) as f:
        line = f.readline()
        while line:
            line = f.readline()
            stripped = line.strip()
            turn_pattern = re.compile(regexes['turn'])
            match = turn_pattern.search(stripped)
            if match and (match.group(1) == speaker):
                yield match.group(2).strip()


def slash_units(file_name, speaker):
    """Returns a generator over all Slash Units from speaker in file. speaker is either A or B"""
    turns_iter = turns(file_name, speaker)
    turn = next(turns_iter)
    while True:
        # concatenating with subsequent turns until all slash units complete
        complete_turn = ''
        while not turn.endswith(('/', '-/', '- /')):
            complete_turn = complete_turn + ' ' + turn
            try:
                turn = next(turns_iter)
            except StopIteration:
                break

        complete_turn = complete_turn + ' ' + turn

        for su in re.split(regexes['slash'], complete_turn):
            if su:
                yield su

        try:
            turn = next(turns_iter)
        except StopIteration:
            break


def rewrite_restarts(text):
    pattern = re.compile('\[ ([^\]\[]+) \+ ([^\]\[]*)\]')

    result = text
    if '-res' in params:
        replaced = pattern.sub("\g<2>", result)
    else:
        replaced = pattern.sub("\g<1> \g<2>", result)

    while replaced != result:
        result = replaced
        if '-res' in params:
            replaced = pattern.sub("\g<2>", result)
        else:
            replaced = pattern.sub("\g<1> \g<2>", result)

    return result


def remove_non_speech(text):
    pattern = re.compile(regexes['ns'])
    if '-ns' in params:
        return pattern.sub('', text)
    return text


def remove_fillers(text):
    pattern = re.compile(regexes['fp'])
    if '-fp' in params:
        return pattern.sub('', text)
    else:
        return pattern.sub('\g<1>', text)


def remove_edit_terms(text):
    pattern = re.compile(regexes['et'])
    if '-et' in params:
        return pattern.sub('', text)
    else:
        return pattern.sub('\g<1>', text)


def remove_discourse_markers(text):
    pattern = re.compile(regexes['dm'])
    if '-dm' in params:
        return pattern.sub('', text)
    else:
        return pattern.sub('\g<1>', text)


def remove_coordinating_conjunctions(text):
    pattern = re.compile(regexes['cc'])
    if '-cc' in params:
        return pattern.sub('', text)
    else:
        return pattern.sub('\g<1>', text)


def remove_asides(text):
    pattern = re.compile(regexes['aside'])
    if '-a' in params:
        return pattern.sub('', text)
    else:
        return pattern.sub('\g<1>', text)


def clean_up(text):
    """removes every non-word token, e.g. # and all punctuation. Currently hardcoded
    :param text:
    :return: cleaned up text
    """
    # remove punctuation
    p = re.compile("[\\?\\.!#,]+")
    result = p.sub('', text)
    # remove dashes
    p = re.compile(" -+")
    result = p.sub('', result)
    # remove parantheses
    p = re.compile("[\(\)]+")
    result = p.sub('', result)
    # organise spaces
    p = re.compile("\\s+")
    result = p.sub(' ', result)
    return result

def process_slash_unit(text):
    """cleans text according to the parameters specified in global params
    :param text:
    :return: cleaned version of the slash unit
    """
    print("processing su: "+text)
    clean = rewrite_restarts(text)
    clean = remove_non_speech(clean)
    clean = remove_fillers(clean)
    clean = remove_edit_terms(clean)
    clean = remove_discourse_markers(clean)
    clean = remove_asides(clean)
    clean = remove_coordinating_conjunctions(clean)
    clean = clean_up(clean)
    print("processed: "+clean)
    return clean


def load_regexes():
    print('loading regexes ...')
    f = open(regexF)
    lines = f.readlines()
    for line in lines:
        line = line.strip()
        parts = line.split('#')
        if not (parts and parts[0]):
            continue

        stripped = parts[0].strip()
        key_value = stripped.split('::')
        regexes[key_value[0].strip()] = key_value[1].strip()
    print('loaded regexes.')


def process_corpus():
    """
    :param params: list of all parameters passed
    :return:
    """
    if not path.exists(corpus_folder):
        print('Error: corpus folder doesn\'t exist: '+corpus_folder)
        return -1

    try:
        # Create output Directory
        mkdir(out_folder)
        print("Output folder '" + out_folder + "' created ")
    except FileExistsError:
        print("Error: output folder '" + out_folder + "' already exists")
        return -2

    process_folder(corpus_folder)


def process_folder(folder):
    for (folder, folders, files) in walk(folder):
        for file in files:
            uttpat = re.compile(regexes['utt_file'])
            match = uttpat.match(file)
            if match:
                process_utt_file(join(folder, file))

        for fol in folders:
            process_folder(fol)


def process_utt_file(utt_file):
    print('processing '+utt_file)
    utt_file_name = path.split(utt_file)[1]
    with open(utt_file) as uf:

        # process slash units from A
        with open(join(out_folder, utt_file_name[0:len(utt_file_name)-4]+'-A.out'), '+w') as outA:
            for slash_unit in slash_units(utt_file, 'A'):
                outA.write(process_slash_unit(slash_unit)+'\n')

        # process slash units from B
        with open(join(out_folder, utt_file_name[0:len(utt_file_name)-4]+'-B.out'), '+w') as outB:
            for slash_unit in slash_units(utt_file, 'B'):
                outB.write(process_slash_unit(slash_unit)+'\n')


def print_usage():
    pass


def main():
    """Usage: python swb-tools.py -c <corpus folder> -o <output folder> -res -ns -fp -et -dm -cc -a
    command line parameters
    -c <corpus folder>: corpus location
    -o <output folder>: output folder
    -res: rewrite/clean repairs
    -ns: remove non-speech events
    -fp: remove filled pauses
    -et: remove edit terms
    -dm: remove discourse markers
    -a: remove aside
    """
    global params
    global out_folder
    global corpus_folder
    i = 1
    parameters = []
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == '-c':
            if i+1 < len(sys.argv) and not sys.argv[i+1].startswith('-'):
                corpus_folder = sys.argv[i+1]
                i = i + 2
                continue
            else:
                print('Usage Error')
                print_usage()
                return
        elif arg == '-o':
            if i+1 < len(sys.argv) and not sys.argv[i+1].startswith('-'):
                out_folder = sys.argv[i+1]
                i = i + 2
                continue
            else:
                print('Usage Error')
                print_usage()
                return
        elif arg.startswith('-'):
            parameters.append(arg)
        else:
            print('Usage Error')
            print_usage()
            return

        if parameters:
            params = parameters

    init()
    return process_corpus()


if __name__ == "__main__":
    main()


