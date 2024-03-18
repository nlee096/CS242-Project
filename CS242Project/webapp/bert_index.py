from transformers import AutoTokenizer, AutoModel
import torch
from tqdm import tqdm
import faiss
import os
import pandas as pd

os.environ['KMP_DUPLICATE_LIB_OK']='True'

class search_bert_index():
    tokenizer = AutoTokenizer.from_pretrained("google-bert/bert-base-multilingual-uncased")
    model = AutoModel.from_pretrained("google-bert/bert-base-multilingual-uncased")
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)
    index = faiss.IndexFlatIP(768)

    def search(self, query, num_results):
        token = self.tokenizer(query, add_special_tokens=True, truncation=True, padding='max_length',  max_length=512, return_tensors='pt', return_token_type_ids=False)
        for k,v in token.items():
            token[k] = v.to(self.device)
        with torch.no_grad():
            embedding = self.model(**token).last_hidden_state
        # mask = token['attention_mask'].unsqueeze(-1).expand(embedding.size()).float()
        # embedding = (embedding*mask)
        embedding = embedding.mean(1).cpu().numpy()
        faiss.normalize_L2(embedding)
        similarity, similar_doc = self.index.search(embedding, k=num_results)
        results = pd.DataFrame.from_dict(similar_doc[0])
        results["similarity"] = similarity[0]
        results.sort_values("similarity", ascending=False, inplace=True)

        return results

    def read_index(self, index_to_read):
        self.index = faiss.read_index(index_to_read)
