jenkins folder path  for xxx.sh

in docker :

/var/jenkins_home/

/var/jenkins_home/xxx.sh

in cicd_server:

/var/fwteam/docker/jenkins/

/var/fwteam/docker/jenkins/xxx.sh

==========================

pipeline {\
    agent any\
\
    stages \
    {\
        stage("set env variable")\
        {\
            steps\
            {\
                script\
                {\
                    env.flag_final_ret = "true"\
\
                    // when create new jobs, modify here \
                    // ============================================================================== //\
                    // module : rmc / bios / bmc / obmc\
                    // type   : daily / review / manual\
\
                    my_title = "x4tf bmc  test start"\
                    func_xxx( bash  xxxx.sh   input 1 2 3 ...)\
\
                    env.cicd_script_type        = "review"\
                    env.cicd_script_project     = "x4tf"\
                    env.cicd_script_module      = "bmc"\
\
                    env.run_filename = "run.json"\
\
                    if ("daily" == cicd_script_type || "review" == cicd_script_type)\
                    {\
                        echo "type = daily or review, copy conf from local"\
\
                        env.cicd_jinkins_parameters_src = "/tmp/robot_framework/fw_cicd_script/project_jenkins"\
                        def copy_file = "${env.cicd_jinkins_parameters_src}/${cicd_script_project}_${cicd_script_module}_${cicd_script_type}_para.json"\
                        echo "${copy_file}"\
\
                        echo " run cmd : cp -r ${copy_file}   ${run_filename} "\
                        sh "cp -r ${copy_file}   ${run_filename}"\
                    }\
                    else if ("manual" == cicd_script_type)\
                    {\
                        echo "type = manual, download conf from Nextcloud"\
\
                        env.download_id = "admin:123qweASD!@#"\
                        env.nc_ip_port = "10.10.95.52:8888"\
                        env.download_folder = "remote.php/dav/files/admin/manual_build"\
\
                        env.download_uri = "http://${nc_ip_port}/${download_folder}/${my_conf_file}"\
                        env.download_cmd = "curl --create-dirs -u ${download_id} -X GET ${download_uri} --output ${run_filename}"\
\
                        echo "download uri : ${download_cmd}"\
                        output = sh(returnStdout: true, script: "${download_cmd}").trim()\
                    }\
\
                    def myFile = readFile "${run_filename}"\
                    def read_line = myFile.readLines()\
\
                    echo "total 13 entry in xxx.json (from nextcloud)"\
                    read_line.each \
                    {\
                        String per_line ->\
                        //println per_line\
                        if (per_line.contains("\\"info_project\\""))\
                        {\
                            def line_token = per_line.tokenize(":");\
                            def get_line = line_token.get(1);\
                            get_line = get_line.replaceAll("\\\\s", "");\
                            env.cicd_script_project     = get_line.substring(1, get_line.length() - 2)\
                        }\
                        else if (per_line.contains("\\"info_target\\""))\
                        {\
                            def line_token = per_line.tokenize(":");\
                            def get_line = line_token.get(1);\
                            get_line = get_line.replaceAll("\\\\s", "");\
                            env.cicd_script_module      = get_line.substring(1, get_line.length() - 2)\
                        }\
                        else if (per_line.contains("\\"build_tag\\""))\
                        {\
                            def line_token = per_line.tokenize(":");\
                            def get_line = line_token.get(1);\
                            get_line = get_line.replaceAll("\\\\s", "");\
                            env.cicd_build_tag      = get_line.substring(1, get_line.length() - 2)\
                        }\
                        else if (per_line.contains("\\"build_type\\""))\
                        {\
                            def line_token = per_line.tokenize(":");\
                            def get_line = line_token.get(1);\
                            get_line = get_line.replaceAll("\\\\s", "");\
                            env.cicd_build_type      = get_line.substring(1, get_line.length() - 2)\
                        }\
                        else if (per_line.contains("\\"build_cov\\""))\
                        {\
                            def line_token = per_line.tokenize(":");\
                            def get_line = line_token.get(1);\
                            get_line = get_line.replaceAll("\\\\s", "");\
                            env.cicd_build_cov      = get_line.substring(1, get_line.length() - 2)\
                        }\
                        else if (per_line.contains("\\"build_cov_type\\""))\
                        {\
                            def line_token = per_line.tokenize(":");\
                            def get_line = line_token.get(1);\
                            get_line = get_line.replaceAll("\\\\s", "");\
                            env.cicd_build_cov_type      = get_line.substring(1, get_line.length() - 2)\
                        }\
                        else if (per_line.contains("\\"scan_cppcheck\\""))\
                        {\
                            def line_token = per_line.tokenize(":");\
                            def get_line = line_token.get(1);\
                            get_line = get_line.replaceAll("\\\\s", "");\
                            env.cicd_scan_cppcheck      = get_line.substring(1, get_line.length() - 2)\
                        }\
                        else if (per_line.contains("\\"scan_whitesource\\""))\
                        {\
                            def line_token = per_line.tokenize(":");\
                            def get_line = line_token.get(1);\
                            get_line = get_line.replaceAll("\\\\s", "");\
                            env.cicd_scan_whitesource      = get_line.substring(1, get_line.length() - 2)\
                        }\
                        else if (per_line.contains("\\"existed_image_name\\""))\
                        {\
                            def line_token = per_line.tokenize(":");\
                            def get_line = line_token.get(1);\
                            get_line = get_line.replaceAll("\\\\s", "");\
                            env.cicd_existed_image_name      = get_line.substring(1, get_line.length() - 2)\
                        }\
                        else if (per_line.contains("\\"script_test\\""))\
                        {\
                            def line_token = per_line.tokenize(":");\
                            def get_line = line_token.get(1);\
                            get_line = get_line.replaceAll("\\\\s", "");\
                            env.cicd_script_test      = get_line.substring(1, get_line.length() - 2)\
                        }\
                        else if (per_line.contains("\\"script_test_set\\""))\
                        {\
                            def line_token = per_line.tokenize(":");\
                            def get_line = line_token.get(1);\
                            get_line = get_line.replaceAll("\\\\s", "");\
                            env.cicd_script_test_set      = get_line.substring(1, get_line.length() - 2)\
                        }\
                        else if (per_line.contains("\\"document_release_note\\""))\
                        {\
                            def line_token = per_line.tokenize(":");\
                            def get_line = line_token.get(1);\
                            get_line = get_line.replaceAll("\\\\s", "");\
                            env.cicd_document_release_note      = get_line.substring(1, get_line.length() - 2)\
                        }\
                        else if (per_line.contains("\\"ducument_previous_tag\\""))\
                        {\
                            def line_token = per_line.tokenize(":");\
                            def get_line = line_token.get(1);\
                            get_line = get_line.replaceAll("\\\\s", "");\
                            env.cicd_ducument_previous_tag      = get_line.substring(1, get_line.length() - 2)\
                        }\
                        \
                    }\
\
                    if (cicd_script_project.contains("x4tf") && cicd_script_module.contains("bmc"))\
                    {\
                        env.cicd_image_name         = "ESR1-511-X4TF_:.ima"\
                    }\
                    else if (cicd_script_project.contains("oe22") && cicd_script_module.contains("obmc"))\
                    {\
                        env.cicd_image_name         = "obmc-phosphor-image-:.static.mtd.tar"\
                    }\
                    else if (cicd_script_project.contains("oe22") && cicd_script_module.contains("bmc"))\
                    {\
                        env.cicd_image_name         = "AE-SERES_BMC_:.ima"\
\
                    }\
                    else\
                    {\
                        env.cicd_image_name         = "ongoing_check_other_project_release_format"\
                    }\
\
                    echo "cicd_script_project = : ${cicd_script_project}"\
                    echo "cicd_script_module = : ${cicd_script_module}"\
                    echo "cicd_build_tag = : ${cicd_build_tag}"\
                    echo "cicd_build_type = : ${cicd_build_type}"\
                    echo "cicd_build_cov = : ${cicd_build_cov}"\
                    echo "cicd_build_cov_type = : ${cicd_build_cov_type}"\
                    echo "cicd_scan_cppcheck = : ${cicd_scan_cppcheck}"\
                    echo "cicd_scan_whitesource = : ${cicd_scan_whitesource}"\
                    echo "cicd_existed_image_name = : ${cicd_existed_image_name}"\
                    echo "cicd_script_test = : ${cicd_script_test}"\
                    echo "cicd_script_test_set = : ${cicd_script_test_set}"\
                    echo "cicd_document_release_note = : ${cicd_document_release_note}"\
                    echo "cicd_ducument_previous_tag = : ${cicd_ducument_previous_tag}"\
\
\
                    //for copy robot script from a to b\
                    env.cicd_robot_source       = "/tmp/robot_framework/fw_cicd_script_ben"\
\
                    env.cicd_cmd_log_folder_script  = "script_log"\
                    env.cicd_cmd_log_folder_build   = "build_log"\
\
                    // ============================================================================== //\
\
                    env.cicd_mounted_volumn     = "/tmp/jenkins"\
                    env.cicd_temp_path          = "${cicd_mounted_volumn}/${JOB_NAME}__${BUILD_NUMBER}"\
                    env.cicd_temp_path_tmp          = "${cicd_mounted_volumn}/${JOB_NAME}__${BUILD_NUMBER}@tmp"\
                    env.cicd_working_path       = env.cicd_temp_path\
                    env.cicd_jenkin_env         = "jenkins_env.log"\
\
                    echo "cicd_working_path = ${cicd_working_path}"\
                    //docker robot image info\
                    // ------------------------------------------------------------------------------ //\
\
                    env.cicd_script_name        = "script_main.sh"\
                    env.cicd_script_docker_name = "script_robot_framework"\
                    env.cicd_script_docker_tag  = ":0.0.20230203"\
                    env.cicd_script_stage_type  = "stage_script"\
\
                    env.cicd_script_start_path  = "-w  ${cicd_working_path}"\
                    env.cicd_script_mount       = "-v  ${cicd_temp_path}:${cicd_working_path}"\
                    env.cicd_script_container   = "${cicd_script_docker_name}${cicd_script_docker_tag}"\
                    env.cicd_script_cmd         = "bash  ${cicd_script_name}  ${cicd_script_stage_type}"\
                    env.cicd_script_timezone    = "-e TZ=Asia/Taipei  --net host --privileged  "\
\
                    //docker build image info\
                    // ------------------------------------------------------------------------------ //\
\
                    env.cicd_build_name         = "script_main.sh"\
                    env.cicd_build_docker_name  = "cicd_fw_build"\
                    env.cicd_build_docker_tag   = ":0.6"\
                    env.cicd_build_stage_type   = "stage_build"\
\
                    env.cicd_build_start_path  = "-w  ${cicd_working_path}"\
                    env.cicd_build_mount       = "-v  ${cicd_temp_path}:${cicd_working_path}"\
                    env.cicd_build_container   = "${cicd_build_docker_name}${cicd_build_docker_tag}"\
                    env.cicd_build_cmd         = "bash  ${cicd_build_name}  ${cicd_build_stage_type}"\
                    env.cicd_build_timezone    = "-e TZ=Asia/Taipei --mac-address='02:42:ac:12:00:20'"\
\
                    env.cicd_used_sut_name_01      = "empty"\
                    env.cicd_used_sut_name_02      = "empty"\
                    env.cicd_used_sut_name_03      = "empty"\
                }\
\
                //copy script_all folder to /tmp/jenkins/PROJECT_xxx_TYPE folder\
\
                sh "mkdir ${cicd_temp_path}"\
                sh "chmod -R 777 ${cicd_temp_path}"\
                sh "env > ${cicd_temp_path}/${cicd_jenkin_env}"\
                sh "cp -r ${cicd_robot_source}/\*   ${cicd_temp_path}"\
            }\
        }\
\
        stage('Build FW image')\
        {\
            agent \
            {\
                docker \
                {\
                    // execute docker\
                    image "${cicd_build_container}"\
                    args  "${cicd_build_start_path}"\
                    args  "${cicd_build_mount}"\
                    args  "${cicd_build_timezone}"\
                }\
            }\
\
            steps\
            {\
                script\
                {\
                    dir(env.cicd_working_path)\
                    {\
                        if (0 == env.cicd_existed_image_name.length())\
                        {\
                            try {\
                                echo "start run cmd in docker ===>"\
                                echo "change @tmp folder --->"\
                                try {\
                                    output = sh(returnStdout: true, script: "chmod -R 777 ${cicd_temp_path_tmp}").trim()\
                                    }\
                                catch(Exception e) {\
                                    echo "Build in docker result -- fail " + e\
                                }\
                                echo "change @tmp folder <---"\
                                output = sh(returnStdout: true, script: "${cicd_build_cmd}").trim()\
                                echo "Build in docker result -- succ"\
                            }\
                            catch(Exception e) {\
                                echo "Build in docker result -- fail " + e\
                                env.flag_final_ret = "false"\
                            }\
                        }\
                        else\
                        {\
                            echo "cicd_existed_image_name != 0"\
                        }\
                    }\
                }\
            }\
\
            check_stage_status pass | fail\
            my_title = "cicd_script_project  build result PASS | FAIL"\
            my_title : [project][target][]\
            my_desc = ""\
            my_link = ""\
            func_xxx( bash  xxxx.sh   input 1 2 3 ...)\
        }\
\
        stage('Run script testing') \
        {\
            agent\
            {\
                docker \
                {\
                    // execute docker\
                    image "${cicd_script_container}"\
                    args  "${cicd_script_start_path}"\
                    args  "${cicd_script_mount}"\
                    args  "${cicd_script_timezone}"\
                }\
            }\
\
            steps\
            {\
                script\
                {\
                    dir(env.cicd_working_path)\
                    {\
                        if ("true" == env.flag_final_ret)\
                        {\
                            try {\
                                output = sh(returnStdout: true, script: "${cicd_script_cmd}").trim()\
                                echo "Scripts in docker result -- succ"\
                            }\
                            catch(Exception e) {\
                                echo "Scripts in docker result -- fail " + e\
                                retry(15)\
                                {\
                                    sleep(time:360,unit:"SECONDS")\
                                    def statusCode  = sh(returnStdout: true, script: "${cicd_script_cmd}").trim()\
                                    if (statusCode.contains("Search free SUT result PASS"))\
                                    {\
                                        env.flag_final_ret = "true"\
                                    }\
                                    else\
                                    {\
                                        env.flag_final_ret = "false"\
                                        def run_ret = ""\
                                        if ("patchset-created" == env.GERRIT_EVENT_TYPE)\
                                        {\
                                            def send_user = "jenkins"\
                                            def send_password = "123qweASD!@#"\
                                            def send_json_file = "/var/jenkins_home/wait_sut_info.txt"\
                                            run_ret = sendGerritWaitSUT(env.GERRIT_HOST, send_user, send_password, env.GERRIT_CHANGE_ID, env.GERRIT_PATCHSET_REVISION, send_json_file)\
                                        }\
                                        else\
                                        {\
                                            run_ret = false\
                                        }\
                                    }\
                                }\
                            }\
                        }\
                        else\
                        {\
                            echo "no free SUT, no execute testing."\
                        }\
                    }\
                }\
            }\
            check_stage_status pass | fail\
            my_title = "cicd_script_project  testing result PASS | FAIL"\
            my_desc = ""\
            my_link = ""\
            func_xxx( bash  xxxx.sh   input 1 2 3 ...)\
\
\
            webhook_info\
\
webhook_bmc_uri\
webhook_bios_uri\
\
webhook_bmc_uri\
webhook_bios_uri\
\
webhook_bmc_uri\
webhook_bios_uri\
\
webhook_bmc_uri\
webhook_bios_uri\
\
webhook_bmc_uri\
webhook_bios_uri\
            txt\
            json\
            {\
            "x4tf_bmc_uri" : "webhook_bmc_uri",\
            "x4tf_bios_uri" : "webhook_bios_uri"\
\
            "z4_bmc_uri" : "webhook_bmc_uri",\
            "z4_bios_uri" : "webhook_bios_uri"\
\
            "oe22_bmc_uri" : "webhook_bmc_uri",\
            "oe22_bios_uri" : "webhook_bios_uri"\
\
            "bmc_uri" : "webhook_bmc_uri",\
            "bios_uri" : "webhook_bios_uri"\
            \
\
            }\
            ...\
        }\
\
        stage('Clear folder') \
        {\
            steps \
            {\
                dir(env.cicd_mounted_volumn)\
                {\
                    echo "sudo rm -rf ${cicd_temp_path}\* -->"\
                    sh "sudo rm -rf ${cicd_temp_path}\*"\
                    echo "sudo rm -rf ${cicd_temp_path}\* <--"\
                }\
            }\
        }\
\
        stage('final check') \
        {\
            steps\
            {\
                script\
                {\
                    if ("true" == env.flag_final_ret)\
                    {\
                        echo "final pass"\
                    }\
                    else\
                    {\
                        echo "final fail"\
                        error("execute fail")\
                    }\
                }\
            }\
        }\
    }\
}\
\
def sendGerritWaitSUT (str_gerrit_ip, str_gerrit_user, str_gerrit_password, str_change_id, str_patchset_rev, str_json_file_path)\
{\
    def cmd_wait_sut = "curl -X POST --header 'Content-Type:application/json;charset=UTF-8' --data-binary @${str_json_file_path} --user ${str_gerrit_user}:${str_gerrit_password} 'http://${str_gerrit_ip}:8080/a/changes/${str_change_id}/revisions/${str_patchset_rev}/review'"\
\
    try {\
        output = sh(returnStdout: true, script: "${cmd_wait_sut}").trim()\
        echo "Send Rest api to wait SUT -- succ"\
        return true\
    }\
    catch(Exception e) {\
        echo "Send Rest api to wait SUT -- fail " + e\
        return false\
    }\
}