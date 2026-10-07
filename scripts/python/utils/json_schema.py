"""
utils/json_schema.py - Schemas JSON para NTs e MOCs.

Define a estrutura robusta de JSON para extracao de documentos fiscais.
"""

# Schema para NTs (Notas Tecnicas)
NT_SCHEMA = {
    "type": "object",
    "required": ["nt", "versao", "documento", "arquivo_origem", "sha256", "extraido_em", "tipo_documento"],
    "properties": {
        "nt": {"type": "string", "description": "Numero da NT (ex: 2025.001)"},
        "versao": {"type": "string", "description": "Versao da NT (ex: 1.14b)"},
        "documento": {"type": "string", "enum": ["NF-e", "CT-e", "MDF-e"]},
        "titulo": {"type": "string", "description": "Titulo da NT"},
        "arquivo_origem": {"type": "string", "description": "Caminho do arquivo original"},
        "sha256": {"type": "string", "description": "Hash SHA256 do arquivo"},
        "extraido_em": {"type": "string", "format": "date-time", "description": "Data/hora da extracao"},
        "tipo_documento": {"type": "string", "const": "NT"},
        "cronograma": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["versao", "homologacao", "producao"],
                "properties": {
                    "versao": {"type": "string"},
                    "homologacao": {"type": "string", "description": "Data literal (ex: Ate 05/10/2026)"},
                    "producao": {"type": "string"}
                }
            }
        },
        "secoes": {
            "type": "array",
            "items": {"$ref": "#/$defs/secao"}
        },
        "estatisticas": {"$ref": "#/$defs/estatisticas"}
    },
    "$defs": {
        "secao": {
            "type": "object",
            "required": ["numero", "titulo", "tipo"],
            "properties": {
                "numero": {"type": "string", "description": "Numero da secao (ex: 3, 3.1, 5)"},
                "titulo": {"type": "string", "description": "Titulo da secao"},
                "tipo": {"type": "string", "enum": ["tabela", "regras", "texto"]},
                "cabecalho": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Cabecalho da tabela (apenas para tipo tabela)"
                },
                "linhas": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "Linhas da tabela (apenas para tipo tabela)"
                },
                "regras": {
                    "type": "array",
                    "items": {"$ref": "#/$defs/regra"},
                    "description": "Regras de validacao (apenas para tipo regras)"
                },
                "paragrafos": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["texto"],
                        "properties": {
                            "texto": {"type": "string"},
                            "marcacao": {"type": "string"},
                            "pagina": {"type": "integer"}
                        }
                    },
                    "description": "Paragrafos de texto (apenas para tipo texto)"
                }
            }
        },
        "regra": {
            "type": "object",
            "required": ["id"],
            "properties": {
                "id": {"type": "string", "description": "ID da regra (ex: 001, C17-10, UB12-11)"},
                "modelo": {"type": "string", "description": "Modelo(s) do documento (ex: 55/65)"},
                "aplicacao": {"type": "string", "description": "Obrig./Facult./Futura"},
                "cStat": {"type": "string", "description": "Codigo de status (ex: 310)"},
                "efeito": {"type": "string", "description": "Rej./Aceito"},
                "mensagem": {"type": "string", "description": "Mensagem de rejeicao"},
                "condicao": {"type": "string", "description": "Condicao da regra"},
                "grupo": {"type": "string", "description": "Rotulo do grupo dentro da secao"},
                "marcacao": {"type": "string", "description": "AMARELO/VERDE/EXCLUIDO/SEM_MARCA"},
                "pagina": {"type": "integer"},
                "notas": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "texto": {"type": "string"},
                            "marcacao": {"type": "string"}
                        }
                    },
                    "description": "Linhas complementares (Excecao/Observacao)"
                },
                "texto_completo": {"type": "string", "description": "Texto bruto completo da regra"}
            }
        },
        "estatisticas": {
            "type": "object",
            "properties": {
                "total_secoes": {"type": "integer"},
                "total_regras": {"type": "integer"},
                "total_tabelas": {"type": "integer"},
                "por_marcacao": {
                    "type": "object",
                    "properties": {
                        "AMARELO": {"type": "integer"},
                        "VERDE": {"type": "integer"},
                        "EXCLUIDO": {"type": "integer"},
                        "SEM_MARCA": {"type": "integer"}
                    }
                }
            }
        }
    }
}

