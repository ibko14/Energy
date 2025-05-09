import pandas as pd
import itertools
import seaborn as sns
import matplotlib.pyplot as plt

##Données entrées
df=pd.read_csv('C:\\Users\\adamh\\Desktop\\Neoma\\Optimisation\\ESG\\eCO2mix_RTE_2024-11-15.txt',encoding='ISO-8859-1',sep='\t')
df=df.iloc[:,[2,3,4,5]]
df=df.T

energies={
    'Nom':['Nuclear','gas','oil','coal','wind','solar'],
    'Prix MWh':[55,70,200,50,70,55],
    'g/MWH':[100,500,800,1000,100,100]
    }
df2=pd.DataFrame(energies)
df2=df2.T

##Variables de decision
values=[round(0.1*i,2) for i in range (1,11)]
combinations=[]
for comb in itertools.product(values,repeat=6):
    if sum(comb)==1:
        combinations.append(comb)

df3=pd.DataFrame(combinations)

##Variables decisions multipliées 
DF=(df2.iloc[1:3,:]@df3.T).T
#DF['quotient']=DF['Prix MWh']/DF['g/MWH']

# Créer le nuage de points avec Seaborn
sns.scatterplot(data=DF, x='Prix MWh', y='g/MWH',color='red')

plt.title('Nuage de Points')
plt.xlabel('PrixMwh')
plt.ylabel('g/Mwh')

# Afficher le graphique
plt.grid()
plt.show()

##Trouver max et min
IminP=DF['Prix MWh'].idxmin()
IminC=DF['g/MWH'].idxmin()
#IminQ=DF['quotient'].idxmin()

##MutliObjective
###Pareto optimaux
###On cherche les solutions telles que CO2(x0)<CO2(x1) && Prix(x0)<Prix(x1)

DF_Prix=DF.sort_values('Prix MWh', axis=0, ascending=True, inplace=False)
DF_CO2=DF.sort_values('g/MWH', axis=0, ascending=True, inplace=False)

PO=DF[(DF['Prix MWh'] <= DF['Prix MWh'].min()) | (DF['g/MWH'] <= DF['g/MWH'].min())]

# Créer le nuage de points avec Seaborn
sns.scatterplot(data=PO, x='Prix MWh', y='g/MWH',color='blue')

plt.title('Nuage de Points')
plt.xlabel('PrixMwh')
plt.ylabel('g/Mwh')

# Afficher le graphique
plt.grid()
plt.show()
##Weighed sum scalarization
for lmb in range(0,10):
    DF[f'comb_{lmb}']=(1-lmb/10)*DF['Prix MWh']+lmb/10*DF['g/MWH']

ImportancePrix=DF.loc[[DF.iloc[:, 2].idxmin()]]
ImportanceEquiv=DF.loc[[DF.iloc[:, 6].idxmin()]]
ImportanceCO2=DF.loc[[DF.iloc[:, 9].idxmin()]]

# Créer le nuage de points avec Seaborn
sns.scatterplot(data=DF, x='Prix MWh', y='g/MWH',color='red')
sns.scatterplot(data=ImportanceEquiv, x='Prix MWh', y='g/MWH',color='blue')
sns.scatterplot(data=ImportancePrix, x='Prix MWh', y='g/MWH',color='blue')
sns.scatterplot(data=ImportanceCO2, x='Prix MWh', y='g/MWH',color='green')




plt.title('Nuage de Points')
plt.xlabel('PrixMwh')
plt.ylabel('g/Mwh')

# Afficher le graphique
plt.grid()
plt.show()



