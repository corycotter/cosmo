import requests

def get(path, params=None):
    headers = {"api-key":"7fa937edbda6181b69c3819d691ed5b0"}
    r = requests.get(path, params=params, headers=headers)

    r.raise_for_status()

    if r.headers['content-type'] == 'application/json':
        return r.json()

    if 'content-disposition' in r.headers:
        filename = r.headers['content-disposition'].split("filename=")[1]
        with open(filename, 'wb') as f:
            f.write(r.content)
        return filename

    return r

mass_min = 10**11.9 / 1e10 * 0.704
mass_max = 10**12.1 / 1e10 * 0.704

search_query = "?mass__gt=" + str(mass_min) + "&mass__lt=" + str(mass_max)

url = "http://www.illustris-project.org/api/Illustris-1/snapshots/z=0/subhalos" + search_query

subhalos = get(url, {'limit':1000})

print subhalos['count']

ids = [subhalos['results'][i]['id'] for i in range(subhalos['count'])]