# Schema para MOCs (Manuais de Orientacao do Contribuinte)
MOC_SCHEMA = {
    "type": "object",
    "required": ["documento", "versao", "tipo_documento", "arquivo_origem", "sha256", "extraido_em"],
    "properties": {
        "documento": {"type": "string", "enum": ["NF-e", "CT-e", "MDF-e"]},
        "versao": {"type": "string", "description": "Versao do MOC (ex: 4.00)"},
        "tipo_documento": {"type": "string", "const": "MOC"},
        "titulo": {"type": "string", "description": "Titulo do MOC"},
        "arquivo_origem": {"type": "string", "description": "Caminho do arquivo original"},
        "sha256": {"type": "string", "description": "Hash SHA256 do arquivo"},
        "extraido_em": {"type": "string", "format": "date-time", "description": "Data/hora da extracao"},
        "secoes": {
            "type": "array",
            "items": {"$ref": "#/$defs/secao_moc"}
        },
        "regras_validacao": {
            "type": "array",
            "items": {"$ref": "#/$defs/regra_moc"}
        },
        "campos_leiaute": {
            "type": "array",
            "items": {"$ref": "#/$defs/campo_leiaute"}
        }
    },
    "$defs": {
        "secao_moc": {
            "type": "object",
            "required": ["numero", "titulo"],
            "properties": {
                "numero": {"type": "string", "description": "Numero da secao (ex: 1, 1.1, 2.3)"},
                "titulo": {"type": "string", "description": "Titulo da secao"},
                "subsecoes": {
                    "type": "array",
                    "items": {"$ref": "#/$defs/secao_moc"},
                    "description": "Subsecoes hierarquicas"
                }
            }
        },
        "regra_moc": {
            "type": "object",
            "required": ["id"],
            "properties": {
                "id": {"type": "string", "description": "ID da regra (ex: C17-10)"},
                "cStat": {"type": "string", "description": "Codigo de status (ex: 229)"},
                "descricao": {"type": "string", "description": "Descricao da regra"},
                "modelo": {"type": "string", "description": "Modelo do documento (ex: 55, 57, 58)"},
                "aplicacao": {"type": "string", "description": "Quem aplica (ex: todas as SEFAZ)"}
            }
        },
        "campo_leiaute": {
            "type": "object",
            "required": ["tag"],
            "properties": {
                "tag": {"type": "string", "description": "Nome da tag XML (ex: infCte)"},
                "tipo": {"type": "string", "description": "Tipo do campo (ex: TCTe, TDec_1302)"},
                "ocorrencia": {"type": "string", "description": "Ocorrencia (ex: 1-1, 0-1)"},
                "descricao": {"type": "string", "description": "Descricao do campo"}
            }
        }
    }
}


def get_nt_schema():
    """Retorna o schema para NTs."""
    return NT_SCHEMA


def get_moc_schema():
    """Retorna o schema para MOCs."""
    return MOC_SCHEMA


def validate_nt_json(json_data):
    """
    Valida se um JSON de NT esta conforme o schema.

    Returns:
        tuple: (is_valid, errors)
    """
    # Validacao basica - campos obrigatorios
    required = ["nt", "versao", "documento", "arquivo_origem", "sha256", "extraido_em", "tipo_documento"]
    errors = []

    for field in required:
        if field not in json_data:
            errors.append(f"Campo obrigatorio ausente: {field}")

    # Validar tipo_documento
    if json_data.get("tipo_documento") != "NT":
        errors.append(f"tipo_documento deve ser 'NT', encontrado: {json_data.get('tipo_documento')}")

    # Validar documento
    if json_data.get("documento") not in ["NF-e", "CT-e", "MDF-e"]:
        errors.append(f"documento invalido: {json_data.get('documento')}")

    # Validar secoes
    if "secoes" in json_data:
        for i, secao in enumerate(json_data["secoes"]):
            if "numero" not in secao:
                errors.append(f"secoes[{i}]: campo 'numero' ausente")
            if "titulo" not in secao:
                errors.append(f"secoes[{i}]: campo 'titulo' ausente")
            if "tipo" not in secao:
                errors.append(f"secoes[{i}]: campo 'tipo' ausente")
            elif secao["tipo"] not in ["tabela", "regras", "texto"]:
                errors.append(f"secoes[{i}]: tipo invalido: {secao['tipo']}")

    return len(errors) == 0, errors


def validate_moc_json(json_data):
    """
    Valida se um JSON de MOC esta conforme o schema.

    Returns:
        tuple: (is_valid, errors)
    """
    required = ["documento", "versao", "tipo_documento", "arquivo_origem", "sha256", "extraido_em"]
    errors = []

    for field in required:
        if field not in json_data:
            errors.append(f"Campo obrigatorio ausente: {field}")

    if json_data.get("tipo_documento") != "MOC":
        errors.append(f"tipo_documento deve ser 'MOC', encontrado: {json_data.get('tipo_documento')}")

    if json_data.get("documento") not in ["NF-e", "CT-e", "MDF-e"]:
        errors.append(f"documento invalido: {json_data.get('documento')}")

    return len(errors) == 0, errors