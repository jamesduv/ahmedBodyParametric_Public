import sys
import os
import matplotlib.pyplot as plt
import numpy as np

def plot_cd(slant_angle, 
            res_vars    = ['cd'],
            is_logy     = False ):
    '''Plot the drag coefficient vs. iteration from an OpenFoam simulation which have been preprocessed
    into a .txt file
    
    Args
        case_name (str) : simulation folder
        res_vars (list) : list of quantities to plot
    '''
    
    res_path = os.path.join(os.environ['AHMED_SLANT_PATH'], 'slant_angle_{}'.format(slant_angle), 'residuals')

    #read the residuals
    plot_dict = {}
    for ii, var in enumerate(res_vars):
        fn_read = os.path.join(res_path, '{}.txt'.format(var))
        curdata = np.loadtxt(fn_read)
        plot_dict[var] = curdata

    #no orthogonal correctors on Cd, keep all indices
    # for ii, var in enumerate(res_vars):
    #     idx_start   = 0
    #     step        = 1
    #     idx_end     = plot_dict[var].shape[0]
    #     idx_keep    = np.arange(start = idx_start, stop = idx_end, step = step)
    #     plot_dict[var] = plot_dict[var][idx_keep]


    fig = plt.figure()
    for var, res in plot_dict.items():
        if is_logy:
            plt.semilogy(res, label=var)
            fn_save = os.path.join(res_path, '{}_vs_iteration_logy.jpg'.format(var))
        else:
            plt.plot(res, label=var)
            fn_save = os.path.join(res_path, '{}_vs_iteration.jpg'.format(var))
        plt.legend()
        
        plt.savefig(fn_save, dpi=150, bbox_inches='tight')
        plt.close()

if __name__ == '__main__':
    slant_angle = sys.argv[1]
    plot_cd(slant_angle=slant_angle, is_logy=True)