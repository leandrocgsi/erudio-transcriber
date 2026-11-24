import unicodedata

CONNECTORS = frozenset({"de", "da", "do", "das", "dos", "e", "of", "the", "and", "for", "to", "para"})

_WORDS = """
a o as os um uma uns umas ao aos num numa de da do das dos em no na nos nas por pelo pela pelos pelas
para pra com sem sobre entre ate desde apos ante contra durante perante sob tras e ou mas que se
como quando onde qual quais quem quanto quantos este esta estes estas esse essa esses essas isso isto
aquilo aquele aquela aqui ali la ca ai muito muita muitos muitas mais menos nao sim ja ainda
tambem entao pois porque porem logo assim bem mal tudo todo toda todos todas nada algo alguem
ninguem cada outro outra outros outras mesmo mesma proprio propria seu sua seus suas meu minha meus
minhas teu tua nosso nossa voce voces eu tu ele ela eles elas nos me te lhe lhes si ser estar ter haver
fazer ir vir foi era sao estao tem tinha vai vou fui sera seria pode podem deve devem
the an or but in on with this that these those it is are was were be been not no yes how what when where
which who why from by at as if so we you they he she his her our your their my me
introducao aula modulo parte passo exemplo slide pagina curso conteudo resumo objetivo objetivos dica
dicas importante atencao material apoio sumario item valor time criando metodos
empresa empresas contato contatos email telefone fones fone local clientes cliente site perfil data
ultimo ultima cargo cidade bairro avenida rua endereco nome numero numeros documento documentos
experiencia experiencias formacao curriculo vaga vagas trabalho emprego salario salarios entrevista
entrevistas projeto projetos tecnologia tecnologias desenvolvimento desenvolvedor analista
coordenador instrutor atuar atualmente
janeiro fevereiro marco abril maio junho julho agosto setembro outubro novembro dezembro
segunda terca quarta quinta sexta sabado domingo
fulano fulaninho ciclano beltrano xyz ert link anexo seguem segue obrigado obrigada ola bom boa dia
tarde noite
nesse nunca jamais minta uf mg ti mp3 mp4 pdf txt png jpg docx xlsx html htm csv avi mkv mov
"""


def fold(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", text.lower())
    return "".join(char for char in decomposed if unicodedata.category(char) != "Mn")


COMMON = frozenset(fold(word) for word in _WORDS.split())
