import requests
import matplotlib.pyplot as plt
import numpy as np

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

mass_min = 10**12.0 / 1e10 * 0.704
mass_max = 1.1 * 10**12.0 / 1e10 * 0.704

search_query = "?mass__gt=" + str(mass_min) + "&mass__lt=" + str(mass_max)

url = "http://www.illustris-project.org/api/Illustris-1/snapshots/z=0/subhalos" + search_query

subhalos = get(url, {'limit':2000})

print subhalos['count']

ids = [subhalos['results'][i]['id'] for i in range(subhalos['count'])]
print len(ids)

ids2 = ids[:]
primary_subhalo = []
temp = []
x = 0
for i in ids2:
    url = "http://www.illustris-project.org/api/Illustris-1/snapshots/z=0/subhalos/" + str(i)
    primary_subhalo.append(get(url))
    temp.append(primary_subhalo[-1])
    if temp[x]['primary_flag'] != 1:
        ids.remove(i)
        primary_subhalo.remove(temp[x])
    x += 1

print len(ids)
print len(primary_subhalo)
ids2 = []
for i in ids:
    ids2.append(i + 1)

secondary_subhalo = []
temp = []
x = 0
for i in ids2:
    url = "http://www.illustris-project.org/api/Illustris-1/snapshots/z=0/subhalos/" + str(i)
    secondary_subhalo.append(get(url))
    temp.append(secondary_subhalo[-1])
    if temp[x]['grnr'] != primary_subhalo[x]['grnr']:
        secondary_subhalo.remove(temp[x])
    x += 1
print len(secondary_subhalo)

secondary_subhalo_temp = secondary_subhalo[:]
for i in secondary_subhalo_temp:
    if i['mass'] <= 5.632 or i['mass'] >= 22.528:
        secondary_subhalo.remove(i)
print len(secondary_subhalo)

vel = []
for i in secondary_subhalo:
    vel.append(np.sqrt(i['vel_x']**2 + i['vel_y']**2 + i['vel_z']**2))

plt.hist(vel, 20)
plt.show()
