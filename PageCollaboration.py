import uuid
import json
from google.cloud import bigquery
from MongoDB import MongoDBManager
from datetime import datetime
import networkx as nx
client = bigquery.Client()
import community
THRESHOLD =1
CATEGORY=[1,2,3,4,5]
def query(query_string,use_legacy=True):
    query_job = client.run_async_query(str(uuid.uuid4()), query_string)
    query_job.use_legacy_sql = use_legacy
    query_job.begin()
    query_job.result()  # Wait for job to complete.
    destination_table = query_job.destination
    destination_table.reload()
    data=[]
    for row in destination_table.fetch_data():
        data.append(row)
    return data
def get_page_dict():
    query_string = """SELECT user_id, page_url,category,name  FROM [datacafethailand:a19.page_info_new]"""
    data = query(query_string)
    page_dict={}
    for row in data:
        page_id = row[0]
        page_url = row[1]
        category = row[2]
        name = row[3]
        page_dict[page_id]={'page_id':page_id,'page_url':page_url,'category':category,'score':{},'name':name}
    return page_dict
def generate_page_id_string(page_dict):
    page_id_string='('
    for page_id in page_dict:
        page_id_string = page_id_string+'\''+page_id+'\','
    page_id_string = page_id_string[:-1]+')'
    return page_id_string
def get_pages_interacted_with_users(page_id,page_dict):
    query_string = """select page_id,count(*) as count from  
        (SELECT user_id,page_id FROM [datacafethailand:a19.page_user_count] where user_id in 
        (SELECT user_id FROM [datacafethailand:a19.page_post_user] where page_id='"""+page_id+"""' group by user_id)
        )
        group by page_id"""
    data = query(query_string)
    page_score = {}
    for row in data:
        page_id = row[0]
        count = row[1]
        page_url = page_dict[page_id]['page_url']
        category =  page_dict[page_id]['category']
        page_score[page_id] ={'count':count,'page_url':page_url,'category':category}
    return page_score
def generate_page_score_tuple(page_score):
    page_score_tuple_list=[]
    for page_id in page_score:
        page_score_tuple = (page_score[page_id]['count'],page_score[page_id]['page_url'],page_score[page_id]['category'])
        page_score_tuple_list.append(page_score_tuple)
    return page_score_tuple_list
def get_intersection_union(page_id_string):
    query_string = """ select host1,host2, nintersect,nunion,postmonth from [datacafethailand:a19.all_page_pairwise_monthly] where host1 in """+page_id_string+""" and host2 in """ +page_id_string
    data = query(query_string)
    all_page_pairwise_list=[]
    for row in data:
        page_id1 = row[0]
        page_id2 = row[1]
        intersect = row[2]
        union = row[3]
        month = row[4]
        pairwise={'pageid1':page_id1,'pageid2':page_id2,'intersect':intersect,'union':union,'month':month}
        all_page_pairwise_list.append(pairwise)
    return all_page_pairwise_list
def main_run_jaccard_single_call():
    mongo = MongoDBManager('PageCollab')
    get_page_dict_from_big_query=False
    get_page_pairwise_from_big_query = False
    if get_page_dict_from_big_query: 
        page_dict = get_page_dict()
        mongo.insert_one('page_dict_monthly',page_dict)
    else:
        page_dict=mongo.get_all_from_collection('page_dict_monthly')[0]
    if get_page_pairwise_from_big_query:
        page_id_string = generate_page_id_string(page_dict)
        all_page_pairwise_list = get_intersection_union(page_id_string)
        mongo.insert_many('all_page_pairwise_monthly',all_page_pairwise_list)
    else:
        all_page_pairwise_list=mongo.get_all_from_collection('all_page_pairwise_monthly')
       
        
    i=0
    #print(len(all_page_pairwise_list))
    for page_pairwise in all_page_pairwise_list:
        print(i)
        page_id1=page_pairwise['pageid1']
        page_id2=page_pairwise['pageid2']
        intersect = page_pairwise['intersect']
        union =page_pairwise['union']
        month = page_pairwise['month']
        jaccard_sim = 1.0*intersect/union
        category1 =  page_dict[page_id1]['category']
        category2 =  page_dict[page_id2]['category']
        name1 = page_dict[page_id1]['name']
        name2 =  page_dict[page_id2]['name']
        page_score_tuple1 = (jaccard_sim,page_id1,name1,category1,intersect,union)
        page_score_tuple2 = (jaccard_sim,page_id2,name2,category2,intersect,union)
        page_dict[page_id1]['score']={}
        if month not in page_dict[page_id2]['score']:
            page_dict[page_id2]['score'][str(month)]=[]
        if month not in page_dict[page_id1]['score']:
            page_dict[page_id1]['score'][str(month)]=[]
        page_dict[page_id1]['score'][str(month)].append(page_score_tuple2)
        page_dict[page_id2]['score'][str(month)].append(page_score_tuple1)
        i=i+1
    for page_id in page_dict:
        if page_id=='_id':
            continue
        for month in page_dict[page_id]['score']:
            page_dict[page_id]['score'][month] = sorted(page_dict[page_id]['score'][month])
    del page_dict['_id']
    mongo.insert_many('page_score_monthly',page_dict.values())
