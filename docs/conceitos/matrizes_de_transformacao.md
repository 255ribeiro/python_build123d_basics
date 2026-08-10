# Matrizes de Transformação 3D
> Base matemática aplicável a CadQuery, Blender, Rhino/Grasshopper e qualquer sistema de coordenadas 3D.

---

## 1. Transformações Homogêneas

Uma [transformação geométrica](https://mathworld.wolfram.com/GeometricTransformation.html) é qualquer operação que mapeia pontos de um espaço em outros pontos do mesmo espaço. Quando essas transformações preservam retas (mas não necessariamente ângulos ou distâncias), elas são chamadas de [transformações afins](https://mathworld.wolfram.com/AffineTransformation.html) — e incluem translação, rotação, escala e cisalhamento.

O problema é que translação **não é uma [transformação linear](https://mathworld.wolfram.com/LinearTransformation.html)**: ela não pode ser expressa como multiplicação por uma matriz 3×3. Para resolver isso, utiliza-se o artifício das **[coordenadas homogêneas](https://mathworld.wolfram.com/HomogeneousCoordinates.html)**: adiciona-se uma dimensão extra ao espaço, elevando um ponto 3D `(x, y, z)` à representação `(x, y, z, 1)` em R⁴.

Nesse espaço aumentado, **todas as transformações afins — incluindo translação — tornam-se multiplicações de matrizes 4×4**. Isso é o que define uma **[transformação homogênea](https://mathworld.wolfram.com/HomogeneousMatrix.html)**: a unificação de qualquer combinação de translação, rotação e escala em uma única matriz, aplicável em uma única operação de [multiplicação matricial](https://mathworld.wolfram.com/MatrixMultiplication.html).

A consequência prática é poderosa: múltiplas transformações podem ser **compostas** (multiplicadas entre si) em uma única matriz `M` antes de serem aplicadas à geometria — economizando operações e eliminando ambiguidades de ordem.

### Estrutura geral da matriz 4×4

```
M = | r00  r01  r02  tx |
    | r10  r11  r12  ty |
    | r20  r21  r22  tz |
    |  0    0    0    1 |
```

- A **submatriz 3×3 superior esquerda** (`rij`) contém rotação e/ou escala
- A **4ª coluna** (`tx, ty, tz`) contém a translação
- A **4ª linha** é sempre `[0, 0, 0, 1]` para [transformações afins](https://mathworld.wolfram.com/AffineTransformation.html)

A [matriz identidade](https://mathworld.wolfram.com/IdentityMatrix.html) representa a ausência de qualquer transformação:

```
I = | 1  0  0  0 |
    | 0  1  0  0 |
    | 0  0  1  0 |
    | 0  0  0  1 |
```

---

## 2. Translação

[Translação](https://mathworld.wolfram.com/Translation.html) é mover um objeto no espaço sem alterar sua forma ou orientação. É a transformação mais simples, mas a única que exige coordenadas homogêneas para ser expressa matricialmente.

```
T(tx, ty, tz) = | 1  0  0  tx |
                | 0  1  0  ty |
                | 0  0  1  tz |
                | 0  0  0   1 |
```

### Exemplo

Transladar o ponto `P = (2, 3, 0)` por `(5, -1, 10)`:

```
| 1  0  0  5  |   | 2 |   | 7  |
| 0  1  0 -1  | × | 3 | = | 2  |
| 0  0  1  10 |   | 0 |   | 10 |
| 0  0  0  1  |   | 1 |   | 1  |
```

### Em código

```python
# CadQuery
m = cq.Matrix([
    [1, 0, 0, tx],
    [0, 1, 0, ty],
    [0, 0, 1, tz],
    [0, 0, 0,  1]
])
shape.transformGeometry(m)
```

```python
# Blender (mathutils)
import mathutils
m = mathutils.Matrix.Translation((tx, ty, tz))
obj.matrix_world = m @ obj.matrix_world
```

---

## 3. Escala

A [escala](https://mathworld.wolfram.com/ScalingMatrix.html) altera o tamanho do objeto em um ou mais eixos, sempre em relação à origem do sistema de coordenadas.

### Escala uniforme (todos os eixos iguais)

```
S(s) = | s  0  0  0 |
       | 0  s  0  0 |
       | 0  0  s  0 |
       | 0  0  0  1 |
```

### Escala não-uniforme (eixos independentes)

```
S(sx, sy, sz) = | sx  0   0   0 |
                |  0  sy  0   0 |
                |  0   0  sz  0 |
                |  0   0   0  1 |
```

Configurar `sz = 1` mantém a altura intacta enquanto XY é escalado — exatamente o caso de uso do algoritmo de pavimentos apresentado neste material.

### Importante: escala e ordem de operações

Como a escala opera em relação à origem, um objeto fora da origem será também **movido** ao ser escalado. A ordem correta de operações é sempre:

```
1. Posicionar na origem
2. Aplicar escala
3. Aplicar rotação
4. Aplicar translação final
```

Ou em [notação matricial](https://mathworld.wolfram.com/MatrixMultiplication.html) (lida da direita para a esquerda):

```
M = T × R × S
```

---

## 4. Rotação

### 4.1 Rotação em torno dos eixos canônicos

As [matrizes de rotação](https://mathworld.wolfram.com/RotationMatrix.html) em torno dos eixos canônicos são derivadas diretamente da geometria do [círculo unitário](https://mathworld.wolfram.com/UnitCircle.html), usando seno e cosseno para projetar o ângulo `θ` nos eixos perpendiculares.

**Rotação em torno de Z ([yaw](https://en.wikipedia.org/wiki/Aircraft_principal_axes)):**
```
Rz(θ) = | cos θ  -sin θ  0  0 |
         | sin θ   cos θ  0  0 |
         |   0       0    1  0 |
         |   0       0    0  1 |
```

**Rotação em torno de X ([pitch](https://en.wikipedia.org/wiki/Aircraft_principal_axes)):**
```
Rx(θ) = | 1    0       0    0 |
         | 0  cos θ  -sin θ  0 |
         | 0  sin θ   cos θ  0 |
         | 0    0       0    1 |
```

**Rotação em torno de Y ([roll](https://en.wikipedia.org/wiki/Aircraft_principal_axes)):**
```
Ry(θ) = |  cos θ  0  sin θ  0 |
         |    0    1    0    0 |
         | -sin θ  0  cos θ  0 |
         |    0    0    0    1 |
```

### 4.2 O problema: Gimbal Lock

Quando rotações são aplicadas sequencialmente em eixos fixos (convenção de [ângulos de Euler](https://mathworld.wolfram.com/EulerAngles.html)), surge o **[Gimbal Lock](https://en.wikipedia.org/wiki/Gimbal_lock)** (travamento de cardan): quando dois dos três eixos de rotação se alinham, **um grau de liberdade é perdido**.

Imagine três aros concêntricos (um [cardan mecânico](https://en.wikipedia.org/wiki/Gimbal)): cada aro representa um eixo de rotação. Quando o aro intermediário gira 90°, o aro interno e o externo ficam no mesmo plano — e o sistema perde um eixo de controle. Qualquer rotação tentada no eixo "perdido" simplesmente duplica outro eixo existente.

**Consequências práticas:**

- Animações com interpolação de Euler apresentam saltos e rotações inesperadas
- Objetos em certas orientações se recusam a rotacionar no eixo desejado
- O problema é **intrínseco à representação**, não um bug de software

**Como identificar:**

No Blender, Rhino ou qualquer editor 3D: rotacione um objeto até que dois eixos do gizmo (manipulador de rotação) fiquem coplanares — o objeto passará a rotacionar de forma estranha em torno desses eixos.

### 4.3 A solução: Quaternions

Um [quaternion](https://mathworld.wolfram.com/Quaternion.html) é uma extensão dos [números complexos](https://mathworld.wolfram.com/ComplexNumber.html) com quatro componentes, introduzido por William Rowan Hamilton em 1843:

```
q = w + xi + yj + zk
```

Onde:
- `w` é a parte escalar (real)
- `x, y, z` são as partes vetoriais (imaginárias)
- `i, j, k` são [unidades imaginárias](https://mathworld.wolfram.com/ImaginaryUnit.html) com as propriedades:
  ```
  i² = j² = k² = ijk = -1
  ```

### Quaternion de rotação

Para representar uma [rotação por quaternion](https://en.wikipedia.org/wiki/Quaternions_and_spatial_rotation) de ângulo `θ` em torno de um [vetor unitário](https://mathworld.wolfram.com/UnitVector.html) `(ax, ay, az)`:

```
w = cos(θ/2)
x = ax × sin(θ/2)
y = ay × sin(θ/2)
z = az × sin(θ/2)
```

Um quaternion de rotação válido é sempre **[unitário](https://mathworld.wolfram.com/UnitQuaternion.html)**: `w² + x² + y² + z² = 1`

### Por que quaternions resolvem o Gimbal Lock?

Quaternions representam rotações como **uma única operação no [espaço 4D](https://mathworld.wolfram.com/Four-DimensionalSpace.html)**, sem decompor em eixos sequenciais. Como não há sequência de eixos, não há como dois deles se alinharem — o [Gimbal Lock](https://en.wikipedia.org/wiki/Gimbal_lock) simplesmente não existe nessa representação.

Além disso, quaternions permitem **interpolação suave** entre duas orientações através da operação **[SLERP](https://en.wikipedia.org/wiki/Slerp)** (Spherical Linear Interpolation):

```
slerp(q1, q2, t) = q1 × (q1⁻¹ × q2)^t,   t ∈ [0, 1]
```

SLERP garante velocidade angular constante ao longo do caminho mais curto entre duas orientações — impossível com Euler sem artefatos.

### Conversão quaternion → matriz 4×4

```
R = | 1-2(y²+z²)   2(xy-wz)    2(xz+wy)   0 |
    |  2(xy+wz)   1-2(x²+z²)   2(yz-wx)   0 |
    |  2(xz-wy)    2(yz+wx)   1-2(x²+y²)  0 |
    |     0            0           0       1 |
```

### 4.4 Como evitar o Gimbal Lock na prática

| Programa | Solução |
|---|---|
| **Blender** | Usar modo de rotação **Quaternion** no painel de propriedades do objeto (N panel → Item → Rotation Mode) |
| **Rhino/Grasshopper** | Usar o componente `Rotate` com eixo arbitrário em vez de rotações sequenciais XYZ |
| **CadQuery** | `.rotate(ponto_eixo1, ponto_eixo2, angulo)` opera sobre um eixo arbitrário — internamente usa quaternion |
| **Qualquer programa** | Preferir rotações em torno de um **eixo arbitrário** em vez de compor rotações X + Y + Z separadas |

---

## 5. Composição de Transformações

A grande vantagem das [matrizes homogêneas](https://mathworld.wolfram.com/HomogeneousMatrix.html) é a **composição**: qualquer sequência de transformações pode ser [multiplicada](https://mathworld.wolfram.com/MatrixMultiplication.html) em uma única matriz `M`, aplicada de uma vez à geometria.

```
M = T × R × S
```

**Atenção:** a [multiplicação de matrizes](https://mathworld.wolfram.com/MatrixMultiplication.html) **não é [comutativa](https://mathworld.wolfram.com/Commutative.html)** — a ordem importa.

```
T × R ≠ R × T
```

Transladar depois de rotacionar produz resultado diferente de rotacionar depois de transladar. A convenção mais comum (e intuitiva) é:

```
1. Scale   (S) — dimensionar em torno da origem
2. Rotate  (R) — orientar em torno da origem
3. Translate (T) — posicionar no mundo
```

### Exemplo combinado em CadQuery

```python
import cadquery as cq
import numpy as np

# Parâmetros
sx, sy, sz = 2.0, 2.0, 1.0   # escala XY dupla, Z intacto
angulo = 45                    # graus
tx, ty, tz = 10, 0, 5         # translação

rad = np.radians(angulo)
cos, sin = np.cos(rad), np.sin(rad)

# Matriz composta M = T × Rz × S
m = cq.Matrix([
    [sx*cos, -sy*sin, 0,  tx],
    [sx*sin,  sy*cos, 0,  ty],
    [0,       0,      sz, tz],
    [0,       0,      0,   1]
])

shape_transformado = shape.transformGeometry(m)
```

---

## 6. Resumo Visual

```
Translação            Escala                Rotação Z
| 1  0  0  tx |      | sx  0   0   0 |     | cos -sin  0  0 |
| 0  1  0  ty |      |  0  sy  0   0 |     | sin  cos  0  0 |
| 0  0  1  tz |      |  0   0  sz  0 |     |  0    0   1  0 |
| 0  0  0   1 |      |  0   0   0  1 |     |  0    0   0  1 |

Identidade
| 1  0  0  0 |
| 0  1  0  0 |
| 0  0  1  0 |
| 0  0  0  1 |
```

---

## 7. Referências

- [Geometric Transformation](https://mathworld.wolfram.com/GeometricTransformation.html) — MathWorld
- [Affine Transformation](https://mathworld.wolfram.com/AffineTransformation.html) — MathWorld
- [Linear Transformation](https://mathworld.wolfram.com/LinearTransformation.html) — MathWorld
- [Homogeneous Coordinates](https://mathworld.wolfram.com/HomogeneousCoordinates.html) — MathWorld
- [Homogeneous Matrix](https://mathworld.wolfram.com/HomogeneousMatrix.html) — MathWorld
- [Rotation Matrix](https://mathworld.wolfram.com/RotationMatrix.html) — MathWorld
- [Scaling Matrix](https://mathworld.wolfram.com/ScalingMatrix.html) — MathWorld
- [Euler Angles](https://mathworld.wolfram.com/EulerAngles.html) — MathWorld
- [Quaternion](https://mathworld.wolfram.com/Quaternion.html) — MathWorld
- [Unit Quaternion](https://mathworld.wolfram.com/UnitQuaternion.html) — MathWorld
- [Identity Matrix](https://mathworld.wolfram.com/IdentityMatrix.html) — MathWorld
- [Gimbal Lock](https://en.wikipedia.org/wiki/Gimbal_lock) — Wikipedia
- [Quaternions and spatial rotation](https://en.wikipedia.org/wiki/Quaternions_and_spatial_rotation) — Wikipedia
- [SLERP](https://en.wikipedia.org/wiki/Slerp) — Wikipedia
- [Aircraft principal axes (yaw/pitch/roll)](https://en.wikipedia.org/wiki/Aircraft_principal_axes) — Wikipedia
