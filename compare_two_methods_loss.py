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


def Compare_two_methods(cca,rtt, bw, loss,nameprefix="", keep=1):
    # exp_table6_1
    maxqsize=100
    print("maxqsize=",maxqsize)
    resfolder = os.path.join(Mininet_testbed.utils.config.RESULTS_DIR,'loss')
    realsub_folder = os.path.join(resfolder,f'{cca}_bw{bw}_rtt{rtt}_loss{loss/100}%')
    print(realsub_folder)
    
    mn_net = Mininet_testbed.analyze.mn_net_topo.mn_network(rtt=rtt,bw=bw,cca=cca,reorder=False,
                                    nameprefix=nameprefix,
                                    maxqsize=maxqsize,sub_folder=realsub_folder)
    mn_net.make_subfolder()
    mn_net.start_mininet()
    mn_net.disable_tso()
    # input()
    mn_net.start_tcpdump(result_save_path=mn_net.workingdir)
    if loss > 0:
        mn_net.set_iptables_prob_packet_loss(percentage=loss/10000)

    # mn_net.start_iperf_size(durition_time=20)
    mn_net.start_iperf_time_json(durition_time=18)

    # mn_net.wait_until_iperf_end()
    # mn_net.kill_tcpdump()
    # input()
    time.sleep(30)
    mn_net.stop_mininet()
    mn_net.save_log()
    # mn_net.return_top_folder()

    files = os.listdir(mn_net.workingdir)
    for item in files:
        if cca in item and item.endswith("name.txt"):
            filename = item
    fc=Mininet_testbed.analyze.fs_compare.fs_compare_class(folder = mn_net.workingdir, filename=filename)
    first_data_send_time = fc.generate()
    print("first_data_send_time",first_data_send_time)
    print('Began parse printk',datetime.now())
    fc.parse_printk(first_data_send_time)
    # print('Began parse_printk_fs_old_method',datetime.now())
    # fc.parse_printk_fs_old_method(first_data_send_time)

    print('Began parse_receiver_tcpdump',datetime.now())
    fc.parse_receiver_tcpdump()
    print('Began parse_sender_tcpdump',datetime.now())
    fc.parse_sender_tcpdump()
    tp_first_data_send_time = fc.merge_tcpdump_and_get_send_time()
    print("first_data_send_time",tp_first_data_send_time)
    fc.change_tcpdump_df_time(tp_first_data_send_time)

    print('Began cal_FlightSize_new',datetime.now())
    fc.cal_FlightSize_new()

    fc.Downgrade_resolution()
    print('Began fs_Lin_tp_printk',datetime.now())
    fc.fs_Lin_tp_printk()

    fc.diff_time()

    fc.check_two_flightsize_results()

    average_E_tp, average_E_pk = Mininet_testbed.analyze.misc.calculat_E(os.path.join(fc.folder,'FlightSize_compare.csv'))
    print(average_E_tp, average_E_pk)
    return average_E_tp, average_E_pk

if __name__ == "__main__":
    for cca in ['cubic','bbr']:
        for rtt in [10]:
            for bw in [10]:
                for loss in [1000,100,1,10,0]:
                    for run in range(10):
                        print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
                        print(datetime.now())
                        try:
                            Compare_two_methods(cca=cca,rtt=rtt,bw=bw,loss=loss)
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
