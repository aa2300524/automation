#!/bin/sh

get_value_from_file() 
{
    jenkins_file=jenkins_env.log
    python_func=cicd_func.py
    func_name=get_from_file

    # key : my_file__my_key, python func parse   my_file=$1   my_key=$2
    fin_key=$(printf "%s__%s" "$1" "$2")

    # python3  cicd_func.py  jenkins_env.log  get_from_file  jenkins_env.log__key1
    my_value=$(python3  $python_func  $jenkins_file  $func_name  $fin_key  2>&1)
    echo $my_value
}

get_value_from_json()
{
    jenkins_file=jenkins_env.log
    python_func=cicd_func.py
    func_name=get_from_json


    # my_file=$1   key_1=$2   key_2=$3
    fin_key=$(printf "%s__%s__%s" "$1" "$2" "$3")

    # python3  cicd_func.py  jenkins_env.log  get_from_json  jenkins_env.log__gerrit_server_info__nc_url
    my_value=$(python3  $python_func  $jenkins_file  $func_name  $fin_key  2>&1)
    echo $my_value
}

upload_to_gerrit()
{
    REVIEW_FILE=$1
    p_file=$2
    p_server=$3

    Gerrit_info_key=gerrit_server_info

    TAG_change_id=GERRIT_CHANGE_ID=
    TAG_pset_rev=GERRIT_PATCHSET_REVISION=

    TAG_gerrit_ip=gerrit_ip
    TAG_gerrit_port=gerrit_port
    TAG_gerrit_user=gerrit_user
    TAG_gerrit_pwd=gerrit_pwd

    echo "Upload review chipset file"

    GERRIT_CHANGE_ID=$(get_value_from_file $p_file $TAG_change_id)
    GERRIT_PATCHSET_REVISION=$(get_value_from_file $p_file $TAG_pset_rev)

    gerrit_ip=$(get_value_from_json $p_server $Gerrit_info_key $TAG_gerrit_ip)
    gerrit_port=$(get_value_from_json $p_server $Gerrit_info_key $TAG_gerrit_port)
    gerrit_user=$(get_value_from_json $p_server $Gerrit_info_key $TAG_gerrit_user)
    gerrit_pwd=$(get_value_from_json $p_server $Gerrit_info_key $TAG_gerrit_pwd)

    URL="${gerrit_ip}:${gerrit_port}"

    upload_cmd="curl -X POST\
    --header Content-Type:application/json;charset=UTF-8 \
    --data-binary @$REVIEW_FILE \
    --user $gerrit_user:$gerrit_pwd \
    $URL/a/changes/$GERRIT_CHANGE_ID/revisions/$GERRIT_PATCHSET_REVISION/review "

    echo "upload_cmd = [$upload_cmd]"
    exe_ret=$($upload_cmd)
    echo "exe_ret = ${exe_ret}"
}

combine_share_url()
{
    p_file=$1

    Gerrit_info_key=gerrit_server_info
    server_info=cicd_func.json

    KEY_PROJECT=cicd_script_project=
    KEY_MODULE=cicd_script_module=
    KEY_EMAIL=GERRIT_CHANGE_OWNER_EMAIL=
    KEY_CHANGE_ID=GERRIT_CHANGE_NUMBER=
    KEY_PATCHSET_NUM=GERRIT_PATCHSET_NUMBER=
    KEY_UPLOAD_URL=nc_url

    p_name=$(get_value_from_file $p_file $KEY_PROJECT)
    p_module=$(get_value_from_file $p_file $KEY_MODULE)
    p_email=$(get_value_from_file $p_file $KEY_EMAIL)
    p_change_id=$(get_value_from_file $p_file $KEY_CHANGE_ID)
    p_patchset=$(get_value_from_file $p_file $KEY_PATCHSET_NUM)

    #Ben5_Lin@asus.com -> Ben5_Lin
    p_user=$(echo $p_email | cut -d'@' -f1)

    cur_date=$(date '+%Y_%m_%d')
    upload_folder=$(printf "review_%s__%s__%s__%s" "$cur_date" "$p_change_id" "$p_patchset" "$p_user")

    nc_url=$(get_value_from_json $server_info $Gerrit_info_key $KEY_UPLOAD_URL)

    upload_url=$(printf "%s%s/%s/review/%s" "$nc_url" "$p_name" "$p_module" "$upload_folder")

    # http://10.10.65.57:8888/apps/files/?dir=x4tf/bmc/review/review_2022_09_01__1348__2__samks_hung
    echo $upload_url
}

