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

    if r.status_code != requests.codes.ok:
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

mass_min = 0.43 * 10**12.0 / 1e10 * 0.704
mass_max = 4.3 * 10**12.0 / 1e10 * 0.704

search_query = "?mass__gt=" + str(mass_min) + "&mass__lt=" + str(mass_max)

url = "http://www.illustris-project.org/api/Illustris-1/snapshots/z=0/subhalos" + search_query

subhalos = get(url, {'limit':5000})

print "Number of Milky Way mass galaxies: ", subhalos['count']


ids = [subhalos['results'][i]['id'] for i in range(subhalos['count'])]
#print len(ids)

primary_subhalo = []
temp = ids[:]
for i in temp:
    #print ids.index(i)
    #print i
    url = "http://www.illustris-project.org/api/Illustris-1/snapshots/z=0/subhalos/" + str(i)
    primary_subhalo.append(get(url))
    if primary_subhalo[-1]['primary_flag'] != 1:
        ids.remove(i)
        primary_subhalo.pop()
    if temp.index(i) % 500 == 0:
        print temp.index(i)

'''
potential_sec_sub = []
for i in primary_subhalo:
    print primary_subhalo.index(i)
    rad = 2 * i['vmaxrad']
    xlow = i['pos_x'] - rad
    xhigh = i['pos_x'] + rad
    ylow = i['pos_y'] - rad
    yhigh = i['pos_y'] + rad
    zlow = i['pos_z'] - rad
    zhigh = i['pos_z'] + rad
    mass_min = 5.632
    mass_max = 22.528
    search_query = "?mass__gt=" + str(mass_min) + "&mass__lt=" + str(mass_max) + "&pos_x__gt=" + str(xlow) + "&pos_x__lt=" + str(xhigh) + "&pos_y__gt=" + str(ylow) + "&pos_y__lt=" + str(yhigh) + "&pos_z__gt=" + str(zlow) + "&pos_z__lt=" + str(zhigh)
    url = "http://www.illustris-project.org/api/Illustris-1/snapshots/z=0/subhalos" + search_query
    potential_sec_sub.append(get(url))
print potential_sec_sub

secondary_subhalo = []
x = 0
while x < len(primary_subhalo):
    if (potential_sec_sub[x]['results'] == []):
        primary_subhalo.pop(x)
    else:
        secondary_subhalo.append(potential_sec_sub[x])
        x += 1
print secondary_subhalo
print len(secondary_subhalo)
print len(primary_subhalo)
exit()
'''
#print len(ids)
#print len(primary_subhalo)
ids2 = []
for i in ids:
    ids2.append(i + 1)

secondary_subhalo = []
temp = []
temp2 = primary_subhalo[:]
x = 0
y = 0
sum_vir_rad = 0.
for i in ids2:
    if y % 500 == 0:
        print y
    for j in range(2):
        url = "http://www.illustris-project.org/api/Illustris-1/snapshots/z=0/subhalos/" + str(i)
        secondary_subhalo.append(get(url))
        temp.append(secondary_subhalo[-1])
        vir_rad = get("http://www.illustris-project.org/api/Illustris-1/snapshots/135/halos/" + str(temp2[y]['grnr']) + "/info.json")['Group']['Group_R_Mean200']
        if (temp[x]['grnr'] != temp2[y]['grnr']):
            secondary_subhalo.remove(temp[x])
            primary_subhalo.remove(temp2[y])
            x += 1
            sum_vir_rad += vir_rad / 0.704
            break
        elif (distance(temp[x],temp2[y]) > (vir_rad / 0.704)):
            secondary_subhalo.remove(temp[x])
            if (j == 1):
                primary_subhalo.remove(temp2[y])
                sum_vir_rad += vir_rad / 0.704
            x += 1
        else:
            x += 1
            sum_vir_rad += vir_rad / 0.704
            break
    y += 1
