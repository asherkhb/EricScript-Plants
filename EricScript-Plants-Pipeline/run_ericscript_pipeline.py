#!/usr/bin/env python

import os
import sys
import urllib2
import json

from datetime import datetime

import work_queue as wq

config = 'sra_example.cfg'
mode = 'sra'  # MODE: 'irods' or 'sra' (NOTE: IRODS is broken...sorry!)
resultsdir = 'results'
avail_cores = 10
references_local = './References'
references_remote = os.path.basename(references_local)


def parse_cfg(fn):
    s = []
    with open(fn, 'r') as cfg_in:
        header = cfg_in.readline()
        header = header.strip().split(',')
        for line in cfg_in:
            line = line.strip()
            if len(line) < 1:
                pass
            elif line[0] == '#':
                pass
            else:
                line = line.split(',')
                entr = {}
                for i in range(0, len(header)):
                    entr[header[i]] = line[i]
                s.append(entr)
    return s

def get_ip():
    """Get IP
    Ping ifconfig.co and return external IP address, or -1 if unable to find.

    :return: IP address if possible, -1 on error.
    """
    try:
        response = urllib2.urlopen('http://ifconfig.co/json')
        data = json.load(response)
        return data["ip"]
    except Exception as e:
        print("WARNING: Unable to obtain IP (%s)." % e)
        return -1


def create_queue(port=wq.WORK_QUEUE_DEFAULT_PORT):
    """Create Queue
    Create a work_queue WorkQueue on a given port and print a useful help message on success. Exit (1) on fail.

    :param port: OPTIONAL, port to listen for workers. Default is work_queue's default port.
    :return: WorkQueue object.
    """
    # Spawn queue.
    try:
        q = wq.WorkQueue(port)
        ip = get_ip()
        # Print instructional message.
        if ip != -1:
            print("Listening for workers @ %s on port %s" % (ip, q.port))
            print("(this is a best guess IP, depending on your computing environment you may need to adjust.)")
            print("\nHINT: To start a worker, you can probably use this command:")
            print("work_queue_worker -d all --cores 0 %s %s\n" % (ip, q.port))
        else:
            print("Listening for workers on port %s" % q.port)
    except Exception as e:
        print("WorkQueue Launch Failed.")
        print(e)
        sys.exit(1)

    # Return queue.
    return q


def create_task_irods(s):
    # Define constant values.
    sample = s['sample_name']
    refid = s['refid']
    p1_irods = s['p1']
    p2_irods = s['p2']

    get_log = sample + '_get.txt'
    run_log = sample + '_log.txt'
    p1_path = os.path.basename(p1_irods)
    p2_path = os.path.basename(p2_irods)

    # Define tasks.
    p1_get = 'time iget -TV %s . > %s 2>&1' % (p1_irods, get_log)
    p2_get = 'time iget -TV %s . >> %s 2>&1' % (p2_irods, get_log)
    es_cmd = 'time ericscript -p %d -db %s --refid %s -name %s -o ./%s %s %s > %s 2>&1' \
             % (avail_cores, references_remote, refid, sample, sample, p1_path, p2_path, run_log)

    # Create & tag task.
    t = wq.Task('bash -c "' + ' && '.join([p1_get, p2_get, es_cmd]) + '"')
    t.specify_tag(sample)

    # Specify references folder as a cached input.
    t.specify_directory(references_local, references_remote, wq.WORK_QUEUE_INPUT, recursive=True, cache=True)

    # Specify anticipated outputs.
    # ... logs.
    t.specify_file(os.path.join(resultsdir, get_log), get_log, wq.WORK_QUEUE_OUTPUT, cache=False)  # get log
    t.specify_file(os.path.join(resultsdir, run_log), run_log, wq.WORK_QUEUE_OUTPUT, cache=False)  # ericscript log
    # ... results.
    t.specify_file(os.path.join(resultsdir, sample + '.results.filtered.tsv'),
                   os.path.join(sample, sample + '.results.filtered.tsv'),
                   wq.WORK_QUEUE_OUTPUT, cache=False)  # filtered results
    t.specify_file(os.path.join(resultsdir, sample + '.results.total.tsv'),
                   os.path.join(sample, sample + '.results.total.tsv'),
                   wq.WORK_QUEUE_OUTPUT, cache=False)  # total results
    t.specify_file(os.path.join(resultsdir, sample + '.Summary.RData'),
                   os.path.join(sample, sample + '.Summary.RData'),
                   wq.WORK_QUEUE_OUTPUT, cache=False)  # RData summary

    return t


