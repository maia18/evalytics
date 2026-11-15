import re
import unicodedata


ALIASES_CURSOS = {
    "eng telecom": "engenharia de telecomunicacoes",
}


def chave_curso(nome: str | None) -> str:
    """Gera uma chave estável para comparar nomes e variações históricas."""
    if not nome:
        return ""

    texto = unicodedata.normalize("NFKD", str(nome).casefold())
    texto = "".join(caractere for caractere in texto if not unicodedata.combining(caractere))
    texto = re.sub(r"[^a-z0-9]+", " ", texto).strip()
    texto = re.sub(r"\s+", " ", texto)
    return ALIASES_CURSOS.get(texto, texto)


def normalizar_nome_curso(
    nome: str | None,
    nomes_cadastrados: list[str] | None = None,
) -> str:
    """Retorna a grafia do cadastro para variações equivalentes do mesmo curso."""
    if not nome or not str(nome).strip():
        return "Curso não informado"

    nome_limpo = " ".join(str(nome).split())
    chave = chave_curso(nome_limpo)

    for cadastrado in nomes_cadastrados or []:
        if chave_curso(cadastrado) == chave:
            return " ".join(str(cadastrado).split())

    if chave == "engenharia de telecomunicacoes":
        return "Engenharia de Telecomunicações"

    return nome_limpo


def criar_indice_cursos_atuais(
    cursos_cadastrados: list[dict],
) -> tuple[dict[str, dict], dict[str, dict]]:
    """Cria índices por ID e nome para validar avaliações contra o catálogo."""
    por_id: dict[str, dict] = {}
    por_nome: dict[str, dict] = {}
    for curso in cursos_cadastrados:
        if curso.get("id"):
            por_id[str(curso["id"])] = curso
        nome = str(curso.get("nome", "")).strip()
        chave = chave_curso(nome)
        if chave:
            por_nome.setdefault(chave, curso)
    return por_id, por_nome


def resolver_curso_avaliacao(
    avaliacao: dict,
    indice_cursos: tuple[dict[str, dict], dict[str, dict]],
) -> dict | None:
    """Retorna o curso atual da avaliação ou None se ele foi removido.

    Quando a avaliação tem curso_id, ele é a identidade canônica: um ID removido
    não pode ser reassociado a um curso recriado com o mesmo nome. Avaliações
    antigas sem ID podem ser validadas pelo nome.
    """
    por_id, por_nome = indice_cursos
    curso_id = str(avaliacao.get("curso_id") or "").strip()
    if curso_id:
        return por_id.get(curso_id)

    nome = avaliacao.get("curso_nome") or avaliacao.get("curso")
    if not nome:
        return None
    return por_nome.get(chave_curso(str(nome)))


def listar_nomes_cursos_filtraveis(
    resultados: list[dict],
    cursos_cadastrados: list[dict],
) -> list[str]:
    """Lista apenas os cursos do catálogo atual para filtros da interface.

    Avaliações antigas podem continuar armazenando nomes de cursos removidos;
    esses nomes permanecem nos dados históricos, mas não devem voltar a aparecer
    como opções dos filtros.
    """
    nomes_cadastrados = [
        str(curso.get("nome", "")).strip()
        for curso in cursos_cadastrados
        if curso.get("nome") and str(curso.get("nome")).strip()
    ]
    nomes_por_chave = {
        chave_curso(nome): normalizar_nome_curso(nome, nomes_cadastrados)
        for nome in nomes_cadastrados
    }
    return sorted(set(nomes_por_chave.values()), key=str.casefold)


def chave_departamento(nome: str | None) -> str:
    """Cria uma chave de comparação de departamento sem diferenças de caixa."""
    return " ".join(str(nome or "").split()).casefold()


def listar_cursos_associados_ao_coordenador(
    cursos: list[dict], email: str | None = None
) -> list[dict]:
    """Lista cursos atribuídos explicitamente ao e-mail do coordenador."""
    if email is None:
        try:
            from components.core.auth.auth_state import auth_state

            email = str((auth_state.usuario or {}).get("email") or "")
        except (AttributeError, TypeError):
            return []

    email_normalizado = str(email).strip().casefold()
    if not email_normalizado:
        return []
    return [
        curso
        for curso in cursos
        if str(
            curso.get("coordenador_email") or curso.get("coordenador") or ""
        ).strip().casefold() == email_normalizado
    ]


def filtrar_cursos_por_coordenador(cursos: list[dict]) -> list[dict]:
    """Limita cursos ao vínculo autenticado e ao curso ativo selecionado."""
    try:
        from components.core.auth.auth_state import auth_state

        usuario = auth_state.usuario or {}
    except (AttributeError, TypeError):
        return cursos

    email = str(usuario.get("email") or "").strip().casefold()
    perfil = str(
        usuario.get("papel")
        or usuario.get("role")
        or usuario.get("perfil")
        or usuario.get("tipo_usuario")
        or ""
    ).strip().casefold()
    eh_coordenador = perfil in {"coordenador", "coordinator", "coordenador_curso"}
    atribuidos = listar_cursos_associados_ao_coordenador(cursos, email)
    if atribuidos:
        curso_id_ativo = str(usuario.get("curso_id_ativo") or "").strip()
        if curso_id_ativo and curso_id_ativo != "*":
            curso_selecionado = [
                curso for curso in atribuidos
                if str(curso.get("id") or "") == curso_id_ativo
            ]
            return curso_selecionado or atribuidos
        return atribuidos
    if not email:
        return [] if eh_coordenador else cursos
    return [] if eh_coordenador else cursos


def chave_escopo_cursos(cursos: list[dict]) -> str:
    """Gera uma chave determinística para caches de análises por catálogo."""
    ids = sorted(str(curso.get("id") or chave_curso(curso.get("nome"))) for curso in cursos)
    return ",".join(ids)


def listar_departamentos_unicos(cursos: list[dict]) -> list[str]:
    """Agrupa grafias equivalentes e prefere a versão em caixa alta, se existir."""
    nomes_por_chave: dict[str, str] = {}
    for curso in cursos:
        nome = " ".join(str(curso.get("departamento", "")).split())
        chave = chave_departamento(nome)
        if not chave:
            continue

        atual = nomes_por_chave.get(chave)
        if atual is None or (nome.isupper() and not atual.isupper()):
            nomes_por_chave[chave] = nome

    return sorted(nomes_por_chave.values(), key=str.casefold)


def nome_departamento_exibicao(nome: str | None, cursos: list[dict]) -> str:
    """Retorna a grafia canônica visível para um departamento."""
    chave = chave_departamento(nome)
    for departamento in listar_departamentos_unicos(cursos):
        if chave_departamento(departamento) == chave:
            return departamento
    return " ".join(str(nome or "").split())
