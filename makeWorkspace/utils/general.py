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
