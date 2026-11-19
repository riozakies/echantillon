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



def equi_inclusion(cum, u):
    """
    Renvoie l'index de la première unité dont la probabilité d'inclusion
    cumulée est >= u (u tombe dans l'intervalle ]cum[j-1], cum[j]]).
    Fonctionne quel que soit l'index du DataFrame (décalé, mélangé...).
    """
    pos = np.searchsorted(cum.to_numpy(), u, side="left")
    pos = min(pos, len(cum) - 1)  # protège contre les erreurs d'arrondi en fin de série
    return cum.index[pos]


def select_sys(base_sondage, taille, poids=None, random_state=42):
    """
    Tirage systématique d'un échantillon de taille `taille`.
    - poids=None : probabilités égales.
    - poids="col" : probabilités proportionnelles à la taille (PPS). Les unités
      dont la probabilité d'inclusion dépasse 1 sont prises d'office (strate
      exhaustive) et le reste de l'échantillon est tiré parmi les autres.
    Renvoie (liste des index tirés, DataFrame de l'échantillon).
    """
    base = base_sondage.copy()  # ne modifie pas le DataFrame de l'utilisateur
    N = len(base)
    taille = int(round(taille))
    u = np.random.default_rng(seed=random_state).random()
    base["id_sys"] = np.arange(1, N + 1)

    if taille <= 0:
        return [], base.iloc[0:0]
    if taille >= N:
        print(f"Taille demandée ({taille}) >= taille de la base ({N}) : toutes les unités sont retenues.")
        return list(base.index), base

    # 1er cas : probabilités égales
    if poids is None:
        k = N / taille
        pos = np.floor(k * u + k * np.arange(taille)).astype(int)
        pos = np.clip(pos, 0, N - 1)  # évite de sortir de la base à cause d'un arrondi
        df = base.iloc[pos]
        return list(df.index), df

    # 2e cas : probabilités inégales (PPS)
    x = pd.to_numeric(base[poids], errors="coerce").fillna(0)
    if (x < 0).any():
        raise ValueError("La variable de poids contient des valeurs négatives.")

    reste = x[x > 0]
    if len(reste) < taille:
        print(f"Seulement {len(reste)} unités ont un poids > 0 : impossible d'en tirer {taille}.")
        taille = len(reste)

    # Unités certaines : on les retire tant qu'il en reste avec p >= 1
    certains = []
    n_reste = taille
    while n_reste > 0:
        p = n_reste * reste / reste.sum()
        gros = p[p >= 1].index
        if len(gros) == 0:
            break
        certains.extend(gros)
        reste = reste.drop(gros)
        n_reste = taille - len(certains)

    base["p_inclusion"] = 0.0
    base.loc[certains, "p_inclusion"] = 1.0

    tires = []
    if n_reste > 0:
        p = n_reste * reste / reste.sum()
        cum = p.cumsum()
        cum = cum * n_reste / cum.iloc[-1]  # garantit que le cumul finit exactement à n_reste
        base.loc[p.index, "p_inclusion"] = p
        points = u + np.arange(n_reste)
        tires = [equi_inclusion(cum, v) for v in points]

    base["cum_p_inclusion"] = base["p_inclusion"].cumsum()
    select = certains + tires
    df = base[base.index.isin(select)]
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