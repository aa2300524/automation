import os, time, sys
import json
import datetime
import pathlib
import threading

from cicd_utility import search_in_json
from cicd_utility import file_mng
from cicd_utility import execute_cmd
from cicd_utility import nc_mng



from cicd_utility import my_telnet

# 77  # para len error : python main.py name_conf name_run_func
# 122 # file not exist in package
# 123 # key not find in file
# 130 # _git_download() return fail
# 131 # _copy_source() fail
# 132 # _overwrite_source() fail
# 133 # __run_script() fail
# 134 # _run_build() fail

# 135 # get_test_list() fail
# 136 # search_sut() fail
# 199 free_sut() fail, len(file) <= 0

# 141 func run_script() fail

class execute_flow ():
    def __init__ (self, p_data, stage_type):

        # load var from  jenkins file
        self.m_dict_info    = {"cmd_log_folder" : ""}
        self.flow_mng       = flow_management(stage_type)

        str_root = os.path.abspath(os.getcwd())
        ret = self.load_conf(p_data, stage_type)
        if (0 != ret):
            print ("load conf fail.[%s]" % ret)
            return fail

        pass

    # load jenkins file here, structure change here
    def load_conf (self, str_file, stage_type):
        if (True == file_mng().check_file_exist(str_file)):

            tmp_cmd_log = "cicd_cmd_log_folder_script="

            if ("stage_build" == stage_type):
                tmp_cmd_log = "cicd_cmd_log_folder_build="

            ret_find, cmd_log_folder_script    = file_mng()._search_in_file(str_file, tmp_cmd_log)
            if (False == ret_find):
                return 123

            m_log_full      = "%s/%s" % (os.path.abspath(os.getcwd()), cmd_log_folder_script.strip().lower())

            self.m_dict_info.update({"cmd_log_folder"       : m_log_full})
            self.m_dict_info.update({"jenkin_filepath"   : str_file.strip().lower()})

        return 0

    def run (self, p_func, stage_type):

        if   ("func_get_script_source"  == p_func):
            return self.flow_mng.get_script_from_server(self.m_dict_info, stage_type)
        elif ("func_modify_script_source"  == p_func):
            return self.flow_mng.modify_script_source(self.m_dict_info, stage_type)
        elif ("func_execute_script"     == p_func):
            return self.flow_mng.execute_script(self.m_dict_info, stage_type)
        elif ("func_execute_build"     == p_func):
            return self.flow_mng.execute_build(self.m_dict_info, stage_type)
        elif ("func_scan_stage"      == p_func):
            return self.flow_mng.run_scan(self.m_dict_info, stage_type)
        elif ("func_upload_report"      == p_func):
            return self.flow_mng.upload_report(self.m_dict_info, stage_type)

        elif ("test_scan_sut"      == p_func):
            return self.flow_mng._get_sut_ip_by_mac(self.m_dict_info, stage_type)

        elif ("func_update_robot_resource"      == p_func):
            return self.flow_mng._func_update_robot_resource(self.m_dict_info, stage_type)

        elif ("get_from_file"      == p_func):
            return self.flow_mng.get_from_file(self.m_dict_info, stage_type)
        elif ("get_from_json"      == p_func):
            return self.flow_mng.get_from_json(self.m_dict_info, stage_type)
        elif ("get_project_json"      == p_func):
            return self.flow_mng.get_project_json(self.m_dict_info, stage_type)


        elif ("func_check_need_testing"      == p_func):
            return self.flow_mng.get_is_test(self.m_dict_info, stage_type)

        else:
            unknown_msg = "unknown unknown unknown"
            return unknown_msg


