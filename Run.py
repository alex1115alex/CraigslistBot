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

        self.locationCode = "lax"


def main(protonLogin, protonPassword, loginEmail, loginPass, contactNumber, contactName, postCode,
         listingFile, waitTime, waitTimeBetweenPosts):
    startExecTime = time.time()

    print("protonLogin: " + protonLogin)
    print("protonPassword: " + protonPassword)
    print("loginEmail: " + loginEmail)
    print("loginPass: " + loginPass)
    print("contactNumber: " + contactNumber)
    print("contactName: " + contactName)
    print("postCode: " + postCode)
    print("listingFile: " + listingFile)
    print("waitTime: " + str(waitTime))
    print("waitTimeBetweenPosts: " + str(waitTimeBetweenPosts))

    amazonGenerator = AmazonListingGenerator.AmazonListingGenerator(listingFile)

    clBot = CraigslistBot.CraigslistBot(protonLogin, protonPassword, loginEmail, loginPass, contactNumber,
                                        contactName, postCode, listingFile, waitTime, waitTimeBetweenPosts)

    # listingsList = clBot.initializelistings(listingFile)
    listingsList = amazonGenerator.generateListingList()

    Run.debug("Execute login")
    clBot.login()

    craigsListPostLinks = []

    Run.debug("Post each listing...")
    i = 0
    for listing in listingsList:
        Run.debug("Posting ad:")
        print(listing.tostring())
        try:
            postLink = clBot.createpost(listing)
            craigsListPostLinks.append(postLink)
        except:
            Run.debug("Post listing " + listing.name + "failed for some reason")

        if i == len(listingsList) - 1:
            break

        i += 1
        time.sleep(waitTimeBetweenPosts)  # do this for less chance of getting noticed by spam filter

    # delete the images folder
    shutil.rmtree('images')
    # and recreate it
    os.mkdir('images')

    endExecTime = time.time()

    Run.debug("Execution time: %s seconds" % int(endExecTime - startExecTime))
    Run.debug("Completed all tasks")

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

# Test Execution
# python {{SCRIPTNAME}} "example@example.com" "password" "123-456-7890" "Bob" "Post Title" "12345" "content.txt" 3
