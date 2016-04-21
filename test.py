import requests
import matplotlib.pyplot as plt
import numpy as np

def distance(first, second):
    temp = []
    temp.append(first['pos_x'] - second['pos_x'])
    temp.append(first['pos_y'] - second['pos_y'])
    temp.append(first['pos_z'] - second['pos_z'])
    for i in range(3):
        if temp[i] > (1000 * 0.704):
            temp[i] = temp[i] - 106500 * 0.704
    return np.sqrt(temp[0]**2 + temp[1]**2 + temp[2]**2) / 0.704

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

mass_min = 1. * 10**12.0 / 1e10 * 0.704
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
temp2 = primary_subhalo[:]
x = 0
y = 0
for i in ids2:
    for j in range(5):
        url = "http://www.illustris-project.org/api/Illustris-1/snapshots/z=0/subhalos/" + str(i)
        secondary_subhalo.append(get(url))
        temp.append(secondary_subhalo[-1])
        if (temp[x]['grnr'] != temp2[y]['grnr']):
            secondary_subhalo.remove(temp[x])
            primary_subhalo.remove(temp2[y])
            x += 1
            break
        elif (distance(temp[x],temp2[y]) > (temp2[y]['vmaxrad'] / 0.704)):
            secondary_subhalo.remove(temp[x])
            if (j == 4):
                primary_subhalo.remove(temp2[y])
            x += 1
        else:
            x += 1
            break
    y += 1
print len(secondary_subhalo)
for i in range(len(primary_subhalo)):
    print primary_subhalo[i]['id']
    print secondary_subhalo[i]['id']

x = 0
temp = secondary_subhalo[:]
temp2 = primary_subhalo[:]
for i in range(len(temp)):
    if temp[i]['mass'] <= 5.632 or temp[i]['mass'] >= 22.528:
        secondary_subhalo.remove(temp[i])
        primary_subhalo.remove(temp2[i])
    x += 1
print len(secondary_subhalo)
print len(primary_subhalo)



vel = []
vec_vel = []
for i in secondary_subhalo:
    vec_vel.append([i['vel_x'], i['vel_y'], i['vel_z']])

for i in vec_vel:
    vel.append(np.sqrt(i[0]**2 + i[1]**2 + i[2]**2))

plt.hist(vel, 20)
plt.title("Velocities of LMC Subhalos")
plt.ylabel("Number of Subhalos")
plt.xlabel(r'Velocity $km/s$')
plt.show()



sub_dist = []
for i in secondary_subhalo:
    sub_dist.append([i['pos_x'], i['pos_y'], i['pos_z']])

halo_dist = []
for i in primary_subhalo:
    halo_dist.append([i['pos_x'], i['pos_y'], i['pos_z']])

vec_dist = []
for i in range(len(halo_dist)):
    vec_dist.append([sub_dist[i][0] - halo_dist[i][0], sub_dist[i][1] - halo_dist[i][1], sub_dist[i][2] - halo_dist[i][2]])
    for j in range(3):
        if (vec_dist[-1][j] > (1000 * 0.704)):
            vec_dist[-1][j] = vec_dist[-1][j] - 106500 * 0.704

dist = []
for i in vec_dist:
    dist.append(np.sqrt(i[0]**2 + i[1]**2 + i[2]**2) / 0.704)

plt.hist(dist, 20)
plt.title("Distances of LMC Subhalos")
plt.xlabel(r'Distance ($kpc$)')
plt.ylabel('Number of Subhalos')
plt.show()

ang = []
vec_ang = np.cross(vec_dist, vec_vel)
for i in vec_ang:
    ang.append(np.sqrt(i[0]**2 + i[1]**2 + i[2]**2))
x = 0
for i in secondary_subhalo:
    ang[x] = i['mass'] * ang[x]
    x += 1

plt.hist(ang, 20)
plt.title("Angular Momentum of LMC Subhalos")
plt.xlabel(r'Angular Momentum ($M_{\odot} kpc km / s$)')
plt.ylabel('Number of Subhalos')
plt.show()
