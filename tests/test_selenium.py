import os
import sys
import re
import unittest
from time import sleep
from random import sample
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import ElementNotInteractableException, NoSuchElementException, StaleElementReferenceException, WebDriverException
from flask import url_for
from app import create_app, db
from app.models import User, Role, Post

class FlaskClientTestCase(unittest.TestCase):
    client = None

    @classmethod
    def setUpClass(cls):
        # start Firefox
        try:
            cls.client = webdriver.Firefox()
        except:
            pass

        # skip these tests if the browser could not be started
        if cls.client:
            # create the application
            cls.app = create_app('testing')
            cls.app_context = cls.app.app_context()
            cls.app_context.push()

            # suppress logging to keep unittest output clean
            import logging
            logger = logging.getLogger('werkzeug')
            logger.setLevel("ERROR")

            # create the database and populate with some fake data
            db.create_all()

            # start the Flask server in a thread
            threading.Thread(target=cls.app.run).start()

            # give the server a second to ensure it is up
            time.sleep(1) 

    @classmethod
    def tearDownClass(cls):
        if cls.client:
            # stop the flask server and the browser
            cls.client.get('http://127.0.0.1:5000/shutdown')
            cls.client.close()

            # destroy database
            db.drop_all()
            db.session.remove()

            # remove application context
            cls.app_context.pop()

    def setUp(self):
        if not self.client:
            self.skipTest('Web browser not available')

    def tearDown(self):
        pass
    

    def check_exists_by_id(self, driver, id):
        try:
            postElem = driver.find_element_by_id(id)
            print type(postElem)
        except NoSuchElementException:
            print 'NoSuchElementException'
            return False

        print 'return:', True
        return True 

    #python fbLogin.py <broswer(String) <is_fb(bool)> <count(no of messages)>
    def get_browser(self, type_of_browser, url_name):
        if (type_of_browser == 'Chrome'):
            driver = webdriver.Chrome()
        elif (type_of_browser == 'FireFox'):
            driver = webdriver.Firefox()
        else:
            return None

        driver.get(url_name)
        print driver.title
        return driver

    def get_url(self, driver):
        return driver.current_url

    def goToHome(self, driver):
        homeElem = driver.find_element_by_id("home-btn")
        homeElem.click()
        sleep(3)

    def goToPost(self, driver, elem):
        elem.click()
        sleep(5)
        print 'current_url: ', driver.current_url
        return driver.current_url

    def goToFb(self, driver):
        fbPageElem = driver.find_element_by_id("fbpage-link")
        sleep(5)
        fbPageElem.click()
        sleep(10)
        urlFb = get_url(driver)
        driver.back()
        sleep(10)
        print 'urlFb', urlFb
        return urlFb

    def goToTw(self, driver):
        twPageElem = driver.find_element_by_id("twpage-link")
        sleep(5)
        twPageElem.click()
        sleep(10)
        urlTw = get_url(driver)
        driver.back()
        sleep(10)
        print 'urlTw', urlTw
        return urlTw

    def goToYtube(self, driver):
        yTubePageElem = driver.find_element_by_id("ytubepg-link")
        sleep(5)
        yTubePageElem.click()
        sleep(10)
        urlyTube = get_url(driver)
        driver.back()
        sleep(10)
        print 'urlYt', urlyTube
        return urlyTube

    def goToFbShrBtn(self, driver):
        mnWdwHdl = driver.current_window_handle

        fbShrBtnElem = driver.find_element_by_id("fb-shareBtn")
        sleep(5)
        fbShrBtnElem.click()
        sleep(5)
        fbWdwHdl = None
        while not fbWdwHdl:
            for handle in driver.window_handles:
                if handle != mnWdwHdl:
                    fbWdwHdl = handle
                    break
                   
        
        driver.switch_to.window(fbWdwHdl)
        sleep(5)
        postElm = driver.find_element_by_id("u_0_1w")
        sleep(5)
        postElm.click()
        sleep(5)
        driver.switch_to.window(mnWdwHdl)

    def goToTwShrBtn(self, driver):
        mnWdwHdl = driver.current_window_handle

        twShrBtnElem = driver.find_element_by_id("tw-shareBtn")
        sleep(5)
        twShrBtnElem.click()
        sleep(5)
        twWdwHdl = None
        while not twWdwHdl:
            for handle in driver.window_handles:
                if handle != mnWdwHdl:
                    twWdwHdl = handle
                    break
                   
        
        driver.switch_to.window(twWdwHdl)
        sleep(5)
        postElm = driver.find_element_by_css_selector("#update-form > div.ft > fieldset.submit > input.button.selected.submit")
        sleep(5)
        postElm.click()
        sleep(5)
        driver.switch_to.window(mnWdwHdl)
        twUrl = get_url(driver)
        print twUrl

    def get_loginElem(self, driver):
        loginElement = driver.find_element_by_id("signin-btn")
        return loginElement

    def get_logoutElem(self, driver):
        logoutElement = driver.find_element_by_id("signout-btn")
        return logoutElement

    def logout(self, driver):
        logoutElement = self.get_logoutElem(driver)
        logoutElement.click()
        sleep(3)
        
    def fb_login(self, driver):
        loginElement = self.get_loginElem(driver)
        sleep(5)
        loginElement.click()
        sleep(5)
        fbElement = driver.find_element_by_id("fb-login-btn")
        sleep(5)
        fbElement.click()
        sleep(5)

        if (self.check_exists_by_id(driver, "signout-btn") == True):
            print 'found element for signout'
            sleep(5)
            return

        fbUser = driver.find_element_by_css_selector('#email')
        sleep(5)
        fbUser.send_keys(os.environ.get('FB_UNAME'))
        sleep(5)
        fbPwd = driver.find_element_by_css_selector('#pass')
        sleep(5)
        fbPwd.send_keys(os.environ.get('FB_PWD'))
        sleep(5)
        login = driver.find_element_by_id('loginbutton')
        sleep(5)
        login.click()
        sleep(3)

    def tw_login(self, driver):
        loginElement = self.get_loginElem(driver)
        sleep(5)
        loginElement.click()
        sleep(5)
        twElement = driver.find_element_by_id("tw-login-btn")
        sleep(5)
        twElement.click()
        sleep(5)

        if (self.check_exists_by_id(driver, "username_or_email") == False):
            print 'found element for signout'
            sleep(5)
            authorizeElem = driver.find_element_by_id('allow')
            authorizeElem.click()
            sleep(3)
            return

        twUser = driver.find_element_by_id('username_or_email')
        sleep(5)
        twUser.send_keys(os.environ.get('TW_UNAME'))
        sleep(5)
        twPwd = driver.find_element_by_id('password')
        sleep(5)
        twPwd.send_keys(os.environ.get('TW_PWD'))
        sleep(5)
        login = driver.find_element_by_id('allow')
        login.click()
        sleep(3)

    def post_now_running(self, driver):
        nowRunning = driver.find_element_by_id("mainPost")
        nowRunning.click()  
        sleep(3)

    def generate_fake_comment(self, count=1):
        from random import seed, sample
        from forgery_py.forgery.lorem_ipsum import paragraphs 

        comments = []
        seed()
        for i in range(count):
            length = sample(range(1, 1000), 1)
            comments.append(paragraphs())

        return comments

    def generate_fake_name(self, count=1):
        from forgery_py.forgery.name import full_name
        name = []
        name = full_name()
        fullName = ''.join(name)
        print 'fullName', fullName
        return fullName 

    def postName(self, driver, name):
        nameFldElem = driver.find_element_by_xpath('//*[@id="inputId"]')
        sleep(5)
        nameFldElem.send_keys(name)
        sleep(2)
        
    def postComment(self, driver, comment, signedIn):
        sleep(5)
        if (signedIn == True):
            textFldElem = driver.find_element_by_xpath('//*[@id="textIdwithUser"]')
            textFldElem.send_keys(comment)
            submitElem = driver.find_element_by_xpath('//*[@id="submitWithOutName"]')
        else:
            textFldElem = driver.find_element_by_xpath('//*[@id="textIdwithOutUser"]')   
            textFldElem.send_keys(comment)
            submitElem = driver.find_element_by_xpath('//*[@id="submitWithName"]')    

        sleep(5)
        submitElem.click()
        sleep(5)

    def postCommentWithSignIn(self, driver, count):
        comments = self.generate_fake_comment(count)
        for comment in comments:
            print 'comment', comment
            self.postComment(driver, comment, True)
            sleep(5)

    def postCommentWithOutSignIn(self, driver, count=1):
        for i in count:
            name = self.generate_fake_name(count)
            comment = self.generate_fake_comment(count)
            print 'name', name
            print 'comment', comment
            self.postName(driver, name)
            self.postComment(driver, comment, False)
            sleep(5)

    def enterPost(self, driver, elm, postId):
        id = "post-" + str(postId)
        print 'id:', id
        while True:
            elm.send_keys(Keys.PAGE_DOWN)
            print 'Page DWN'

            postElem = self.check_exists_by_id(driver, id)
            if postElem == False:
                sleep(2)
                continue

            try:
                postElem.click()
                print 'clicked page'
                sleep(10)
            except ElementNotInteractableException:
                print 'NonInteractable exception'
                sleep(2)
                continue

            break

        self.goToHome(driver)

    def walkPosts(self, driver, is_signedin, count):
        baseUrl = "http://127.0.0.1:5000"

        elm = driver.find_element_by_id('header')
        i = 0

        try:
            elems = driver.find_elements_by_class_name("effect-marley")
        except NoSuchElementException:    
            elm.send_keys(Keys.PAGE_DOWN)
            print 'NoSuchElementException exception'

        print 'elems len-', len(elems)
        for j, elem in enumerate(elems):
            print 'j=', j
            print 'elem=', type(elem)

        j = 0
        while j < len(elems):
            try:
                elems[j].click()
                sleep(5)
            except StaleElementReferenceException:
                print 'j', j
                sleep(5)
            except NoSuchElementException:
                print 'NoSuchElementException exception'

            if (is_signedin == True):
                self.postCommentWithSignIn(browser, count)
            else:
                self.postCommentWithOutSignIn(browser, count)                         

            driver.back()
            sleep(5)
            elems = driver.find_elements_by_class_name("effect-marley")
            j = j+1
            sleep(5)
            
        sleep(5)

    def walkPagination(self, driver, direction, is_signedin, count):
        paginationElems = driver.find_elements_by_xpath('/html/body/div[6]/div/ul/li[*]/a')
        
        print 'direction', direction
        print 'elems ', len(paginationElems)
        rand_numbers = count + 1
        if direction == 0:
            i = 0   
        
            while (i < len(paginationElems)):
                paginationElems[i].click()

                sleep(5)
                
                self.walkPosts(driver, is_signedin, rand_numbers)
                i = i+1
                paginationElems = driver.find_elements_by_xpath('/html/body/div[6]/div/ul/li[*]/a')
                print 'i=', i            
                sleep(5)
        else:
            i = len(paginationElems) - 1

            while (i >= 0):
                paginationElems[i].click()

                sleep(5)
                self.walkPosts(driver, is_signedin, rand_numbers)
                i = i - 1
                paginationElems = driver.find_elements_by_xpath('/html/body/div[6]/div/ul/li[*]/a')
                print 'i=', i
                sleep(5)      
     
    def walkRelatedPosts(self, driver, postPath, is_signedin, count):
        relatedPostElems = driver.find_elements_by_class_name('portfolio-item')

        no_of_elems = len(relatedPostElems)
        print 'no_of_elems:', no_of_elems
        
        count = count + 1
        i = 0
        while (i < no_of_elems):
            url_of_post = self.goToPost(driver, relatedPostElems[i])

            driver.back()
            sleep(5)
            if postPath == url_of_post:
                print 'Error: Same post'

            if (is_signedin == True):
                self.postCommentWithSignIn(browser, count)
            else:
                self.postCommentWithOutSignIn(browser, rand_numbers)

            relatedPostElems = driver.find_elements_by_class_name('portfolio-item')
            sleep(5)
        i = i + 1

    def test_tactification(self):
        for case in range(1,20):
            print 'CASE:', case
            if (case == 1):
                print "This case is to enter into main post with fb and add comments"
                self.fb_login(browser)
                self.post_now_running(browser)
                self.postCommentWithSignIn(browser, count)
                self.logout(browser)
                self.goToHome(browser)
            elif (case == 2):
                print "This case is to enter into all posts by walking pages with fb and add comments"
                self.fb_login(browser)
                #fb in descending order
                self.walkPagination(browser, 0, 1, 1)
                self.logout(browser)
                self.goToHome(browser)
            elif (case == 3):
                print 'covered in case 1'
            elif (case == 4):
                print 'walk on related posts with fb signin'
                self.fb_login(browser)
                post_number = sample(range(1, no_of_posts), 1)
                comment_cnt = sample(range(1, 5), 1)
                post_url = "http://127.0.0.1:5000/post/" + str(post_number[0])
                print post_url
                browser.get(post_url)
                sleep(5)
                #related posts
                self.walkRelatedPosts(browser, post_url, 1, 1)
                self.logout(browser)
                self.goToHome(browser)   
            elif (case == 5): 
                print 'enter into main post in case 5, call back in case 6 after posting comment, call forward in case 6 and post comment'
                #5, 6, 7 executes together. No clean up needed in 5.
                self.fb_login(browser)
                self.post_now_running(browser)
                self.postCommentWithSignIn(browser, 1)
            elif (case == 6):
                browser.back()
                sleep(3)
                self.post_now_running(browser)
                self.postCommentWithSignIn(browser, 1)
            elif (case == 7):
                browser.back()
                sleep(3)
                browser.forward()
                self.postCommentWithSignIn(browser, 1)
                self.logout(browser)
                self.goToHome(browser)
            elif (case == 8):
                print 'Go to FB page for tactification with FB login'
                self.fb_login(browser)
                self.goToFb(browser)
                self.logout(browser)
            elif (case == 9):
                print 'Go to Tw page for tactification with FB login'
                self.fb_login(browser)
                goToTw(browser)
                self.logout(browser)
            elif (case == 10):
                print 'Try sharing in FB with FB login'
                self.fb_login(browser)
                post_number = sample(range(1, no_of_posts), 1)
                post_url = "http://127.0.0.1:5000/post/" + str(post_number[0])
                print post_url
                browser.get(post_url)
                sleep(5)
                self.goToFbShrBtn(browser)
                self.logout(browser)
            elif (case == 11):
                print 'Try sharing in TW with FB login'
                self.fb_login(browser)
                post_number = sample(range(1, no_of_posts), 1)
                post_url = "http://127.0.0.1:5000/post/" + str(post_number[0])
                print post_url
                self.goToTwShrBtn(browser)
                self.logout(browser)
            if (case == 12):
                print 'Tw login and post comment in main post'
                self.tw_login(browser)
                self.post_now_running(browser)
                self.postCommentWithSignIn(browser, count)
                self.logout(browser)
                self.goToHome(browser)
            elif (case == 13):
                print 'Tw login and walk through all posts'
                self.tw_login(browser)
                #fb in descending order
                self.walkPagination(browser, 0, 1, 1)
                self.logout(browser)
                self.goToHome(browser)
            elif (case == 14):
                print 'case 12 and 14 are same'
            elif (case == 15):
                print 'enter a random page and signin with tw and post comment'
                self.tw_login(browser)
                post_number = sample(range(1, no_of_posts), 1)
                comment_cnt = sample(range(1, 5), 1)
                post_url = "http://127.0.0.1:5000/post/" + str(post_number[0])
                print post_url
                browser.get(post_url)
                #related posts
                self.walkRelatedPosts(browser, post_url, 1, 1)
                self.logout(browser)
                self.goToHome(browser)   
            elif (case == 16): 
                print 'enter into main post in case 17, call back in case 18 after posting comment, call forward in case 19 and post comment'
                #5, 6, 7 executes together. No clean up needed in 5.
                self.tw_login(browser)
                self.post_now_running(browser)
                self.postCommentWithSignIn(browser, 1)
            elif (case == 17):
                browser.back()
                sleep(3)
                self.post_now_running(browser)
                self.postCommentWithSignIn(browser, 1)
            elif (case == 18):
                browser.back()
                sleep(3)
                browser.forward()
                self.postCommentWithSignIn(browser, 1)
                self.logout(browser)
                self.goToHome(browser)
            elif (case == 19):
                print 'tw login and enter fb page'
                self.tw_login(browser)
                self.goToFb(browser)
                self.logout(browser)
            elif (case == 20):
                print 'tw login and enter tw page'
                self.tw_login(browser)
                goToTw(browser)
                self.logout(browser)
            elif (case == 21):
                print 'enter random post and opt for fb shr button'
                self.tw_login(browser)
                post_number = sample(range(1, no_of_posts), 1)
                post_url = "http://127.0.0.1:5000/post/" + str(post_number[0])
                print post_url
                browser.get(post_url)
                self.goToFbShrBtn(browser)
                self.logout(browser)
            elif (case == 22):
                print 'enter random post and opt for tw shr button'
                self.tw_login(browser)
                post_number = sample(range(1, no_of_posts), 1)
                post_url = "http://127.0.0.1:5000/post/" + str(post_number[0])
                print post_url
                browser.get(post_url)
                self.goToTwShrBtn(browser)
                self.logout(browser)
            elif (case == 23):
                print 'enter into a pg and login to fb, comment'
                post_number = sample(range(1, no_of_posts), 1)
                post_url = "http://127.0.0.1:5000/post/" + str(post_number[0]) 
                print post_url
                broswer.get(post_url)
                self.fb_login(browser)
                self.postCommentWithSignIn(browser, count)
                self.logout(broswer)
                self.goToHome(broswer)
            elif (case == 24):
                print 'enter into a pg and login to tw, comment'
                post_number = sample(range(1, no_of_posts), 1)
                post_url = "http://127.0.0.1:5000/post/" + str(post_number[0]) 
                print post_url
                broswer.get(post_url)
                self.tw_login(browser)
                self.postCommentWithSignIn(browser, count)
                self.logout(broswer)
                self.goToHome(broswer)  
            elif (case == 25):
                print 'enter into page and go to FB page for tactification'
                post_number = sample(range(1, no_of_posts), 1)
                post_url = "http://127.0.0.1:5000/post/" + str(post_number[0])         
                print post_url
                broswer.get(post_url)
                self.goToFb(browser)
                self.goToHome(browser)
            elif (case == 26):
                print 'enter into page, and go to tw page for tactification'
                post_number = sample(range(1, no_of_posts), 1)
                post_url = "http://127.0.0.1:5000/post/" + str(post_number[0])        
                print post_url
                broswer.get(post_url)
                self.tw_login(browser)
                self.logout(browser)
            elif (case == 27):
                print 'comment without signin'
                self.post_now_running(browser)
                self.postCommentWithOutSignIn(browser, 1, count)
                self.goToHome(browser)     
            elif (case == 28):
                print 'walk all pages without signin'
                self.post_now_running(browser)
                self.walkPagination(browser, 0, 1, 1)
                self.goToHome(browser)  
            elif (case == 29):
                print 'walk related pages without signin'
                post_number = sample(range(1, no_of_posts), 1)
                post_url = "http://127.0.0.1:5000/post/" + str(post_number[0])        
                print post_url
                browser.get(post_url)
                sleep(5)
                self.walkRelatedPosts(browser, post_url, 0, 1)
                self.goToHome(browser)  
            elif (case == 30): 
                print 'enter into main post in case 30, call back in case 31 after posting comment, call forward in case 32 and post comment'
                #31, 32, 33 executes together. No clean up needed in 5.
                self.fb_login(browser)
                self.post_now_running(browser)
                self.postCommentWithSignIn(browser, 1)
            elif (case == 31):
                browser.back()
                sleep(3)
                self.post_now_running(browser)
                self.postCommentWithOutSignIn(browser, 1)
                self.goToHome(browser)
            elif (case == 33):
                browser.back()
                sleep(3)
                browser.forward()
                self.postCommentWithOutSignIn(browser, 1)
                self.goToHome(browser)    
            elif (case == 34):
                print 'go to fb page without signin in homw page'
                self.goToFb(browser)
            elif (case == 35):
                print 'go to tw page withoug signin in home page'
                goToTw(browser)
            elif (case == 34):
                print 'go to a post and click fb shr btn'
                post_number = sample(range(1, no_of_posts), 1)
                post_url = "http://127.0.0.1:5000/post/" + str(post_number[0])
                print post_url
                browser.get(post_url)
                sleep(5)
                self.goToFbShrBtn(browser)
            elif (case == 35):
                print 'go to a post and click tw shr btn'
                post_number = sample(range(1, no_of_posts), 1)
                post_url = "http://127.0.0.1:5000/post/" + str(post_number[0])
                browser.get(post_url)
                sleep(5)
                self.goToTwShrBtn(browser)
