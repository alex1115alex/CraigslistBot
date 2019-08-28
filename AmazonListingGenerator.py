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
import requests
from amazonify import amazonify


class AmazonListingGenerator:

    #region Helper methods

    #region WaitFor methods

    def waitForName(self, name):
        for i in range(0, 30):
            #self.debug("waiting for id \"" + name + "\"...")
            if len(self.client.find_elements_by_name(name)) != 0:
                break
            time.sleep(2)

    def waitForId(self, idName):
        for i in range(0, 30):
            #self.debug("waiting for id \"" + idName + "\"...")
            if len(self.client.find_elements_by_id(idName)) != 0:
                break
            time.sleep(2)

    def waitForCss(self, css):
        for i in range(0, 30):
            #self.debug("waiting for css selector \"" + css + "\"...")
            if len(self.client.find_elements_by_css_selector(css)) != 0:
                break
            time.sleep(2)

    def waitForClass(self, className):
        for i in range(0, 30):
            #self.debug("waiting for class \"" + className + "\"...")
            if len(self.client.find_elements_by_class_name(className)) != 0:
                break
            time.sleep(2)

    #endregion

    @staticmethod
    def debug(inString):
        print(" [AMAZON] - %s" % inString.encode('utf-8').strip())

    #endregion

    def __init__(self, amazonLinksFile):
        self.display = ""

        if not os.name == 'nt':
            self.display = Display(visible=0, size=(1248, 1000))  # 800x600
            self.display.start()

        profile = webdriver.FirefoxProfile()
        profile.set_preference("browser.cache.disk.enable", False)
        profile.set_preference("browser.cache.memory.enable", False)
        profile.set_preference("browser.cache.offline.enable", False)
        profile.set_preference("network.http.use-cache", False)
        self.client = webdriver.Firefox(firefox_profile=profile)

        self.amazonLinksFile = amazonLinksFile
        self.affiliateTag = 'goodtastyfrui-20'

    def __del__(self):
        if not os.name == 'nt':
            self.display.stop()

        self.client.quit()
        return 0

    # formats an Amazon link with your affiliate tag
    def formatAmazonLink(self, link):
        formattedLink = amazonify(link, self.affiliateTag)
        # self.debug("formattedLink: " + formattedLink)
        return formattedLink

    # returns a list of Listing objects
    def generateListingList(self):
        i = 1
        listings = []
        f = open("links.txt", "r")  # open listings file
        f1 = f.readlines()
        for x in f1:  # for each link
            if("###" in x):
                break
                
            try:
                self.debug("Getting listing " + str(i) + "/" + str(len(f1) - 1))
                newListing = self.generateListing(x)  # create a new listing from that amazon link
                listings.append(newListing)  # add the listing to the list
            except:
                self.debug("Couldn't process link: " + x)
                
            i += 1

        return listings  # return the list

    # returns a Listing object constructed from an Amazon link
    def generateListing(self, amazonLink):
        title = ""
        desc = ""
        formattedLink = ""

        # self.debug("Go to Amazon link")
        self.client.get(amazonLink)

        # region Get title and description

        # self.debug("Grabbing title")
        self.waitForId("productTitle")
        title = self.client.find_element_by_id("productTitle").text

        # self.debug("Grabbing description")
        desc = self.client.find_element_by_id("productDescription").text

        # endregion

        # region Get images

        self.waitForId("imageBlock")
        imagesBlock = self.client.find_element_by_id("imageBlock")
        time.sleep(4)
        imageElementList = imagesBlock.find_elements_by_css_selector('img')

        imagePaths = []  # save all image paths here
        i = 0
        for image in imageElementList:
            if i > 8:  # don't allow more than 8 images
                break

            # self.debug("Downloading image")
            titleString = title.encode("utf-8")  # convert the title to a string
            imagePath = 'images/' + titleString[0:14] + " " + str(i) + ".png"  # specify image path
            imageSrc = imageElementList[i].get_attribute('src')  # get the image source
            #self.debug("imageSrc: " + imageSrc)
            #self.debug("imagePath: " + imagePath)

            # write the image source to the image path
            with open(imagePath, 'wb') as handle:
                response = requests.get(imageSrc, stream=True)

                if not response.ok:
                    print(response)
                for block in response.iter_content(1024):
                    if not block:
                        break

                    handle.write(block)

            i += 1
            imagePaths.append(imagePath)

        # endregion

        # region Format amazon link
        # self.debug("Formatting Amazon link: " + amazonLink)
        formattedLink = self.formatAmazonLink(amazonLink)

        # We're using amzn.pw. This site is dogshit so plan to migrate to another in the future
        # self.debug("Shortenening link, loading amzn.pw")
        self.client.get("https://amzn.pw?url=" + amazonLink)

        # Reload the hompage by clicking main logo
        self.waitForClass("mlogo")
        self.client.find_element_by_class_name("mlogo").click()
        time.sleep(2)

        # Wait for the new field and then put the link in
        self.waitForId("urlin")
        self.client.find_element_by_id("urlin").send_keys(formattedLink)
        self.client.find_element_by_id("shortenurl").click()

        # Like I said, this website is dogshit and will sometimes give us cached links.
        # Idk why running it again works... but it works. I guess.
        self.client.get("http://example.com")
        self.client.get("https://amzn.pw?url=" + amazonLink)
        self.client.find_element_by_id("urlin").send_keys(formattedLink)
        self.client.find_element_by_id("shortenurl").click()

        # page displays a QR code when complete
        self.waitForClass("qr")
        linkDiv = self.client.find_element_by_class_name("short-url")

        formattedLink = linkDiv.find_element_by_css_selector("a").get_attribute('href')
        # self.debug("newLink: " + formattedLink)

        # endregion

        newListing = Listing.Listing(title, desc, formattedLink, imagePaths)

        return newListing
