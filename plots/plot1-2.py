import os
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
from matplotlib.ticker import ScalarFormatter, MultipleLocator
# import Mininet_testbed.analyze.misc

def calculat_E(csvpath):
    FlightSize_compare_csv = csvpath
    FlightSize_compare_df = pd.read_csv(FlightSize_compare_csv).reset_index(drop=True)
    # FlightSize_compare_df.drop(FlightSize_compare_df.head(10).index,inplace=True)
    # FlightSize_compare_df.drop(FlightSize_compare_df.tail(10).index,inplace=True)

    FlightSize_compare_df['FlightSizeTP'] = FlightSize_compare_df['FlightSizeTP'].astype(int)
    FlightSize_compare_df['LinuxFlightSize'] = FlightSize_compare_df['LinuxFlightSize'].astype(int)
    FlightSize_compare_df['FlightSizePrintK'] = FlightSize_compare_df['FlightSizePrintK'].astype(int)

    last_time = 0
    for index, row in FlightSize_compare_df.iterrows():
        curr_time = row['Time']
        # if curr_time - last_time < 0.032:
            # continue
        last_time = curr_time
        FlightSize_compare_df.loc[index,'PrintkDiff'] = row['LinuxFlightSize'] - row['FlightSizePrintK']
        FlightSize_compare_df.loc[index,'TPDiff'] = row['LinuxFlightSize'] - row['FlightSizeTP']
    sum_FS_TP = sum(FlightSize_compare_df['FlightSizeTP'].to_list())
    sum_printk_FS = sum(FlightSize_compare_df['FlightSizePrintK'].to_list())
    # sum_FS_Lin = sum(FlightSize_compare_df['LinuxFlightSize'].to_list())

    sum_tp_average_error = sum(FlightSize_compare_df['TPDiff'].to_list())
    sum_pk_average_error = sum(FlightSize_compare_df['PrintkDiff'].to_list())

    average_E_tp = sum_tp_average_error/sum_FS_TP*100
    average_E_pk = sum_pk_average_error/sum_printk_FS*100
    return average_E_tp, average_E_pk
def calculat_E_2(csvpath):
    FlightSize_compare_csv = csvpath
    FlightSize_compare_df = pd.read_csv(FlightSize_compare_csv).reset_index(drop=True)
    # FlightSize_compare_df.drop(FlightSize_compare_df.head(10).index,inplace=True)
    # FlightSize_compare_df.drop(FlightSize_compare_df.tail(10).index,inplace=True)
   
    FlightSize_compare_df['FlightSizeTP'] = FlightSize_compare_df['FlightSizeTP'].astype(int)
    FlightSize_compare_df['LinuxFlightSize'] = FlightSize_compare_df['LinuxFlightSize'].astype(int)
    FlightSize_compare_df['FlightSizePrintK'] = FlightSize_compare_df['FlightSizePrintK'].astype(int)

    last_time = 0
    period_LinFS_list = []
    period_TcpDumpFS_list = []
    period_PrintkFS_list = []

    Diff_list = []
    Diff_list_pk = []

    period_LinFS = 0
    period_TcpDumpFS = 0
    period_PrintkFS = 0

    for index, row in FlightSize_compare_df.iterrows():
        # print(row)
        curr_time = row['Time']

        LinFS = row['LinuxFlightSize']
        TcpDumpFS = row['FlightSizeTP']
        PrintkFS = row['FlightSizePrintK']
        # print(LinFS,TcpDumpFS,PrintkFS)
        

        period_LinFS += LinFS
        period_TcpDumpFS += TcpDumpFS
        period_PrintkFS += PrintkFS

        if curr_time - last_time > 0.03:
            last_time = curr_time

            period_LinFS_list.append(period_LinFS)
            period_TcpDumpFS_list.append(period_TcpDumpFS)
            period_PrintkFS_list.append(period_PrintkFS)

            Diff_list.append(period_LinFS - period_TcpDumpFS)
            Diff_list_pk.append(period_LinFS - period_PrintkFS)

            period_LinFS = 0
            period_TcpDumpFS = 0
            period_PrintkFS = 0

    # print(period_TcpDumpFS_list)
    average_E_tp = sum(Diff_list)/sum(period_TcpDumpFS_list)*100
    average_E_pk = sum(Diff_list_pk)/sum(period_PrintkFS_list)*100

    return average_E_tp, average_E_pk

def main():
    plt.rcParams["pdf.fonttype"] = 42
    data = []
    plt.figure(figsize=(6,1.5))
    for cca in ['bbr']:
        plt.clf()
        for bw in [1,10,100]:
            plt1 = []
            plt2 = []
            for rtt in [1,10,100]:
                resultfile = f'/home/lisong-20/flightsize2025/comapre_results/noloss-5/{cca}_bw{bw}_rtt{rtt}_loss0.0%/FlightSize_compare.csv'
                # print(resultfile,os.path.exists(resultfile))

                FlightSize_compare_csv = resultfile
                average_E_tp, average_E_pk = calculat_E(FlightSize_compare_csv)
                plt1.append(average_E_tp)
                plt2.append(average_E_pk)
                # print(FlightSize_compare_df,average_error/sum_FS_TP*100)
                item = [cca,bw,rtt,average_E_tp,average_E_pk]
                data.append(item)
            plt.plot([1,10,100],plt1,label=f'Offline, {bw}Mbps',marker='*')
            plt.plot([1,10,100],plt2,label=f'Online, {bw}Mbps',marker='+')
            plt.legend(prop={'size':10},loc=2, bbox_to_anchor=(1, 1.0),ncol=1)
        plt.xlabel('RTT(ms)')
        plt.xscale('log')
        plt.ylabel('PE(%)')
        plt.title(f'{cca}')
        plt.savefig(f'plot1-{cca}.png',bbox_inches='tight',dpi=720,pad_inches=0.01)
        plt.savefig(f'plot1-{cca}.pdf',bbox_inches='tight',dpi=720,pad_inches=0.01)
    df = pd.DataFrame(data,columns=['CCA', 'BW', 'RTT', 'Average(E)Tcpdump','Average(E)PrintK'])
    df.to_csv("noloss.csv")
    print(df)


if __name__ == "__main__":
    main()