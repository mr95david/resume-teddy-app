#

TYPE_FILE : list = ["pdf"]
TYPE_IMG  : list = ["jpg", "jpeg", "png"]

URL_PATTERN = (
    r"(?:https?://)?(?:www\.)?[a-zA-Z0-9.-]+"
    r"\.[a-zA-Z]{2,}(?:\.[a-zA-Z]{2,})?" 
    r"(?:/[a-zA-Z0-9._/~:%+#&=?-]*)?"
)

resume_keywords_en = [
    "experience", "education", "skills", "qualification",
    "projects", "certification", "work", "employment",
    "job", "profile", "accomplishment", "achievement",
    "responsibility", "university", "college", "degree",
]

resume_keywords_es = [
    "experiencia", "educacion", "habilidades", "competencias",
    "proyectos", "certificaciones", "trabajo", "empleo",
    "perfil", "logros", "responsabilidades", "universidad",
    "colegio", "titulo", "formacion",
]

resume_keywords_pt = [
    "experiencia", "educacao", "habilidades", "competencias",
    "projetos", "certificacoes", "trabalho", "emprego",
    "perfil", "conquistas", "responsabilidades", "universidade",
    "faculdade", "graduacao", "formacao",
]

TESSERACT_LANGS = "eng+spa+por"
