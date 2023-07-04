import os, time, sys
import json
import subprocess
import shutil

import telnetlib


class my_telnet (object):

    def __init__(self):
        return

        # tn_info : (tn_ip, tn_id, tn_pwd) (10.10.65.172, sysadmin, superuser)
        # tn_port : port (2000)
        # tn_send_cmd : command (ifconfig eth0 | grep xxx)
    def telnet_get (self, tn_info, tn_send_cmd):

        # unknow how to set the xx value in read_until(xx, timeout) 
        ret = 0
        timeout = 1
        timeout_01 = 2

        # print ("telnet conn.")
        try:
            tn_conn = telnetlib.Telnet(tn_info["tn_ip"], tn_info["tn_port"], timeout)
        except socket.timeout:
            # print ("telnet conn : socket timeout")
            ret = -1
            get_msg = "telnet conn : socket timeout"
            return ret, get_msg
        # else:
        finally:
            tmp_str = tn_conn.read_until(b": ", timeout)

            str_in_use = "in use"
            checked = tmp_str.decode("utf-8")
            if (0 < checked.find(str_in_use)):
                tn_conn.close()
                ret = -1
                get_msg = "Port already in use"
                return ret, get_msg

            # print("Send username")
            tn_conn.write(tn_info["tn_id"].encode('ascii') + b"\r\n")

            time.sleep(timeout_01)
            tmp_str = tn_conn.read_until(b":", timeout )
            # print ("read prompt = %s" % tmp_str.splitlines())

            if (0 >= len(tmp_str)):
                tn_conn.close()
                ret = -1
                get_msg = "telnet conn() no recv"
                return ret, get_msg


            # print ("Send password")
            tn_conn.write(tn_info["tn_pwd"].encode('ascii') + b"\r\n")

            time.sleep(timeout_01)
            tmp_str = tn_conn.read_until(b"#", timeout )
            # print ("read prompt = %s" % tmp_str.splitlines())

            # print ("Send command [%s]" % (tn_send_cmd))
            tn_conn.write(tn_send_cmd.encode('ascii') + b"\r\n")

            time.sleep(timeout_01)
            # print ("Read return message")
            tmp_str = tn_conn.read_until(b"#", timeout )
            # print ("read prompt = %s" % tmp_str.splitlines())

            # print ("Send exit")
            cmd_exit = "exit"
            tn_conn.write(cmd_exit.encode('ascii') + b"\r\n")

            time.sleep(timeout_01)

            # -2 : only for single line, multi lines NOT workable
            # print ("Read exit msg")
            tmp_str = tn_conn.read_until(b"#", timeout )
            # print ("read prompt = %s" % tmp_str.splitlines())

            get_msg = ""
            if (0 >= len(tmp_str)):
                # print ("recv len = [%s]" % len(tmp_str))
                ret = -1
                get_msg = "recv data len = 0"
            else:
                ret = 0
                get_msg = tmp_str.splitlines()[-2].decode("utf-8") 
                print ("recv = [%s]" % tmp_str)


            # print ("get_msg = %s" % get_msg)

            tn_conn.close()

        return ret, get_msg


class search_in_json (object):

    def __init__(self):
        return

    def get_struct_by_key (self, str_json_file, str_tag):

        ret_data    = []
        ret_empty   = {}
        if (False == os.path.isfile(str_json_file)):
            return ret_empty # file not exist, return False

        with open(str_json_file) as data_file:
            ret_data = json.load(data_file)

        if str_tag in ret_data:
            return ret_data[str_tag]
        else:
            return ret_empty


