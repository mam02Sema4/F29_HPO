import sys
import pandas as pd

labels = sys.argv[1]
synonyms = sys.argv[2]
dictionary = sys.argv[3]
template = sys.argv[4]

df_labels = pd.read_csv(labels)
df_labels.columns = ['term','annotation']
df_labels = df_labels.astype(str)
print("Labels: {}".format(len(df_labels)))

df_synonyms = pd.read_csv(synonyms)
df_synonyms.columns = ['term','annotation']
df_synonyms=df_synonyms.dropna()
df_synonyms = df_synonyms.astype(str)
print("Synonyms: {}".format(len(df_synonyms)))

print(df_synonyms.head())
print(df_labels.head())

df_dict = pd.read_csv(dictionary)
df_dict.columns = ['be','ae']
df_dict = df_dict.astype(str)
print("Dictionary: {}".format(len(df_dict)))

df_dict_cap = df_dict.copy()
df_dict_cap = df_dict_cap.astype(str)
df_dict_cap['ae']=df_dict_cap['ae'].str.capitalize()
df_dict_cap['be']=df_dict_cap['be'].str.capitalize()
df_dict=df_dict.append(df_dict_cap,ignore_index = True)
df_dict=df_dict.set_index('ae').T.to_dict('list')

def translate_be(df, dict):
	be = []
	for label in df['annotation']:
		new_label = []
		for lsub in label.split(" "):
			if lsub in dict:
				new_label.append(dict[lsub][0])
			else:
				new_label.append(lsub)
		be.append(" ".join(new_label))
	return be

df_labels['be']=translate_be(df_labels,df_dict)
df_synonyms['be']=translate_be(df_synonyms,df_dict)

df_be_syns = df_labels[['term','be']].dropna()
df_be_syns.append(df_synonyms[['term','be']].dropna(),ignore_index = True)

print(df_be_syns.head())

df_rem = df_labels[['term','be']]
df_rem = df_rem.append(df_synonyms[['term','be']])
df_rem.drop_duplicates(inplace=True)

df_be_syns.drop_duplicates(inplace=True)

df_be_syns=df_be_syns[~df_be_syns['be'].isin(df_synonyms['annotation'].tolist())]
df_be_syns=df_be_syns[~df_be_syns['be'].isin(df_labels['annotation'].tolist())]
df_be_syns['Type']="http://purl.obolibrary.org/obo/hp#uk_spelling"
df_be_syns.loc[-1] = ['ID', 'A http://www.geneontology.org/formats/oboInOwl#hasExactSynonym','>AI http://www.geneontology.org/formats/oboInOwl#hasSynonymType']  # adding a row
df_be_syns.index = df_be_syns.index + 1  # shifting index
df_be_syns.sort_index(inplace=True) 

print(df_be_syns.head())
print(len(df_be_syns))
df_be_syns.columns = ['ID','Synonym','Type']


df_be_syns.to_csv(template, index=False)