class flow_management (object):
    def __init__ (self, stage_type):

        self.m_file_sut_info    = "/tmp/robot_framework/sut_info/test_sut_info"
        self.str_nextcloud  = "nextcloud_server_info"
        self.search_json         = search_in_json()

        # self.t_list             = []

        if ("stage_script" == stage_type): # stage_script / stage_build
            self.upload_tag             = "Upload_Script_list"
        elif ("stage_build" == stage_type):
            self.upload_tag             = "Upload_Build_list" # build : upload report

        pass


    def get_cicd_download_key (self, run_type, stage_type):

        run_key = ""
        # stage_build / stage_script
        # type   : daily / review / manual / hotfix
        if ("stage_build" == stage_type):
            if ("daily" == run_type):
                run_key = "Download_Build_Daily_list"
            elif ("review" == run_type):
                run_key = "Download_Build_Review_list"
            elif ("manual" == run_type):
                run_key = "Download_Build_Manual_list"
            elif ("hotfix" == run_type):
                run_key = ""
            else:
                run_key = ""
        elif ("stage_script" == stage_type):
            if ("daily" == run_type):
                run_key = "Download_Script_list"
            elif ("review" == run_type):
                run_key = "Download_Script_list"
            elif ("manual" == run_type):
                run_key = "Download_Script_list"
            elif ("hotfix" == run_type):
                run_key = ""
            else:
                run_key = ""
        else:
            run_key = ""

        return run_key

    def get_cicd_execute_key (self, run_type, stage_type):

        run_key = ""
        # stage_build / stage_script
        # type   : daily / review / manual / hotfix
        if ("stage_build" == stage_type):
            if ("daily" == run_type):
                run_key = "Execute_Build_list"
            elif ("review" == run_type):
                run_key = "Execute_Build_list"
            elif ("manual" == run_type):
                run_key = "Execute_Build_list"
            elif ("hotfix" == run_type):
                run_key = ""
            else:
                run_key = ""
        elif ("stage_script" == stage_type):
            if ("daily" == run_type):
                run_key = "Execute_Script_Daily_list"
            elif ("review" == run_type):
                run_key = "Execute_Script_Review_list"
            elif ("manual" == run_type):
                run_key = "Execute_Script_Manual_list"
            elif ("hotfix" == run_type):
                run_key = ""
            else:
                run_key = ""
        else:
            run_key = ""

        return run_key

    def get_cicd_upload_key (self, run_type, stage_type):

        run_key = ""
        # stage_build / stage_script
        # type   : daily / review / manual / hotfix
        if ("stage_build" == stage_type):
            if ("daily" == run_type):
                run_key = "Upload_Build_list"
            elif ("review" == run_type):
                run_key = "Upload_Build_list"
            elif ("manual" == run_type):
                run_key = "Upload_Build_list"
            elif ("hotfix" == run_type):
                run_key = "Upload_Build_list"
            else:
                run_key = ""
        elif ("stage_script" == stage_type):
            if ("daily" == run_type):
                run_key = "Upload_Script_list"
            elif ("review" == run_type):
                run_key = "Upload_Script_list"
            elif ("manual" == run_type):
                run_key = "Upload_Script_list"
            elif ("hotfix" == run_type):
                run_key = "Upload_Script_list"
            else:
                run_key = ""
        else:
            run_key = ""

        return run_key


    # return daily / review / manual
    def get_type (self, jenkin_info, stage_type):

        ret, ret_type = file_mng()._search_in_file(jenkin_info["jenkin_filepath"], "cicd_script_type=")

        return ret_type

    def get_manual_info (self, local_conf, query_key, return_key):

        nc_srv_info         = self.search_json.get_struct_by_key(local_conf, query_key)

        log_folder          = "no_use"
        log_name            = "%s" % (query_key)
        http_user_pwd       = "%s:%s" % (nc_srv_info["user"], nc_srv_info["pwd"])
        http_url_port       = "%s:%s" % (nc_srv_info["ip"], nc_srv_info["port"])
        nc_user             = "%s" % (nc_srv_info["user"])
        nc_auto_info_path   = "%s" % (nc_srv_info["manual_build_info_path"])
        str_dn_filename     = "%s" % (nc_srv_info["manual_build_info_file"])

        str_output_filename = "get_info.json"
        # from NC  xxx.json had renamed  date_proj_module_type.json   2022_09_02_proj_01_bmcbmc_tag_01.json
        # var xxx in jenkins env file
        
        ret, my_conf = file_mng()._search_in_file("jenkins_env.log", "my_conf_file=")
        str_dn_filename = my_conf

        # check if file is exist, if ture, read info from file, if not download from NC and read info from file
        if (False == file_mng().check_file_exist(str_output_filename)):

            print ("[%s] not exist, download from NC" % (str_output_filename))
            exec_cmd            = "curl --create-dirs -u %s  -X GET  %s/remote.php/dav/files/%s/%s/%s --output %s" % (http_user_pwd, http_url_port, nc_user, nc_auto_info_path, str_dn_filename, str_output_filename)
            ret_tmp             = execute_cmd().exec_shell_cmd(log_folder, log_name, exec_cmd)

        key_in_json         = "manual_build_info"
        build_info          = self.search_json.get_struct_by_key(str_output_filename, key_in_json)
        return build_info[return_key]

    def get_project_info (self,jenkin_info, local_conf, run_type):

        t_project   = "" # oe22, x4tf, z4, amirr13.3
        t_module    = "" # bios, bmc, rmc, xxx
        conf_path   = "" # in script folder project_info/x4tf/x4tf_bmc.json

        if ("manual" == run_type):
            t_project   = self.get_manual_info (local_conf, self.str_nextcloud, "info_project")
            t_module    = self.get_manual_info (local_conf, self.str_nextcloud, "info_target")
            conf_path   = "project_info/%s/%s_%s.json" % (t_project, t_project, t_module)

        else: # type = daily / review
            ret_find, t_project = file_mng()._search_in_file(jenkin_info["jenkin_filepath"], "cicd_script_project=")
            ret_find, t_module  = file_mng()._search_in_file(jenkin_info["jenkin_filepath"], "cicd_script_module=")
            conf_path   = "project_info/%s/%s_%s.json" % (t_project, t_project, t_module)

        return t_project, t_module, conf_path

    def get_local_conf (self):

        tmp_json            = os.path.basename(__file__)
        conf_filename       = "%s.json" % (tmp_json.split(".")[0])
        return conf_filename

    def get_script_from_server (self, jenkin_info, stage_type):

        ret                 = 0
        local_conf           = self.get_local_conf()

        project_info_path   = ""
        project_name        = ""
        run_type            = self.get_type(jenkin_info, stage_type)
        run_key             = self.get_cicd_download_key(run_type, stage_type)

        if (0 < len(run_type)):
            project_name, proj_module, project_info_path = self.get_project_info(jenkin_info, local_conf, run_type)
        else:
            print ("error get_type() return empty")

        str_json_info       = self.search_json.get_struct_by_key(project_info_path, run_key)

        int_count           = int(str_json_info["count"])

        # loop to execute list 
        for i_idx in range(1, int_count + 1) :

            query_key   = str(i_idx).zfill(2)
            str_type    = str_json_info[query_key]
            ret_tmp     = self._git_download(jenkin_info, str_type, stage_type)
            ret |= ret_tmp

        return ret

    def modify_script_source (self, jenkin_info, stage_type):

        local_conf          = self.get_local_conf()
        run_type            = self.get_type(jenkin_info, stage_type)
        run_key             = self.get_cicd_download_key(run_type, stage_type)
        project_name, proj_module, project_info_path = self.get_project_info(jenkin_info, local_conf, run_type)

        ret = file_mng()._copy_source(project_info_path, "Copy_Script")
        print ("Copy_Script ret = %s" % ret)
        if (False == ret):
            return 131 

        ret = file_mng()._overwrite_source(project_info_path, "Overwrite_Script")
        print ("Overwrite_Script ret = %s" % ret)
        if (False == ret):
            return 132

        return 0


    def execute_script (self, jenkin_info, stage_type):

        ret                 = 0
        local_conf          = self.get_local_conf()
        run_type            = self.get_type(jenkin_info, stage_type)
        run_key             = self.get_cicd_execute_key(run_type, stage_type)

        if (0 < len(run_type)):
            project_name, proj_module, project_info_path = self.get_project_info(jenkin_info, local_conf, run_type)
        else:
            print ("error get_type() return empty")

        str_json_info       = self.search_json.get_struct_by_key(project_info_path, run_key)
        int_count           = int(str_json_info["count"])

        root_path = pathlib.Path().resolve()

        # loop to execute list 
        for i_idx in range(1, int_count + 1):

            # python multi thread here~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            # stop multi thread, some data no mutex() lock(), will error

            query_key   = str(i_idx).zfill(2)
            str_type    = str_json_info[query_key]

            # self.t_list.append( 
            # threading.Thread(target=self.run_script, args=(jenkin_info, str_type, root_path)) )

            ret_tmp     = self.run_script(jenkin_info, str_type, stage_type, root_path)
            ret |= ret_tmp

        # for i_idx in range(len(self.t_list)):
        #     self.t_list[i_idx].start()

        # for i_idx in self.t_list:
        #     i_idx.join()

        return ret

    def run_scan_cppcheck (self, jenkin_info, stage_type):
        ret = 0

        # cppcheck : run cppcheck in type = review only

        local_conf          = self.get_local_conf()
        run_type            = self.get_type(jenkin_info, stage_type)
        run_key             = self.get_cicd_download_key(run_type, stage_type)

        if (0 < len(run_type)):
            project_name, proj_module, project_info_path = self.get_project_info(jenkin_info, local_conf, run_type)
        else:
            print ("error get_type() return empty")

        str_default_dir = pathlib.Path().resolve()
        print ("scan : cppcheck")
        if ("review" == run_type):
            cppcheck_info       = self.search_json.get_struct_by_key(project_info_path, "cpp_check_cmd")
            print ("cppcheck_info = %s" % cppcheck_info)

            print ("curr path = %s" % str_default_dir)

            new_dir = cppcheck_info["work_dir"]
            print ("change to cpp_check_cmd-work_dir = %s" % new_dir)

            cmd_work_dir = "%s/%s" % (str_default_dir, new_dir)
            if (0 < len(cmd_work_dir)):
                print ("chdir to %s" % cmd_work_dir)
                os.chdir(cmd_work_dir)

            ret_flag = 0
            print ("ret_flag bf = %s" % ret_flag)
            int_count = int(cppcheck_info["count"])
            log_folder = cppcheck_info["log_folder"]
            log_name = "cpp_check_cmd"
            for i_idx in range(1, int_count + 1):

                query_key   = str(i_idx).zfill(2)
                exec_cmd    = cppcheck_info[query_key]

                print ("exec_cmd = %s" % exec_cmd)
                ret_tmp         = execute_cmd().exec_shell_cmd(log_folder, log_name, exec_cmd)
                ret_flag = ret_flag | ret_tmp

                print ("[%s] ret_flag = %s" % (i_idx, ret_flag))


            print ("ret_flag af = %s" % ret_flag)




        print ("return to default work dir")
        os.chdir(str_default_dir)
        return ret

    def run_scan_white_source (self, jenkin_info, stage_type):

        ret = 0

        # check cmd execute result, using flag ret
        # if (0 != cmd_ret):
        #     ret = 1999

        # if (0 == ret):
        #     print("do next step")


        local_conf          = self.get_local_conf()
        run_type            = self.get_type(jenkin_info, stage_type)
        run_key             = self.get_cicd_execute_key(run_type, stage_type)

        if (0 < len(run_type)):
            project_name, proj_module, project_info_path = self.get_project_info(jenkin_info, local_conf, run_type)
        else:
            print ("error get_type() return empty")

        ret_find, job_build_id = file_mng()._search_in_file(jenkin_info["jenkin_filepath"], "BUILD_ID=")
        print ("find build id from jenkins env for ws folder name : ret, value = [%s][%s]\n" % (ret_find, job_build_id))

        if ( "manual" == run_type):

            is_white_source     = self.get_manual_info (local_conf, self.str_nextcloud, "scan_whitesource")

            if ("Y" == is_white_source):
                print ("load win10 server info from cicd_func.json")

                # load from [cicd_func.json] key = [scan_white_source]
                run_key         = "white_source_info"
                ws_info         = self.search_json.get_struct_by_key(local_conf, run_key)

                ws_ip           = ws_info["ws_ip"]

                ws_ssh_key = ""
                if ("bios" == proj_module): # bios run win10
                    ws_ssh_key      = ws_info["ws_ssh_key_bios_win10"]
                else: # bmc / rmc  run docker
                    ws_ssh_key      = ws_info["ws_ssh_key_bmc_docker"]

                print ("RUN MODULE [%s], SSH KEY path [%s]" % (proj_module, ws_ssh_key))

                ws_id           = ws_info["ws_id"]

                org_api_key     = ws_info["org_api_key"]
                product_token   = ws_info["product_token"]
                user_key        = ws_info["user_key"]

                ws_net_disk_ip          = ws_info["ws_net_disk_ip"]
                ws_net_disk_folder          = ws_info["ws_net_disk_folder"]

                ws_dir          = ws_info["ws_dir"]

                ws_client_zip   = ws_info["ws_client_zip"]

                ws_run_bat_path = ws_info["ws_run_bat_path"]
                ws_run_bat      = ws_info["ws_run_bat"]

                ws_jar_config_path     = ws_info["ws_jar_config_path"]
                ws_jar_config   = ws_info["ws_jar_config"]

                ws_jar_path     = ws_info["ws_jar_path"]
                ws_jar          = ws_info["ws_jar"]
                ws_jar_ver      = ws_info["ws_jar_ver"]

                ws_netdisk_bios_ip      = ws_info["ws_netdisk_bios_ip"]
                ws_netdisk_bios_id      = ws_info["ws_netdisk_bios_id"]
                ws_netdisk_bios_pwd      = ws_info["ws_netdisk_bios_pwd"]
                ws_netdisk_bios_folder = ws_info["ws_netdisk_bios_folder"]


                # folder name - proj_module_buildID
                ws_dir_folder   = "%s_%s_%s" % (project_name, proj_module, job_build_id)


                # load from [x4tf.json] key = [scan_white_source]
                run_key         = "scan_white_source"
                wwss_info       = self.search_json.get_struct_by_key(project_info_path, run_key)

                scan_folder     = wwss_info["scan_info"]["folder"]
                ws_log_folder   = wwss_info["scan_info"]["log_folder"]
                log_file        = wwss_info["scan_info"]["log_file"]

                # flow
                # - mkdir F_XXX folder [project_module_build_id][x4tf_bmc_18]
                # - copy asus_oss.zip to ./F_XXX
                # - unzip asus_oss.zip
                # - copy scan folder into asus_oss/sourcecode/
                # - copy wss-unified-agent.jar to asus_oss/config/unifiedagent/wss-unified-agent-22.0.8.jar
                # - update asus_oss/config/wss-unified-agent.config
                # - update asus_oss/scan.bat
                # - ssh to win10 and mount network disk ( net use \\10.10.65.115\public\FOLDER)
                # - ssh to win10 and run \\10.10.65.115\public\FOLDER\ASUS_OSS\Scan.bat
                # - ssh to win10 and umount network disk ( net use /delete \\10.10.65.115\public\FOLDER)


                ################
                # create foder X for win10 use
                ################
                # mkdir x4tf_bmc_9

                mkdir_cmd = "mkdir %s" % (ws_dir_folder)

                print ("create foder for win10 use")
                ret_tmp  = execute_cmd().exec_shell_cmd(ws_log_folder, log_file, mkdir_cmd)
                print ("cmd = %s \n    ret = %s\n" % (mkdir_cmd, ret_tmp))


                ################
                # unzip ASUS_OSS.zip to foder X
                ################
                # docker : unzip ASUS_OSS.zip -d x4tf_bmc_9/
                # win10  : tar -xf ASUS_OSS.zip -C ws_console


                cp_cmd = ""
                if ("bios" == proj_module): # bios run win10
                    cp_cmd = "tar -xf %s -C %s" % (ws_client_zip, ws_dir_folder)
                else: # bmc / rmc  run docker
                    cp_cmd = "unzip %s -d %s" % (ws_client_zip, ws_dir_folder)

                print ("unzip ASUS_OSS.zip to foder X")
                ret_tmp  = execute_cmd().exec_shell_cmd(ws_log_folder, log_file, cp_cmd)
                print ("cmd = %s \n    ret = %s\n" % (cp_cmd, ret_tmp))

                ################
                # copy wss-unified-agent.jar to folder X /config/unifiedagent/wss-unified-agent-x.x.x.jar
                ################
                # ws_jar : wss-unified-agent.jar
                # jar_new : wss-unified-agent-22.8.2.jar
                # jar_path : x4tf_bios_25/Config/UnifiedAgent

                # docker : cp  ws_jar  jar_path/jar_new
                # win10  : copy ws_jar jar_path && cd jar_path && ren ws_jar jar_new

                # "x4tf_bios_25/Config/UnifiedAgent/"
                jar_new = "%s-%s.%s" % (ws_jar.split(".")[0], ws_jar_ver, ws_jar.split(".")[1])
                jar_path= "%s/%s/" % (ws_dir_folder, ws_jar_path)

                cp_cmd = ""
                if ("bios" == proj_module): # bios run win10
                    cp_cmd = "copy %s \"%s\" && cd %s && ren %s %s" % (ws_jar, jar_path, jar_path, ws_jar, jar_new)
                else: # bmc / rmc  run docker
                    cp_cmd = "cp %s  %s/%s" % (ws_jar, jar_path, jar_new)

                print ("copy wss.jar to foder X /config/unifiedagent/wss-ver.jar")
                ret_tmp  = execute_cmd().exec_shell_cmd(ws_log_folder, log_file, cp_cmd)
                print ("cmd = %s \n    ret = %s\n" % (cp_cmd, ret_tmp))


                ################
                # copy scan folders to folder X /Sourcecode/xxx
                ################
                # cmd = cp -r build/MDS/workspace/Build/busybox x4tf_bmc_24/SourceCode 
                # docker: cp -r project_info ws_console
                # win10 : xcopy project_info ws_console /s /h /e /k /f /c

                folder_cnt   = int(scan_folder["count"])

                for idx in range(1, folder_cnt + 1):
                    my_key      = str(idx).zfill(2)
                    cp_src      = scan_folder[my_key]
                    cp_dest     = "%s/%s" % (ws_dir_folder, "SourceCode")

                    cp_cmd = ""
                    if ("bios" == proj_module): # bios run win10
                        cp_cmd = "xcopy \"%s\" \"%s\" /s /h /e /k /f /c" % (cp_src, cp_dest)
                    else: # bmc / rmc  run docker
                        cp_cmd = "cp -r %s %s" % (cp_src, cp_dest)


                    print ("copy scan folder to folder X /SourceCode")
                    ret_tmp  = execute_cmd().exec_shell_cmd(ws_log_folder, log_file, cp_cmd)
                    print ("cmd = %s \n    ret = %s\n" % (cp_cmd, ret_tmp))


                ################
                # update Scan.bat
                ################
                # Scan.bat : save_data_to_file() [x4tf_bmc_24/Scan.bat][set version=][22.8.2]
                # rm pause in Scan.bat  cmd = sed -i 's/pause//g' x4tf_bmc_24/Scan.bat 

                modify_file = "%s/%s" % (ws_dir_folder, ws_run_bat)
                if ("bios" == proj_module): # bios run win10

                    old_string="set version="
                    new_string="set version=%s" % (ws_jar_ver)
                    replace_cmd = "powershell -Command \"(gc %s) -replace '%s', '%s' | Out-File -encoding ASCII %s\"" % (modify_file, old_string, new_string, modify_file)
                    print ("replace string in [%s],old[%s],new[%s]" % (ws_run_bat, old_string, new_string))
                    ret_tmp  = execute_cmd().exec_shell_cmd(ws_log_folder, log_file, replace_cmd)
                    print ("cmd = %s \n    ret = %s\n" % (replace_cmd, ret_tmp))

                    old_string="set apiKey="
                    new_string="set apiKey=%s" % (org_api_key)
                    replace_cmd = "powershell -Command \"(gc %s/%s) -replace '%s', '%s' | Out-File -encoding ASCII %s/%s\"" % (ws_dir_folder, ws_run_bat, old_string, new_string, ws_dir_folder, ws_run_bat)
                    print ("replace string in [%s],old[%s],new[%s]" % (ws_run_bat, old_string, new_string))
                    ret_tmp  = execute_cmd().exec_shell_cmd(ws_log_folder, log_file, replace_cmd)
                    print ("cmd = %s \n    ret = %s\n" % (replace_cmd, ret_tmp))

                    old_string="set productToken="
                    new_string="set productToken=%s" % (product_token)
                    replace_cmd = "powershell -Command \"(gc %s/%s) -replace '%s', '%s' | Out-File -encoding ASCII %s/%s\"" % (ws_dir_folder, ws_run_bat, old_string, new_string, ws_dir_folder, ws_run_bat)
                    print ("replace string in [%s],old[%s],new[%s]" % (ws_run_bat, old_string, new_string))
                    ret_tmp  = execute_cmd().exec_shell_cmd(ws_log_folder, log_file, replace_cmd)
                    print ("cmd = %s \n    ret = %s\n" % (replace_cmd, ret_tmp))

                    old_string="set projectName="
                    new_string="set projectName=%s_%s" % (project_name, proj_module)
                    replace_cmd = "powershell -Command \"(gc %s/%s) -replace '%s', '%s' | Out-File -encoding ASCII %s/%s\"" % (ws_dir_folder, ws_run_bat, old_string, new_string, ws_dir_folder, ws_run_bat)
                    print ("replace string in [%s],old[%s],new[%s]" % (ws_run_bat, old_string, new_string))
                    ret_tmp  = execute_cmd().exec_shell_cmd(ws_log_folder, log_file, replace_cmd)
                    print ("cmd = %s \n    ret = %s\n" % (replace_cmd, ret_tmp))

                    old_string="pause"
                    new_string="rem pause"
                    replace_cmd = "powershell -Command \"(gc %s/%s) -replace '%s', '%s' | Out-File -encoding ASCII %s/%s\"" % (ws_dir_folder, ws_run_bat, old_string, new_string, ws_dir_folder, ws_run_bat)
                    print ("replace string in [%s],old[%s],new[%s]" % (ws_run_bat, old_string, new_string))
                    ret_tmp  = execute_cmd().exec_shell_cmd(ws_log_folder, log_file, replace_cmd)
                    print ("cmd = %s \n    ret = %s\n" % (replace_cmd, ret_tmp))

                else:

                    old_string="set version="
                    new_string="%s" % (ws_jar_ver)
                    print ("%s : save_data_to_file() [%s][%s][%s]" % (ws_run_bat, modify_file, old_string, new_string))
                    write_ret = self.save_data_to_file (modify_file, old_string, new_string)

                    old_string="set apiKey="
                    new_string="%s" % (org_api_key)
                    print ("%s : save_data_to_file() [%s][%s][%s]" % (ws_run_bat, modify_file, old_string, new_string))
                    write_ret = self.save_data_to_file (modify_file, old_string, new_string)

                    old_string="set productToken="
                    new_string="%s" % (product_token)
                    print ("%s : save_data_to_file() [%s][%s][%s]" % (ws_run_bat, modify_file, old_string, new_string))
                    write_ret = self.save_data_to_file (modify_file, old_string, new_string)

                    old_string="set projectName="
                    new_string="%s_%s" % (project_name, proj_module)
                    print ("%s : save_data_to_file() [%s][%s][%s]" % (ws_run_bat, modify_file, old_string, new_string))
                    write_ret = self.save_data_to_file (modify_file, old_string, new_string)

                    cmd_rm_pause = "sed -i 's/pause//g' %s" % modify_file

                    print ("remove command prompt [pause] in Scan.bat")
                    ret_tmp  = execute_cmd().exec_shell_cmd(ws_log_folder, log_file, cmd_rm_pause)
                    print ("cmd = %s \n    ret = %s\n" % (cmd_rm_pause, ret_tmp))
                # end else

                ################
                # update Config/wss-unified-agent.config
                ################
                # docker : wss-unified-agent.config : save_data_to_file() [x4tf_bmc_24/Config/wss-unified-agent.config][apiKey=][8a59fd0dd4b9414b8dba058d8b47be298da78ae8a8124773adcc533907606fd3]
                # win10 : powershell -Command "(gc x4tf_bios_25/Config/wss-unified-agent.config) -replace 'userKey=', 'userKey=b2933982493344e5802eee9f796a44158f23c97e65044c31b7f66960ce675425' | Out-File -encoding ASCII x4tf_bios_25/Config/wss-unified-agent.config"

                modify_file = "%s/%s/%s" % (ws_dir_folder, ws_jar_config_path, ws_jar_config)
                if ("bios" == proj_module): # bios run win10

                    old_string="apiKey="
                    new_string="apiKey=%s" % (org_api_key)
                    replace_cmd = "powershell -Command \"(gc %s) -replace '%s', '%s' | Out-File -encoding ASCII %s\"" % (modify_file, old_string, new_string, modify_file)
                    print ("replace string in [%s],old[%s],new[%s]" % (ws_run_bat, old_string, new_string))
                    ret_tmp  = execute_cmd().exec_shell_cmd(ws_log_folder, log_file, replace_cmd)
                    print ("cmd = %s \n    ret = %s\n" % (replace_cmd, ret_tmp))


                    old_string="userKey="
                    new_string="userKey=%s" % (user_key)
                    replace_cmd = "powershell -Command \"(gc %s) -replace '%s', '%s' | Out-File -encoding ASCII %s\"" % (modify_file, old_string, new_string, modify_file)
                    print ("replace string in [%s],old[%s],new[%s]" % (ws_run_bat, old_string, new_string))
                    ret_tmp  = execute_cmd().exec_shell_cmd(ws_log_folder, log_file, replace_cmd)
                    print ("cmd = %s \n    ret = %s\n" % (replace_cmd, ret_tmp))
                    
                else:

                    old_string="apiKey="
                    new_string="%s" % (org_api_key)
                    print ("%s : save_data_to_file() [%s][%s][%s]" % (ws_jar_config, modify_file, old_string, new_string))
                    write_ret = self.save_data_to_file (modify_file, old_string, new_string)

                    old_string="userKey="
                    new_string="%s" % (user_key)
                    print ("%s : save_data_to_file() [%s][%s][%s]" % (ws_jar_config, modify_file, old_string, new_string))
                    write_ret = self.save_data_to_file (modify_file, old_string, new_string)


                ################
                # execute folder x /Scan.bat
                ################
                # # ssh -i /var/jenkins_home/.ssh/win10 neil@10.10.65.115  "\\\\10.10.65.57\public\JENKINS_JOB\x4tf_bmc_9\Scan.bat"
                # JOB_NAME=x4tf_bios_CodeReview     BUILD_ID=3


                if ("bios" == proj_module): # bios run win10

                    ret_find, ws_job_name   = file_mng()._search_in_file(jenkin_info["jenkin_filepath"], "JOB_NAME=")
                    ret_find, ws_job_id     = file_mng()._search_in_file(jenkin_info["jenkin_filepath"], "BUILD_ID=")


                    job_folder = "%s__%s" % (ws_job_name, ws_job_id)

                    print ("execute folder x /Scan.bat (test docker path)")
                    run_cmd = "ssh -i %s %s@%s \" \\\\\\\\%s\\%s\\%s\\%s\\%s \"" % (ws_ssh_key, ws_id, ws_ip, ws_net_disk_ip, ws_net_disk_folder, job_folder, ws_dir_folder, ws_run_bat)
                    # ret_tmp  = execute_cmd().exec_shell_cmd(ws_log_folder, log_file, run_cmd)
                    ret_tmp = 99999
                    print ("cmd = %s \n    ret = %s\n" % (run_cmd, ret_tmp))


                    remote_dis_ip   = ws_netdisk_bios_ip
                    remote_dis_id   = ws_netdisk_bios_id
                    remote_dis_pwd  = ws_netdisk_bios_pwd
                    ret_find, script_folder     = file_mng()._search_in_file(jenkin_info["jenkin_filepath"], "bios_build_folder=")
