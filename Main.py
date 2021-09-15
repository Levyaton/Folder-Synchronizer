
import sys, shutil, logging
from Lib import os
from apscheduler.schedulers.blocking import BlockingScheduler


sched = BlockingScheduler()

system_arguments = sys.argv
source_path = system_arguments[1]
replica_path = system_arguments[2]
log_file_path = system_arguments[3]
logging.basicConfig(filename=log_file_path, filemode='w', format='%(asctime)s - %(message)s', level=logging.INFO)
sync_interval = int(system_arguments[4])  # in seconds

#Returns all files from a path, including subfolders
def get_all_files(dir):
    list = []
    for name in os.listdir(dir):
        if os.path.isfile(os.path.join(dir, name)):
            list.append(name)
        else:
            list.append(name)
            path = os.path.join(dir, name)
            temp = get_all_files(path)
            for file in temp:
                list.append(os.path.join(name, file))
    return list

#function for the creation of a new file or directory copy
def create(name):
    file = os.path.join(source_path, name)
    path = os.path.join(replica_path, name)
    if os.path.isfile(file):
        shutil.copy(file, path)
        print("Created file " + path)
        logging.info("Created file " + path)
    else:
        if not os.path.exists(path):
            os.makedirs(os.path.join(replica_path, name))
            print("Created directory " + path)
            logging.info("Created directory " + path)

#function for the overwriting of an existing file
def copy(name):
    file = os.path.join(source_path, name)
    path = os.path.join(replica_path,name)
    if os.path.isfile(file):
        os.remove(os.path.join(replica_path,name))
        shutil.copy(file, path)
        print("Copied and overwritten file " + path)
        logging.info("Copied and overwritten file " + path)

#call to all the operations that are performed when copying files and directories from the source folder
def source_folder_copy(source_files, replica_files):
    for name in source_files:
        name_path = os.path.join(source_path,name)
        if name not in replica_files:
            create(name)
        else:
            if os.path.isfile(name_path):
                copy(name)

#function that serves to delete removed files from the replica folder
def remove_extras(source_files,replica_files):
    for name in replica_files:
        if name not in source_files:
            path = os.path.join(replica_path, name)
            if os.path.isfile(path):
                os.remove(path)
                print("Deleted file " + path)
                logging.info("Deleted file " + path)
            else:
                delete_messaging(path)
                shutil.rmtree(path, ignore_errors=True)

#function that recurssivly handles the delete messanging between paths
def delete_messaging(path):
    deleted_files = get_all_files(path)
    print("Deleted directory " + path)
    logging.info("Deleted directory " + path)
    for deleted in deleted_files:
        p = os.path.join(path,deleted)
        if os.path.isfile(p):
            print("Deleted file " + p)
            logging.info("Deleted file " + p)
        else:
            delete_messaging(p)

#The function that is called every n-seconds, as provided by the user through the command line arguments
@sched.scheduled_job('interval', seconds=sync_interval)
def sync():
    source_files = get_all_files(source_path)
    replica_files = get_all_files(replica_path)

    source_folder_copy(source_files,replica_files)
    remove_extras(source_files,replica_files)


if __name__ == '__main__':
    sched.start()