print "Number of Milky Way mass galaxies with companions in R200: ", len(secondary_subhalo)
print "Average Virial Radius: ", sum_vir_rad / len(ids2)

x = 0
temp = secondary_subhalo[:]
temp2 = primary_subhalo[:]
for i in range(len(temp)):
    if temp[i]['mass'] <= 5.632 or temp[i]['mass'] >= 22.528:
        secondary_subhalo.remove(temp[i])
        primary_subhalo.remove(temp2[i])
    x += 1

print "Number of LMC candidates: ", len(secondary_subhalo)

sub_vel = []
vec_vel = []
for i in secondary_subhalo:
    sub_vel.append([i['vel_x'], i['vel_y'], i['vel_z']])

halo_vel = []
for i in primary_subhalo:
    halo_vel.append([i['vel_x'], i['vel_y'], i['vel_z']])

for i in range(len(halo_vel)):
    vec_vel.append([sub_vel[i][0] - halo_vel[i][0], sub_vel[i][1] - halo_vel[i][1], sub_vel[i][2] - halo_vel[i][2]])

vel = []
for i in vec_vel:
    vel.append(np.sqrt(i[0]**2 + i[1]**2 + i[2]**2))

print "Average velocity of LMC: ", np.mean(vel)
print "Standard deviation of velocity of LMC: ", np.std(vel)

mu1 = np.mean(vel)
sigma1 = np.std(vel)

plt.hist(vel, 20)
plt.title("Velocities of LMC Subhalos")
plt.text(x, y, r'$\mu={},\ \sigma={}$'.format(mu1, sigma1))
plt.ylabel("Number of Subhalos")
plt.xlabel(r'Velocity $km/s$')
plt.savefig("lmc_vel.png")
plt.clf()


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

print "Average distance of LMC: ", np.mean(dist)
print "Standard deviation of distance of LMC: ", np.std(dist)

mu2 = np.mean(dist)
sigma2 = np.std(dist)

plt.hist(dist, 20)
plt.title("Distances of LMC Subhalos")
plt.text(x, y, r'$\mu={},\ \sigma={}$'.format(mu2, sigma2))
plt.xlabel(r'Distance ($kpc$)')
plt.ylabel('Number of Subhalos')
plt.savefig("lmc_dist.png")
plt.clf()

ang = []
vec_ang = np.cross(vec_dist, vec_vel)
for i in vec_ang:
    ang.append(np.sqrt(i[0]**2 + i[1]**2 + i[2]**2))
x = 0
for i in secondary_subhalo:
    ang[x] = i['mass'] * 1e10 / 0.704 * ang[x]
    x += 1

for i in range(len(ang)):
    ang[i] = ang[i] * 6.136e52

print "Average angular momentum of LMC", np.mean(ang)
print "Standard deviation of angular momentum of LMC: ", np.std(ang)

mu3 = np.mean(ang)
sigma3 = np.std(ang)

plt.hist(ang, 20)
plt.title("Angular Momentum of LMC Subhalos")
plt.text(mu3, sigma3, r'$\mu={},\ \sigma={}$'.format(mu3, sigma3))
plt.xlabel(r'Angular Momentum ($kg m^2 / s$)')
plt.ylabel('Number of Subhalos')
plt.savefig("lmc_ang.png")
plt.clf()


prim_mass = []
sec_mass = []
for i in range(len(primary_subhalo)):
    prim_mass.append(primary_subhalo[i]['mass'] * 1e10 / 0.704)
    sec_mass.append(secondary_subhalo[i]['mass'] * 1e10 / 0.704)

print "Average mass of LMC hosts: ", np.mean(prim_mass)
print "Standard deviation of mass of LMC hosts: ", np.std(prim_mass)
print "Average mass of LMC: ", np.mean(sec_mass)
print "Standard deviation of mass of LMC: ", np.std(sec_mass)

