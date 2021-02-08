# ==============================
# Helper functions for general usage
# ==============================

import re

def read_key_for_year(key, year):
    '''Helper function to get if the given key is going to be used for the given year.'''
    if year == 2017:
      return '17' in key
    elif year == 2018:
      return '18' in key
    raise RuntimeError('Year not recognized: {}'.format(year))

def get_nuisance_name(nuisance, year):
    '''Return the modified nuisance name for the given nuisance (to match with the content in datacard).'''
    name=None
    if str(year) in nuisance:
        tmp = nuisance.split('_')[-2:]
        name = '_'.join(tmp)
    else:
        name = nuisance.split('_')[-1]

    if not name:
        raise RuntimeError('Could not determine a valid name for nuisance: {}'.format(nuisance))

    # Remove "up/down" tag from the nuisance name
    name = re.sub('Up|Down', '', name)
 
    return name

def extract_year(category):
    m = re.match(".*(201\d).*", category)
    assert(m)
    groups = m.groups()
    assert(len(groups)==1)
    return groups[0]

def extract_channel(category):
    channels = ['monojet','monov','vbf']
    matches = [c for c in channels if c in category]
    assert(len(matches)==1)
    return matches[0]

def is_MC_bkg(name):
    model_bkg_list = [
            "signal_zjets",
            "signal_wjets",
            "gjets_gjets",
            "wen_wjets",
            "wmn_wjets",
            "zee_zll",
            "zmm_zll",
            "signal_qcd",
            "gjets_qcd",
            ]
    if name in model_bkg_list:
        return False
    else:
        return True
