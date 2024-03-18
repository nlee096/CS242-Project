import gradio as gr
import json
import pandas as pd
import numpy as np
from bert_index import *
from pylucene_search import *

list_data_obj = json.load(open("../data/sample_dataset.json"))
search_index = search_bert_index()
search_index.read_index("multi_full_index_no_mask.index")

pylucene_search_index = search_pylucene_index()
pylucene_index = "imdb_lucene_index/"
initVM_bool = False

# class test_obj:
#     def __init__(self, x, y):
#         self.x = x
#         self.y = y

def method_call(radio_button, num_results, inp):
    if radio_button == "PyLucene":     
        # place_holder_obj = [
        #     test_obj(1, 1),
        #     test_obj(2, 2),
        #     test_obj(3, 3)
        # ]
        global initVM_bool
        if not initVM_bool:
            lucene.initVM(vmargs=['-Djava.awt.headless=true'])
            initVM_bool = True

        movie_pylucene_results = pylucene_search_index.retrieve(pylucene_index, inp, num_results=num_results)
        for i in range(len(movie_pylucene_results)):
            t_const_id = movie_pylucene_results[i]["tconst"]
            movie_pylucene_results[i]["URL"] = f"https://www.imdb.com/title/{t_const_id}"

        return pd.DataFrame(movie_pylucene_results)
        # return pd.DataFrame([t.__dict__ for t in place_holder_obj])

    elif radio_button == "Bert":
        # place_holder_obj = [
        #     test_obj(1, 1),
        #     test_obj(2, 2),
        #     test_obj(3, 3)
        # ]
        movie_indexes = search_index.search(inp, num_results=num_results)
        movie_bert_results = []
        for index,similarity in zip(movie_indexes[0], movie_indexes["similarity"]):
            movie_bert_results.append(list_data_obj[index])
            movie_bert_results[-1]["Score"] = similarity
        for i in range(len(movie_bert_results)):
            t_const_id = movie_bert_results[i]["tconst"]
            movie_bert_results[i]["URL"] = f"https://www.imdb.com/title/{t_const_id}"
        final_df = pd.DataFrame(movie_bert_results)
        insert_front_col = final_df.pop("Score")
        final_df.insert(0, "Score", insert_front_col)
        return final_df
            
        # return pd.DataFrame([t.__dict__ for t in place_holder_obj])

    return pd.DataFrame([{
        "Error": "Make Sure to Select A search Method"
    }])


def change_instructions(choice):
    if choice == "PyLucene":
        return gr.Markdown("""
                            #### PyLucene Search Instructions:
                            > For a basic text search, enter a search query with the format `field`:`search_val`

                            > For a range search on `start_year`, enter a search query with the format `start_year`:`YYYY TO YYYY`

                            > For a wildcard search, enter a search query with the format `field`:`value`

                            > For field/term boosting, add ^X.X after the search value
                            """)
    else:
        return gr.Markdown(
                            """
                            #### Bert Search Instructions:
                            > Enter your query in the textbox below
                            """)

with gr.Blocks() as demo:
    radio_button = gr.Radio(["PyLucene", "Bert"], value="PyLucene", label="Search Method")
    num_results = gr.Number(value=1, label="Number of Results")
    instructions = gr.Markdown("""
                                #### PyLucene Search Instructions:
                                > For a basic text search, enter a search query with the format `field`:`search_val`

                                > For a range search on `start_year`, enter a search query with the format `start_year`:`YYYY TO YYYY`

                                > For a wildcard search, enter a search query with the format `field`:`value`

                                > For field/term boosting, add ^X.X after the search value
                                """)
    inp = gr.Textbox(placeholder="Search...", label="Search Engine")
    submit = gr.Button(value="Submit", variant="primary")
    submit.click(fn=method_call, inputs=[radio_button, num_results, inp], outputs=gr.Dataframe())
    radio_button.change(fn=change_instructions, inputs=radio_button, outputs=instructions)
    
if __name__ == "__main__":
    demo.launch(server_port=8080, server_name="0.0.0.0")
