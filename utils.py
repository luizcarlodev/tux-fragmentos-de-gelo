def checar_colisao(rect1, rect2):
    return rect1.colliderect(rect2)


def limitar(valor, minimo, maximo):
    return max(minimo, min(valor, maximo))
