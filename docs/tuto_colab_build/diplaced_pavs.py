# %% [markdown]
# [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/255ribeiro/cadquery_basics/blob/master/docs/tuto_colab_build/multi_pav_b3d_ramdom_disp_resolvido.ipynb)

# %% [markdown]
# # ExercÃ­cio resolvido: Pavimentos deslocados
# ## Fernando Ferraz Rbeiro
#
#
#
#

# %% [markdown]
# #### InstalaÃ§Ã£o dos pacotes

# %%
import sys
IN_COLAB = 'google.colab' in sys.modules
if IN_COLAB:
    print("Running in Colab, installing packages...")
    !pip install build123d
    !wget -q -N https://raw.githubusercontent.com/255ribeiro/cadquery_basics/master/docs/tuto_colab_build/build123d_simpleviewer.py
else:
    print("Not running in Colab, skipping package installation.")

# %% [markdown]
# ### ImportaÃ§Ã£o dos pacotes

# %%
import itertools
from build123d import *
from cadquery_simpleviewer import show
import numpy as np


# %%
cota_inicial = 0
pap = 3
n_pav = 30
displace = 3

### --- code
displace_dir = np.array([-1, 0, 1])

lista_pav = []
for i in range(n_pav + 1):

  # direÃ§Ãµes de deslocamento
  dir_x = np.random.choice(displace_dir) * displace
  # dir_y = np.random.choice(displace_dir) * displace


  cota_atual =   cota_inicial + (pap * i)
  cota_atual = round(cota_atual, 2)
  # criar caixa na cota atual
  box = Box(30, 30, pap, align=(Align.CENTER, Align.CENTER, Align.MIN)).translate((dir_x, 0, cota_atual))

  lista_pav.append(box)
  # print(f"Cota do pavimento {i} = {cota_atual}")
# print(lista_pav)

show(lista_pav)

# %%
# Atribui um label (nome) a cada pavimento e agrupa tudo em um Compound
for i, pav in enumerate(lista_pav):
    pav.label = f"pav_{i}"

assy = Compound(children=lista_pav)

# Exporta o Compound para um arquivo STEP
export_step(assy, "output.step")

# Alternativa: unir (fundir) os sÃ³lidos com "+" antes de exportar,
# equivalente ao mode="fused" do cq.Assembly.export() do CadQuery
# fused = lista_pav[0]
# for pav in lista_pav[1:]:
#     fused = fused + pav
# export_step(fused, "output.step")