plt.hist(sec_mass, 20)
plt.title("Mass Distribution of LMC Subhalos")
plt.ylabel(r'Number of Subhalos')
plt.xlabel(r'LMC mass ($M_{\odot}$)')
plt.savefig("lmc_mass.png")
plt.clf()


lmc_sfr = []
for i in range(len(secondary_subhalo)):
    lmc_sfr.append(secondary_subhalo[i]['sfr'])

print "Average SFR of LMC: ", np.mean(lmc_sfr)
print "Standard deviation of SFR of LMC: ", np.std(lmc_sfr)

plt.hist(lmc_sfr, 20)
plt.title("SFR Distribution of LMC Subhalos")
plt.ylabel("Number of Subhalos")
plt.xlabel(r'LMC SFR ($M_{\odot} / yr$)')
plt.savefig("lmc_sfr.png")
plt.clf()


tertiary_subhalo = []
temp = []
new_sec_sub = secondary_subhalo[:]
new_prim_sub = primary_subhalo[:]
x = 0
y = 0
for i in secondary_subhalo:
    if y % 500 == 0:
        print y
    for j in range(2):
        url = "http://www.illustris-project.org/api/Illustris-1/snapshots/z=0/subhalos/" + str(i['id'] + 1)
        tertiary_subhalo.append(get(url))
        temp.append(tertiary_subhalo[-1])
        vir_rad = get("http://www.illustris-project.org/api/Illustris-1/snapshots/135/halos/" + str(i['grnr']) + "/info.json")['Group']['Group_R_Mean200']
        if (temp[x]['grnr'] != i['grnr']):
            tertiary_subhalo.remove(temp[x])
            new_prim_sub.pop(new_sec_sub.index(i))
            new_sec_sub.remove(i)
            x += 1
            break
        elif (distance(temp[x],i) > (vir_rad / 0.704)):
            tertiary_subhalo.remove(temp[x])
            if (j == 1):
                new_prim_sub.pop(new_sec_sub.index(i))
                new_sec_sub.remove(i)
            x += 1
        else:
            x += 1
            break
    y += 1

x = 0
temp = tertiary_subhalo[:]
temp2 = new_sec_sub[:]
temp3 = new_prim_sub[:]
for i in range(len(temp)):
    if temp[i]['mass'] <= 2.816 or temp[i]['mass'] >= 11.264:
        tertiary_subhalo.remove(temp[i])
        new_sec_sub.remove(temp2[i])
        new_prim_sub.remove(temp3[i])
    x += 1


print "Number of SMC analogs in systems with LMC analogs: ", len(tertiary_subhalo)

smc_dist = []
for i in range(len(tertiary_subhalo)):
    smc_dist.append(distance(tertiary_subhalo[i], new_prim_sub[i]))

print "Average distance of SMC: ", np.mean(smc_dist)
print "Standard deviation of distance of SMC: ", np.std(smc_dist)

mu4 = np.mean(smc_dist)
sigma4 = np.std(smc_dist)

plt.hist(smc_dist, 20)
plt.title("Distances of SMC Subhalos")
plt.text(x, y, r'$\mu={},\ \sigma={}$'.format(mu4, sigma4))
plt.xlabel(r'Distance ($kpc$)')
plt.ylabel('Number of Subhalos')
plt.savefig("smc_dist.png")
plt.clf()


sub_smc_vel = []
vec_smc_vel = []
for i in tertiary_subhalo:
    sub_smc_vel.append([i['vel_x'], i['vel_y'], i['vel_z']])

halo_vel = []
for i in new_prim_sub:
    halo_vel.append([i['vel_x'], i['vel_y'], i['vel_z']])

for i in range(len(halo_vel)):
    vec_smc_vel.append([sub_smc_vel[i][0] - halo_vel[i][0], sub_smc_vel[i][1] - halo_vel[i][1], sub_smc_vel[i][2] - halo_vel[i][2]])

smc_vel = []
for i in vec_smc_vel:
    smc_vel.append(np.sqrt(i[0]**2 + i[1]**2 + i[2]**2))

