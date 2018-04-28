import sys, os
from bs4 import BeautifulSoup
import json
import types
from xml.dom.minidom import Document
import xml.sax
import xml.sax.xmlreader
import xml.sax.saxutils

reload(sys)
sys.setdefaultencoding('utf8')

global file_name
global testcase_name_list
global testcase_status_list

testcase_name_list = []
testcase_status_list = []

'''
Read log.html to get result
'''


def read_html(file):
    html_file = open(file)
    html_page = html_file.read()
    html_file.close()

    soup = BeautifulSoup(html_page, "html.parser")

    cctag = soup.find_all('script', attrs={'type': 'text/javascript'})
    for i in cctag:
        if str(i).find("window.output[\"stats\"]") > 0:
            data = str(i).replace("<script type=\"text/javascript\">", "").replace("</script>", "").replace(
                "window.output[\"stats\"] = ", "").replace(";", "")
    return data


'''
Create env tmp file.
For device type, host name, version
'''


def write_env(deivce_type, host_name, output_tmp):
    data_tmp = file(output_tmp, "w+")
    # output = os.popen("dpkg -l | grep road-scene-player |awk {'print $3'}")
    # version = output.read().strip("\n")
    version = "2.3.1.x"
    data_tmp.writelines(deivce_type + ",")
    data_tmp.writelines(host_name + ",")
    data_tmp.writelines(version + ",")
    branch = ""
    if version.count("0.") == 3:
        branch = "master"
    else:
        tmp_branch = version.split(".")
        for i in range(0, len(tmp_branch) - 1):
            branch += tmp_branch[i] + "."
        branch += "x"
    data_tmp.writelines(branch)
    data_tmp.close()


'''
Create total table tmp file.
'''


def write_data(data, output_tmp):
    data_tmp = file(output_tmp, "w+")
    data_tmp.writelines(str(data))
    data_tmp.close()


class XMLHandler(xml.sax.ContentHandler):
    def startElement(self, tag, attrs):
        global testcase_name_list
        global testcase_status_list
        if tag == "test":
            if len(attrs) > 0:
                name_attr = attrs.get("name")
                testcase_name_list.append(name_attr)
        if tag == "status":
            if attrs.get("critical") == "yes":
                status = attrs.get("status")
                testcase_status_list.append(status)

    def endDocument(self):
        global testcase_name_list
        global testcase_status_list
        global file_name
        fail_test = ""
        for i in range(0, len(testcase_status_list)):
            if testcase_status_list[i] == "FAIL":
                test_case = "<font color=\"red\">" + str(testcase_name_list[i]) + "</font><br><br>"
                fail_test += test_case
        data_tmp = file(file_name, "w+")
        data_tmp.writelines(str(fail_test))
        data_tmp.close()


'''
Read output.xml to get failed testcase and write the temp file
'''


def read_and_write_xml(input_xml_file, output_testcase_tmp):
    global file_name
    file_name = output_testcase_tmp
    parser = xml.sax.make_parser()
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)
    handler = XMLHandler()
    parser.setContentHandler(handler)
    parser.parse(input_xml_file)


if __name__ == "__main__":
    input_folder = sys.argv[1]
    output_file = sys.argv[2]
    deivce_type = sys.argv[3]
    host_name = sys.argv[4]
    input_html_file = input_folder + "log.html"
    input_xml_file = input_folder + "output.xml"
    output_table_tmp = output_file + ".table.tmp"
    output_testcase_tmp = output_file + ".testcase.tmp"
    output_env_tmp = output_file + ".env.tmp"
    write_data(read_html(input_html_file), output_table_tmp)
    read_and_write_xml(input_xml_file, output_testcase_tmp)
    write_env(deivce_type, host_name, output_env_tmp)
