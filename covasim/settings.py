'''
Define options for Covasim, mostly plotting and Numba options. All options should
be set using set() or directly, e.g.::

    cv.options(font_size=18)

To reset default options, use::

    cv.options('default')
'''

import os
import pylab as pl
import sciris as sc

# Only the class instance is public
__all__ = ['options']


#%% General settings

# Specify which keys require a reload
matplotlib_keys = ['backend', 'style', 'dpi', 'font_size', 'font_family']
numba_keys      = ['precision', 'numba_parallel', 'numba_cache']

default_fonts = ['Arial', 'Liberation Sans', 'DejaVu Sans', 'sans-serif']

# Define simple plotting options -- similar to Matplotlib default
rc_simple = {
    'figure.facecolor': 'white',
    'axes.spines.right': False,
    'axes.spines.top': False,
    'font.family': 'sans-serif',
    'font.sans-serif': ['Muli'] + default_fonts,
    'legend.frameon': False,
}

# Define default plotting options -- based on Seaborn
rc_covasim = sc.mergedicts(rc_simple, {
    'axes.facecolor': 'efefff',
    'axes.grid': True,
    'grid.color': 'white',
    'grid.linestyle': '-',
    'grid.linewidth': 1,
    'font.sans-serif': ['Rosario', 'Muli'] + default_fonts,
})


#%% Define the options class