class file_mng (object):
    def __init__(self):
        return

    def _copy_source (self, conf_file, json_tag):

        ret             = False
        search_json     = search_in_json()
        p_copy_src      = ""
        copy_desc       = ""
        work_dir        = ""

        if (False == os.path.isfile(conf_file)):
            return ret

        json_info       = dict(search_json.get_struct_by_key(conf_file, json_tag))

        if "entry" in json_info:

            dict_run_module     = json.dumps(json_info["entry"])
            p_copy_src          = json.loads(dict_run_module)

            if "copy_desc" in json_info:
                copy_desc       = json_info["copy_desc"]
            if "work_dir" in json_info:
                work_dir        = json_info["work_dir"]

        # change working dir, maybe work_dir = "" current folder
        if (True == self.check_folder_exist(work_dir)):
            os.chdir(work_dir)

        if (False == self.check_folder_exist(copy_desc)):
            self.create_folder(copy_desc)

        copy_ret = True
        for item in p_copy_src:
            str_src  = p_copy_src[item]
            str_dest = copy_desc

            print ("copy folder from [%s] to [%s]" % (str_src, str_dest))

            ret = shutil.copytree(str_src, str_dest, dirs_exist_ok=True)
            if (ret != str_dest):
                print ("copy folder fail")
                copy_ret = False

        return copy_ret

    def _overwrite_source (self, conf_file, json_tag):

        search_json     = search_in_json()
        str_json_info   = dict(search_json.get_struct_by_key(conf_file, json_tag))
        dict_run_module = json.dumps(str_json_info["act_info"])
        p_copy_src      = json.loads(dict_run_module)

        work_dir        = str_json_info["work_dir"]

        # change working dir
        if (True == self.check_folder_exist(work_dir)):
            os.chdir(work_dir)

        move_ret = True
        for item in p_copy_src:
            
            file_src = p_copy_src[item]["file_src"]
            file_desc = p_copy_src[item]["file_desc"]

            print ("overwrite file from [%s] to [%s]" % (file_src, file_desc))
            ret = shutil.copy(file_src, file_desc)
            if (ret != file_desc):
                print ("move file fail")
                move_ret = False
        
        return move_ret

    def _search_in_file (self, str_file, str_keyword):

        found = False
        search_value = ""
        if (False == self.check_file_exist(str_file)):
            search_value = "check_file_exist_FAIL"
            return found, search_value

        datafile = open(str_file)
        for line in datafile:
            if str_keyword in line:
                found = True
                search_value = line.split(str_keyword)[1].rstrip("\n")
                break
        datafile.close()

        return found, search_value

    def check_file_exist (self, str_file):
        return os.path.isfile(str_file)

    def check_folder_exist (self, str_folder):
        return os.path.isdir(str_folder)

    def create_folder (self, str_folder):

        try:
            os.makedirs(str_folder) # Return Type: This method does not return any value.
            return True

        except FileExistsError:
            print ("file exist")
            return False


