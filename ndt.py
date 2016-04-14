import numpy as np

header = np.dtype({'names':   ['header'     , 'unknown_1', 'always_0x28',
                              'addr_palette', 'unknown_3', 'addr_names',
                              'unknown_4', 'unknown_5', 'unknown_6'],
                    'formats':['a6' , '<u2'  , '<u4'    ,
                              '<u4', '<u4', '<u4',
                              '<u4', '<u4', '<u4']})

palette = np.dtype({'names':  ['red', 'green','blue'],
                    'formats': ['u1', 'u1', 'u1']})

palettes = np.dtype({'names': ['entries'],
                     'formats': [(palette,256)]})

