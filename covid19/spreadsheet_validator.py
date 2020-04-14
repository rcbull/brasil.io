from django.forms import ValidationError


def format_spreadsheet_rows_as_dict(rows):
    """
    Receives rows as a rows.Table object and return a dict in the following format:

    {
    'total': {'confirmados': 100, 'mortes': 30},
    'importados_indefinidos': {'confirmados': 2, 'mortes': 1},
    'cidades': {
        'Cidade1': {'confirmados': 9, 'mortes': 1},
        'Cidade2': {'confirmados': 11, 'mortes': 2},
        ...
    }

    This is an auxiliary method used by covid19.forms.StateSpreadsheetForm with the uploaded file
    """
    # TODO: https://github.com/turicas/brasil.io/issues/209
    # TODO: https://github.com/turicas/brasil.io/issues/210
    result = {
        'total': {},
        'importados_indefinidos': {},
        'cidades': {},
    }

    confirmed_field_name = _get_field_name(rows, ['confirmados', 'confirmado', 'casos_confirmados'])
    if confirmed_field_name is None:
        raise ValidationError('A coluna "Confirmados" está faltando na planilha')
    deaths_field_name = _get_field_name(rows, ['obitos', 'obito', 'morte', 'mortes'])
    if deaths_field_name is None:
        raise ValidationError('A coluna "Mortes" está faltando na planilha')

    TOTAL_LINE_DISPLAY = 'TOTAL NO ESTADO'
    UNDEFINED_DISPLAY = 'Importados/Indefinidos'
    for entry in rows:
        try:
            city = entry.municipio
        except AttributeError:
            raise ValidationError('A coluna "Município" está faltando na planilha')

        confirmed = getattr(entry, confirmed_field_name)
        deaths = getattr(entry, deaths_field_name)
        data = {'confirmados': confirmed, 'mortes': deaths}

        if city == TOTAL_LINE_DISPLAY:
            result['total'] = data
        elif city == UNDEFINED_DISPLAY:
            result['importados_indefinidos'] = data
        else:
            result['cidades'][city] = data

    if not result['total']:
        raise ValidationError(f'A linha "{TOTAL_LINE_DISPLAY}" está faltando na planilha')
    elif not result['importados_indefinidos']:
        raise ValidationError(f'A linha "{UNDEFINED_DISPLAY}" está faltando na planilha')

    return result


def _get_field_name(rows, valid_names):
    try:
        return [n for n in valid_names if n in rows.field_names][0]
    except IndexError:
        return None
