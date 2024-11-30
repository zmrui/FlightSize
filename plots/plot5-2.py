import os
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
from matplotlib.ticker import ScalarFormatter, MultipleLocator
# import Mininet_testbed.analyze.misc

def calculat_E2(csvpath):
    FlightSize_compare_csv = csvpath
    FlightSize_compare_df = pd.read_csv(FlightSize_compare_csv).reset_index(drop=True)
    if len(FlightSize_compare_df) > 100:
        FlightSize_compare_df.drop(FlightSize_compare_df.head(10).index,inplace=True)
        FlightSize_compare_df.drop(FlightSize_compare_df.tail(10).index,inplace=True)

    FlightSize_compare_df['FlightSizeTP'] = FlightSize_compare_df['FlightSizeTP'].astype(int)
    FlightSize_compare_df['LinuxFlightSize'] = FlightSize_compare_df['LinuxFlightSize'].astype(int)

    for index, row in FlightSize_compare_df.iterrows():
        # curr_time = row['Time']
        # if curr_time > 18:
        #     break
        FlightSize_compare_df.loc[index,'TPDiff'] = row['LinuxFlightSize'] - row['FlightSizeTP']
    sum_FS_TP = sum(FlightSize_compare_df['FlightSizeTP'].to_list())
    # sum_FS_Lin = sum(FlightSize_compare_df['LinuxFlightSize'].to_list())

    sum_tp_average_error = sum(FlightSize_compare_df['TPDiff'].to_list())

    average_E_tp = sum_tp_average_error/sum_FS_TP*100

    return sum_tp_average_error/len(FlightSize_compare_df['TPDiff'].to_list())

def main():
    plt.rcParams["pdf.fonttype"] = 42
    data = []
    marker = {
        'cubic':'*',
        'bbr':'x'
    }
    BasePath = '/home/lisong-20/flightsize2025/tests'
    plt.figure(figsize=(6,1.5))
    for cca in ['cubic','bbr']:
        plt1 = []
        # for simulation in ['loss_based']:
        #     for condition in ['good','median','poor']:
        for simulation in ['experience_based']:
            for condition in ['noloss','good','fair','passable','poor','verypoor']:
                for flows in [0]:
                    parameter_path = (os.path.join(BasePath,f'{cca}_{simulation}_{condition}_flow{flows}'))
                    csvpath = os.path.join(parameter_path,'FlightSize_compare.csv') 
                    average_E_tp = calculat_E2(csvpath)
                    plt1.append(average_E_tp)
        plt.plot([0,1,2,3,4,5],plt1,label=f'{cca}',marker=marker[cca],linewidth=0.8)
    plt.xticks([0,1,2,3,4,5],['noloss','good','fair','passable','poor','verypoor'],font={'size':8})
    plt.yticks(font={'size':8})
    plt.xlabel('Network Condition',font={'size':8})
    plt.title('Experience-based Network Emulation',font={'size':8})
    plt.ylabel('AE',font={'size':8})
    # plt.legend(loc=2, bbox_to_anchor=(1, 1.0),ncol=1)
    plt.legend()
    plt.savefig(f'plot5-2.jpg',bbox_inches='tight',dpi=720,pad_inches=0.01)
    plt.savefig(f'plot5-2.pdf',bbox_inches='tight',dpi=720,pad_inches=0.01)



if __name__ == "__main__":
    main()