def generate_networkx(page_dict,all_page_pairwise_list):
    g= nx.Graph()
    for page_id in page_dict:
        g.add_node(page_id)
    for edge in all_page_pairwise_list:
        intersect = edge['intersect']
        union =edge['union']
        jaccard_sim = 100.0*intersect/union
        if(jaccard_sim>THRESHOLD):
            g.add_edge(edge['pageid1'],edge['pageid2'],weight=jaccard_sim)
    return g
def generate_nodes_list(page_dict,betweenness,closeness,eigenvector,degree):
    node_list=[]
    for page_id in page_dict:
        node = {
            'id':page_id,
            'group':page_dict[page_id]['category'],
            'name':page_dict[page_id]['name'],
            'betweenness':betweenness[page_id],
            'closeness':closeness[page_id],
            'eigenvector':eigenvector[page_id],
            'degree':degree[page_id]
        }
        node_list.append(node)
    return node_list
def generate_edge_list(all_page_pairwise_list):
    edge_list=[]
    for page_pairwise in all_page_pairwise_list:
        intersect = page_pairwise['intersect']
        union =page_pairwise['union']
        jaccard_sim = 100.0*intersect/union
        if(jaccard_sim>THRESHOLD):
            link={
                'source':page_pairwise['pageid1'],
                'target':page_pairwise['pageid2'],
                'value':jaccard_sim
            }
            edge_list.append(link)
    return edge_list
def write_json(filepath,data):
    with open(filepath, 'w') as fp:
        json.dump(data, fp)
def main_generate_entire_network():
    mongo = MongoDBManager('PageCollab')
    page_dict=mongo.get_all_from_collection('page_dict')[0]
    del page_dict['_id']
    all_page_pairwise_list=mongo.get_all_from_collection('all_page_pairwise')
    graph = generate_networkx(page_dict,all_page_pairwise_list)
    degree = nx.degree_centrality(graph)
    betweenness = nx.betweenness_centrality(graph)
    closeness = nx.closeness_centrality(graph)
    eigenvector = nx.eigenvector_centrality(graph)
    node_list = generate_nodes_list(page_dict,betweenness,closeness,eigenvector,degree)
    edge_list = generate_edge_list(all_page_pairwise_list)
    data={
        'nodes':node_list,
        'links':edge_list
    }
    file_path = './view/data_'+str(THRESHOLD)+'.json'
    write_json(file_path,data)
def extract_top_from_each_category(page_score_list):
    num_top=5
    page_score={}
    for page in page_score_list:
        page_id = page['page_id']
        page_score[page_id] = page
        page_score[page_id]['brand']=[]
        page_score[page_id]['media']=[]
        page_score[page_id]['artist']=[]
        score = page_score[page_id]['score']
        score = score[:-2]
        num_page_in_list =0
        for page_tuple in reversed(score):            
            if num_page_in_list == (num_top*3):
                break
            category = page_tuple[3]
            if category==1:
                if len(page_score[page_id]['brand'])<num_top:
                    page_score[page_id]['brand'].append(page_tuple)
                    num_page_in_list = num_page_in_list+1
            elif category==2 or category==4 or category==5:
                if len(page_score[page_id]['media'])<5:
                    page_score[page_id]['media'].append(page_tuple)
                    num_page_in_list = num_page_in_list+1
            elif category==3:
                if len(page_score[page_id]['artist'])<num_top:
                    page_score[page_id]['artist'].append(page_tuple)
                    num_page_in_list = num_page_in_list+1
    return page_score 