create_review_file()
{
    REVIEW_FILE=$1
    PLAIN_RSLT=$2
    CHANGED_FILE=$3
    p_file=$4

    pre_file=no_filter.txt

    TAG_gerrit_proj=GERRIT_PROJECT=
    TAG_patch_rev=GERRIT_PATCHSET_REVISION=

    GERRIT_PROJECT=$(get_value_from_file $p_file $TAG_gerrit_proj)
    PATCHSET_REV=$(get_value_from_file $p_file $TAG_patch_rev)

    echo "git diff-tree --no-commit-id --name-only -r ${PATCHSET_REV} > ${CHANGED_FILE}"

    chang_file_ret=$(git diff-tree --no-commit-id --name-only -r ${PATCHSET_REV} > $pre_file)
    filter_ret=$(cat $pre_file | grep -E '\.(c|cpp|h)$' > ${CHANGED_FILE})
    cppcheck --enable=all --inconclusive  --file-list=${CHANGED_FILE} 2> ${PLAIN_RSLT}

    str_url=$(combine_share_url $p_file)

    # CNT=$(grep -rnw . $PLAIN_RSLT | wc -l)
    CNT=$(grep -rnw "error:" $PLAIN_RSLT | wc -l)
    echo "CNT = $CNT"

    if [ "x$CNT" == "x0" ] ; then
        REVIEW_MSG=$(printf "Cppcheck found 0 error(s) \n to see cppcheck_result.xml \n %s" "$str_url")
    else
        REVIEW_MSG=$(printf "Cppcheck found $CNT error(s) in your codes.\n\n to see cppcheck_result.xml \n %s" "$str_url")
    fi

    echo "REVIEW_MSG = $REVIEW_MSG"

    CHANGED_FILES=$(cat ${CHANGED_FILE})

    echo "{" > $REVIEW_FILE
    echo "  \"tag\": \"jenkins\"" >> $REVIEW_FILE
    echo ", \"message\": \"$REVIEW_MSG\"" >> $REVIEW_FILE

    # if [ "x$CNT" ] ; then # all msg update to gerrit change id
    if [ "x$CNT" != "x0" ] ; then
        echo ", \"labels\": {\"Code-Review\": -1}" >> $REVIEW_FILE
        echo ", \"comments\": {" >> $REVIEW_FILE
        awk -v folder=$GERRIT_PROJECT"/" \
            -v cc="$CHANGED_FILES" \
            'BEGIN{
              FS=":";
              split(cc, ccs, " ");
              for(f in ccs) {
                valids[ccs[f]]=1;
              }
            }
            {
              f=$1;n=$2;c="";
              for(i=3;i<=NF;i++){
                if(c == "") {
                  c = $i;
                }
                else {
                  c = c":"$i;
                }
              }
              gsub("[[]","",f);
              sub(folder,"",f);
              gsub("]","",n);
              gsub("\"","`",c);
              msg[f][line][0] = n;
              msg[f][line][1] = c;
              line++;
            }
            END{
              file=0;
              for(f in msg) {
                if(valids[f] == 1) {
                  line=0;
                  if(file > 0) { printf(",\n"); }
                  printf("   \"%s\": [\n", f);
                  for(n in msg[f]) {
                    if(line > 0) { printf(",\n"); }
                    printf("    {\"line\": %s, \"message\": \"%s\"}", 
                                                     msg[f][n][0], msg[f][n][1]);
                    line++;
                  }
                  printf("\n   ]\n");
                  file++;
                }
              }
            }' $PLAIN_RSLT >> $REVIEW_FILE
        echo "  }" >> $REVIEW_FILE
    fi >> $REVIEW_FILE
    echo "}" >> $REVIEW_FILE
}

filter_cppcheck()
{
  python_func=cppcheck_filter.py
  filter_cppcheck=$(python $python_func $PLAIN_RSLT $CHANGED_FILES $jenkins_file 2>&1)
  echo $filter_cppcheck
}

# #=========================================================#
# main
# #=========================================================#

REVIEW_FILE=$1
PLAIN_RSLT=$2
CHANGED_FILES=$3


jenkins_file=jenkins_env.log
server_info=cicd_func.json

# #=========================================================#
echo "generate file for update gerrit-cppcheck info."
create_review_file $REVIEW_FILE  $PLAIN_RSLT  $CHANGED_FILES  $jenkins_file

#=========================================================#
echo 'filter_cppcheck'
CHANGED_FILES=$3
filter_cppcheck $REVIEW_FILE $PLAIN_RSLT $CHANGED_FILES $jenkins_file

# # #=========================================================#
echo "upload file to gerrit via curl"
# upload_to_gerrit $REVIEW_FILE $jenkins_file $server_info

# ben test
# combine_share_url ${jenkins_file}


# bash update_gerrit_chipset.sh  tmp_struct.txt  cppcheck_result.xml  cppcheck_scan_file.txt


# REVIEW_FILE    - final file upload to gerrit (tmp_struct.txt)
# PLAIN_RSLT     - cppcheck report (cppcheck_result.xml)
# CHANGED_FILES   (cppcheck_scan_file.txt)
