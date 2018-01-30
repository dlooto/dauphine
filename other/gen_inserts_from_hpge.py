# 2017数据补齐
# 根据SPE文件和RPT文件生成导入SQL

import os
import time


def parse_spe(filename):
    f = open(filename)
    line = f.readline()
    while line:
        if line.startswith('$DATE_MEA:'):
            begin_time_line = f.readline()
            begin_time = time.strptime(begin_time_line.strip(), '%m/%d/%Y %H:%M:%S')
            begin_time = int(time.mktime(begin_time))
            f.readline()
            end_time_line = f.readline().strip().split(' ')
            end_time_diff = int(end_time_line[1])
            break
        line = f.readline()
    end_time = begin_time + end_time_diff
    return (begin_time, end_time, end_time + 30)


def parse_rpt(filename):
    f = open(filename)
    line = f.readline()
    while line:
        if 'Start time:' in line:
            begin_time_line = line[line.find('20'):].strip()
            
            begin_time = time.strptime(begin_time_line.strip('\x00'), '%Y/%m/%d %H:%M:%S')
            begin_time = int(time.mktime(begin_time))
        elif 'Real time:' in line:
            end_time_line = line[line.find('time') + 5:].strip()
            end_time_diff = int(end_time_line)
            break
        line = f.readline()
    end_time = begin_time + end_time_diff
    return (begin_time, end_time, end_time + 50)




def to_insert_sql(sid, filepath, file_type, start_time, end_time, data_time):
    file_name = os.path.basename(filepath)
    
    file_link = '/var/www/almada/api/storage/static/hpge/%s/%s' % (sid, file_name)
    return '(null, %d, %d, %d, \'%s\', \'%s\', \'%s\', %d, 1, 0, 0)' % (data_time, start_time, end_time, sid, file_link, file_name, file_type)
  
w = open('a.sql', 'w')

def scanfile(path):
    filelist = os.listdir(path)
    allfile = []
    sid = os.path.relpath(path, '/Users/healer/Downloads/ff')
    
    for filename in filelist:
        filepath = os.path.join(path, filename)
        if os.path.isdir(filepath):
            scanfile(filepath)
        
        if filepath.lower().endswith('.spe'):
            sql = to_insert_sql(sid, filepath, 1, *parse_spe(filepath))
        elif filepath.lower().endswith('.rpt'):
            sql = to_insert_sql(sid, filepath, 2, *parse_rpt(filepath))
        else:
            sql = None
        if sql:
            w.write("insert into dt_data_13 values %s;\n" % sql)

    

allfile = scanfile('/Users/healer/Downloads/ff')
w.close()