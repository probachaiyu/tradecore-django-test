import json
import logging
import random
import string
import urllib.error
import urllib.parse
import urllib.request
from http.client import HTTPException, UNAUTHORIZED, FORBIDDEN, NOT_FOUND
from socket import error

import names


class RequestClient:

    @classmethod
    def _do_request(cls, url, http, json_response, response_errors=[], timeout=300):
        """
        Does the request, handles the possible exceptions and
        returns the data.
        """
        try:
            response = urllib.request.urlopen(http, timeout=timeout)
        except urllib.error.HTTPError as e:  # if HTTP status is not 200
            response = e.read()
            if e.code in response_errors:
                return {"response": response, "error": e}
            elif e.code in [UNAUTHORIZED, FORBIDDEN]:
                raise ValueError("You are not authorised to access this page %s" % response)
            elif e.code == NOT_FOUND:
                raise ValueError("Resource not found: %s" % url)
            else:
                raise ValueError("Url %s returned an invalid response: %s" % (url, response))
        except error:
            hostname = urllib.parse.urlparse(url)
            raise ValueError("Cannot access %s" % hostname.netloc)
        except (HTTPException, error) as e:
            raise ValueError("Invalid response: %s" % e.message)
        data = response.read()
        if data and json_response:
            try:
                data = json.loads(data)
            except ValueError:
                raise ValueError("Invalid response: %s" % data)
        return data

    @classmethod
    def make_request(cls,
        url,
        data=None,
        headers={},
        method=None,
        json_type=True,
        json_response=True,
        response_errors=[],
        timeout=300,
    ):
        if data:
            if json_type:
                data = json.dumps(data)
                headers["Content-Type"] = "application/json"
            else:
                if isinstance(data, dict):
                    for k, v in data.items():
                        if isinstance(v, str):
                            data[k] = v.encode("utf-8") if isinstance(v, str) else v
                data = urllib.parse.urlencode(data)

            if isinstance(data, str):
                data = data.encode("utf-8")

        http = urllib.request.Request(url, data, headers)
        if method:
            http.get_method = lambda: method

        return cls._do_request(url, http, json_response, response_errors, timeout=timeout)

    @classmethod
    def authenticated_request(cls,
            url,
            data=None,
            method=None,
            json_response=True,
            operation=None,
            response_errors=[],
            timeout=60,
             token=None
        ):
            headers = {"Authorization": "Bearer " + token}
            for i in [1, 2, 3]:  # repeat 3 times to let PDF API warm up
                try:
                    logging.info("auth. request %s" % url)
                    logging.info("token %s" % token)
                    result = cls.make_request(
                        url,
                        data,
                        headers,
                        method,
                        json_type=True,
                        json_response=json_response,
                        response_errors=response_errors,
                        timeout=timeout,
                    )
                except ValueError as e:
                    result = {"status": "ERR", "message": str(e)}

                    return result
                if not isinstance(result, dict) or result.get("message", "").startswith(
                    "Cannot access"
                ):
                    break
                return result

class RandomCreator:

    @staticmethod
    def create_password():
        letters = "".join(random.choice(string.ascii_lowercase) for _ in range(5))
        letters_b = "".join(random.choice(string.ascii_uppercase) for _ in range(3))
        numbers = "".join(random.choice(string.digits) for _ in range(3))
        return letters + numbers  + letters_b

    @staticmethod
    def get_email():
        #need to get data from third-party services, so need existing emails
        emails = ['steli@close.io', 'antoine@hunter.io', 'dustin@asana.com', 'ciaran@intercom.io', 'kevin@instagram.com']
        return random.choice(emails)

    @staticmethod
    def get_name():
        # need to get data from third-party services, so need existing emails
        names_list = list(set([names.get_first_name() for name in range(20)]))
        return random.choice(names_list)