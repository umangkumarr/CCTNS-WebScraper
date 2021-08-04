import requests
import pandas
import json
import xlrd
from datetime import datetime as dt

URL = "http://digitalpolicecitizenservices.gov.in/centercitizen/"
URL_F = ["login.htm", "sendOtp.htm", "j_spring_security_check",
         "searchproclaimedOffender.htm?", "printProclaimedOffender.htm"]
path = "CCTNS/pdf/"  # directory path to save the offender detials

r = requests.get(URL+URL_F[0])
cookie = r.headers['Set-Cookie'].split(';')[0]
header = {'User-Agent': 'Mozilla/5.0', 'Cookie': cookie}

p_no = input("Enter Mobile Number: ")
data = {'mobileNo': int(p_no)}
r = requests.post(URL+URL_F[1], headers=header, data=data)

OTP = input("Enter OTP: ")
data = {'j_username': p_no, 'j_password': OTP,
        'firstName': 'u', 'userFlag': '0'}
r = requests.post(URL+URL_F[2], headers=header, data=data)

cookie = r.headers['Set-Cookie'].split(';')[0]
header['Cookie'] = cookie

df = pandas.read_excel(open("CCTNS/dummydata.xlsx", "rb"))
record = json.load(open("CCTNS/records.json",))

start_row = 0  # row number to start from (0 indexing)

for l in range(start_row, len(df)):
    row = df.iloc[l]

    data1 = {'stateCd': int(record[row["State"]][0]),
             'districtCd': int(record[row["State"]][1][row["District"]][0]),
             'policeStationCd': record[row["State"]][1][row["District"]][1][row["Police Station"]],
             'proclaimedoffendername': row["Name"],
             'courtDateRangeFrom': "/".join(str(dt.date(row["Date Range of Proclamation1"])).split("-")[::-1]),
             'courtDateRangeTo': "/".join(str(dt.date(row["Date Range of Proclamation2"])).split("-")[::-1]),
             'firNumber': int(row["FIR Number"]),
             'pageStartNo': 0,
             'pageCacheRows': 50,
             'pageTotalCount': 0}

    r = requests.post(URL+URL_F[3], headers=header, data=data1)
    d = json.loads(r.content)

    if int(d["count"]):
        data = {"accusedNo": "", "fileuploadno": "",
                "psCd": "", "FULL_FIR_NUMBER": ""}

        for i in range(d["count"]):
            file_path = path+str(row["UniqueID"])+".pdf"
            with open(file_path, "wb") as f:
                data["accusedNo"] = d["list"][i]["accusedNo"]
                data["fileuploadno"] = d["list"][i]["fileuploadno"]
                data["psCd"] = d["list"][i]["psCd"]
                data["FULL_FIR_NUMBER"] = d["list"][i]["FULL_FIR_NUMBER"]
                r = requests.post(URL+URL_F[4], headers=header, data=data)
                f.write(r.content)
                print(str(row["UniqueID"]))
    else:
        print("\nNo Record exists in the system for the selected criteria")