# bios_build_folder in jenkins
                    # \\10.10.65.108\BIOS
                    # \\10.10.65.108\BIOS\J_PROJ\J_TYPE\J_BUILD_ID\ooxx_script_folder\ws_dir_folder\ws_run_bat
                    # \\10.10.65.108\BIOS  x4tf   manual   5       script_all_draft   x4tf_bios_5   scan.bat
                    print ("execute folder x /Scan.bat")
                    # remote_disk = "\\\\\\\\%s\\%s" % (remote_dis_ip, ws_netdisk_bios_folder)
                    remote_disk = "\\\\%s\\%s" % (remote_dis_ip, ws_netdisk_bios_folder)
                    # remote_work = "\\\\\\\\%s\\%s\\%s\\%s\\%s\\%s\\%s" % (remote_dis_ip, ws_netdisk_bios_folder, project_name, run_type, job_build_id, ws_dir_folder, ws_run_bat)
                    remote_work = "\\\\%s\\%s\\%s\\%s\\%s\\%s\\%s\\%s" % (remote_dis_ip, ws_netdisk_bios_folder, project_name, run_type, job_build_id, script_folder,  ws_dir_folder, ws_run_bat)
                    run_cmd = "ssh -i %s %s@%s \"net use %s /user:%s %s && %s \"" % (ws_ssh_key, ws_id, ws_ip, remote_disk, remote_dis_id, remote_dis_pwd, remote_work)
                    ret_tmp  = execute_cmd().exec_shell_cmd(ws_log_folder, log_file, run_cmd)
                    print ("cmd = %s \n    ret = %s\n" % (run_cmd, ret_tmp))

                    # ssh -i c:/Users/bios/.ssh/win10 neil@10.10.65.115 "net use \\10.10.65.108\ben /user:bios bios && \\10.10.65.108\ben\x4tf_bios_25\Scan.bat "
                    #"net use \\10.10.65.108\BIOS /user:bios bios && \\10.10.65.108\BIOS\J_PROJ\J_MODULE\J_BUILD_ID\ws_dir_folder\ws_run_bat"
                    # ssh -i c:/Users/bios/.ssh/win10 neil@10.10.65.115 "net use /delete \\10.10.65.108\ben

                    print ("unmount network disk")
                    remote_disk = "\\\\\\\\%s\\%s" % (remote_dis_ip, ws_netdisk_bios_folder)
                    
                    run_cmd = "ssh -i %s %s@%s \"net use /delete %s \"" % (ws_ssh_key, ws_id, ws_ip, remote_disk)
                    ret_tmp  = execute_cmd().exec_shell_cmd(ws_log_folder, log_file, run_cmd)
                    print ("cmd = %s \n    ret = %s\n" % (run_cmd, ret_tmp))

                else:

                    # create folder name (xxx) in /tmp/jenkins/xxx  ==  \\ip\public\xxx
                    ret_find, ws_job_name = file_mng()._search_in_file(jenkin_info["jenkin_filepath"], "JOB_NAME=")
                    ret_find, ws_job_id = file_mng()._search_in_file(jenkin_info["jenkin_filepath"], "BUILD_ID=")


                    job_folder = "%s__%s" % (ws_job_name, ws_job_id)

                    print ("execute folder x /Scan.bat")
                    run_cmd = "ssh -i %s %s@%s \" \\\\\\\\%s\\%s\\%s\\%s\\%s \"" % (ws_ssh_key, ws_id, ws_ip, ws_net_disk_ip, ws_net_disk_folder, job_folder, ws_dir_folder, ws_run_bat)
                    ret_tmp  = execute_cmd().exec_shell_cmd(ws_log_folder, log_file, run_cmd)
                    print ("cmd = %s \n    ret = %s\n" % (run_cmd, ret_tmp))
                # end else



                # mount network disk and run Scan.bat
