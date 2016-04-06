import matplotlib.pyplot as plt
import illustris_python as il

basePath = './Illustris-3/'
fields = ['SubhaloMass','SubhaloSFRinRad']
GroupFirstSub = il.groupcat.loadHalos(basePath,135,fields=['GroupFirstSub'])

ptNumDM = 1


for i in range(5):
    all_fields = il.groupcat.loadSingle(basePath,135,subhaloID=GroupFirstSub[i])
    dm_mass = all_fields['SubhaloMass'] * 1e10 / 0.704
    print GroupFirstSub[i], dm_mass
'''
plt.plot(temp,temp2,'.')
plt.xscale('log')
plt.yscale('log')
plt.xlabel('Total Mass [$M_\odot$]')
plt.ylabel('Star Formation Rate [$M_\odot / yr$]')
plt.show()
'''