def create_task_sra(s):
    # Define constant values.
    sample = s['sample_name']
    refid = s['refid']
    sra = s['sra']

    get_log = sample + '_get.txt'
    run_log = sample + '_log.txt'
    p1_path = sra + '_1.fastq'
    p2_path = sra + '_2.fastq'

    # Define tasks.
    get = 'time fastq-dump --split-files %s > %s 2>&1' % (sra, get_log)

    es_cmd = 'time ericscript -p %d -db %s --refid %s -name %s -o ./%s %s %s > %s 2>&1' \
             % (avail_cores, references_remote, refid, sample, sample, p1_path, p2_path, run_log)
    cleanup = 'rm -r ${HOME}/ncbi'
    
    # Create & tag task.
    t = wq.Task('bash -c "' + ' && '.join([get, es_cmd]) + '"')
    t.specify_tag(sample)

    # Specify references folder as a cached input.
    t.specify_directory(references_local, references_remote, wq.WORK_QUEUE_INPUT, recursive=True, cache=True)

    # Specify anticipated outputs.
    # ... logs.
    t.specify_file(os.path.join(resultsdir, get_log), get_log, wq.WORK_QUEUE_OUTPUT, cache=False)  # get log
    t.specify_file(os.path.join(resultsdir, run_log), run_log, wq.WORK_QUEUE_OUTPUT, cache=False)  # ericscript log
    # ... results.
    t.specify_file(os.path.join(resultsdir, sample + '.results.filtered.tsv'),
                   os.path.join(sample, sample + '.results.filtered.tsv'),
                   wq.WORK_QUEUE_OUTPUT, cache=False)  # filtered results
    t.specify_file(os.path.join(resultsdir, sample + '.results.total.tsv'),
                   os.path.join(sample, sample + '.results.total.tsv'),
                   wq.WORK_QUEUE_OUTPUT, cache=False)  # total results
    t.specify_file(os.path.join(resultsdir, sample + '.Summary.RData'),
                   os.path.join(sample, sample + '.Summary.RData'),
                   wq.WORK_QUEUE_OUTPUT, cache=False)  # RData summary

    return t

# Check & create results directory.
if os.path.exists(resultsdir):
    print("[ES PIPELINE] %s - ERROR - Results directory %s already exists!" % (datetime.now(), resultsdir))
    exit()
else:
    os.makedirs(resultsdir)

# Create a queue.
q = create_queue()

# Create & submit tasks.
samples = parse_cfg(config)
submissions = 0
for s in samples:
    if mode == 'irods':
        t = create_task_irods(s)
    elif mode == 'sra':
        t = create_task_sra(s)
    else:
        print()
    if t:
        taskid = q.submit(t)
        print("[ES PIPELINE] %s - INFO - Submitted task (%d): %s ..." % (datetime.now(), taskid, t.command))
        submissions += 1
    else:
        print("[ES PIPELINE] %s - WARNING - Failed to create task for %s ..." % (datetime.now(), s['sample_name']))

print("[ES PIPELINE] %s - INFO - Submitted %d tasks ... waiting ..." % (datetime.now(), submissions))

# Wait for tasks to complete.
while not q.empty():
    t = q.wait(5)
    if t:
        if t.return_status == 0:
            print("[ES PIPELINE] %s - INFO - Task %s (%d) complete ... success ..."
                  % (datetime.now(), t.tag, t.id))
        else:
            print("[ES PIPELINE] %s - WARNING - Task %s (%d) complete ... failure (%d) ..."
                  % (datetime.now(), t.tag, t.id, t.return_status))

# Log & print concluding message.
print("[ES PIPELINE] %s - INFO - All tasks completed! See %s for results." % (datetime.now(), resultsdir))