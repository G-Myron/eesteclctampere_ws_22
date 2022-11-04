#%%
import requests, json

resp = requests.post('https://ecg4everybody.com/service/getdata.php', data = {'i': "cGJTZDVSMlc1djVTRWRqT0c2SWRmdz09"})
resp = json.loads(resp.text)
print(resp)