# ssh -i c:/Users/bios/.ssh/win10 neil@10.10.65.115 "net use \\10.10.65.108\ben /user:bios bios && \\10.10.65.108\ben\x4tf_bios_25\Scan.bat"



                # print ("- ssh to win10 and mount network disk ( net use \\10.10.65.115\public\FOLDER)")
                # print ("- ssh to win10 and umount network disk ( net use /delete \\10.10.65.115\public\FOLDER)")

        return ret

    # python3  cicd_func.py  jenkins_env.log  func_scan_stage  stage_build
    def run_scan (self, jenkin_info, stage_type):

        ret         = 0
        run_type    = self.get_type(jenkin_info, stage_type)

        # scan : cppcheck run or not
        ret_find, is_need_need_cppcheck = file_mng()._search_in_file("jenkins_env.log", "cicd_scan_cppcheck=")
        if (True != ret_find):
            ret_flag = 145
            ret_msg = "load cppcheck various from jenkins env fail."
            print (ret_msg)

        if (("review" == run_type) and ("Y" == is_need_need_cppcheck)):
            ret = self.run_scan_cppcheck(jenkin_info, stage_type)
            print ("run_scan_cppcheck : ret = %s" % ret)
        else:
            print ("scan : cppcheck [no run]")
            print ("scan cppcheck various = [%s] or cicd type = [%s]." % (is_need_need_cppcheck, run_type))


        # scan : whitesource run or not
        ret_find, is_need_need_whitesource = file_mng()._search_in_file("jenkins_env.log", "cicd_scan_whitesource=")
        if (True != ret_find):
            ret_flag = 145
            ret_msg = "load whitesource various from jenkins env fail."
            print (ret_msg)

        if ("Y" == is_need_need_whitesource):
            ret = self.run_scan_white_source (jenkin_info, stage_type)
            print ("run_scan_white_source : ret = %s" % ret)
        else:
            print ("scan : whitesource [no run]")
            print ("scan whitesource various = [%s]" % (is_need_need_whitesource))

        return ret

    def execute_build (self, jenkin_info, stage_type):

        ret                 = 0
        local_conf           = self.get_local_conf()

        project_info_path   = ""
        project_name        = ""
        run_type            = self.get_type(jenkin_info, stage_type)
        run_key             = self.get_cicd_execute_key(run_type, stage_type)

        if (0 < len(run_type)):
            project_name, proj_module, project_info_path = self.get_project_info(jenkin_info, local_conf, run_type)
        else:
            print ("error get_type() return empty")


        str_json_info       = self.search_json.get_struct_by_key(project_info_path, run_key)
        int_count           = int(str_json_info["count"])

        # loop to execute list 
        for i_idx in range(1, int_count + 1) : # 01 02 03   range (1,4)

            query_key   = str(i_idx).zfill(2)
            str_type    = str_json_info[query_key]

            ret_tmp     = self._run_build(jenkin_info, str_type)
            ret |= ret_tmp

        if (0 != ret):
            return 134

        return ret


    def upload_report (self, jenkin_info, stage_type):

        ret                 = 0
        local_conf          = self.get_local_conf()
        run_type            = self.get_type(jenkin_info, stage_type)
        run_key             = self.get_cicd_execute_key(run_type, stage_type)

        upload_key          = self.get_cicd_upload_key(run_type, stage_type)

        if (0 < len(run_type)):
            project_name, proj_module, project_info_path = self.get_project_info(jenkin_info, local_conf, run_type)
        else:
            print ("error get_type() return empty")

        str_json_info       = self.search_json.get_struct_by_key(project_info_path, upload_key)
        int_count           = int(str_json_info["count"])

        # loop to execute list 
        for i_idx in range(1, int_count + 1) : # 01 02 03   range (1,4)

            query_key   = str(i_idx).zfill(2)
            str_type    = str_json_info[query_key]
            ret_tmp     = self._upload_report(jenkin_info, local_conf, str_type)
            ret |= ret_tmp

        return ret


    def load_data_from_file (self, str_file, load_key):

        load_value = ""

        # check file exist here.
        reading_file = open(str_file, "r")

        new_file_content = ""
        for line in reading_file:

            stripped_line = line.strip()
            if (0 <= stripped_line.find(load_key)):
                new_line = load_key + load_value
                load_value = stripped_line.split(load_key)[1]

        reading_file.close()

        return load_value

    def save_data_to_file (self, str_file, update_key, str_value):

        b_ret = 0
        # check file exist here.
        # if (file not exist, b_ret = False, return False, print "err msg")
        
        reading_file = open(str_file, "r")

        new_file_content = ""
        for line in reading_file:
            stripped_line = line.strip()
            if (0 <= stripped_line.find(update_key)):
                new_line = "%s%s" % (update_key, str_value)
            else:
                new_line = stripped_line
            new_file_content += new_line +"\r\n"

        reading_file.close()

        writing_file = open(str_file, "w")
        writing_file.write(new_file_content)
        writing_file.close()

        return b_ret


    def free_sut (self, jenkin_info, json_key):

        local_conf          = self.get_local_conf()
        run_type            = self.get_type(jenkin_info, stage_type)
        run_key             = self.get_cicd_execute_key(run_type, stage_type)

        if (0 < len(run_type)):
            project_name, proj_module, project_info_path = self.get_project_info(jenkin_info, local_conf, run_type)
        else:
            print ("error get_type() return empty")

        test_info       = dict(self.search_json.get_struct_by_key(project_info_path, json_key))
        str_sut_name    = self.load_data_from_file (jenkin_info["jenkin_filepath"], test_info["sut_name"])

        if(0 >= len(str_sut_name)):
            return 199
        update_key      = "%s=" % str_sut_name
        update_value    = "N"
        write_ret = self.save_data_to_file (self.m_file_sut_info, update_key, update_value)

        # print ("free sut = %s" % str_sut_name)
        return 0


    # python3  cicd_func.py  jenkins_env.log  test_scan_sut  stage_script
    def _get_sut_ip_by_mac (self, jenkin_info, stage_type, str_searched="z4_bmc_01"):

        print ("get_sut_ip_by_mac --> search sut name = [%s]" % (str_searched))
        ret_msg             = "" # error msg  or  sut ip
        str_mac_from_nc     = ""
        ret_flag            = 0
        local_conf          = self.get_local_conf()
        run_type            = self.get_type(jenkin_info, stage_type)

        # get nextcloud info
        srv_info            = self.search_json.get_struct_by_key(local_conf, self.str_nextcloud)
        nc_user             = srv_info["user"]
        nc_sut_info_path    = srv_info["autotest_sut_info_path"]
        nc_sut_info_file    = srv_info["autotest_sut_info_file"]
        http_user_pwd       = "%s:%s" % (nc_user, srv_info["pwd"])
        http_url_port       = "%s:%s" % (srv_info["ip"], srv_info["port"])

        #check file exist [nc_sut_info_file][ESR.json]
        if (False == file_mng().check_file_exist(nc_sut_info_file)):

            print ("[%s] not found, download from NC" % (nc_sut_info_file))
            exec_cmd    = "curl --create-dirs -u %s  -X GET  %s/remote.php/dav/files/%s/%s/%s --output %s" % (http_user_pwd, http_url_port, nc_user, nc_sut_info_path, nc_sut_info_file, nc_sut_info_file)
            log_folder  = jenkin_info["cmd_log_folder"]
            str_tag     = "search_sut_ip.txt"
            ret_tmp     = execute_cmd().exec_shell_cmd(log_folder, str_tag, exec_cmd)

            if (0 != ret_tmp):
               ret_flag = 144
               ret_msg = "download ESR.json fail"

        if (0 == ret_flag):

            jenkin_env = "jenkins_env.log"
            ret_find, key_project = file_mng()._search_in_file(jenkin_env, "cicd_script_project=")
            if (True != ret_find):
                ret_flag = 145
                ret_msg = "search in jenkin env fail"

            ret_find, key_module  = file_mng()._search_in_file(jenkin_env, "cicd_script_module=")
            if (True != ret_find):
                ret_flag = 145
                ret_msg = "search in jenkin env fail"

        if (0 == ret_flag):

            pi_key = "console_info"
            pi_info    = self.search_json.get_struct_by_key(nc_sut_info_file, pi_key)

            i_cnt = int(pi_info["count"])
            for idx in range(1, i_cnt + 1):

                check_name      = "%s_%s" % (pi_key, str(idx).zfill(2))

                pi_ip           = pi_info[check_name]["console_ip"]
                pi_id           = pi_info[check_name]["console_id"]
                pi_ssh_key      = pi_info[check_name]["console_cert"]
                pi_ser2net_path = pi_info[check_name]["conf_path"]
                pi_ser2net_name = pi_info[check_name]["conf_name"]
                pi_console_id   = pi_info[check_name]["tn_id"]
                pi_console_pwd  = pi_info[check_name]["tn_pwd"]

            proj_key    = "%s_%s" % (key_project, key_module)
            sut_info    = self.search_json.get_struct_by_key(nc_sut_info_file, proj_key)

            for str_key in sut_info:
                if str_key == str_searched:
                    str_mac_from_nc = sut_info[str_key]["check_mac"]
                    print ("find sut [%s], get mac [%s]" % (str_searched, str_mac_from_nc))

            if (0 >= len(str_mac_from_nc)):
                ret_flag = 146
                ret_msg = "cannot find mac on nc xxx.json"

        if (0 == ret_flag):

            # nmap -sP 10.10.65.172/24 | grep -i 10:96:E8:FE:A2:A2 -B 2 | grep "Nmap scan" | awk '{print $5}' | sed 's/[()]//g'
            # 10.10.65.88

            find_key = "Nmap scan report for"
            #run_cmd  = "nmap -sP %s/24  | grep -i %s -B 2 | grep \"%s\" | awk '{print $5}' | sed 's/[()]//g'" % (pi_ip, str_mac_from_nc, find_key)
            run_cmd  = "arp -n|grep -i %s | awk '{print $1}'" % (str_mac_from_nc)
            print ("find ip via nmap, cmd = [%s]" % (run_cmd))

            log_path = jenkin_info["cmd_log_folder"]
            log_name = "download_from_pi.txt"
            ret_tmp, my_out, my_err  = execute_cmd().exec_shell_cmd_and_get(log_path, log_name, run_cmd)
            if (0 == ret_tmp):
                ret_msg = my_out.strip()
            else:
                ret_msg = "cannot get ip via nmap command"

                ########### Do NOT remove, can be used while connnect to console log ###########

                ### put win.pub to pi server  &  download ser2net.conf ###
                # cat win10.pub | ssh pi@10.10.65.172 "mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
                # scp -i win10 -r pi@10.10.65.172:/etc/ser2net.conf ./ser2net.conf

                

                # # run_cmd  = "scp -i %s -r %s@%s:/%s/%s %s" % (pi_ssh_key, pi_id, pi_ip, pi_ser2net_path, pi_ser2net_name, pi_ser2net_name)
                # # add para -o StrictHostKeyChecking=no to avoid [Are you sure you want to continue connecting (yes/no/[fingerprint])?]
                # run_cmd  = "scp -i %s -o StrictHostKeyChecking=no -r %s@%s:/%s/%s %s" % (pi_ssh_key, pi_id, pi_ip, pi_ser2net_path, pi_ser2net_name, pi_ser2net_name)
                # log_path = jenkin_info["cmd_log_folder"]
                # log_name = "download_from_pi.txt"
                # ret_tmp  = execute_cmd().exec_shell_cmd(log_path, log_name, run_cmd)
                # print ("cmd = %s \n    ret = %s\n" % (run_cmd, ret_tmp))


                # for loop ser2net.conf, line 1 no used
                # BANNER:banner:\r\nser2net port \p device \d [\s] (Debian GNU/Linux)\r\n\r\n
                # 2000:telnet:0:/dev/ttyUSB0:115200 8DATABITS NONE 1STOPBIT banner

                # fopen ser2net.conf as f:
            #     for line in lines:
            #         line = line.strip() # remove white spaces
            #         if line:
            #             if i == 1:
            #                 # BANNER:banner:\r\nser2net port \p device \d [\s] (Debian GNU/Linux)\r\n\r\n
            #                 # print ("line 1 : do nothing")
            #                 i = i + 1
            #             else:
            #                 # here need retry [10.10.10.10 maybe recv  10.xxxx.1xxx0.10.10]
            #                 # 2000:telnet:0:/dev/ttyUSB0:115200 8DATABITS NONE 1STOPBIT banner
            #                 # def func_get_sut_mac (tn_info, send_cmd)
            #                 while mac_retry_cnt >= idx:

            #                     get_port = line.split(":")[0]
            #                     print ("\nport = %s" % get_port)
            #                     cmd_get_mac = "ifconfig eth0 | grep 'HWaddr' | awk '{print $5}'"
            #                     tn_info     = {"tn_ip":pi_ip, "tn_port":get_port, "tn_id":pi_console_id, "tn_pwd":pi_console_pwd}
            #                     ret, sut_mac= tn.telnet_get(tn_info, cmd_get_mac)
            #                     print ("search sut mac ret[%s], msg[%s]" % (ret, sut_mac))

            #                     if (0 == ret and (sut_mac.lower() == str_mac_from_nc.lower())):
            #                         cmd_get_ip  = "ifconfig eth0 | grep 'inet addr' | cut -d: -f2 | awk '{print $1}'"
            #                         tn_info     = {"tn_ip":pi_ip, "tn_port":get_port, "tn_id":pi_console_id, "tn_pwd":pi_console_pwd}
            #                         ret, sut_ip = tn.telnet_get(tn_info, cmd_get_ip)

            #                         if (0 == ret):
            #                             print ("get sut ip ret=[%s], msg=[%s]" % (ret, sut_ip))
            #                             ret_msg = sut_ip

            # print ("get ip = %s" % ret_msg)
                ########### Do NOT remove, can be used while connnect to console log ###########

            # print ("get ip = %s" % ret_msg)
            if (0 >= len(ret_msg)):
                ret_flag = 149
                ret_msg = "cannot find sut ip / mac"

        return ret_flag, ret_msg

    def search_sut (self, jenkin_info, json_key):

        ret_searched        = ""
        ret_flag            = 0
        local_conf          = self.get_local_conf()
        run_type            = self.get_type(jenkin_info, stage_type)
        run_key             = self.get_cicd_execute_key(run_type, stage_type)

        if (0 < len(run_type)):
            project_name, proj_module, project_info_path = self.get_project_info(jenkin_info, local_conf, run_type)
        else:
            print ("error get_type() return empty")

        test_info       = dict(self.search_json.get_struct_by_key(project_info_path, json_key))
        tag_sut_name    = test_info["sut_name"]

        #################################################
        # download json from nextcloud
        str_tag         = "Download_SUT_info.log"
        list_sut_name   = list()
        wait_seconds    = 10 # wait X seconds per search
        b_find          = False
        i_retry         = 1
        i_retry_total   = 3 # retry count
        str_find_SUT    = "" # if find free SUT  save here and print, back to jenkins

        # get nextcloud info
        srv_info            = self.search_json.get_struct_by_key(local_conf, self.str_nextcloud)
        nc_ip               = srv_info["ip"]
        nc_port             = srv_info["port"]
        nc_user             = srv_info["user"]
        nc_pwd              = srv_info["pwd"]
        nc_sut_info_path    = srv_info["autotest_sut_info_path"]
        nc_sut_info_file    = srv_info["autotest_sut_info_file"]
        http_user_pwd       = "%s:%s" % (nc_user, nc_pwd)
        http_url_port       = "%s:%s" % (nc_ip, nc_port)

        exec_cmd    = "curl --create-dirs -u %s  -X GET  %s/remote.php/dav/files/%s/%s/%s --output %s" % (http_user_pwd, http_url_port, nc_user, nc_sut_info_path, nc_sut_info_file, nc_sut_info_file)
        log_folder = jenkin_info["cmd_log_folder"]
        ret_tmp     = execute_cmd().exec_shell_cmd(log_folder, str_tag, exec_cmd)

        if (0 != ret_tmp):
           ret_flag = 136

        job_project = test_info["proj_sut"]
        sut_info                = self.search_json.get_struct_by_key(nc_sut_info_file, job_project)

        # print("check SUT for project[%s]" % job_project)


        for str_key in sut_info:
            if "SUT_CNT" != str_key:
                list_sut_name.append(str_key)

        # print ("list_sut_name = %s" % list_sut_name)

        while i_retry_total >= i_retry and False == b_find:
            for str_sut in list_sut_name:

                search_name         = "%s=" % str_sut
                ret_find, job_ret   = file_mng()._search_in_file(self.m_file_sut_info, search_name)

                if "N" == job_ret and False == b_find:

                    b_find = True
                    # print ("find sut to use, sut_name = %s" % str_sut)

                    update_key = "%s=" % str_sut
                    update_value = "Y"
                    ret_searched = str_sut
                    write_ret = self.save_data_to_file (self.m_file_sut_info, update_key, update_value)

                    str_find_SUT = str_sut

            # print("search cnt[%s], result = [%s]" % (i_retry, b_find))
            if False == b_find:

                i_retry = i_retry + 1
                if i_retry_total >= i_retry:
                    time.sleep(wait_seconds)

        if True == b_find:
            print ("sut = %s" % str_find_SUT)
            write_ret = self.save_data_to_file (jenkin_info["jenkin_filepath"], tag_sut_name, str_find_SUT)
            ret_flag = 0
        else:
            print ("no free SUT found.")
            ret_flag = 136
        return ret_flag, ret_searched


    def __get_test_list (self, jenkin_info, json_key, stage_type, str_list_name):

        ret_flag            = 0
        log_name            = "generate_script_list"
        local_conf          = self.get_local_conf()
        run_type            = self.get_type(jenkin_info, stage_type)
        run_key             = self.get_cicd_download_key(run_type, stage_type)

        if (0 < len(run_type)):
            project_name, proj_module, project_info_path = self.get_project_info(jenkin_info, local_conf, run_type)
        else:
            print ("error get_type() return empty")

        # get nextcloud info
        srv_info            = self.search_json.get_struct_by_key(local_conf, self.str_nextcloud)

        nc_user             = srv_info["user"]
        nc_auto_file_path   = srv_info["autotest_file_path"]
        nc_auto_file_name   = srv_info["autotest_file_name"]
        nc_auto_info_path   = srv_info["autotest_info_path"]

        http_user_pwd       = "%s:%s" % (srv_info["user"], srv_info["pwd"])
        http_url_port       = "%s:%s" % (srv_info["ip"], srv_info["port"])

        log_folder          = jenkin_info["cmd_log_folder"] # gen list log folder

        print ("project = [%s],module = [%s], type = [%s]" % (project_name, proj_module, run_type))

        # download ProjectName.json from nextcloud
        str_dn_filename = "%s.json" % (project_name)

        exec_cmd        = "curl --create-dirs -u %s  -X GET  %s/remote.php/dav/files/%s/%s/%s --output %s" % (http_user_pwd, http_url_port, nc_user, nc_auto_info_path, str_dn_filename, str_dn_filename)
        ret_tmp         = execute_cmd().exec_shell_cmd(log_folder, log_name, exec_cmd)
        print ("download test item key.json from NC file : [%s], ret : [%s]" % (str_dn_filename, ret_tmp))
        if (0 != ret_tmp):
            ret_flag = 135

        # parse, get various autotest_cases ( used for generate script_list)
        autotest_info   = self.search_json.get_struct_by_key(str_dn_filename, json_key)
        print ("selected [json][module] = [%s][%s]" % (str_dn_filename, json_key))
        autotest_flag   = autotest_info[run_type]
        

        # - download  () autotest_cases.xlsx on nextcloud
        exec_cmd        = "curl --create-dirs -u %s  -X GET  %s/remote.php/dav/files/%s/%s/%s --output %s" % (http_user_pwd, http_url_port, nc_user, nc_auto_file_path, nc_auto_file_name, nc_auto_file_name)
        ret_tmp         = execute_cmd().exec_shell_cmd(log_folder, log_name, exec_cmd)
        # print ("dn excel file ret[%s]:[%s]" % (ret_tmp,exec_cmd))
        if (0 != ret_tmp):
            ret_flag = 135

        # check manual build tag here, modify [[ autotest_flag ]]
        if ("manual" == run_type):
            str_json_info   = self.search_json.get_struct_by_key(project_info_path, json_key)
            is_test_set     = self.get_manual_info (local_conf, self.str_nextcloud, "script_test_set")

            if ("Official" == is_test_set): # load default [autotest_info/PROJECT.json key = (script_key)(manual)]
                autotest_flag = autotest_flag
            else:
                autotest_flag = is_test_set

        # - parse autotest_cases.xlsx by autotest_flag and create lists_tag_is_[autotest_flag]
        exec_cmd        = "robot --variable test_list_name:%s --variable test_case_type:%s generate_test_list.robot" % (str_list_name, autotest_flag )
        ret_tmp         = execute_cmd().exec_shell_cmd(log_folder, log_name, exec_cmd)
        print ("create test list ret[%s]:[%s]" % (ret_tmp,exec_cmd))
        if (0 != ret_tmp):
            ret_flag = 135

        return ret_flag


    def _func_update_robot_resource (self, jenkin_info, stage_type):

        print ("update robot conf func() --->")

        jenkins_file        = "jenkins_env.log"
        script_folder       = "temp_pkg"
        config_folder       = "script_conf"

        key_cicd_project    = "cicd_script_project="
        key_cicd_target     = "cicd_script_module="
        print ("Load project / target by jenkins env")
        save_file = "%s/%s" % ("temp_pkg", "lib/resource.robot")
        print ("modify file = [%s]" % (save_file))

        ret, my_project = file_mng()._search_in_file(jenkins_file, key_cicd_project)
        ret, my_target =  file_mng()._search_in_file(jenkins_file, key_cicd_target)
        data_src = "%s/%s/%s_%s/robot_conf/script_resource.robot" % (script_folder, config_folder, my_project, my_target)
        print ("data src = [%s]" % (data_src))
        ret, OPENBMC_USERNAME = file_mng()._search_in_file(data_src, '${local_OPENBMC_USERNAME}  ')
        print ("local OPENBMC_USERNAME = [%s]" % (OPENBMC_USERNAME))
        ret, OPENBMC_PASSWORD = file_mng()._search_in_file(data_src, '${local_OPENBMC_PASSWORD}  ')
        print ("local OPENBMC_PASSWORD = [%s]" % (OPENBMC_PASSWORD))

        ret, REST_USERNAME = file_mng()._search_in_file(data_src, '${local_REST_USERNAME}  ')
        print ("local REST_USERNAME = [%s]" % (REST_USERNAME))
        ret, REST_PASSWORD = file_mng()._search_in_file(data_src, '${local_REST_PASSWORD}  ')
        print ("local REST_PASSWORD = [%s]" % (REST_PASSWORD))

        ret, IPMI_USERNAME = file_mng()._search_in_file(data_src, '${local_IPMI_USERNAME}  ')
        print ("local IPMI_USERNAME = [%s]" % (IPMI_USERNAME))
        ret, IPMI_PASSWORD = file_mng()._search_in_file(data_src, '${local_IPMI_PASSWORD}  ')
        print ("local IPMI_PASSWORD = [%s]" % (IPMI_PASSWORD))

        ret, console_host = file_mng()._search_in_file(data_src, '${console_host_via_pi}  ')
        print ("local console_host = [%s]" % (console_host))
        ret, console_port = file_mng()._search_in_file(data_src, '${console_port_via_pi}  ')
        print ("local console_port = [%s]" % (console_port))

        write_ret     = self.save_data_to_file (save_file, "${OPENBMC_USERNAME}  ", OPENBMC_USERNAME)
        write_ret     = self.save_data_to_file (save_file, "${OPENBMC_PASSWORD}  ", OPENBMC_PASSWORD)

        write_ret     = self.save_data_to_file (save_file, "${REST_USERNAME}  ", REST_USERNAME)
        write_ret     = self.save_data_to_file (save_file, "${REST_PASSWORD}  ", REST_PASSWORD)

        write_ret     = self.save_data_to_file (save_file, "${IPMI_USERNAME}  ", IPMI_USERNAME)
        write_ret     = self.save_data_to_file (save_file, "${IPMI_PASSWORD}  ", IPMI_PASSWORD)

        write_ret     = self.save_data_to_file (save_file, "${OPENBMC_SERIAL_HOST}  ", console_host)
        write_ret     = self.save_data_to_file (save_file, "${OPENBMC_SERIAL_PORT}  ", console_port)

        print ("update robot conf func() <---")


    def _git_download (self, jenkin_info, json_key, stage_type):

        ret = 0
        str_default_dir     = pathlib.Path().resolve()

        local_conf          = self.get_local_conf()
        run_type            = self.get_type(jenkin_info, stage_type)
        run_key             = self.get_cicd_download_key(run_type, stage_type)

        if (0 < len(run_type)):
            project_name, proj_module, project_info_path = self.get_project_info(jenkin_info, local_conf, run_type)
        else:
            print ("error get_type() return empty")

        # get git server info
        git_srv             = self.search_json.get_struct_by_key(local_conf, "git_server_info")
        jenkins_file        = "jenkins_env.log"
        str_json_info       = self.search_json.get_struct_by_key(project_info_path, json_key)
        dn_count            = int(str_json_info["count"])
        cmd_work_dir        = str_json_info["work_dir"]
        log_folder          = str_json_info["log_folder"]

        # keyword from file ( type review, replace string )
        # update {key, value}
        str_gerrit_url      = "GERRIT_CHANGE_URL="
        str_gerrit_refspec  = "GERRIT_REFSPEC="
        str_gerrit_patchset = "GERRIT_PATCHSET_REVISION="

        dict_replace_keyword= {str_gerrit_url:"", str_gerrit_refspec:"", str_gerrit_patchset:""}

        # clone http://my_dn_id:my_dn_pwd@my_dn_ip:my_dn_port/ -b develop-ami-rr13.3 dev/bmc/common/asus_rr13_common.git
        str_id              = "my_dn_id"
        str_pwd             = "my_dn_pwd"
        str_ip              = "my_dn_ip"
        str_port            = "my_dn_port"
        str_branch          = "my_branch"

        str_dn_id           = git_srv["user"]
        str_dn_pwd          = git_srv["pwd"]
        str_dn_ip           = git_srv["ip"]
        str_dn_port         = git_srv["port"]

        dict_key_dn         = {str_id:str_dn_id, str_pwd:str_dn_pwd, str_ip:str_dn_ip, str_port:str_dn_port}
        manual_tag         = ""

        if ("review" == run_type):
            for str_key in dict_replace_keyword:

                ret_find, ret_data = file_mng()._search_in_file(jenkins_file, str_key)
                if (True == ret_find):
                    tmp_data = ret_data.rstrip("\n")

                    # special case : gerrit path  /a/ /c/
                    if (str_gerrit_url == str_key):
                        tmp_data_01 = tmp_data.split("/+/")[0]
                        tmp_data_02 = tmp_data_01.replace("/c/", "/a/")
                        tmp_data    = tmp_data_02

                    # in review  http://10.10.55.55 -> http://key_x:key_y@10.10.55.55
                    str_old    = "://"
                    str_new    = "://" + str_id + ":" + str_pwd + "@"

                    value_modified     = "%s" % tmp_data.replace(str_old, str_new)
                    dict_replace_keyword.update({str_key:value_modified})

        if ("manual" == run_type):
            manual_tag           = self.get_manual_info (local_conf, self.str_nextcloud, "build_tag")

        # check working folder is exist, if no, then create it
        if (False == file_mng().check_folder_exist(cmd_work_dir)  and  0 < len(cmd_work_dir)):
            file_mng().create_folder(cmd_work_dir)

        # change working dir
        if (0 < len(cmd_work_dir)):
            os.chdir(cmd_work_dir)

        dn_p_cmd = dict()
        for i_idx in range(1, dn_count + 1) : # 01 02 03   range (1,4)

            query_key           = str(i_idx).zfill(2)
            str_tmp             = str_json_info[query_key]

            # for replace fw tag from build_info.json
            str_tmp  = str_tmp.replace("my_manual_build_info", manual_tag)

            for str_key in dict_replace_keyword:
                replace_key     = "my_%s" % str_key[ :-1]
                str_tmp         = str_tmp.replace(replace_key, dict_replace_keyword[str_key])
            for str_key in dict_key_dn:
                str_tmp         = str_tmp.replace(str_key, dict_key_dn[str_key])

            dn_cmd      = str_json_info["cmd"]
            git_dn      = "%s %s" % (dn_cmd, str_tmp)
            cmd_key     = "cmd_" + str(i_idx).zfill(2)
            dn_p_cmd.update({cmd_key : git_dn})



        for str_key in dn_p_cmd:
            print ("execute cmd = [%s]" % dn_p_cmd[str_key])
            ret_tmp = execute_cmd().exec_shell_cmd(log_folder, run_key, dn_p_cmd[str_key])
            print ("result = [%s]" % ret_tmp)
            ret |= ret_tmp

        # change working dir to default
        if (True == file_mng().check_folder_exist(str_default_dir)):
            os.chdir(str_default_dir)

        if (0 == ret):
            return 0
        else:
            return 130


    def _run_build (self, jenkin_info, json_key):

        str_cov_test        = "test"
        str_cov_official    = "official"

        str_cov_database    = "my_cov_type"
        str_build_type      = "my_security_build_type"
        str_build_key_path  = "my_key_fullpath"
        str_build_prj_file  = "my_project_file"

        is_cov              = "N" # default no coverity
        cov_type            = ""
        cov_steam_name      = ""

        # string (upletter :  DEVELOP : OFFICIAL)
        key_type            = ""
        download_key_path   = ""

        ret_final           = 0
        ret_tmp             = 0

        str_default_dir = pathlib.Path().resolve()

        local_conf          = self.get_local_conf()
        run_type            = self.get_type(jenkin_info, stage_type)
        run_key             = self.get_cicd_execute_key(run_type, stage_type)

        if (0 < len(run_type)):
            project_name, proj_module, project_info_path = self.get_project_info(jenkin_info, local_conf, run_type)
        else:
            print ("error get_type() return empty")
            ret_tmp = 150

        print ("CICD type = [%s]" % (run_type))
        if (("manual" == run_type) and (0 ==ret_tmp)):
            is_cov          = self.get_manual_info (local_conf, self.str_nextcloud, "build_cov")
            cov_type        = self.get_manual_info (local_conf, self.str_nextcloud, "build_cov_type")

            json_script     = "%s/%s" % (pathlib.Path().resolve(), project_info_path)
            cov_info        = dict(self.search_json.get_struct_by_key(json_script, json_key))

            cov_test        = cov_info["cov_stream_test"]
            cov_official    = cov_info["cov_stream_official"]

            # check coverity scan
            if (str_cov_test == cov_type.lower()):
                cov_steam_name = cov_test
            elif (str_cov_official == cov_type.lower()):
                cov_steam_name = cov_official
            else:
                cov_steam_name = cov_test

            print ("stream name report added [%s]" % cov_steam_name)

        str_json_info   = dict(self.search_json.get_struct_by_key(project_info_path, json_key))

        str_root        = os.path.abspath(os.getcwd())
        cmd_work_dir    = str_json_info["work_dir"]
        log_folder      = str_json_info["log_folder"]
        build_prj       = str_json_info["project_prj_file"]

        # change working dir
        if (0 < len(cmd_work_dir)):
            if (False == file_mng().check_folder_exist(cmd_work_dir)):
                file_mng().create_folder(cmd_work_dir)
            os.chdir(cmd_work_dir)

        # load script command from project_info/target/project_target.json
        cmd_cnt = 0
        if ("Y" == is_cov):
            cmd_cnt = int(str_json_info["count_cov"])
        else:
            cmd_cnt = int(str_json_info["count"])

        if (0 < cmd_cnt): # type = file, loop json
            for idx in range (1, cmd_cnt + 1):

                cmd_idx = ""
                if ("Y" == is_cov):
                    cmd_idx = "%s_cov" % (str(idx).zfill(2))
                else:
                    cmd_idx = "%s" % (str(idx).zfill(2))

                my_cmd  = str_json_info[cmd_idx] 

                # if manual , replace coverity_database_name into cov_type
                if (("manual" == run_type) and (0 == ret_tmp)):

                    # use manual or  various cov_xxx ????
                    if (0 <= my_cmd.find(str_cov_database)):
                        my_cmd  = my_cmd.replace(str_cov_database, cov_steam_name)

                    # find [my_security_build_type][my_key_fullpath] in command
                    if ((0 <= my_cmd.find(str_build_type)) or (0 <= my_cmd.find(str_build_key_path))):

                        jenkins_file = "%s/%s" % (str_default_dir, jenkin_info["jenkin_filepath"])
                        ret, key_type = file_mng()._search_in_file(jenkins_file, "cicd_build_type=")
                        key_type = key_type.upper()

                        if (False == ret):
                            key_type = "DEVELOP"

                        if (("DEVELOP" != key_type.upper()) and ("OFFICIAL" != key_type.upper())):
                            key_type = "DEVELOP"

                        print ("key type = [%s]" % (key_type))

                        # type = OFFICIAL , download key, download_key_path=[folder fullpath]
                        if ("OFFICIAL" == key_type): 
                            # download ssh key from gitlab : http://10.10.65.57:8880/dev/sw_security_key/key_PROJECT
                            ret, download_key_path = self.download_build_key(str_default_dir, project_name)
                            if (True == ret):
                                print ("key download to [%s]" % (download_key_path))
                            else:
                                print ("[%s][%s]" % (ret, download_key_path))
                                ret_tmp = 150
                        else: # type = DEVELOP , download_key_path=[no used]
                            download_key_path   = "no_used_when_develop"

                else:
                    key_type            = "DEVELOP"
                    download_key_path   = "no_used_when_develop"

                # replace command by keyword my_xxx
                my_cmd     = "%s" % my_cmd.replace(str_build_type, key_type)
                my_cmd     = "%s" % my_cmd.replace(str_build_key_path, download_key_path)
                my_cmd     = "%s" % my_cmd.replace(str_build_prj_file, build_prj)

                print ("execute cmd = [%s]" % my_cmd)
                ret_tmp = execute_cmd().exec_shell_cmd(log_folder, "Execute_Build_list", my_cmd)

                ret_final |= ret_tmp
        else:
            ret_final = 134

        # change working dir to default
        if (True == file_mng().check_folder_exist(str_default_dir)):
            os.chdir(str_default_dir)

        print ("result = [%s]" % ret_final)
        return ret_final

    def download_build_key (self,str_default_dir, project_name):
        my_ret          = False
        ret_msg         = ""

        conf_file       = "%s/%s" % (str_default_dir, self.get_local_conf())

        git_srv     = self.search_json.get_struct_by_key(conf_file, "git_server_info")
        key_info    = self.search_json.get_struct_by_key(conf_file, "build_security_key")

        download_path       = key_info["download_local_path"]
        key_download_method = key_info["current_key_type"]

        if ("src_gitlab" == key_download_method):
            download_fullpath = "%s/key_%s" % (download_path, project_name)
            #  git clone -u ben:ben1234 http://10.10.65.57:8880/dev/sw_security_key/key_x4tf /tmp/key_x4tf 
            # cmd_download_key = "git clone -u %s:%s http://%s:%s/%s/key_%s %s" % (git_srv["user"], git_srv["pwd"], git_srv["ip"], git_srv["port"], key_info[key_download_method]["key_uri"], project_name, download_fullpath)
            # git clone single branch [OFFICIAL]
            # git clone -b develop --single-branch 
            official_key_branch = "OFFICIAL"
            cmd_download_key = "git clone -u %s:%s -b %s --single-branch http://%s:%s/%s/key_%s %s" % (git_srv["user"], git_srv["pwd"], official_key_branch, git_srv["ip"], git_srv["port"], key_info[key_download_method]["key_uri"], project_name, download_fullpath)

            ret_tmp, my_out, my_err  = execute_cmd().exec_shell_cmd_and_get("/tmp", "download_key.txt", cmd_download_key)
            if (0 == ret_tmp):
                ret_msg = download_fullpath
                my_ret  = True
            else:
                ret_msg = "download key fail, msg=[%s][%s]" % (my_out, my_err)
                my_ret  = False
        elif ("src_nextcloud" == key_download_method):
            ret_msg = "unsupport download type [%s]" % key_download_method
            my_ret  = False
        elif ("src_nextcloud" == key_download_method):
            ret_msg = "unsupport download type [%s]" % key_download_method
            my_ret  = False
        else :
            ret_msg = "get download type from [%s] fail" % (conf_file)
            my_ret  = False

        return my_ret, ret_msg

    # python3  cicd_func.py  jenkins_env.log  get_from_file  stage_build
    def get_from_file (self, jenkin_info, stage_type):

        search_file = stage_type.split("__")[0]
        search_key = stage_type.split("__")[1]
        str_value = self.load_data_from_file (search_file, search_key)

        print ("%s" % str_value)

        return 0

    # python3  cicd_func.py  jenkins_env.log  get_from_json  stage_build
    def get_from_json (self, jenkin_info, stage_type):

        recv_para = stage_type.split("__")

        if (3 != len(recv_para)):
            return ""

        search_json     = recv_para[0]
        search_key_1    = recv_para[1]
        search_key_2    = recv_para[2]

        ret             = 0
        local_conf      = self.get_local_conf()
        tmp_array       = dict(self.search_json.get_struct_by_key(local_conf, search_key_1))

        nc_url          = tmp_array[search_key_2]
        print ("%s" % nc_url)


        return ret

    # python3  cicd_func.py  jenkins_env.log  get_project_json  stage_build
    def get_project_json (self, jenkin_info, stage_type):

        ret                 = 0
        local_conf          = self.get_local_conf()
        run_type            = self.get_type(jenkin_info, stage_type)
        run_key             = self.get_cicd_execute_key(run_type, stage_type)

        if (0 < len(run_type)):
            project_name, proj_module, project_info_path = self.get_project_info(jenkin_info, local_conf, run_type)
        else:
            print ("error get_type() return empty")
    
        print ("%s" % project_info_path)

    def get_is_test (self, jenkin_info, stage_type):

        is_test = "Y"
        local_conf          = self.get_local_conf()
        run_type            = self.get_type(jenkin_info, stage_type)
        run_key             = self.get_cicd_execute_key(run_type, stage_type)

        if ("manual" == run_type):
            is_test = self.get_manual_info (local_conf, self.str_nextcloud, "script_test")

        return is_test

    def run_script (self, jenkin_info, json_key, stage_type, root_path):

        ret                 = 0
        local_conf          = self.get_local_conf()
        run_type            = self.get_type(jenkin_info, stage_type)

        search_ret = 0

        if (0 < len(run_type)):
            project_name, proj_module, project_info_path = self.get_project_info(jenkin_info, local_conf, run_type)
        else:
            print ("error get_type() return empty")
            ret = -1

        # check type = manual and execute testing or not
        if ("manual" == run_type):
            is_test             = self.get_manual_info (local_conf, self.str_nextcloud, "script_test")
            
        else:
            str_project_info    = "project_jenkins/%s_%s_%s_para.json" % (project_name, proj_module, run_type)
            curr_proj_info      = self.search_json.get_struct_by_key(str_project_info, "build_parameter")
            is_test             = curr_proj_info["script_test"]

        print ("Check execute testing or not, is_test = [%s]" % (is_test))
        if ("N" == is_test):
            ret = 0
            return ret

        # search have idle SUT to use
        if (0 == ret):
            print ("search have idle SUT to use")

            test_info       = dict(self.search_json.get_struct_by_key(project_info_path, json_key))
            search_ret, sut_name         = self.search_sut (jenkin_info, json_key)
            if (0 != search_ret):
                ret = search_ret
            print ("search idle SUT : ret = [%s], name=[%s]" % (search_ret, sut_name))

        # get SUT IP for update file /lib/resource.robot
        if (0 == ret):
            print ("get SUT IP by MAC")

            # mac in ESR.json
            ret_search_sut, sut_ip = self._get_sut_ip_by_mac (jenkin_info, stage_type, sut_name)
            if (0 != ret_search_sut):
                ret = ret_search_sut
            print ("get SUT IP ret=[%s], info=[%s]" % (ret, sut_ip))

        if (0 == ret):
            print ("update ip to robot script config")
            # modify sut ip to robot script lib/resource.robot  
            # ${OPENBMC_HOST}   10.10.65.49
            str_script_resource_folder = "temp_pkg"
            str_script_resource_file = "lib/resource.robot"
            save_file = "%s/%s" % (str_script_resource_folder, str_script_resource_file)

            old_string      ="${OPENBMC_HOST}   "
            new_string      ="%s" % (sut_ip)
            print ("%s : save_data_to_file() [%s][%s][%s]" % (str_script_resource_file, save_file, old_string, new_string))
            write_ret     = self.save_data_to_file (save_file, old_string, new_string)
            if (0 != write_ret):
                ret = write_ret

        if (0 == ret):
            # target_img      = test_info["target_img"]
            # print ("testing for build : [%s]" % target_img)

            # gen file
            print ("\ngenerate test list")
            act_gen_name    = test_info["act_gen_list_name"] # generate test list [filename]
            ret_gen         = self.__get_test_list (jenkin_info, json_key, stage_type, act_gen_name)
            if (0 != ret_gen):
                ret = ret_gen

            print ("gen robot list : ret = %s" % ret_gen)

        # 02 run robot script
        if (0 == ret):
            print ("run robot script")
            ret_run         = self.__run_script (jenkin_info, json_key, root_path)
            if (0 != ret_run): # value from exec_shell_cmd()
                ret = ret_run
            print ("run robot test : ret = %s" % ret_run)

        # 03 free sut, NOT see ret,  change to search_ret
        if (0 == search_ret):
            print ("free sut flag")
            ret_free        = self.free_sut(jenkin_info, json_key)
            if (0 != ret_free): # 199
                ret = ret_free
            print ("free sut : ret = %s" % ret_free)

        return ret

    def __run_script (self, jenkin_info, json_key, root_path):

        local_conf          = self.get_local_conf()
        run_type            = self.get_type(jenkin_info, stage_type)
        run_key             = self.get_cicd_execute_key(run_type, stage_type)

        if (0 < len(run_type)):
            project_name, proj_module, project_info_path = self.get_project_info(jenkin_info, local_conf, run_type)
        else:
            print ("error get_type() return empty")

        str_curr_dir = pathlib.Path().resolve()
        # print ("str_curr_dir = %s" % str_curr_dir)

        json_script         = "%s/%s" % (root_path, project_info_path)
        cmd_log_folder      = jenkin_info["cmd_log_folder"]

        str_json_info       = dict(self.search_json.get_struct_by_key(json_script, json_key))

        re_folder           = str_json_info["log_folder"]
        act_cmd             = str_json_info["act_cmd"]
        act_folder          = str_json_info["act_folder"]


        str_root = os.path.abspath(os.getcwd())

        cmd_work_dir = "%s/%s" % (root_path, str_json_info["work_dir"])
        # change working dir
        if (0 < len(cmd_work_dir)):
            print ("chdir to %s" % cmd_work_dir)
            os.chdir(cmd_work_dir)

        log_dir = "%s/%s" % (cmd_work_dir, re_folder)

        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # report_tag  = "fw_%s_%s" % ((datetime.datetime.now()).strftime("%Y%m%d"), json_key)
        report_tag  = "fw_%s_%s" % ((datetime.datetime.now()).strftime("%m%d"), json_key)

        name_output = " -o " + report_tag + "_output.xml "
        name_log    = " -l " + report_tag + "_log.html "
        name_report = " -r " + report_tag + "_report.html "
        name_log_dir= " -d " + log_dir
        run_lists   = " -A " +  act_cmd
        run_folder  = " " + act_folder

        run_cmd     = "robot " + name_log_dir + name_output + name_log + name_report + run_lists + run_folder
        print ("run script command [%s]" % run_cmd)
        ret_tmp     = execute_cmd().exec_shell_cmd(cmd_log_folder, json_key, run_cmd)
        print ("result [%s]" % ret_tmp)

        os.chdir(str_curr_dir)

        return ret_tmp


    def ___gen_folder_by_test_type (self, jenkins_file, str_type, jenkin_info):

        # daily   : daily_2022_03_11
        # hotfix  : hotfix_2022_03_11
        # review  : review_2022_03_11_GerritID_GerritPatchNum_GeerritOwner ( GERRIT_PATCHSET_NUMBER)
        # manual : manual_json_filename_on_nc_manual_build
        # type   : "daily / review / manual / hotfix"

        str_name = ""
        if   ("daily" == str_type):
            str_name = "daily_" + (datetime.datetime.now()).strftime("%Y_%m_%d")
        elif ("review" == str_type):

            str_key = "%s%s" % ("GERRIT_PATCHSET_NUMBER", "=")
            ret_find, ret_data = file_mng()._search_in_file(jenkins_file, str_key)

            if (True == ret_find):
                str_gerrit_patchset_num = ret_data
            else:
                str_gerrit_patchset_num = "unknown"


            str_key = "%s%s" % ("GERRIT_CHANGE_OWNER_EMAIL", "=")
            ret_find, ret_data = file_mng()._search_in_file(jenkins_file, str_key)
            if (True == ret_find):
                str_tmp = ret_data.split("@")[0]
                str_change_owner = str_tmp
            else:
                str_change_owner = "unknown"

            str_key = "%s%s" % ("GERRIT_CHANGE_NUMBER", "=")
            ret_find, ret_data = file_mng()._search_in_file(jenkins_file, str_key)
            if (True == ret_find):
                str_gerrit_uid = ret_data
            else:
                str_gerrit_uid = "unknown"

            str_name     = "review_%s__%s__%s__%s" % ((datetime.datetime.now()).strftime("%Y_%m_%d"), str_gerrit_uid, str_gerrit_patchset_num, str_change_owner)


        elif ("manual" == str_type):
            ret_find, ret_data = file_mng()._search_in_file(jenkins_file, "my_conf_file=")
            if (True == ret_find):
                str_manual_conf_name = ret_data
            else:
                str_manual_conf_name = "unknown"

            ret_find, check_type = file_mng()._search_in_file(jenkins_file, "cicd_existed_image_name=")
            if (True == ret_find):
                str_manual_type = "DevTest"
            else:
                str_manual_type = "manual"

            str_name = "%s_%s" % (str_manual_type, str_manual_conf_name.split(".json")[0])
        elif ("hotfix" == str_type):
            str_name = "hotfix_" + (datetime.datetime.now()).strftime("%Y_%m_%d")
        else:
            str_name = "unknown"

        print ("folder name on server [%s]" % str_name)

        return str_name


    def _upload_report (self, jenkin_info, json_server, json_key):

        task_ret            = False
        local_conf          = self.get_local_conf()
        run_type            = self.get_type(jenkin_info, stage_type)
        run_key             = self.get_cicd_download_key(run_type, stage_type)

        if (0 < len(run_type)):
            project_name, proj_module, project_info_path = self.get_project_info(jenkin_info, local_conf, run_type)
        else:
            print ("error get_type() return empty")


        # check type = manual and execute testing or not
        if ("manual" == run_type):
            is_test             = self.get_manual_info (local_conf, self.str_nextcloud, "script_test")
            
        else:
            str_project_info    = "project_jenkins/%s_%s_%s_para.json" % (project_name, proj_module, run_type)
            curr_proj_info      = self.search_json.get_struct_by_key(str_project_info, "build_parameter")
            is_test             = curr_proj_info["script_test"]

        print ("Check execute testing or not, is_test = [%s], run type = [%s]" % (is_test, stage_type))
        if (("N" == is_test) and ("stage_script" == stage_type)):
            ret = 0
            return ret


        jenkins_file        = jenkin_info["jenkin_filepath"]

        # get upload task info
        task_info           = self.search_json.get_struct_by_key(project_info_path, json_key)
        up_file_info        = task_info["file"]
        up_folder_info      = task_info["folder"]
        local_work_dir      = task_info["work_dir"]

        # get nextcloud server info
        nc_srv_info         = self.search_json.get_struct_by_key(json_server, self.str_nextcloud)
        nc_user             = "%s:%s" % (nc_srv_info["user"], nc_srv_info["pwd"]) # id:password
        nc_url              = "%s:%s" % (nc_srv_info["ip"], nc_srv_info["port"]) # http://ip:port
        nc_root             = nc_srv_info["user"]   # admin
        nc_start_path       = "%s/%s/%s" % (project_name, proj_module, run_type)

        if ("manual" == run_type):
            print ("type = [%s], check key[%s] in [%s] for build image type " % (run_type, "cicd_existed_image_name=", jenkin_info["jenkin_filepath"]))

            str_start_folder = ""
            ret_find, is_existed_image = file_mng()._search_in_file(jenkin_info["jenkin_filepath"], "cicd_existed_image_name=")
            if (True == ret_find):
                str_start_folder = "%s/%s/DevTest" % (project_name, proj_module)
            else:
                str_start_folder = "%s/%s/manual" % (project_name, proj_module)

            nc_start_path       = "%s/" % (str_start_folder)

        stu_nc_info = dict()
        stu_nc_info.update({"nc_user" : nc_user})
        stu_nc_info.update({"nc_url" : nc_url})
        stu_nc_info.update({"nc_root" : nc_root})
        stu_nc_info.update({"nc_start_path" : nc_start_path})

        stu_log_info = dict()
        stu_log_info.update({"log_folder" : jenkin_info["cmd_log_folder"]})
        stu_log_info.update({"log_filename" : json_key})

        nc_log_folder = ""
        if ( (0 < int(up_file_info["count"]))  or  (0 < int(up_folder_info["count"])) ):

            # create folder on nc, change nc_start_path to nc_start_path / nc_log_folder
            nc_log_folder   = self.___gen_folder_by_test_type(jenkins_file, run_type, "jenkin_info")
            stu_nc_info.update({"nc_log_folder" : nc_log_folder})
            ret             = nc_mng()._create_folder_on_nc (stu_nc_info, stu_log_info)

            stu_nc_info["nc_start_path"] = "%s/%s" % (stu_nc_info["nc_start_path"], stu_nc_info["nc_log_folder"])
            stu_nc_info["nc_log_folder"] = "" 

        # upload file
        if (0 < int(up_file_info["count"])): # type = file, loop json
            for idx in range (1, int(up_file_info["count"]) + 1):

                local_filepath  = up_file_info[str(idx).zfill(2)] 
                split_file      = local_filepath.split("/", -1)
                str_file_name   = split_file[len(split_file) - 1]

                str_src  = "%s/%s" % (local_work_dir, local_filepath)
                str_dest = "%s/%s/%s/%s" % (nc_root, nc_start_path, nc_log_folder, str_file_name)

                ret = nc_mng()._upload_file(stu_nc_info, stu_log_info, str_src, str_dest)
        else:
            print ("file cnt = [%d]" % int(up_file_info["count"]))

        # upload folder
        if (0 < int(up_folder_info["count"])): # type = folder, loop folder

            for idx in range (1, int(up_folder_info["count"]) + 1):

                tmp_up_folder       = up_folder_info[str(idx).zfill(2)]
                split_folder        = tmp_up_folder.split("/", -1)
                str_folder_name     = split_folder[len(split_folder) - 1]

                local_folder = "%s/%s/%s" % (os.path.dirname(os.path.realpath(__file__)), local_work_dir, tmp_up_folder)
                do_ret = nc_mng()._upload_folder_on_nc(stu_nc_info, stu_log_info, local_folder, str_folder_name)

        else:
            print ("folder cnt [%d]" % int(up_folder_info["count"]))

        return 0


# print (" [%s]" % sys.argv)
if (4 != len(sys.argv)):
    print ("para len error : python main.py name_conf name_run_func")
    sys.exit( 77 )

jenkins_file    = sys.argv[1] # "jenkins_env.log"
call_func       = sys.argv[2] # func_get_script_source
stage_type      = sys.argv[3] # stage_build / stage_script

my_flow         = execute_flow(jenkins_file, stage_type)
ret             = my_flow.run(call_func, stage_type)

sys.exit (ret)
