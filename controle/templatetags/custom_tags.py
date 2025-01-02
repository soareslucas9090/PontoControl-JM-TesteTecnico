from django import template

register = template.Library()


@register.filter(name="add_class")
def add_class(value, arg):
    """
    Adiciona uma classe CSS a um campo de formulário no Django.

    Parâmetros:
        value (BoundField): O campo do formulário a ser modificado.
        arg (str): A classe CSS a ser adicionada ao widget.

    Retorna:
        SafeText: O widget do campo renderizado com a classe CSS adicionada.
    """
    return value.as_widget(attrs={"class": arg})
