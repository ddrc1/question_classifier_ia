import pandas as pd

question_df: pd.DataFrame = pd.read_json('./anexos/questoes.jsonl', lines=True)
question_df = question_df[question_df.columns[:-2]]
question_df.rename(
    columns={
        "id": "question_id", 
        "enunciado_html": "question", 
        "comando": "prompt", 
        "alternativas": "options"},
    inplace=True)

question_df["options"] = question_df["options"].apply(lambda x: "\n".join(list(x.values())))
question_list: list[dict] = question_df.to_dict(orient="records")

subject_df: pd.DataFrame = pd.read_csv("./anexos/temas.csv")
subject_df.rename(columns={"tema_id": "subject_id", "titulo": "name"}, inplace=True)

df_active: pd.DataFrame = subject_df[subject_df["status"] == "active"]
df_root_subject: pd.DataFrame = df_active[df_active["nivel"] == 0]
df_child_subject: pd.DataFrame = df_active[df_active["nivel"] == 1]

df_root_subject = df_root_subject[["subject_id", "name"]]
df_child_subject = df_child_subject[["parent_id", "subject_id", "name"]]
multi_part_child_subjects: list[str] = [
    'Dos Crimes Contra a Administração Pública',
    'Dos Crimes Contra a Administração Pública (Parte 1)',
    'Dos Crimes contra a Administração Pública (Parte 2)',
    'Dos Crimes Contra o Patrimônio',
    'Dos Crimes Contra o Patrimônio (Parte 1)',
    'Dos Crimes contra o Patrimônio (Parte 2)',
    'Teoria da Pena',
    'Teoria da Pena (Parte 1)',
    'Teoria da Pena (Parte 2)',
    'Competência',
    'Competência (Parte 1)',
    'Competência (Parte 2)',
    'Sentença Penal',
    'Sentença Penal (Parte 1)',
    'Sentença Penal (Parte 2)',
    'Recursos em Espécies (Parte 3)',
    'Recursos em Espécies'
]

multipart_child_keep: list[str] = [subject for subject in multi_part_child_subjects if not "parte" in subject.lower()]
multipart_child_remove: list[str] = [subject for subject in multi_part_child_subjects if "parte" in subject.lower()]

df_child_subject = df_child_subject[~df_child_subject["name"].isin(multipart_child_remove)]

subject_tree: list[dict] = df_root_subject.apply(
    lambda x: 
        {
            "parent": x.to_dict(), 
            "subject_branch": df_child_subject[df_child_subject["parent_id"] == x.subject_id][["subject_id", "name"]].to_dict(orient="records")
        }, 
    axis=1)

def get_subject_tree():
    return subject_tree

def get_questions():
    return question_list

def get_removed_multipart_child_subjects() -> list[str]:
    return multipart_child_remove

def get_main_part_multipart_child_subjects() -> list[str]:
    return multipart_child_keep
