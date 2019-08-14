#!/usr/bin/env python

# Developed by Alex Israelov
# Alex Enterprise
#
# Dear Craigslist:
# Your site has too much email integration, and needs an API
# even though you strongly disallow bots like this one.
# also thanks for providing a free affiliate marketing platform.

import os
import time
import Listing

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

from pyvirtualdisplay import Display

import spintax


class CraigslistBot:

    @staticmethod
    def debug(inString):
        print(" [BOT] - %s" % inString.encode('utf-8').strip())

    def __init__(self, protonLogin="", protonPassword="", loginEmail="", loginPass="", contactNumber="", contactName="",
                 postCode="", listingsFile="", waitTime=10, waitTimeBetweenPosts=30):
        self.display = ""

        if not os.name == 'nt':
            self.display = Display(visible=0, size=(1248, 1000))  # 800x600
            self.display.start()

        self.client = webdriver.Firefox()
        self.isLoggedIn = False

        self.protonLogin = protonLogin
        self.protonPassword = protonPassword
        self.loginEmail = loginEmail
        self.loginPass = loginPass
        self.contactNumber = contactNumber
        self.contactName = contactName
        self.postCode = postCode
        self.listingsFile = listingsFile
        self.waitTime = waitTime
        self.waitTimeBetweenPosts = waitTimeBetweenPosts

        self.locationCode = "lax"

    @classmethod
    def initializelistings(cls):
        listings = []

        name = ""
        desc = ""
        link = ""

        # read listings from file
        f = open("listings.txt", "r")
        f1 = f.readlines()
        i = 0
        looking = 0  # 0 = name, 1 = desc, 2 = link

        for x in f1:
            if x in ["\n", "\r\n"]:
                continue

            if x.__contains__("Name="):
                looking = 0
                continue
            if x.__contains__("Desc="):
                looking = 1
                continue
            if x.__contains__("Link="):
                looking = 2
                continue
            if x.__contains__("###"):
                break

            if looking == 0:
                name += x
            if looking == 1:
                desc += x
            if looking == 2:
                link = x  # assume links are 1 line only
                myListing = Listing(name, desc, link)
                listings.append(myListing)
                name = ""
                desc = ""
                link = ""
                looking = 0

        f.close()
        return listings

    def __del__(self):
        if not os.name == 'nt':
            self.display.stop()

        self.client.quit()
        return 0

    def login(self, oneTimeLoginLink=""):
        self.debug("loginEmail: " + self.loginEmail)
        self.debug("loginPass: " + self.loginPass)

        self.debug("Navigating to craigslist login")

        if oneTimeLoginLink == "":
            self.client.get("https://accounts.craigslist.org/login")
        else:
            self.client.get(oneTimeLoginLink)

        self.debug("Logging in")

        self.waitForId("inputEmailHandle")

        self.client.find_element_by_css_selector("#inputEmailHandle").send_keys(self.loginEmail)

        self.client.find_element_by_css_selector("#inputPassword").send_keys(self.loginPass)

        self.client.find_element_by_id("login").click()

        # if need activation:
        # otl = self.validatePostInEmail()
        # self.login(otl)
        # return

        try:
            self.client.find_element_by_css_selector('.tab')
        except NoSuchElementException:
            self.debug("Not logged in")
            return
        self.debug("Logged in")

        self.isLoggedIn = True

    def createpost(self, listing):
        if not self.isLoggedIn:
            return 0

        self.debug("Attempting to post this listing:")
        self.debug(listing.tostring() + "\n")

        self.debug("Navigating to post page")

        self.debug("locationCode: " + self.locationCode)
        initialPostUrl = "https://post.craigslist.org/c/" + self.locationCode
        self.debug("navigating to " + initialPostUrl)
        self.client.get(initialPostUrl)

        self.client.find_element_by_css_selector("input[value='1']").click()

        # fso = for sale by owner
        # so  = service offered
        self.client.find_element_by_css_selector("input[value='fso']").click()
        # time.sleep(self.waitTime)

        # 199 = computer parts
        # 7   = computers
        # 96  = electronics
        self.client.find_element_by_css_selector("input[value='96']").click()
        # time.sleep(self.waitTime)

        """
        self.debug("Trying to fill in email")
        try:
            self.client.find_element_by_css_selector(
                '#FromEMail').send_keys(self.loginEmail)
        except NoSuchElementException:
            self.debug("Not avaliable")
        try:
            self.client.find_element_by_css_selector(
                '#FromEMail').send_keys(self.loginEmail)
        except NoSuchElementException:
            self.debug("Not avaliable")
        """

        self.debug("Checking 'Okay to contact by phone'")
        self.waitForName("show_phone_ok")
        self.client.find_element_by_name("show_phone_ok").click()
        self.client.find_element_by_name("contact_phone_ok").click()

        self.debug("Checking 'Okay to contact by text'")
        self.client.find_element_by_name("contact_text_ok").click()

        self.debug("Filling in contact phone number")
        self.client.find_element_by_name(
            "contact_phone").send_keys(self.contactNumber)

        self.debug("Filling in contact name")
        self.client.find_element_by_name(
            "contact_name").send_keys(self.contactName)

        self.debug("Filling in post title")
        spinName = spintax.spin(listing.name)
        self.client.find_element_by_name("PostingTitle").send_keys(spinName)

        self.debug("Filling in zip code")
        self.client.find_element_by_id("postal_code").send_keys(self.postCode)

        self.debug("Filling in post content")
        spinDescription = spintax.spin(listing.description)
        self.client.find_element_by_name("PostingBody").send_keys(spinDescription)

        self.debug("Checking 'Okay to contact for other offers'")
        self.waitForName("contact_ok")
        self.client.find_element_by_name("contact_ok").click()

        # self.debug("Unchecking 'Want a map' if checked")
        # try:
        #    self.client.find_element_by_css_selector("#wantamap:checked")
        # except NoSuchElementException:
        #    self.debug("Not checked")
        # finally:
        #    self.client.find_element_by_css_selector("#wantamap:checked").click()
        # time.sleep(self.waitTime)

        self.debug("Clicking continue")
        self.client.find_element_by_name("go").click()

        # if "editimage" in self.client.current_url:  # FIX tHIS
        #   self.debug("Clicking continue")
        #   self.client.find_element_by_css_selector('button.done').click()
        # else:
        #   self.debug(
        #      "Could not submit. Maybe a bad email address or phone number")

        self.debug("Clicking publish")
        self.waitForClass("bigbutton")
        self.client.find_element_by_class_name('bigbutton').click()

        # determine if we need to switch to classic uploading
        time.sleep(self.waitTime)
        if len(self.client.find_elements_by_id('classic')) != 0:
            self.debug("clicking use classic image uploader")
            self.waitForId("classic")
            time.sleep(self.waitTime)
            self.client.find_element_by_id('classic').click()
            time.sleep(self.waitTime)  # must wait for classic to pop into the viewport

        self.debug("uploading images")
        self.waitForName("file")
        for imagePath in listing.imagePathList:
            self.debug("Attempting to upload image: " + os.getcwd() + "/" + imagePath)
            self.client.find_element_by_name("file").send_keys(os.getcwd() + "/" + imagePath)
            time.sleep(self.waitTime)

        self.debug("Clicking done with images")
        self.client.find_element_by_class_name('bigbutton').click()

        self.debug("Click publish (again)")
        self.waitForName("go")
        self.client.find_element_by_name('go').click()

        # check if we need to verify the post
        time.sleep(self.waitTime)
        htmlText = self.client.find_element_by_css_selector("body").text
        # self.debug(htmlText)
        if "FURTHER ACTION REQUIRED" in htmlText:
            # wait for the email to come through and then varify it
            time.sleep(45)
            self.validatePostInEmail()

        return self.client.find_element_by_css_selector("ul.ul").find_elements_by_css_selector("a")[0].get_attribute(
            "href")

    # region WaitFor methods

    def waitForName(self, name):
        for i in range(0, 30):
            self.debug("waiting for id \"" + name + "\"...")
            if len(self.client.find_elements_by_name(name)) != 0:
                break
            time.sleep(2)

    def waitForId(self, idName):
        for i in range(0, 30):
            self.debug("waiting for id \"" + idName + "\"...")
            if len(self.client.find_elements_by_id(idName)) != 0:
                break
            time.sleep(2)

    def waitForCss(self, css):
        for i in range(0, 30):
            self.debug("waiting for css selector \"" + css + "\"...")
            if len(self.client.find_elements_by_css_selector(css)) != 0:
                break
            time.sleep(2)

    def waitForClass(self, className):
        for i in range(0, 30):
            self.debug("waiting for class \"" + className + "\"...")
            if len(self.client.find_elements_by_class_name(className)) != 0:
                break
            time.sleep(2)

    # endregion

    def validatePostInEmail(self):
        self.debug("NOW, WE VALIDATE!")
        self.client.get("https://mail.protonmail.com/login")

        self.waitForId("username")
        self.client.find_element_by_id("username").send_keys(self.protonLogin)
        self.client.find_element_by_id("password").send_keys(self.protonPassword)
        self.client.find_element_by_id("login_btn").click()

        self.waitForClass("menuLabel-item")
        labelItem = self.client.find_elements_by_class_name("menuLabel-item")[0]
        labelLink = labelItem.find_elements_by_css_selector("a")[0].get_attribute('href')
        self.client.get(labelLink)

        self.waitForClass("conversation")
        self.client.find_elements_by_class_name("conversation")[0].click()

        self.waitForClass("message")
        correctMessage = self.client.find_elements_by_class_name("message")[-1]

        self.waitForCss("a")
        oneTimeLink = correctMessage.find_elements_by_css_selector("a")[-1].get_attribute('href')

        if oneTimeLink == "https://www.craigslist.org/about/scams?lang=en&cc=us":
            oneTimeLink = correctMessage.find_elements_by_css_selector("a")[-2].get_attribute('href')

        self.client.get(oneTimeLink)

        self.waitForCss("a")
        labelItem.find_elements_by_css_selector("a")[0].get_attribute('href')

        time.sleep(2)

        return self.client.current_url

# Test Execution
# python {{SCRIPTNAME}} "example@example.com" "password" "123-456-7890" "Bob" "Post Title" "12345" "content.txt" 3
