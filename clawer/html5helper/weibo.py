#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
import urllib
import traceback
import logging
from django.utils import simplejson
from django.utils.encoding import smart_str


def get_redirect_url(appkey, redirect_url):
    url = "https://api.weibo.com/oauth2/authorize"
    params = urllib.urlencode({"client_id": appkey, 
              "response_type": "code", 
              "forcelogin": "true",
              "scope": "all",
              "redirect_uri": redirect_url})
    return url + "?" + params


def get_token(appkey, appsecret, target, code):
    """ result dict:
    { 
        "access_token": "",
        "expires_in": "",
        "uid": ""
    }
    """
    url = "https://api.weibo.com/oauth2/access_token"
    params = urllib.urlencode({"client_id": appkey, 
                               "client_secret": appsecret, 
                               "grant_type": "authorization_code", 
                               "redirect_uri": target,
                               "code": code})
    try:
        resp = urllib2.urlopen(url, params)
    except:
        logging.error(traceback.format_exc(10))
        return None
        
    result = simplejson.loads(resp.read())
    resp.close()
    return result


def get_user_info(token, uid):
    """ return json format:
    {
    "id": 1404376560,
    "screen_name": "zaku",
    "name": "zaku",
    "province": "11",
    "city": "5",
    "location": "北京 朝阳区",
    "description": "人生五十年，乃如梦如幻；有生斯有死，壮士复何憾。",
    "url": "http://blog.sina.com.cn/zaku",
    "profile_image_url": "http://tp1.sinaimg.cn/1404376560/50/0/1",
    "domain": "zaku",
    "gender": "m",
    "followers_count": 1204,
    "friends_count": 447,
    "statuses_count": 2908,
    "favourites_count": 0,
    "created_at": "Fri Aug 28 00:00:00 +0800 2009",
    "following": false,
    "allow_all_act_msg": false,
    "geo_enabled": true,
    "verified": false,
    "status": {
        "created_at": "Tue May 24 18:04:53 +0800 2011",
        "id": 11142488790,
        "text": "我的相机到了。",
        "source": "<a href="http://weibo.com" rel="nofollow">新浪微博</a>",
        "favorited": false,
        "truncated": false,
        "in_reply_to_status_id": "",
        "in_reply_to_user_id": "",
        "in_reply_to_screen_name": "",
        "geo": null,
        "mid": "5610221544300749636",
        "annotations": [],
        "reposts_count": 5,
        "comments_count": 8
    },
    "allow_all_comment": true,
    "avatar_large": "http://tp1.sinaimg.cn/1404376560/180/0/1",
    "verified_reason": "",
    "follow_me": false,
    "online_status": 0,
    "bi_followers_count": 215
    }
    """
    url = "https://api.weibo.com/2/users/show.json"
    params = urllib.urlencode({"access_token": token, "uid": uid})
    try:
        resp = urllib2.urlopen(url + "?" + params, timeout = 1)
    except:
        logging.error(traceback.format_exc())
        return {}
    result = simplejson.loads(resp.read())
    resp.close()
    return result


def get_uid(token):
    """ return uid string
    """
    url = "https://api.weibo.com/2/account/get_uid.json"
    params = urllib.urlencode({"access_token": token})
    try:
        resp = urllib2.urlopen(url + "?" + params, timeout = 1)
    except:
        logging.error(traceback.format_exc())
        return ""
    
    result = simplejson.loads(resp.read())
    resp.close()
    return result["uid"]


def update_status(token, status):
    """ return json format:
    created_at    string    微博创建时间
    id    int64    微博ID
    mid    int64    微博MID
    idstr    string    字符串型的微博ID
    ......
    """
    url = "https://api.weibo.com/2/statuses/update.json"
    params= urllib.urlencode({"access_token": token, "status": smart_str(status)})
    try:
        resp = urllib2.urlopen(url, params)
    except:
        return {}
    result = simplejson.loads(resp.read())
    resp.close()
    
    if result.get("id", None) is None:
        logging.error("update status error: %s", result)
        return {}
    return result


def short_url(token, from_url):
    url = "https://api.weibo.com/2/short_url/shorten.json"
    params = urllib.urlencode({"access_token": token, "url_long": from_url})
    try:
        resp = urllib2.urlopen(url + "?" + params, timeout = 1)
    except:
        return from_url
    result = simplejson.loads(resp.read())
    resp.close()
    return result["urls"][0]["url_short"]


def get_active_follows(token, uid, count=20):
    """ weibo returned json is:
    {
        "users": [
            {
                "id": 1404376560,
                "screen_name": "zaku",
                "name": "zaku",
                "province": "11",
                "city": "5",
                "location": "北京 朝阳区",
                "description": "人生五十年，乃如梦如幻；有生斯有死，壮士复何憾。",
                "url": "http://blog.sina.com.cn/zaku",
                "profile_image_url": "http://tp1.sinaimg.cn/1404376560/50/0/1",
                "domain": "zaku",
                "gender": "m",
                "followers_count": 1204,
                "friends_count": 447,
                "statuses_count": 2908,
                "favourites_count": 0,
                "created_at": "Fri Aug 28 00:00:00 +0800 2009",
                "following": false,
                "allow_all_act_msg": false,
                "remark": "",
                "geo_enabled": true,
                "verified": false,
                "status": {
                    "created_at": "Tue May 24 18:04:53 +0800 2011",
                    "id": 11142488790,
                    "text": "我的相机到了。",
                    "source": "<a href="http://weibo.com" rel="nofollow">新浪微博</a>",
                    "favorited": false,
                    "truncated": false,
                    "in_reply_to_status_id": "",
                    "in_reply_to_user_id": "",
                    "in_reply_to_screen_name": "",
                    "geo": null,
                    "mid": "5610221544300749636",
                    "annotations": [],
                    "reposts_count": 5,
                    "comments_count": 8
                },
                "allow_all_comment": true,
                "avatar_large": "http://tp1.sinaimg.cn/1404376560/180/0/1",
                "verified_reason": "",
                "follow_me": false,
                "online_status": 0,
                "bi_followers_count": 215
            },
            ...
        ]
    }
    """
    url = "https://api.weibo.com/2/friendships/followers/active.json"
    params = urllib.urlencode({"access_token": token, "uid": uid, "count": count})
    try:
        resp = urllib2.urlopen(url + "?" + params, timeout = 1)
    except:
        return []
    result = simplejson.loads(resp.read())
    resp.close()
    return result["users"]


def get_tags(token, uid, count = 20):
    """ Returns
    [
        {
            "name": "80后"
            "221012100001985342": "80后",
            "weight": 50
        },
        ...
    ]
    """
    url = "https://api.weibo.com/2/tags.json"
    params = urllib.urlencode({"access_token": token, "uid": uid, "count": count})
    try:
        resp = urllib2.urlopen(url + "?" + params, timeout = 1)
    except:
        return []
    result = simplejson.loads(resp.read())
    resp.close()
    return result


def friendship_create(token, uid):
    url = "https://api.weibo.com/2/friendships/create.json"
    params = urllib.urlencode({"access_token":token, "uid":uid})
    try:
        resp = urllib2.urlopen(url, params, timeout = 1)
    except:
        return None
    
    result = simplejson.loads(resp.read())
    logging.debug(result)
    resp.close()
    return result

