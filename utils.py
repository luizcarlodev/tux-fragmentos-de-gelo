def checar_colisao(rect1, rect2):
    return rect1.colliderect(rect2)


def limitar(valor, minimo, maximo):
    if valor < minimo:
        return minimo
    if valor > maximo:
        return maximo
    return valor