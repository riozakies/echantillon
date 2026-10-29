import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import math
import warnings

warnings.filterwarnings('ignore')


# Fonctions utilitaires

## maximun d'un ensemble de valeur d'un dictionaire
def max_key_dic(dic):
    if isinstance(dic, dict):
        max_v=max(dic.values())
        for key in dic.keys():
            if float(dic[key])>=max_v:
                max_v=dic[key]
                cle=key
        return cle,max_v
    else:
        print("L'entrée n'est pas un dictionnaire")
        return None,None

## Arrondi d'hamilton

def arrondi_hamilton(dic):
    if isinstance(dic,dict):
        taille=int(sum(dic.values()))
        dic_int={}
        dic_reste={}
        for key in dic.keys():
            dic_int[key]=math.floor(dic[key])
            dic_reste[key]=dic[key]-dic_int[key]
        if sum(dic_int.values())==taille:
            return dic_int
        elif sum(dic_int.values())<taille:
            n_reste=taille-sum(dic_int.values())
            while n_reste>0:
                key_max,max_dic=max_key_dic(dic_reste)
                dic_int[key_max]=dic_int[key_max]+1
                del dic_reste[key_max]
                n_reste=n_reste-1
            return dic_int
        else:
            n_reste=sum(dic_int.values())-taille
            while n_reste>0:
                key_max,max_dic=max_key_dic(dic_reste)
                dic_int[key_max]=dic_int[key_max]-1
                del dic_reste[key_max]
                n_reste=n_reste-1
            return dic_int



def equi_inclusion(df,u):
    """
    Cette fonction permet de recuper l'indexe du 
    plus petit élement d'une serie iméditement supérieur à une valuer donnée.
    """
    db=df-u
    index=db[db==db[db>=0].min()].index
    return index[0]


def select_sys(base_sondage,
               taille,
               poids=None,
               random_state=42
              ):
    """
    fonction pour selectionnner un échantillon probabiliste suivant la 
    méthode de tirage systématique.
    Il est demandé de préciser outre la base de sondage (DataFrame) et 
    les colonnes identifiant et nom des unités, le pas qui est le random state 
    et la taille de l'échantillon. 
    """

    # génération du nombre aléatoire
    nb_alea=np.random.default_rng(seed=random_state).random()


    # vérifier si le paramètre poids est None. S'il est None c'est un sondage à probabilité égale
    
    # 1er cas: probabilité égale:
    
    # création des numéros d'ordres
    base_sondage["id_sys"]=range(1,len(base_sondage)+1)
    
    if poids==None:
        if taille>= len(base_sondage):
            print("la taille de l'échantillon est supérieur ou égal à la taille de la base de sondage")
        else:
            k=len(base_sondage)/taille if taille!=0 else 0
            select=[]
            for i in range(taille):
                select.append(math.floor(k*nb_alea+(i*k))+1)
            df = base_sondage[base_sondage["id_sys"].isin(select)]
            return select,df

    # 2er cas: probabilité inégale:
    else:
        c_poids=base_sondage[poids].apply(pd.to_numeric,errors="coerce").sum()
        for idx,row in base_sondage.iterrows():
            base_sondage.loc[idx,"poids_relatif"]=base_sondage.loc[idx,poids].sum()/c_poids
            base_sondage.loc[idx,"p_inclusion"]=base_sondage.loc[idx,"poids_relatif"]*taille
            base_sondage.loc[idx,"cum_p_inclusion"]=base_sondage.loc[0:idx,"p_inclusion"].sum()
        
        p_inclusion=base_sondage["p_inclusion"]>1
        # vérifier que les probabilié d'inclusion sont toutes inférieur à <1
        if p_inclusion.sum()==0:
            select=[nb_alea+i for i in range(taille)]
            select_cor=[equi_inclusion(base_sondage["cum_p_inclusion"],u) for u in select]
            df = base_sondage[base_sondage.index.isin(select_cor)]
            return select_cor,df
        else:
            select_cor_p=[next(u for u in p_inclusion if u==False),None]
            if len(select_cor_p)==taille:
                df=base_sondage[base_sondage["cum_p_inclusion"].isin(select_cor_p)]
                return select_cor_p,df
            else:
                long_reste=taille-len(select_cor_p)
                select=[nb_alea+i for i in range(long_reste)]
                select_cor=[equi_inclusion(base_sondage["cum_p_inclusion"],u) for u in select]
                df = base_sondage[base_sondage.index.isin(select_cor+select_cor_p)]
                select=select_cor+select_cor_p
                return select, df
## prise en compte de la stratification dans l'échantillonage

def select_sys_complete(base_sondage, 
                        taille, 
                        strate,
                        poids_u=None, # précise le type de sondage. si poids_u précisé alors sondage à probabilité inégale
                        poids=None,
                        random_state=42, 
                        share=0
                       ):
    """
    cette fonction permet de prendre en compte la stratification dans le plan de sondage
    les paramettres sont 
    """
    stra_stat=base_sondage[strate].value_counts()
    strates=stra_stat.index
    df=pd.DataFrame() # Dataframe devant contenir les échantillons par strate
    nbre_strate=len(strates)
    dic_strates={}
    poids_strate={}
    select=[] # Numéro des unités tirées 
    
    #calcul de la taille de l'échantillon par strate
    
    if share not in (0,1):
        print("L'option share doit être 0 ou 1")
        return select,df
    elif  share==0:
        for stra in strates:
            # échantillonnage pour la grappe 
            dic_strates[stra]=taille*stra_stat[stra]/stra_stat.sum()
        dic_strates=arrondi_hamilton(dic_strates)
        total_poids=pd.Series(dic_strates.values()).sum()
        if total_poids<taille:
            print(f"Les strates sont nombreuses et ne permettent pas de repartir assez bien l'echantillon de taille {taille}")
            return select,df
        else:
            for stra in strates:
                select_stra,df_ech_stra=select_sys(base_sondage[base_sondage[strate]==stra],
                                                   dic_strates[stra],
                                                   poids_u,
                                                   random_state
                                                  )
                df=pd.concat([df,df_ech_stra])
                select.extend(select_stra)
            return select,df
    elif share==1 and poids!=None:
        for stra in strates:
            dic_strates[stra]=stra_stat[stra]*base_sondage[base_sondage[strate]==stra][poids].sum()
        total_strates=pd.Series(dic_strates.values()).sum()
        for stra in strates:
            poids_strate[stra]=taille*dic_strates[stra]/total_strates
        poids_strate=arrondi_hamilton(poids_strate)
        total_poids=pd.Series(poids_strate.values()).sum()
        if total_poids<taille:
            print(f"Les strates sont nombreuses et ne permettent pas de repartir assez bien l'echantillon de taille {taille}")
            return select,df
        else:
            for stra in strates:
                select_stra,df_ech_stra=select_sys(base_sondage[base_sondage[strate]==stra],
                                               poids_strate[stra],
                                               poids_u,
                                               random_state
                                              )
                df=pd.concat([df,df_ech_stra])
                select.extend(select_stra)
            return select,df
    else:
        print("share=1 nécessite une variable de poids")
        return select,df