class execute_cmd (object):
    def __init__(self):
        return

    def exec_shell_cmd (self, str_report_path, stdout_filename, str_cmd ):

        if (False == file_mng().check_folder_exist(str_report_path)):
            file_mng().create_folder(str_report_path)

        str_tmp             = "=== run cmd === : %s \n" % str_cmd
        str_report          = "%s/%s.log" % (str_report_path, stdout_filename)
        log_out_file        = open(str_report, 'ab')

        log_out_file.write(str_tmp.encode())
        log_out_file.flush()

        rc = 199
        try:
            ret                 = subprocess.Popen(str_cmd, shell=True, universal_newlines=True, stderr=subprocess.STDOUT, stdout=log_out_file)
            stdout, stderr      = ret.communicate()
            exit_code           = ret.wait()

            log_out_file.flush()
            log_out_file.close()

            rc = ret.returncode
        except KeyboardInterrupt:
            print ("recv Keyboard interrupt")
            sys.exit (666)

        return rc

    def exec_shell_cmd_and_get (self, str_report_path, stdout_filename, str_cmd ):

        if (False == file_mng().check_folder_exist(str_report_path)):
            file_mng().create_folder(str_report_path)

        str_tmp             = "=== run cmd === : %s \n" % str_cmd
        str_report          = "%s/%s.log" % (str_report_path, stdout_filename)
        log_out_file        = open(str_report, 'ab')

        log_out_file.write(str_tmp.encode())
        log_out_file.flush()

        rc = 199
        try:
            ret                 = subprocess.Popen(str_cmd, shell=True, universal_newlines=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr      = ret.communicate()
            exit_code           = ret.wait()

            log_out_file.flush()
            log_out_file.close()

            rc = ret.returncode
        except KeyboardInterrupt:
            print ("recv Keyboard interrupt")
            sys.exit (666)

        return rc, stdout, stderr


# curl command example :
# download file from nc
# curl -u "admin:admin" -X GET   "http://192.168.235.100:8888/remote.php/dav/files/admin/FW/d_hotfix/hotfix_2022_03_21/tox.ini"  --output "tox.ini"

# upload file to nc
# curl -X PUT -u <user>:<pass> https://<nextcloud root>/remote.php/dav/files/<user>/<path to upload> -T <file path to send>

# create folder
# curl -X MKCOL -u <user>:<pass> https://<nextcloud root>/remote.php/dav/files/<user>/<folder path to create>

# delete folder
# curl -X DELETE -u <user>:<pass> https://<nextcloud root>/remote.php/dav/files/<user>/<folder path to delete>
############################################################

class nc_mng (object):
    def __init__(self):
        return

# stu_nc_info = dict()
# stu_nc_info.update({"nc_user" : nc_user})
# stu_nc_info.update({"nc_url" : nc_url})
# stu_nc_info.update({"nc_root" : nc_root})
# stu_nc_info.update({"nc_start_path" : nc_start_path})

# stu_log_info = dict()
# stu_log_info.update({"log_folder" : jenkins_env["cmd_log_folder"]})
# stu_log_info.update({"log_filename" : json_tag})

    def _create_folder_on_nc (self, stu_nc_info, log_info):

        create_cmd  = "curl -u %s -X MKCOL  %s/remote.php/dav/files/%s/%s/%s -k" % (stu_nc_info["nc_user"], stu_nc_info["nc_url"], stu_nc_info["nc_root"], stu_nc_info["nc_start_path"], stu_nc_info["nc_log_folder"])
        print ("create folder [%s]" % create_cmd)
        ret_tmp     = execute_cmd().exec_shell_cmd(log_info["log_folder"], log_info["log_filename"], create_cmd)
        print ("result [%s]" % ret_tmp)
        return ret_tmp
        # return 0


    def _upload_file (self, stu_nc_info, log_info, str_src, str_dest):

        up_file_cmd = " curl -u %s -T %s  %s/remote.php/dav/files/%s" % (stu_nc_info["nc_user"], str_src, stu_nc_info["nc_url"], str_dest)
        print ("upload file [%s]" % up_file_cmd)
        ret_tmp     = execute_cmd().exec_shell_cmd(log_info["log_folder"], log_info["log_filename"], up_file_cmd)
        print ("result [%s]" % ret_tmp)
        return ret_tmp

    def _upload_folder_on_nc (self, stu_nc_info, stu_log_info, tmp_up_folder, str_folder_name):

        if (True == os.path.isdir(tmp_up_folder)):

            stu_nc_info["nc_log_folder"] = "%s" % (str_folder_name) 
            ret = self._create_folder_on_nc (stu_nc_info, stu_log_info)


            arr = os.listdir(tmp_up_folder)

            for idx_file in range(0, len(arr)) :
                new_check_path  = "%s/%s" % (tmp_up_folder, arr[idx_file])
                local_folder    = "%s/%s" % (tmp_up_folder, arr[idx_file])
                server_folder   = "%s/%s" % (str_folder_name, arr[idx_file])

                if (True == os.path.isdir(new_check_path)):
                    self._upload_folder_on_nc(stu_nc_info, stu_log_info, local_folder, server_folder)
                else:

                    split_file      = new_check_path.split("/", -1)
                    str_file_name   = split_file[len(split_file) - 1]

                    str_dest = "%s/%s/%s" % (stu_nc_info["nc_root"], stu_nc_info["nc_start_path"], server_folder)
                    str_src = new_check_path

                    ret = self._upload_file(stu_nc_info, stu_log_info, str_src, str_dest)

        else:#  path NOT dir
            if (True == os.path.isfile(tmp_up_folder) ):
                split_file      = tmp_up_folder.split("/", -1)
                str_file_name   = split_file[len(split_file) - 1]

                str_dest = "%s/%s/%s" % (stu_nc_info["nc_root"], stu_nc_info["nc_start_path"], str_file_name)
                str_src = tmp_up_folder

                ret = self._upload_file(stu_nc_info, stu_log_info, str_src, str_dest)
            else:
                print ("[%s] not dir, not folder xxxxxxxxxx" % tmp_up_folder)

        return 0