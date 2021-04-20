# Import required modules
import requests
import pandas as pd
import json
import subprocess
from tqdm import tqdm
import re

# Set pandas to show full rows and columns
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

'''
This is API Query Function
'''
# Main function


def query(cname="cname", apikey="apikey", apiquery="apiquery"):
    tqdm.pandas()
    global icpd, icd
    icd = requests.get("https://"+cname+".infocyte.com/api/" +
                       apiquery+"?access_token="+apikey + "&count=True")
    if "There is no method to handle GET" in icd.content.decode("utf-8"):
        print("API Endpoint not found, suffix \"/explorer/#/\" at the end of URL to find the correct end point")
    elif icd.reason == "Not Found":
        print("Please check the CNAME used is correct")
    elif icd.reason == "Unauthorized":
        print("Please check the APIKey / Token has the permission to access the instance")
    elif icd.reason != "OK":
        print("Something went wrong and unable to find the reason")
    else:
        iccount = (str(icd.headers.get("X-Total-Count"))[:-3])
        if (len(iccount) == 0):
            loopic = icd
            for x in tqdm(range(1), desc="Loading " + apiquery, ncols=100, unit='Loop(s)', bar_format='{l_bar}{bar} | {n_fmt}/{total_fmt} {unit}', colour='GREEN'):
                icdata = json.loads(loopic.text)
                icdb = pd.DataFrame(icdata)
                icpd = icdb
        else:
            icdata = json.loads(icd.text)
            icdb = pd.DataFrame(icdata)
            icpd = icdb
            for x in (num+1 for num in tqdm(range(int(iccount)), desc="Loading " + apiquery, ncols=100, unit='Loop(s)', bar_format='{l_bar}{bar} | {n_fmt}/{total_fmt} {unit}', colour='GREEN')):
                if x > 9:
                    loopic = requests.get("https://"+cname+".infocyte.com/api/"+apiquery +
                                          "?access_token=" + apikey+"&filter={\"skip\": "+str(x).ljust(5, '0')+"}")
                    icdata = json.loads(loopic.text)
                    icdb = pd.DataFrame(icdata)
                    icpd = icpd.append(icdb, ignore_index=True)
                else:
                    loopic = requests.get("https://"+cname+".infocyte.com/api/"+apiquery +
                                          "?access_token=" + apikey+"&filter={\"skip\": "+str(x).ljust(4, '0')+"}")
                    icdata = json.loads(loopic.text)
                    icdb = pd.DataFrame(icdata)
                    icpd = icpd.append(icdb, ignore_index=True)
    #mask = icpd.astype(str).apply(lambda x: x.str.match(r'(\d{2,4}-\d{2}-\d{2,4})+').all())
    #icpd.loc[:, mask] = icpd.loc[:, mask].apply(pd.to_datetime)
    return icpd


'''
This is PowerShell Function
'''


def ps(cname="cname", apikey="apikey", pscmd="pscmd"):
    global psout, psraw, psoutput
    key = "Set-ICToken -Instance " + cname + " -Token " + \
        apikey + ";Set-ICBox -Global -Last 90;"
    pscmd = pscmd.replace('\n', ';')
    for line in tqdm(pscmd.splitlines(), desc="Loading ", ncols=100, unit='Line(s)', bar_format='{l_bar}{bar} | {n_fmt}/{total_fmt} {unit}', colour='BLUE'):
        psraw = subprocess.run(
            ["powershell.exe", "-Command", key + line], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        psoutput = psraw.stdout.decode("utf-8")
        psout = re.sub('(True)\r\n', '', psoutput)
    return(psout)


'''
This is PowerShell base64-Encoded Funcation
'''


def pse(cname="cname", apikey="apikey", psecmd="psecmd"):
    global pseout, pseraw, pseoutput
    key = "Set-ICToken -Instance " + cname + " -Token " + \
        apikey + ";Set-ICBox -Global -Last 90;"
    psecmd = psecmd.replace('\n', ';')
    etext = ("$pt=\'" + key+psecmd +
             "\';$enc = [convert]::ToBase64String([System.Text.encoding]::Unicode.GetBytes($pt));$enc")
    for line in tqdm(etext.splitlines(), desc="Loading ", ncols=100, unit='Line(s)', bar_format='{l_bar}{bar} | {n_fmt}/{total_fmt} {unit}', colour='BLUE'):
        pseraw = subprocess.run(["powershell.exe", line],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        eoutcome = pseraw.stdout.decode("utf-8")
        data = subprocess.run(
            ["powershell.exe", "-encoded", eoutcome], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        pseoutput = data.stdout.decode("utf-8")[6:]
        pseout = re.sub('(True)\r\n', '', pseoutput)
    return(pseout)

# EOF
