#!/usr/bin/env python
#
#  Copyright (c) 2019, Andrey "Limych" Khrolenok <andrey@khrolenok.ru>
#  Creative Commons Attribution-NonCommercial-ShareAlike License v4.0
#  (see COPYING, LICENSE or https://creativecommons.org/licenses/by-nc-sa/4.0/)
#
import datetime
import multiprocessing
import os
import re
import subprocess
import psutil
import json


class HddTemp:
    @staticmethod
    def hdd_temp(hdd):
        try:
            for line in subprocess.Popen(['smartctl', '-A', str('/dev/' + hdd)],
                                         stdout=subprocess.PIPE, encoding='utf8') \
                    .stdout.read().split('\n'):
                line = line.split()
                if len(line) and line[0] == '194':
                    return [hdd, line[9]]
        except FileNotFoundError:
            pass

    def hdds_temp_dict(self, hdds_list):
        pool = multiprocessing.Pool(min(8, max(multiprocessing.cpu_count(), 1)))
        results = []
        for hdd in hdds_list:
            results.append(pool.apply_async(func=self.hdd_temp, args=(hdd,)))
        pool.close()
        pool.join()
        hddict = {}
        for res in results:
            val = res.get()
            if val:
                hddict[val[0]] = val[1]
        return hddict

    def all_hdds_temp_dict(self):
        drives = []
        if psutil.WINDOWS:
            for part in psutil.disk_partitions(all=False):
                if 'cdrom' in part.opts or part.fstype == '':
                    # skip cd-rom drives
                    continue
                drives.append(part.mountpoint)
        else:
            reg = []
            if psutil.FREEBSD:
                reg.append("ad[0-9]+")
                reg.append("da[0-9]+")
                # reg.append("pass[0-9]+")
                reg.append("ada[0-9]+")
                reg.append("ciss[0-9]")
            elif psutil.LINUX:
                reg.append("sd[a-z]")
                reg.append("nst.*")
                reg.append("sg.*")
                reg.append("tw[eal][0-9]")
                reg.append("sg[0-9].*")
            combined = "(" + ")|(".join(reg) + ")"
            for dev in os.scandir("/dev/"):
                if re.match(combined, dev.name):
                    drives.append(dev.name)
        return self.hdds_temp_dict(drives)


def zpool_stat():
    zp = {}
    try:
        for line in subprocess.Popen(['zpool', 'list', '-Hp'],
                                     stdout=subprocess.PIPE, encoding='utf8') \
                .stdout.read().split('\n'):
            line = line.split('\t')
            if len(line) > 2 and line[10] != '-':
                zp[line[0]] = {
                    'total': int(line[1]),
                    'used': int(line[2]),
                    'free': int(line[3]),
                    'percent': round(int(line[2]) * 100 / int(line[1]), 1)
                }
    except FileNotFoundError:
        pass
    return zp


# ==================== Main Code ====================
if __name__ == '__main__':
    stat = {}

    # Basic stat
    stat['last_boot'] = datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%FT%T%z")

    # CPU stat
    cpu_stat = psutil.cpu_times_percent(interval=1, percpu=False)
    stat['cpu_load'] = round(100 - cpu_stat.idle, 1)
    stat['cpu_stat'] = cpu_stat._asdict()

    # Mem stat
    mem_stat = psutil.virtual_memory()
    stat['mem_load'] = mem_stat.percent
    stat['mem_stat'] = mem_stat._asdict()

    # Swap stat
    swap_stat = psutil.swap_memory()
    stat['swap_load'] = swap_stat.percent
    stat['swap_stat'] = swap_stat._asdict()

    # Disks stat
    disks = {}
    for part in psutil.disk_partitions(all=False):
        if psutil.WINDOWS:
            if 'cdrom' in part.opts or part.fstype == '':
                # skip cd-rom drives
                continue
        else:
            if part.fstype in ['nullfs', 'devfs', 'fdescfs', 'tmpfs']:
                # Skip some virtual filesystems
                continue
        disk_usage = psutil.disk_usage(part.mountpoint)
        disks[part.mountpoint] = disk_usage._asdict()
    stat['disks_stat'] = disks
    #
    stat['disks_temp'] = HddTemp().all_hdds_temp_dict()
    #
    stat['pools_stat'] = zpool_stat()

    #
    # Cumulative stat
    print()
    print(json.dumps(stat))