print "Average velocity of SMC: ", np.mean(smc_vel)
print "Standard deviation of velocity of SMC: ", np.std(smc_vel)

mu1 = np.mean(smc_vel)
sigma1 = np.std(smc_vel)

plt.hist(smc_vel, 20)
plt.title("Velocities of SMC Subhalos")
plt.text(x, y, r'$\mu={},\ \sigma={}$'.format(mu1, sigma1))
plt.ylabel("Number of Subhalos")
plt.xlabel(r'Velocity $km/s$')
plt.savefig("smc_vel.png")
plt.clf()


smc_dist = []
for i in tertiary_subhalo:
    smc_dist.append([i['pos_x'], i['pos_y'], i['pos_z']])

halo_dist = []
for i in new_prim_sub:
    halo_dist.append([i['pos_x'], i['pos_y'], i['pos_z']])

vec_smc_dist = []
for i in range(len(halo_dist)):
    vec_smc_dist.append([smc_dist[i][0] - halo_dist[i][0], smc_dist[i][1] - halo_dist[i][1], smc_dist[i][2] - halo_dist[i][2]])
    for j in range(3):
        if (vec_smc_dist[-1][j] > (1000 * 0.704)):
            vec_smc_dist[-1][j] = vec_smc_dist[-1][j] - 106500 * 0.704

smc_ang = []
vec_smc_ang = np.cross(vec_smc_dist, vec_smc_vel)
for i in vec_smc_ang:
    smc_ang.append(np.sqrt(i[0]**2 + i[1]**2 + i[2]**2))
x = 0
for i in tertiary_subhalo:
    smc_ang[x] = i['mass'] * smc_ang[x] * 1e10 / 0.704
    x += 1

for i in range(len(smc_ang)):
    smc_ang[i] = smc_ang[i] * 6.136e52

print "Average angular momentum of SMC: ", np.mean(smc_ang)
print "Standard deviation of angular momentum of SMC: ", np.std(smc_ang)

mu3 = np.mean(smc_ang)
sigma3 = np.std(smc_ang)

plt.hist(smc_ang, 20)
plt.title("Angular Momentum of SMC Subhalos")
plt.text(mu3, sigma3, r'$\mu={},\ \sigma={}$'.format(mu3, sigma3))
plt.xlabel(r'Angular Momentum ($kg m^2 / s$)')
plt.ylabel('Number of Subhalos')
plt.savefig("smc_ang.png")
plt.clf()


prim_mass = []
smc_mass = []
for i in range(len(tertiary_subhalo)):
    prim_mass.append(primary_subhalo[i]['mass'] * 1e10 / 0.704)
    smc_mass.append(tertiary_subhalo[i]['mass'] * 1e10 / 0.704)

print "Average mass of SMC hosts: ", np.mean(prim_mass)
print "Standard deviation of mass of SMC hosts: ", np.std(prim_mass)
print "Average mass of SMC: ", np.mean(smc_mass)
print "Standard deviation of mass of SMC: ", np.std(smc_mass)

plt.hist(smc_mass, 20)
plt.title("Mass Distribution of SMC Subhalos")
plt.ylabel(r'Number of Subhalos')
plt.xlabel(r'SMC mass ($M_{\odot}$)')
plt.savefig("smc_mass.png")
plt.clf()


smc_sfr = []
for i in range(len(tertiary_subhalo)):
    smc_sfr.append(tertiary_subhalo[i]['sfr'])

print "Average SFR of SMC: ", np.mean(smc_sfr)
print "Standard deviation of SFR of SMC: ", np.std(smc_sfr)

plt.hist(smc_sfr, 20)
plt.title("SFR Distribution of SMC Subhalos")
plt.ylabel("Number of Subhalos")
plt.xlabel(r'SMC SRF ($M_{\odot} / yr$)')
plt.savefig("smc_sfr.png")
plt.clf()