def generate_data_of_top(page_score):
    node_list=[]
    edge_list=[]
    category_list = ['brand','media','artist']
    node_exist={}

    for pageid1 in page_score:
        for category in category_list:
            for page_tuple in page_score[pageid1][category]:
                score = page_tuple[0] *100
                pageid2 = page_tuple[1]
                category = page_tuple[3]
                if (pageid1 not in node_exist) or (pageid2 not in node_exist[pageid1]):
                    link={
                        'source':pageid1,
                        'target':pageid2,
                        'value':score
                    }
                    if len(page_score[pageid1]['score'])>0 and page_score[pageid1]['category'] in CATEGORY and page_score[pageid2]['category'] in CATEGORY:
                        edge_list.append(link)
                    if (pageid1 not in node_exist):
                        node_exist[pageid1]={}
                    if (pageid2 not in node_exist):
                        node_exist[pageid2]={}
                    node_exist[pageid1][pageid2]=True
                    node_exist[pageid2][pageid1]=True
    g= nx.Graph()
    for page_id in page_score:
        if len(page_score[page_id]['score'])>0 and page_score[page_id]['category'] in CATEGORY:
            g.add_node(page_id)
    for edge in edge_list:
        if len(page_score[edge['source']]['score'])>0 and page_score[edge['source']]['category'] in CATEGORY and page_score[edge['target']]['category'] in CATEGORY:
            g.add_edge(edge['source'],edge['target'],weight=edge['value'])
    partition = community.best_partition(g)
    degree = nx.degree_centrality(g)
    betweenness = nx.betweenness_centrality(g)
    closeness = nx.closeness_centrality(g)
    eigenvector = nx.eigenvector_centrality(g)
    page_info_data={}
    for page_id in page_score:
        if len(page_score[page_id]['score'])>0 and page_score[page_id]['category'] in CATEGORY:
            catetory_id = page_score[page_id]['category']
            if catetory_id==2 or catetory_id==4 or catetory_id==5:
                catetory_id=2
            node = {
                'id':page_id  
            }
            node_list.append(node)
            page_info_data[page_id]={
                'group':catetory_id,
                'partition':partition[page_id],
                'name':page_score[page_id]['name'],
                'betweenness':betweenness[page_id],
                'closeness':closeness[page_id],
                'eigenvector':eigenvector[page_id],
                'degree':degree[page_id],
                'brand':page_score[page_id]['brand'],
                'media':page_score[page_id]['media'],
                'artist':page_score[page_id]['artist']
            }
    category_data=[]
    for category_num in CATEGORY:
        if category_num==4 or category_num==5:
            category_num=2 #group cat4,5 to cat2
        category_num = category_num-1
        category_data.append(category_list[category_num])
    data={
        'nodes':node_list,
        'links':edge_list,
        'page_info':page_info_data,
        'category':list(set(category_data))
    }
    return data
def main_generate_network_of_top():
    mongo = MongoDBManager('PageCollab')
    page_dict=mongo.get_all_from_collection('page_dict')[0]
    del page_dict['_id']
    page_score_list = mongo.get_all_from_collection('page_score')
    all_page_pairwise_list = mongo.get_all_from_collection('all_page_pairwise')
    page_score = extract_top_from_each_category(page_score_list)
    data = generate_data_of_top(page_score)
    file_name = './view/datatop5 cat'+str(CATEGORY).replace('\'','').replace('[','').replace(']','').replace(', ','')+'.json'
    write_json(file_name,data)
if __name__=="__main__":
    print('begin')
    main_run_jaccard_single_call()
    print('done')