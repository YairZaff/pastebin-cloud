# -*- coding: utf-8 -*-
import requests
import binascii
import time
from datetime import datetime
import os

'''
a pastebin cloud. slow upload(not if pro-user), unlimited space.
a patebin user is a must to use the paste https request properly and to keep the data on the files uploaded.

'''

DELAY = 60 #time delay in seconds for a user between pastes, uploading pastes without a delay will result the anti-spam filter to be triggerd. which does't return any error from server, causeing pastes to be lost with out knowing.
DELAY_PRO = 1 #time delay in seconds for a pro-user between pastes (spam protection is off).

UPLOAD_LIMIT = 500*(10**3) #size limit of a single paste in bytes.
UPLOAD_LIMIT_PRO = 10*(10**4) #size limit of a single paste in bytes for pro users.


def post(url,post_args):
    try:
        #pastebin api returns an error in the format of "Bad API request, [error message]" in cases of wrong post arguments or server problems etc.
        resp = requests.post(url,data=post_args)
        content = resp.text
        #return error message for undesired response, added "Bad API request" for easier message handling.
        if(resp.status_code!=requests.codes.ok):
            content = "Bad API request, connection error,check internet connection or destination status (error: "+str(resp.status_code)+" )"
        
    except Exception as err:
        #incase of request exception(bad url,bad arguemnts, etc), added "Bad API request" for easier message handling.
        content = "Bad API request, request error,check url or args: "+str(err)
        
    return content;

def file_handle(path):
    #get file contents,return error if failed.
    try:
        file=open(path,'rb')
        #take the file contents in a binary format, and convert it to a string of hex.
        content=str(binascii.b2a_hex(file.read()))[2:-1]
        if(content==None or content==False):
            content="bad file, empty"
    except Exception as err:
        content="bad file, "+str(err)
   
    return content;

def file_create(path,cont):
    #create file, return error if failed.
    try:
        file=open(path,"wb")
        #convert the string hex that the file was originally uploaded in back to binary.
        file.write(binascii.a2b_hex(cont))
        return "created on "+path+" successfully."
    except Exception as err:
        return "can't create file at "+path+" "+str(err)
        

