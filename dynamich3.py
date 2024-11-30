import os
import time
import Mininet_testbed.analyze.mn_net_topo
import Mininet_testbed.analyze.fs_compare
import Mininet_testbed.analyze.misc
import Mininet_testbed.utils.config
import random
from matplotlib import pyplot as plt
import pandas as pd
from datetime import datetime


def Compare_two_methods(cca, backtraffic, simulation="loss_based", condition ="good", nameprefix="", keep=1):
    # exp_table6_1
    maxqsize=100
    # maxqsize = max(int(rtt * bw * 1000 / 8 / 1480) , maxqsize)
    print("maxqsize=",maxqsize)
    resfolder = os.path.join(Mininet_testbed.utils.config.MN_TESTBED_DIR,'dynamic')
    realsub_folder = os.path.join(resfolder,f'{cca}_{simulation}_{condition}_flow{backtraffic}')
    print(realsub_folder)

    
    mn_net = Mininet_testbed.analyze.mn_net_topo.mn_network(rtt=10,bw=10,cca=cca,reorder=False,
                                    nameprefix=nameprefix,
                                    maxqsize=maxqsize,sub_folder=realsub_folder)
    mn_net.make_subfolder()
    mn_net.start_mininet()
    mn_net.disable_tso()

    mn_net.dynamich3(simulation=simulation,condition=condition)
    mn_net.dynamich2(simulation=simulation,condition=condition)

    mn_net.start_tcpdump(result_save_path=mn_net.workingdir)

    for i in range(backtraffic):
        mn_net.start_iperf_time_json_back(durition_time=300,port=6000+i)

    mn_net.start_iperf_time_json(durition_time=60)


    mn_net.wait_until_iperf_end()

    time.sleep(5)
    mn_net.stop_mininet()
    mn_net.save_log()


    files = os.listdir(mn_net.workingdir)
    for item in files:
        if cca in item and item.endswith("name.txt"):
            filename = item
    fc=Mininet_testbed.analyze.fs_compare.fs_compare_class(folder = mn_net.workingdir, filename=filename)
    first_data_send_time = fc.generate()
    print("first_data_send_time",first_data_send_time)
    print('Began parse printk',datetime.now())
    fc.parse_printk(first_data_send_time)


    print('Began parse_receiver_tcpdump',datetime.now())
    fc.parse_receiver_tcpdump()
    print('Began parse_sender_tcpdump',datetime.now())
    fc.parse_sender_tcpdump()
    tp_first_data_send_time = fc.merge_tcpdump_and_get_send_time()
    print("first_data_send_time",tp_first_data_send_time)
    fc.change_tcpdump_df_time(tp_first_data_send_time)

    print('Began cal_FlightSize_new',datetime.now())
    fc.cal_FlightSize_new()


    fc.Downgrade_resolution2()
    print('Began fs_Lin_tp_printk',datetime.now())
    # fc.fs_Lin_tp_printk()
    fc.fs_Lin_tp(stoptime=60)

    average_E_tp = Mininet_testbed.analyze.misc.calculat_E2(os.path.join(fc.folder,'FlightSize_compare.csv'))
    print(average_E_tp)
    return average_E_tp

if __name__ == "__main__":
    for cca in ['cubic','bbr']:
        for simulation in ['experience_based']:
            for condition in ['noloss','good','fair','passable','poor','verypoor']:
                for flows in [0]:
                    for run in range(10):
                        print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
                        print(datetime.now())
                        try:
                            Compare_two_methods(cca=cca,simulation=simulation,condition=condition,backtraffic=flows)
                        except KeyboardInterrupt:
                            print("Got KeyboardInterrupt CTRL-C, exiting")
                            os.system('sudo mn -c')
                            os.system(f'sudo chown {Mininet_testbed.utils.config.USER} -R {Mininet_testbed.utils.config.ROOTDIR}')
                            exit()
                        except Exception as e:
                            print(repr(e))
                            print("Exception")
                            continue
                        else:
                            break
    os.system(f'sudo chown {Mininet_testbed.utils.config.USER} -R {Mininet_testbed.utils.config.ROOTDIR}')