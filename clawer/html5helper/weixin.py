# coding=utf-8
""" weixin sdk
"""
import urllib
import json
import requests
import types
from xml.dom import minidom

from django.core.cache import cache


class Weixin:
    MSGTYPE = "MsgType"
    TOUSERNAME = "ToUserName"
    FROMUSERNAME = "FromUserName"
    CREATETIME="CreateTime"
    CONTENT="Content"
    FUNCFLAG="FuncFlag"
    Location_X = "Location_X"
    Location_Y = "Location_Y"
    Label = "Label"
    
    MSG_TEXT = "text"
    MSG_LOCATION = "location"
    
    app_id = ""
    app_secret = ""
    access_token = ""
    acess_token_expires_in = 7200
    
    
    def __init__(self, app_id, app_secret):
        self.app_id = app_id
        self.app_secret = app_secret
        #get access token now
        self.get_access_token()
            
    
    def parse_msg(self, body):
        """ parse msg of xml, return dict
        """
        result = {}
        doc = minidom.parseString(body)
        root = doc.getElementsByTagName("xml")[0]
        for item in root.childNodes:
            if item.firstChild:
                value = item.firstChild.nodeValue
            else:
                value = item.nodeValue
            result[item.nodeName] = value
        return result
    
    
    def pack_msg_text(self, data):
        """ data is dict, return string.
        Return format:
        <xml>
         <ToUserName><![CDATA[toUser]]></ToUserName>
         <FromUserName><![CDATA[fromUser]]></FromUserName>
         <CreateTime>12345678</CreateTime>
         <MsgType><![CDATA[text]]></MsgType>
         <Content><![CDATA[content]]></Content>
         <FuncFlag>0</FuncFlag>
        </xml>
        """
        doc = minidom.getDOMImplementation().createDocument(None, "xml", None)
        root = doc.documentElement
        for key, value in data.iteritems():
            node = doc.createElement(key)
            if key in [self.MSGTYPE, self.TOUSERNAME, self.FROMUSERNAME, self.CONTENT]:
                cdata = doc.createCDATASection(value)
                node.appendChild(cdata)
            else:
                node.nodeValue = value
            root.appendChild(node)
        return doc.toxml("utf-8")
    
    
    def get_access_token(self):
        """ return token string
        """
        TOKEN_CACHE = "weixin_token"
        
        self.access_token = cache.get(TOKEN_CACHE)
        if self.access_token:
            return self.access_token
        
        params = urllib.urlencode({"grant_type": "client_credential", 
                                   "appid": self.app_id,
                                   "secret": self.app_secret})
        url =  "https://api.weixin.qq.com/cgi-bin/token" + "?" + params
        resp = urllib.urlopen(url)
        result = json.loads(resp.read())
        if result.get("errcode") != None:
            raise Exception(result["errcode"])
        
        self.access_token = result["access_token"]
        self.acess_token_expires_in = result["expires_in"]
        cache.set(TOKEN_CACHE, self.access_token, self.acess_token_expires_in)
        print result
    
    
    def create_menu(self, menus):
        """ set menus
        Args:
           menus: string, its format at http://mp.weixin.qq.com/wiki/13/43de8269be54a0a6f64413e4dfa94f39.html
        """
        url = "https://api.weixin.qq.com/cgi-bin/menu/create?access_token=%s" % self.access_token
        resp = requests.post(url, data=menus.encode("utf-8"))
        
        result= resp.json()
        if result["errcode"] != 0:
            raise Exception(result["errmsg"])
        
        print result
    
    def remove_menus(self):
        url = "https://api.weixin.qq.com/cgi-bin/menu/delete?access_token=%s" % self.access_token
        resp = urllib.urlopen(url)
        result= json.loads(resp.read())
        
        if result["errcode"] != 0:
            raise Exception(result["errmsg"])
        print result
        
    def query_menu(self, token=None): 
        url = "https://api.weixin.qq.com/cgi-bin/menu/get?access_token=%s" % self.access_token
        resp = urllib.urlopen(url)
        result= json.loads(resp.read())
        
        if result.get("errcode") != None:
            raise Exception(result["errmsg"])
        print result
        
    def authorize_url(self, redirect_uri, state):
        query = {"appid": self.app_id, "redirect_uri":redirect_uri, "response_type":"code", "scope":"snsapi_base", "state":state}
        path = "https://open.weixin.qq.com/connect/oauth2/authorize"
        return "%s?%s#wechat_redirect" % (path, urllib.urlencode(query))
        
    def get_openid(self, code):
        url = "https://api.weixin.qq.com/sns/oauth2/access_token"
        query = {"appid":self.app_id, "secret":self.app_secret, "code":code, "grant_type":"authorization_code"}
        
        resp = urllib.urlopen(url+"?"+urllib.urlencode(query))
        result= json.loads(resp.read())
        
        if result.get("errcode") != None:
            raise Exception(result["errmsg"])
        print result
        
        return result["openid"]
    
    def send_template_msg(self, openid, template_id, target_url, data):
        if not (isinstance(data, types.DictType) or isinstance(data, types.DictionaryType)):
            data = json.loads(data)
            
        url = "https://api.weixin.qq.com/cgi-bin/message/template/send?access_token=%s" % self.access_token
        body = {
            "touser": openid,
            "template_id": template_id,
            "url": target_url,
            "topcolor":"#FF0000",
            "data": data
        }
        
        resp = requests.post(url, data=json.dumps(body).encode("utf-8"))
        result= resp.json()
        if result["errcode"] != 0:
            raise Exception(result["errmsg"])
        
        print result
        return result