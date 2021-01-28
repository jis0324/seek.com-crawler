# -*- coding: utf-8 -*-
import os
import time
import traceback
import re
import json
import csv
import requests
from scrapy import Selector

base_dir = os.path.dirname(os.path.abspath(__file__))
output_csv_path = base_dir + "/result.csv"

class Crawler():

    # get query list
    def find_phone(self, res_content):
        try:
            phone = re.search(r"tel:([\d\s]+)", res_content).groups()[0]
            return phone
        except:
            return ""

    def find_email(self, res_content):
        try:
            mail = re.search(r"mailto:(.{50})", res_content).groups()[0]
            return mail.split("\"")[0]
        except:
            return ""

    # get Businesses on Google
    def getJobs(self, jobURLs):
        for jobURL in jobURLs:
            try:
                jobURL = "https://www.seek.com.au" + jobURL
                response = requests.get(jobURL)
                jobHtmlDom = Selector(text=response.text)

                try:
                    jobTitle = jobHtmlDom.xpath("//span[@data-automation='job-detail-title']//h1/text()").get()
                except:
                    jobTitle = ""

                try:
                    companyName = jobHtmlDom.xpath("//span[@data-automation='advertiser-name']/span/text()").get()
                except:
                    companyName = ""

                if not companyName:
                    try:
                        companyName = jobHtmlDom.xpath("//span[@data-automation='job-header-company-review-title']/span/text()").get()
                    except:
                        pass
                
                try:
                    phoneNumber = self.find_phone(response.text)
                except:
                    phoneNumber = ""

                try:
                    email = self.find_email(response.text)
                except:
                    email = ""

                resultDict = {"Job Title": jobTitle, "Company Name": companyName, "Phone Number": phoneNumber, "Email": email, "Job URL": jobURL}
                # insert data to csv file.
                file_exist = os.path.isfile(output_csv_path)
                with open(output_csv_path, 'a', newline="", encoding="utf-8") as output_file:
                    fieldnames = ["Job Title", "Company Name", "Phone Number", "Email", "Job URL"]
                    writer = csv.DictWriter(output_file, fieldnames=fieldnames)

                    # wirte fileds if file not exist
                    if not file_exist:
                        writer.writeheader()

                    writer.writerow(resultDict)

                print("-----------------------------------")
                print(json.dumps(resultDict, indent=2))

            except:
                traceback.print_exc()
                continue
        
    # main function
    def start(self):
        # Search from Google.
        try:
            page = 1
            while True:
                startURL = "https://www.seek.com.au/melbourne-insurance-industry-jobs/in-All-Australia?page={}".format(page)
                response = requests.get(startURL)
                htmlDom = Selector(text = response.text)

                # get podiartist offices
                jobURLs = htmlDom.xpath("//a[@data-automation='jobTitle']/@href").extract()
                nextBtn = htmlDom.xpath("//a[@data-automation='page-next']/@href")

                if jobURLs:
                    print("************** Extracting Page", str(page), "**************")
                    self.getJobs(jobURLs)
                else:
                    break
                
                if nextBtn:
                    page += 1
                    continue
                else:
                    break

            else:
                print("Can Not Find Google Search Result. Try Again With Other Query.")
                return

        except:
            traceback.print_exc()
        
if __name__ == "__main__":
    # delete result csv file 
    file_exist = os.path.isfile(output_csv_path)
    if file_exist:
        os.remove(output_csv_path)

    crawler = Crawler()
    crawler.start()
    
