import torch
import pandas as pd
import json
import numpy as np
import faiss
import time
import os
import sys
from transformers import AutoTokenizer, AutoModel
from tqdm import tqdm
os.environ['KMP_DUPLICATE_LIB_OK']='True'

# !pip install tqdm boto3 requests regex sentencepiece sacremoses
# !pip install faiss-cpu

class BERT_indexer():
    # tokenizer = AutoTokenizer.from_pretrained("google-bert/bert-base-uncased")
    # model = AutoModel.from_pretrained("google-bert/bert-base-uncased")

    # tokenizer = AutoTokenizer.from_pretrained("distilbert/distilbert-base-uncased")
    # model = AutoModel.from_pretrained("distilbert/distilbert-base-uncased")

    tokenizer = AutoTokenizer.from_pretrained("google-bert/bert-base-multilingual-uncased")
    model = AutoModel.from_pretrained("google-bert/bert-base-multilingual-uncased")

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)

    string_list = []
    embedding_list = []
    index = faiss.IndexFlatIP(768)
    index_time = 0

    def read_json(self, file):
        f = open(file)
        data = json.load(f)
        self.movie_json = data

    def read_file(self, string_file):
        self.file = string_file
        # f = open(self.file, "r", encoding="utf-8")
        with open(self.file, "r", encoding="utf-8") as f:
            self.string_list = f.readlines()

    def index_json_batch(self):
        start_time = time.time()
        list_cnt = 0
        for movie in tqdm(self.movie_json):
            # if list_cnt==2000: break
            # get string
            title = movie["title"]
            # genres = movie["genres"]
            # genres = genres.split(", ")
            genres = ""
            for g in movie["genres"].split(","):
                if g is not None:
                    # writers += (writer + ",")
                    genres += (g + " ")
            genres = genres.strip()
            directors = ""
            for director in movie["directors Names"]:
                if director is not None:
                    # directors += (director + ",")
                    directors += (director + " ")
            if directors == "":
                directors = "Unknown"
                # directors = ""
            else:
                directors = directors[:-1]
            writers = ""
            for writer in movie["writer Names"]:
                if writer is not None:
                    # writers += (writer + ",")
                    writers += (writer + " ")
            if writers == "":
                writers = "Unknown"
                # writers = ""
            else:
                writers = writers[:-1]
            summary = movie["synopsis"] if len(movie["synopsis"]) > 0 else "Unknown"

            input = f"{title} {genres} {directors} {writers} {summary}"
            input = str(input)
            # input = str(title)
            # input = f"the movie title is {title}. The genres of this movie are: {genres}. This movie is directed by {directors}. The writers of this movie are {writers}. The plot synopsis is: {summary}"
            self.string_list.append(input)
            list_cnt+=1
        # self.write_string_list('batch-strings.txt')

        batch_size = 100
        batch_list = [self.string_list[i:i + batch_size] for i in range(0, len(self.string_list), batch_size)]

        for input in tqdm(batch_list):
            # start embedding
            token = self.tokenizer(input, add_special_tokens=True, truncation=True, padding='max_length',  max_length=512, return_tensors='pt', return_token_type_ids=False)
            # put data on GPU
            for k,v in token.items():
                token[k] = v.to(self.device)
            self.model.warn_if_padding_and_no_attention_mask(token['input_ids'], token['attention_mask'])
            with torch.no_grad():
                embedding = self.model(**token).last_hidden_state
            # mask = token['attention_mask'].unsqueeze(-1).expand(embedding.size()).float()
            # embedding = (embedding*mask)
            embedding = embedding.mean(1).cpu().numpy()
            # print(embedding.shape)
            faiss.normalize_L2(embedding)
            self.index.add(embedding)

        self.index_time = time.time() - start_time
        print("Execution Time: %s seconds" % self.index_time)
        return self.index_time

    def write_string_list(self, output):
        with open(output, "w", encoding="utf-8") as f:
            for line in self.string_list:
                f.write(f"{line}\n")

    def write_index(self, name):
        faiss.write_index(self.index, name)

    def read_index(self, index_to_read):
        self.index = faiss.read_index(index_to_read)

class search_bert_index():
    # tokenizer = AutoTokenizer.from_pretrained("google-bert/bert-base-uncased")
    # model = AutoModel.from_pretrained("google-bert/bert-base-uncased")
    # tokenizer = AutoTokenizer.from_pretrained("distilbert/distilbert-base-uncased")
    # model = AutoModel.from_pretrained("distilbert/distilbert-base-uncased")
    tokenizer = AutoTokenizer.from_pretrained("google-bert/bert-base-multilingual-uncased")
    model = AutoModel.from_pretrained("google-bert/bert-base-multilingual-uncased")
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)
    index = faiss.IndexFlatIP(768)

    def search(self, query):
        token = self.tokenizer(query, add_special_tokens=True, truncation=True, padding='max_length',  max_length=512, return_tensors='pt', return_token_type_ids=False)
        for k,v in token.items():
            token[k] = v.to(self.device)
        with torch.no_grad():
            embedding = self.model(**token).last_hidden_state
        # mask = token['attention_mask'].unsqueeze(-1).expand(embedding.size()).float()
        # embedding = (embedding*mask)
        embedding = embedding.mean(1).cpu().numpy()
        faiss.normalize_L2(embedding)
        similarity, similar_doc = self.index.search(embedding, k=10)
        results = pd.DataFrame.from_dict(similar_doc[0])
        results["similarity"] = similarity[0]
        results.sort_values("similarity", ascending=False, inplace=True)
        
        return results

    def read_index(self, index_to_read):
        self.index = faiss.read_index(index_to_read)

fname = sys.argv[1]
indexer = BERT_indexer()
indexer.read_json(fname)
indexer.index_json_batch()
indexer.write_index('multi_full_index_no_mask.index')

#search_index = search_bert_index()
#search_index.read_index("multi_full_index_no_mask.index")
#query_string = 'blacksmith scene'
#results = search_index.search(query_string)
#print("\nRESULTS RETRIEVED: ")
#f = open('CS242 Final Combined IMDB Dataset (nulls replaced).json')
#data = json.load(f)
#for result in results[0]:
#    print(data[result]['title'])
#    # print('\t'+str(data[result]['directors Names']))
#print("Done")

# # SEARCH INDEX
#search_index = search_bert_index()
#search_index.read_index("multi_full_index_no_mask.index")

#query_string = input("Enter a search query: ")
# query_string = 'blacksmith scene'
#print("SEARCHING FOR: "+query_string)
#results = search_index.search(query_string)
#print("\nRESULTS RETRIEVED: ")
#f = open('CS242 Final Combined IMDB Dataset (nulls replaced).json')
#data = json.load(f)
#for result in results[0]:
#    print('\t'+data[result]['title'])
    # print(data[result])

# Test indexing time
# dir = 'CS242 Datasets IMDB'
# for f in os.listdir(dir):
#     indexer = BERT_indexer()
#     indexer.read_json(os.path.join(dir, f))
#     index_time = indexer.index_json_batch()
#     index_name = f+'_index_'+str(round(index_time, 2))
#     indexer.write_index(os.path.join('Test_Indexes', index_name))

# 0: 142566 42:32
# 1: 285132 1:15:40
# 2: 427698 1:57:28
# 3: 570264 2:31:10
# 4: 712830 3:15:12
# 5: 855396 3:50:42
# 6: 997962 4:26:45
# 7: 1140528 5:19:11
# 8: 1140528 6:05:41
# 9: 1425660 6:56:02
        
