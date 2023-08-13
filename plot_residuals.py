import sys
import os
import matplotlib.pyplot as plt
import numpy as np

def plot_residuals( slant_angle, 
                    res_vars            = ['ux', 'uy', 'uz', 'p', 'omega', 'k', 'continuity'],
                    n_ortho_corrector   = [0, 0, 0, 1, 0, 0, 0],
                    is_limit_yaxis_max     = True,
                    yaxis_max_value     = 1 ):
    '''Plot the residuals from an OpenFoam simulation which have been preprocessed
    into .txt files for each variable
    
    Args
        case_name (str) : simulation folder
        res_vars (list of str) : residual variables
        n_ortho_corrector (list of int) : number of orthogonal correctors per residual variables
        '''
    res_path = os.path.join(os.environ['AHMED_SLANT_PATH'], 'slant_angle_{}'.format(slant_angle), 'residuals')

    #TODO: add check to read the number of non-orthogonal correctors

    #read the residuals
    plot_dict = {}
    for ii, var in enumerate(res_vars):
        fn_read = os.path.join(res_path, '{}.txt'.format(var))
        curdata = np.loadtxt(fn_read)
        plot_dict[var] = curdata

    #get the final residuals per iteratin given the number of orthogonal correctors
    for ii, var in enumerate(res_vars):
        ncorr       = n_ortho_corrector[ii]
        idx_start   = 0
        step        = ncorr + 1
        idx_end     = plot_dict[var].shape[0]
        idx_keep    = np.arange(start = idx_start, stop = idx_end, step = step)
        plot_dict[var] = plot_dict[var][idx_keep]


    fig = plt.figure()
    for var, res in plot_dict.items():
        plt.semilogy(res, label=var)
    plt.legend()

    if is_limit_yaxis_max:
        ylim = plt.ylim()
        ylim_new = [ylim[0], yaxis_max_value]
        plt.ylim(ylim_new)
    fn_save = os.path.join(res_path, 'residuals_vs_iteration.jpg')
    plt.savefig(fn_save, dpi=150, bbox_inches='tight')
    plt.close()

if __name__ == '__main__':
    slant_angle = sys.argv[1]
    plot_residuals(slant_angle=slant_angle)