class Cloud:
    def __init__(self,username,password,devkey):
        self.__user=0
        self.__pswrd=0
        self.__dk=0
        self.user_key=0 #user key generated by pastebin to handle pastes and user options.
        self.file_list={} #dictionary with file names as keys, and pastebin 'paste key' as the value of that file.
        self.date_list=[] #dates of uploads in the same order of the file dictionary.
        self.__logged=False #is user logged in.
        self.__pro=0 #is user a premium user.
        self.__upload_delay=DELAY #delay needed between pastes to not get a captcha.
        self.__upload_limit=UPLOAD_LIMIT #upload limit of bytes per paste.
        self.login(username,password,devkey) #update the values above.
            
    def login(self,username,password,devkey):#login to pastebin user and generate the userkey.
        self.__user=username
        self.__pswrd=password
        self.__dk=devkey
        self.user_key = post("https://pastebin.com/api/api_login.php",{"api_dev_key":self.__dk,"api_user_name":self.__user,"api_user_password":self.__pswrd})
        if(self.user_key.find("Bad API request,")==-1):
            self.__logged=True
            self.update_list()
            user_data=post("https://pastebin.com/api/api_post.php",{"api_dev_key":self.__dk,"api_user_key":self.user_key,"api_option":"userdetails"})
            self.__pro=int(user_data[user_data.find("<user_account_type>")+19:user_data.find("</user_account_type>")]) # get from the raw XML response, data about user membership type.
            if self.__pro:
                self.__upload_delay=DELAY_PRO
                self.__upload_limit=UPLOAD_LIMIT_PRO
            else:
                self.__upload_delay=DELAY
                self.__upload_limit=UPLOAD_LIMIT
        else:
            print(self.user_key[self.user_key.find(",")+2:len(self.user_key)])
            self.__logged=False
            
    def is_logged(self):
        return self.__logged
    
    def delay(self):
        return self.__upload_delay()
    
    def update_list(self): #generate the pastes of the user into the dictionary. this data will never be updated locally to prevent errors (out of sync data with server). so we will always use this method to get the file list from the server.
        file_list_raw = post("https://pastebin.com/api/api_post.php",{"api_dev_key":self.__dk,"api_user_key":self.user_key,"api_option":"list"})
        if(file_list_raw.find("Bad API request,")==-1): 
            start=0 #the dictionary and date list will be generated from the raw XML data about the exsisting pastes.
            index=file_list_raw.find("<paste>",start)
            while(index!=-1):    
                self.file_list[file_list_raw[file_list_raw.find("<paste_title>",start)+13:file_list_raw.find("</paste_title>",start)]]=file_list_raw[file_list_raw.find("<paste_key>",start)+11:file_list_raw.find("</paste_key>",start)]
                self.date_list.append(file_list_raw[file_list_raw.find("<paste_date>",start)+12:file_list_raw.find("</paste_date>",start)])
                start=file_list_raw.find("</paste>",start)+8
                index=file_list_raw.find("<paste>",start)
        else:
            print(file_list_raw[file_list_raw.find(",")+2:len(file_list_raw)])
        
    def get_list(self): #get list in a string format 
        self.update_list()
        tmp=list(self.file_list.keys())
        for j in range(len(tmp)):
            if(tmp[j].rfind("|0")==-1):
                tmp[j]=tmp[j][0:tmp[j].rfind("|")]+str(" paste continued part - "+tmp[j][tmp[j].rfind("|")+1])
            else:
                tmp[j]=tmp[j][0:tmp[j].rfind("|0")]+str((64-len(tmp[j][0:tmp[j].rfind("|0")]))*" ")+datetime.utcfromtimestamp(int(self.date_list[j])).strftime('%Y-%m-%d %H:%M:%S')
        
        return tmp;
    
    def print_list(self):
        tmp=self.get_list()
        print("Paste(s):"+str(" "*55)+"date and time uploaded:")
        for i in range(len(tmp)):
            print(tmp[(len(tmp)-1)-i])
            
    def __upload(self,name,cont,private=0): #upload a single paste.
        if not self.date_list: #when last upload occured.
            last=0
        else:
            last=int(self.date_list[0])
        if (time.time()-last)>self.__upload_delay: # to prevent captcha and anti-spam from pastebin.
            to_upload=cont
            file_name=name
            if(str(to_upload).find("bad file,")==-1):
                resp=post("https://pastebin.com/api/api_post.php",{"api_dev_key":self.__dk,"api_user_key":self.user_key,"api_option":"paste","api_paste_private":private,"api_paste_name":file_name,"api_paste_expire_date":"N","api_paste_code":to_upload})
                if(resp.find("Bad API request,")==-1):
                    print("uploaded successfully.")
                    return True
                else:
                    print(resp[resp.find(",")+2:len(resp)])
            else:
                to_upload=str(to_upload)
                print(to_upload[to_upload.find(",")+2:len(to_upload)])
        else:
            print("can't upload, delay cool down left: "+str(self.__upload_delay-(time.time()-last))+" seconds")
        return False
    
    def upload(self,file_path,name=None,private=0): #takes a file and dissects it into mulitple pastes, uploading them.
         self.update_list()
         if name==None:
             file_name=file_path[file_path.rfind("/")+1:len(file_path)]
         else:
             file_name=name
         if file_name+"|0" in self.file_list:
             print("can't have colliding names on the cloud,("+file_name+") change name of uploaded file or change name on cloud.")
         else:
             to_upload=file_handle(file_path)
             parts=int(len(to_upload)/(self.__upload_limit))
             print(file_name+" consists of "+str(len(to_upload))+" byte(s). (after hex conversion)")
             print("limit per paste of "+str(self.__upload_limit)+" byte(s).")   
             print("required delay between pastes: "+str(self.__upload_delay)+" second(s).")
             print("uploading "+file_path+" in "+str(parts+1)+" paste(s):")
             print("estimated upload time: "+str((parts)*self.__upload_delay+(parts+1))+" second(s).")
             i=0
             for i in range(parts):
                 print("part - "+str(i+1))
                 if not self.__upload(file_name+"|"+str(i),to_upload[(self.__upload_limit)*i:(self.__upload_limit)*(i+1)],private):
                     return False
                 print("waiting "+str(self.__upload_delay)+" seconds (delay between pastes to prevent anti-spam protection).")
                 time.sleep(self.__upload_delay) #wait the given delay
             if(i!=0):
                 i+=1
             print("part - "+str(i+1))
             ret=self.__upload(file_name+"|"+str(i),to_upload[(self.__upload_limit)*i:len(to_upload)],private)
             self.update_list()
             return ret
         
    def __download(self,file_name,num): #gets and returns combined content of all pastes assoicated with a name in thier indexed order, starting from 0 (num).
        if file_name+"|"+str(num) in self.file_list:
            key=self.file_list[file_name+"|"+str(num)]
            content=post("https://pastebin.com/api/api_raw.php",{"api_dev_key":self.__dk,"api_user_key":self.user_key,"api_option":"show_paste","api_paste_key":key})
            if(content.find("Bad API request,")==-1):
                print("downloaded paste "+str(num+1)+".")
                if file_name+"|"+str(num+1) in self.file_list:
                    return (content+self.__download(file_name,num+1))
                else:
                    return content
            else:
                print(content[content.find(",")+2:len(content)])
        else:
            print("couldn't find "+file_name+".")
        return None
    
    def download(self,file_name,path=os.getcwd()): #downloads a file to a given (optional) path.
        self.update_list()
        print("downloading "+file_name+".")
        content=self.__download(file_name,0)
        print(file_create(path+file_name,content))
        
    def __delete(self,file_name,num):#deletes all pastes associated with a name, from a given index  (num).
        if file_name+"|"+str(num) in self.file_list:
            key=self.file_list[file_name+"|"+str(num)]
            resp=post("https://pastebin.com/api/api_post.php",{"api_dev_key":self.__dk,"api_user_key":self.user_key,"api_paste_key":key,"api_option":"delete"})
            if(resp.find("Bad API request,")==-1):
                print(file_name+" deleted successfully paste part: "+str(num+1)+".")
                if file_name+"|"+str(num+1) in self.file_list:
                    self.__delete(file_name,num+1)
            else:
                print(resp[resp.find(",")+2:len(resp)])
        else:
            print("couldn't find "+file_name+".")
            
    def delete(self,file_name,default_start=0):
        self.update_list()
        print("deleting "+file_name+" starting from instance "+str(default_start)+".")
        self.__delete(file_name,default_start)
        time.sleep(1) #to compensate server delay on updateing the data.
        self.update_list()
    
