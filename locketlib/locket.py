import requests
import json
from uuid import uuid4
from random import randint
from locketlib.converter import image_to_webp


API_KEY = "AIzaSyB5dTd-xiLD5dEfWq5OpptnQtnMpE0W0u8"
ANDROID_CERT = "187A27D3D7364A044307F56E66230F973DCCD5B7"
FIREBASE_CLIENT_CERT = "H4sIAAAAAAAAAKtWykhNLCpJSk0sKVayio7VUSpLLSrOzM9TslIyUqoFAFyivEQfAAAA"
LOGIN_API = f"https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key={API_KEY}"
STORY_API = "https://api.locketcamera.com/getLatestMomentV2"
UPLOAD_API = "https://firebasestorage.googleapis.com/v0/b/locket-img/o?name=users/<local_id>/moments/thumbnails/<img_name>&uploadType=resumable"
POST_UPLOAD_API = "https://api.locketcamera.com/postMomentV2"


class Locket:

    def __init__(self, email : str, password : str) -> None:
        self.tokenID = ""
        self.random_device_id = str(uuid4())
        self.random_session_id = randint(1000000000000, 9999999999999)
        self.user_data = self.set_IDtoken(email, password)
        


    def is_logged_in(self) -> bool:
        if self.tokenID == "":
            return False
        return True



    def set_IDtoken(self, email : str, password : str) -> None:
        headers = {
            "content-type": "application/json",
            "x-android-package": "com.locket.Locket",
            "x-android-cert": ANDROID_CERT,
            "x-firebase-client": FIREBASE_CLIENT_CERT,
            "host": "www.googleapis.com",
        }
        data = {
            "email": email,
            "password": password,
            "returnSecureToken": "true",
        }
        r = requests.post(LOGIN_API, headers=headers, json=data)
        resp = json.loads(r.text)
        self.tokenID = resp["idToken"]
        return resp



    def get_latest_moment(self):
        headers = {
            "authorization": f"Bearer {self.tokenID}",
            "content-type": "application/json; charset=utf-8",
            "host": "api.locketcamera.com",
        }
        data = '{"data":{"analytics":{"platform":"android","amplitude":{"device_id":"' + \
                self.random_device_id + '","session_id":' + str(self.random_session_id) + \
                '}},"should_count_missed_moments":true,"last_fetch":1}}'
        
        r = requests.post(STORY_API, headers=headers, data=data)
        return r.json()
    


    def get_localID(self) -> str:
        return self.user_data["localId"]



    def get_upload_URL(self, filename : str, image_content_type : str) -> str:
        querystring = {
            "name": f"users/{self.get_localID()}/moments/thumbnails/{filename}",
            "uploadType": "resumable",
        }
        payload = {"contentType": image_content_type, "cacheControl": "public, max-age=604800"}
        headers = {
            "authorization": f"Firebase {self.tokenID}",
            "x-goog-upload-command": "start",
            "x-goog-upload-protocol": "resumable",
            "x-goog-upload-header-content-type": image_content_type,
            "content-type": "application/json",
            "host": "firebasestorage.googleapis.com",
        }
        r = requests.post(
            UPLOAD_API.replace("<local_id>", self.get_localID()).replace("<img_name>", filename),
            params=querystring,
            headers=headers,
            json=payload
        )
        return r.headers["X-Goog-Upload-Control-URL"].replace("%2F", "/")



    def upload_image(self, filepath : str):
        """Image which uploaded to locket is stored on the firebase cloud first."""   
        try:
            webp = image_to_webp(filepath)
            UPLOAD_URL = self.get_upload_URL(webp, "image/webp")
            image_data = open(webp, "rb").read()
            upload_id = (self.get_upload_URL(webp, "image/webp").split("&")[4]).split("=")[1]
            querystring = {
                "name": f"users/{self.get_localID}/moments/thumbnails/{webp}",
                "uploadType": "resumable",
                "upload_id": upload_id,
                "upload_protocol": "resumable",
            }
            headers = {
                "authorization": f"Firebase {self.tokenID}",
                "x-goog-upload-command": "upload, finalize",
                "x-goog-upload-protocol": "resumable",
                "x-goog-upload-offset": "0",
                "content-type": "application/x-www-form-urlencoded",
                "host": "firebasestorage.googleapis.com",
            }
            
            r = requests.post(
                UPLOAD_URL,
                params=querystring,
                headers=headers,
                data=image_data
            )
            
            if r.status_code == 200:
                return (True, r.json())
            else: 
                return (False, r.json())

        except Exception as e:
            return (False, str(e))
        

    def post_image(self, filepath : str, caption: str) -> bool:
        """Post image to your friends. Everybody can see it."""
        
        upload_data = self.upload_image(filepath)
        if upload_data[0] == False:
            return False
        
        upload_data_json = upload_data[1]

        thumbnail_url = f"https://firebasestorage.googleapis.com/v0/b/locket-img/o/" + \
                        upload_data_json["name"].replace("/", "%2F") + \
                        f"?alt=media&token={upload_data_json["downloadTokens"]}"
        headers = {
            "authorization" : f"Bearer {self.tokenID}",
            "content-type" : "application/json; charset=utf-8",
            "host" : "api.locketcamera.com"
        }
        payload = {
            "data": {
                "analytics": {
                "platform": "android",
                "amplitude": {
                    "device_id": self.random_device_id,
                    "session_id": self.random_session_id
                }
                },
                "caption": caption,
                "thumbnail_url": thumbnail_url,
                "recipients": []
            }
        }

        r = requests.post(
            POST_UPLOAD_API,
            headers=headers,
            json=payload
        )

        if r.status_code == 200:
            return (True, r.json())
        else:
            return (False, r.json())