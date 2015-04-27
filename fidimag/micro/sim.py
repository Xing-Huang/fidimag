import fidimag

KNOWN_DRIVERS = {'llg': fidimag.micro.llg.LLG,
                 'llg_stt': fidimag.micro.llg_stt.LLG_STT, 
                 'llbar': fidimag.baryakhtar.LLBar,
                 'llbar_full': fidimag.baryakhtar.LLBarFull}

def Sim(*args, **kwargs):
    
    driver = 'llg'
    
    if kwargs.has_key('driver'):
        driver = kwargs['driver']
        kwargs.pop('driver')
    
    if driver not in KNOWN_DRIVERS:
        raise NotImplementedError("""Driver '{}' is not implemented.
                                  Valid choices: one of '{}'.""".format(driver, KNOWN_DRIVERS.keys()))
    
    return KNOWN_DRIVERS[driver](*args, **kwargs)
