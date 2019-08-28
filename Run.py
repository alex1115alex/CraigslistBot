#!/usr/bin/env python

# Developed by Alex Israelov
# Alex Enterprise

import argparse
import os
import time
import shutil
import Listing
import AmazonListingGenerator
import CraigslistBot


class Run:

    @staticmethod
    def debug(inString):
        print(" [LOG] [RUNNER] - %s" % inString.encode('utf-8').strip())

    @staticmethod
    def wipeimagesfolder():
        # delete the images folder
        shutil.rmtree('images')
        # and recreate it
        os.mkdir('images')
    
    @staticmethod
    def printmenu():
        print("CraigslistBot with Amazon by Alex Israelov")
        print("===Main Menu===")
        print("1. Initialize listings from Amazon links file")
        print("2. Initialize listings from listings content file")
        print("3. Login to Craigslist")
        print("4. Batch post listings")
        print("5. Do everthing (Amazon)")
        print("6. Save listings list to content file")
        print("7. Quit")

    def __init__(self, protonLogin="", protonPassword="", loginEmail="", loginPass="", contactNumber="", contactName="",
                 postCode="", listingsFile="", waitTime=10, waitTimeBetweenPosts=30):
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
        self.listingsList = []
        self.loggedIn = False

        self.clBot = CraigslistBot.CraigslistBot(protonLogin, protonPassword, loginEmail, loginPass, contactNumber,
                                        contactName, postCode, listingsFile, waitTime, waitTimeBetweenPosts)

        Run.wipeimagesfolder()

    # fills the listingList with listings derived from Amazon links
    def populatelistingslistfromamazonlinksfile(self):
        Run.debug("Populating listings from Amazon links...")
        startExecTime = time.time()
        amazonGenerator = AmazonListingGenerator.AmazonListingGenerator(self.listingsFile)
        self.listingsList = amazonGenerator.generateListingList()
        Run.debug("Complete!\nExecution time: %s seconds" % int(time.time() - startExecTime))
        return

    # post all listings in the listingsList array. Return a list of craigslist post links
    def postAllListings(self):
        Run.debug("Post each listing...")
        startExecTime = time.time()
        craigslistPostLinks = []
        i = 0
        for listing in self.listingsList: # for each listing
            Run.debug("Posting ad (" + str(i) + "/" + str(len(self.listingsList) - 1) + "): " + listing.name) #print which listing it is
            try:
                postLink = self.clBot.createpost(listing) # post the listing
                craigslistPostLinks.append(postLink) # add the link to the list
            except:
                Run.debug("Post listing " + listing.name + " failed for some reason")

            if i == len(self.listingsList) - 1: # if this is the last listing then end the loop
                break

            i += 1
            #time.sleep(self.waitTimeBetweenPosts)  # do this for less chance of getting noticed by spam filter

        Run.debug("Complete!\nExecution time: %s seconds" % int(time.time() - startExecTime))
        return craigslistPostLinks

    # reads the listing file and populates listingsList with its information
    def populatelistingslistfromfile(self, listingsFilePath):
        listings = []

        name = ""
        desc = ""
        link = ""
        imagePaths = []

        # read listings from file
        f = open(listingsFilePath, "r")
        f1 = f.readlines()
        i = 0
        looking = 0  # 0 = name, 1 = desc, 2 = link

        for x in f1:
            if x in ["\n", "\r\n"]:
                continue

            if x.__contains__("Name="):
                looking = 0
                if len(listings) != 0:
                    myListing = Listing(name, desc, link, imagePaths)
                    listings.append(myListing)
                    name = ""
                    desc = ""
                    link = ""
                    imagePaths = []

                continue
            if x.__contains__("Desc="):
                looking = 1
                continue
            if x.__contains__("Link="):
                looking = 2
                continue
            if x.__contains__("Images="):
                looking = 3
            if x.__contains__("###"):
                break

            if looking == 0:
                name += x
            if looking == 1:
                desc += x
            if looking == 2:
                link = x  # assume links are 1 line only
            if looking == 3:
                imagePaths.append(x)

        f.close()
        self.listingsList = listings
        return


def main(protonLogin, protonPassword, loginEmail, loginPass, contactNumber, contactName, postCode,
        listingsFile, waitTime, waitTimeBetweenPosts): 

        runner = Run(protonLogin, protonPassword, loginEmail, loginPass, contactNumber, contactName, postCode, listingsFile, waitTime, waitTimeBetweenPosts)

        j = -1
        while(j != 7):
            Run.printmenu()

            j = int(raw_input("Enter an option: "))

            if(j == 1):
                runner.populatelistingslistfromamazonlinksfile()
            if(j == 2):
                runner.populatelistingslistfromfile()
            if(j == 3):
                runner.clBot.login()
            if(j == 4):
                runner.postAllListings()
            if(j == 5):
                runner.populatelistingslistfromamazonlinksfile()
                runner.clBot.login()
                runner.postAllListings()
            if(j == 6):
                Run.debug("unimplemented feature")
            if(j == 7):
                Run.debug("Goodbye!")
            else:
                Run.debug("Invalid input")

        return 0


parser = argparse.ArgumentParser(description="Craigslist Poster Script")

parser.add_argument('protonLogin', metavar='PROTONLOGIN', type=str, help='memes')
parser.add_argument('protonPassword', metavar='PROTONPASSWORD', type=str, help='memes')

parser.add_argument('loginEmail', metavar='LOGINEMAIL',
                    type=str, help='Email to use for login')
parser.add_argument('loginPass', metavar='LOGINPASS',
                    type=str, help='Password to use for login')

parser.add_argument('contactNumber', metavar='CONTACTNUM',
                    type=str, help='Contact number for post')
parser.add_argument('contactName', metavar='CONTACTNAME', type=str, help='Contact name for post')

parser.add_argument('postCode', metavar='POSTCODE', type=str, help='Zip code for post')

parser.add_argument('listingsFile', metavar='LISTINGSFILE', type=str, help='Path to file for listngs')

parser.add_argument('waitTime', metavar='WAITTIME', type=int,
                    help='Time to wait in between actions (Recommend 3)')

parser.add_argument('waitTimeBetweenPosts', metavar='WAITTIMEBETWEENPOSTS', type=int, help='Wait time between posting')

args = parser.parse_args()
main(args.protonLogin, args.protonPassword, args.loginEmail, args.loginPass, args.contactNumber, args.contactName,
      args.postCode, args.listingsFile, args.waitTime, args.waitTimeBetweenPosts)
#main()

# Test Execution
# python {{SCRIPTNAME}} "example@example.com" "password" "123-456-7890" "Bob" "Post Title" "12345" "content.txt" 3