class Options(dict):
    '''
    Set options for Covasim. Use ``cv.options.set('defaults')`` to reset all
    values to default, or ``cv.options.set(dpi='default')`` to reset one parameter
    to default. See ``cv.options.help()`` for more information.

    Args:
        key    (str):    the parameter to modify, or 'defaults' to reset everything to default values
        value  (varies): the value to specify; use None or 'default' to reset to default
        kwargs (dict):   if supplied, set multiple key-value pairs

    Options are (see also ``cv.options.help()``):

        - verbose:        default verbosity for simulations to use
        - style:          the plotting style to use
        - font_size:      the font size used for the plots
        - font_family:    the font family/face used for the plots
        - dpi:            the overall DPI for the figure
        - show:           whether to show figures
        - close:          whether to close the figures
        - backend:        which Matplotlib backend to use
        - interactive:    convenience method to set show, close, and backend
        - precision:      the arithmetic to use in calculations
        - numba_parallel: whether to parallelize Numba functions
        - numba_cache:    whether to cache (precompile) Numba functions

    **Examples**::

        cv.options.set('font_size', 18) # Larger font
        cv.options.set(font_size=18, show=False, backend='agg', precision=64) # Larger font, non-interactive plots, higher precision
        cv.options.set(interactive=False) # Turn off interactive plots
        cv.options.set('defaults') # Reset to default options
        cv.options.set('jupyter') # Defaults for Jupyter

    | New in version 3.1.1: Jupyter defaults
    | New in version 3.1.2: Updated plotting styles; refactored options as a class
    '''

    def __init__(self):
        super().__init__()
        self._set_default_options()
        self.orig_options = sc.dcp(self.options)
        self.load_custom_fonts() # Load custom fonts on module import
        return

    # Overwrite dictionary methods with the options dict rather than the base class
    def __getitem__( self, *args, **kwargs): return self.options.__getitem__( *args, **kwargs)
    def __setitem__( self, *args, **kwargs): return self.options.__setitem__( *args, **kwargs)
    def __contains__(self, *args, **kwargs): return self.options.__contains__(*args, **kwargs)
    def __len__(     self, *args, **kwargs): return self.options.__len__(     *args, **kwargs)
    def get(         self, *args, **kwargs): return self.options.get(         *args, **kwargs)
    def items(       self, *args, **kwargs): return self.options.items(       *args, **kwargs)
    def keys(        self, *args, **kwargs): return self.options.keys(        *args, **kwargs)
    def setdefault(  self, *args, **kwargs): return self.options.setdefault(  *args, **kwargs)
    def update(      self, *args, **kwargs): return self.options.update(      *args, **kwargs)
    def values(      self, *args, **kwargs): return self.options.values(      *args, **kwargs)


    def __call__(self, *args, **kwargs):
        '''Allow ``cv.options(dpi=150)`` instead of ``cv.options.set(dpi=150)`` '''
        return self.set(*args, **kwargs)


    def __repr__(self):
        output = 'Covasim options (see also cv.options.help()):\n'
        for k,v in self.items():
            output += f'  {k:>12s}: {repr(v)}\n'
        return output


    def _set_default_options(self):
        '''
        Set the default options for Covasim -- not to be called by the user, use
        ``cv.options.set('defaults')`` instead.
        '''

        # Options acts like a class, but is actually an objdict for simplicity
        optdesc = sc.objdict() # Help for the options
        options = sc.objdict() # The options

        optdesc.verbose = 'Set default level of verbosity (i.e. logging detail)'
        options.verbose = float(os.getenv('COVASIM_VERBOSE', 0.1))

        optdesc.sep = 'Set thousands seperator for text output'
        options.sep = str(os.getenv('COVASIM_SEP', ','))

        optdesc.show = 'Set whether or not to show figures (i.e. call pl.show() automatically)'
        options.show = int(os.getenv('COVASIM_SHOW', True))

        optdesc.close = 'Set whether or not to close figures (i.e. call pl.close() automatically)'
        options.close = int(os.getenv('COVASIM_CLOSE', False))

        optdesc.backend = 'Set the Matplotlib backend (use "agg" for non-interactive)'
        options.backend = os.getenv('COVASIM_BACKEND', pl.get_backend())

        optdesc.interactive = 'Convenience method to set figure backend, showing, and closing behavior'
        options.interactive = os.getenv('COVASIM_INTERACTIVE', True)

        optdesc.style = 'Set the default plotting style -- options are "covasim" and "simple" plus those in pl.style.available; see also options.rc'
        options.style = os.getenv('COVASIM_STYLE', 'covasim')

        optdesc.rc = 'Default Matplotlib rc (run control) parameters for Covasim; used with style="covasim"'
        options.rc = sc.dcp(rc_covasim)

        optdesc.rc_simple = 'Simple Matplotlib rc (run control) parameters for Covasim; used with style="simple"'
        options.rc_simple = sc.dcp(rc_simple)

        optdesc.dpi = 'Set the default DPI -- the larger this is, the larger the figures will be'
        options.dpi = int(os.getenv('COVASIM_DPI', pl.rcParams['figure.dpi']))

        optdesc.font_size = 'Set the default font size'
        options.font_size = int(os.getenv('COVASIM_FONT_SIZE', pl.rcParams['font.size']))

        optdesc.font_family = 'Set the default font family (e.g., Arial)'
        options.font_family = os.getenv('COVASIM_FONT_FAMILY', 'Rosario')

        optdesc.precision = 'Set arithmetic precision for Numba -- 32-bit by default for efficiency'
        options.precision = int(os.getenv('COVASIM_PRECISION', 32))

        optdesc.numba_parallel = 'Set Numba multithreading -- none, safe, full; full multithreading is ~20% faster, but results become nondeterministic'
        options.numba_parallel = str(os.getenv('COVASIM_NUMBA_PARALLEL', 'none'))

        optdesc.numba_cache = 'Set Numba caching -- saves on compilation time; disabling is not recommended'
        options.numba_cache = bool(int(os.getenv('COVASIM_NUMBA_CACHE', 1)))

        self.optdesc = optdesc
        self.options = options

        return


    def set(self, key=None, value=None, **kwargs):

        reload_required = False

        # Reset to defaults
        if key in ['default', 'defaults']:
            kwargs = self.orig_options # Reset everything to default

        # Handle Jupyter
        elif sc.isstring(key) and 'jupyter' in key.lower():
            jupyter_kwargs = dict(
                dpi = 100,
                show = False,
                close = True,
            )
            kwargs = sc.mergedicts(jupyter_kwargs, kwargs)
            try: # This makes plots much nicer, but isn't available on all systems
                if not os.environ.get('SPHINX_BUILD'): # Custom check implemented in conf.py to skip this if we're inside Sphinx
                    import matplotlib_inline
                    matplotlib_inline.backend_inline.set_matplotlib_formats('retina')
            except:
                pass

        # Handle other keys
        elif key is not None:
            kwargs = sc.mergedicts(kwargs, {key:value})


        # Handle interactivity
        if 'interactive' in kwargs.keys():
            interactive = kwargs['interactive']
            if interactive in [None, 'default']:
                interactive = self.orig_options['interactive']
            if interactive:
                kwargs['show'] = True
                kwargs['close'] = False
                kwargs['backend'] = self.orig_options['backend']
            else:
                kwargs['show'] = False
                kwargs['backend'] = 'agg'

        # Reset options
        for key,value in kwargs.items():
            if key not in options:
                keylist = self.orig_options.keys()
                keys = '\n'.join(keylist)
                errormsg = f'Option "{key}" not recognized; options are "defaults" or:\n{keys}\n\nSee help(cv.options.set) for more information.'
                raise sc.KeyNotFoundError(errormsg)
            else:
                if value in [None, 'default']:
                    value = self.orig_options[key]
                options[key] = value
                if key in numba_keys:
                    reload_required = True
                if key in matplotlib_keys:
                    self.set_matplotlib_global(key, value)

        if reload_required:
            self.reload_numba()
        return


    def get_default(self, key=None):
        ''' Helper function to get the original default options '''
        return self.orig_options[key]


    def get_help(self, output=False):
        '''
        Print information about options.

        Args:
            output (bool): whether to return a list of the options

        **Example**::

            cv.options.help()
        '''

        optdict = sc.objdict()
        for key in self.orig_options.keys():
            entry = sc.objdict()
            entry.key = key
            entry.current = options[key]
            entry.default = self.orig_options[key]
            if not key.startswith('rc'):
                entry.variable = f'COVASIM_{key.upper()}' # NB, hard-coded above!
            else:
                entry.variable = 'No environment variable'
            entry.desc = self.optdesc[key]
            optdict[key] = entry

        # Convert to a dataframe for nice printing
        print('Covasim global options ("Environment" = name of corresponding environment variable):')
        for key,entry in optdict.items():
            sc.heading(f'\n{key}', spaces=1)
            changestr = '' if entry.current == entry.default else ' (modified)'
            print(f'          Key: {key}')
            print(f'      Current: {entry.current}{changestr}')
            print(f'      Default: {entry.default}')
            print(f'  Environment: {entry.variable}')
            print(f'  Description: {entry.desc}')

        if output:
            return optdict
        else:
            return


    def set_matplotlib_global(self, key, value, available_fonts=None):
        ''' Set a global option for Matplotlib -- not for users '''
        if value: # Don't try to reset any of these to a None value
            if   key == 'font_size':   pl.rcParams['font.size']   = value
            elif key == 'dpi':         pl.rcParams['figure.dpi']  = value
            elif key == 'backend':     pl.switch_backend(value)
            elif key == 'font_family':
                if available_fonts is None or value in available_fonts: # If available fonts are supplied, don't set to an invalid value
                    pl.rcParams['font.family'] = value
            elif key == 'style':
                if value is None or value.lower() == 'covasim':
                    pl.style.use('default')
                elif value in pl.style.available:
                    pl.style.use(value)
                else:
                    errormsg = f'Style "{value}"; not found; options are "covasim" (default) plus:\n{sc.newlinejoin(pl.style.available)}'
                    raise ValueError(errormsg)
            else: raise sc.KeyNotFoundError(f'Key {key} not found')
        return


    def handle_show(self, do_show):
        ''' Convenience function to handle the slightly complex logic of show -- not for users '''
        backend = pl.get_backend()
        if do_show is None:  # If not supplied, reset to global value
            do_show = options.show
        if backend == 'agg': # Cannot show plots for a non-interactive backend
            do_show = False
        if do_show: # Now check whether to show
            pl.show()
        return do_show


    def reload_numba(self):
        '''
        Apply changes to Numba functions -- reloading modules is necessary for
        changes to propagate. Not necessary to call directly if cv.options.set() is used.

        **Example**::

            import covasim as cv
            cv.options.set(precision=64)
            sim = cv.Sim()
            sim.run()
            assert sim.people.rel_trans.dtype == np.float64
        '''
        print('Reloading Covasim so changes take effect...')
        import importlib
        import covasim as cv
        importlib.reload(cv.defaults)
        importlib.reload(cv.utils)
        importlib.reload(cv)
        print("Reload complete. Note: for some options to take effect, you may also need to delete Covasim's __pycache__ folder.")
        return


    def load_custom_fonts(self):
        '''
        Load custom fonts for plotting
        '''
        folder = str(sc.thisdir(__file__, aspath=True) / 'data' / 'assets')
        sc.fonts(add=folder)
        return




# Add these here to be more accessible to the user
options = Options()

