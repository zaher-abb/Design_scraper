from selenium import webdriver
from time import sleep
import pandas as pd
import csv
from selenium.webdriver.common.keys import Keys
import datetime
import json
import couchdb
from itertools import zip_longest

import mysql.connector
#
# mydb = mysql.connector.connect(host="fbi-mysqllehre.th-brandenburg.de", user="abboudz", password="TfaePMQDEfD33RTc")

couch = couchdb.Server('http://admin:admin@localhost:5984/')
db = couch['design_data']

all_saved_user=[]
for i in db :
   key= db[i]['Design_made_by']
   all_saved_user.append(key)



# Chrome  Driver
driver = webdriver.Chrome("D:\chromedriver.exe")
key = 0
user_data = []
make_data = []
des_dict = {}
all_coll = []
all_fav = []
url_list = []

with open('Robot_maker.csv', newline='') as f:
    urls = csv.reader(f)
    for row in urls:
        url_list += row

def get_design_make_etc(class_name):
    url_list2 = []
    condition = True
    while condition:
        result = driver.find_elements_by_class_name(class_name)
        for i in range(len(result)):
            try:
                url_list2.append(result[i].get_property('href'))
                # print(result[i].get_property('href'))
            except Exception as e:
                print(e)
        try:
            driver.find_element_by_xpath("//div[@class='Pagination__button--2X-2z Pagination__more--24exV']").click()
            # testTemp+=1
            # if testTemp >=1 :
            #     break
            sleep(3)
        except Exception as e:
            condition = False
            print(e)

    return url_list2

# von https://www.thingiverse.com/marcuss 104
# we are in the user Number :104
y=292
# TODO Groupen muessen auch damit schreiben
for url in url_list:
    design_data = []
    if str(url).split("/", 3)[3] in all_saved_user:
        continue
    print(url)
    y = y + 1
    print(y)
    print("we are in the user Number :{}".format(y))
    driver.get(url)
    sleep(3)
    all_des = []
    # TODO Design
    driver.get(url + '/designs')
    try:
        # Design
        sleep(2)
        all_design_url = get_design_make_etc('ThingCardBody__cardBodyWrapper--ba5pu')
        for i in all_design_url:
            all_des.append(i)

        user_number_of_design = len(all_design_url)
        print(user_number_of_design)
    except:
        user_number_of_design = 0
    # #
    # TODO Design 2
    for des in all_des:
        try:
            driver.get(des)
        except:
            continue

        sleep(3)
        try:
            design_img_url = driver.find_element_by_xpath(
                "/html/body/div[1]/div/div/div/div[5]/div[1]/div/div[2]/div/div/div/div/div[1]/div/ul/li[1]/img").get_property(
                'src')
        except:
            design_img_url = "not found"
        design_key = str(des).split("/", 3)[3]
        try:
            design_name = driver.title.split(" by")[0]
        except:
            try:
                design_name = driver.find_element_by_class_name('ThingPage__modelName--3CMsV').text
            except:
                design_name = "not found"
        try:
            design_made_by = str(url).split("/", 3)[3]
        except:
            design_made_by = "not found"
        try:
            design_created_at = str(driver.find_element_by_xpath(
                '//*[@id="react-app"]/div/div/div/div[5]/div[1]/div/div[1]/div/div[2]').text).split(" ", 2)[2:][0]
        except:
            design_created_at = "not found"
        design_setting = []
        try:
            setting = driver.find_elements_by_class_name('ThingPage__preHistory--312bi')
            for s in setting:
                design_setting.append(s.text)
            str(design_setting).replace("\n"," ")
            if len(design_setting)==0 :
                design_setting = "not found"
        except:
            design_setting = "not found"
        try:
            # Summary
            design_summary = driver.find_element_by_xpath(
                "//div[@class='ThingPage__description--14TtH']//p[1]").text
        except:
            design_summary = "not found"
        design_tags = []
        try:
            tags = driver.find_elements_by_class_name('Tags__tag--2Rr15')
            for tag in tags:
                design_tags.append(tag.text)
            if len(design_tags) == 0:
                design_tags = "not found"
        except:
            design_tags = "not found"
        # TODO COMMENTS
        try:
            driver.get(des + "/comments")
            sleep(2)
            all_comments_text = []
            all_comments_username = driver.find_elements_by_class_name('ThingComment__madeBy--sERFH')
            for i in all_comments_username:
                comment = str(i.text).split("\n")
                comment_writer_username = comment[0]
                comment_data = comment[1]
                all_comments_text.append((comment_writer_username, comment_data))
            if len(all_comments_text) == 0:
                all_comments_text = "not found"
        except:
            all_comments_text = "not found"

        # design_data.append(
        #     (design_key, design_name, design_made_by, design_created_at, design_summary, design_setting,
        #      design_tags, design_img_url, str(datetime.date.today()), '3D Printable Humanoid Robots'))

        myDict={
            'Design_key':design_key, 'Design_name':design_name, 'Design_made_by':design_made_by, 'Design_created_at':design_created_at,
            'Design_summary':design_summary, 'Design_setting':design_setting, 'Design_tags':design_tags,
            'Design_img_url':design_img_url,
            'design_Scraping date': str(datetime.date.today()), 'from_Group':'3D Printable Humanoid Robots'
        }

        db.save(myDict)
        sleep(2)


        # design_data_frame = pd.DataFrame(data=design_data,
        #                                  columns=['Design_key', 'Design_name', 'Design_made_by', 'Design_created_at',
        #                                           'Design_summary', 'Design_setting', 'Design_tags',
        #                                           'Design_img_url',
        #                                           'design_Scraping date', 'from_Group'])
        # myDict=design_data_frame.to_dict()
        # print(myDict)
        # db.save(myDict)
        # temp_Dict = design_data_frame.to_json('design_data.json', orient='index', default_handler=str)
        # design_data_frame.
        # db.save(temp_Dict)
