import uuid
from google.cloud import bigquery
client = bigquery.Client()
def query(query_string ):
    query_job = client.run_async_query(str(uuid.uuid4()), query_string)
    query_job.begin()
    query_job.result()  # Wait for job to complete.
    destination_table = query_job.destination
    destination_table.reload()
    data=[]
    for row in destination_table.fetch_data():
        data.append(row)
    return data
def get_page_list():
    query_string = "SELECT user_id,page_url FROM [datacafethailand:social_insight.customer_connection_profile] where source = 'Facebook'"
    data = query(query_string)
    page_dict={}
    for row in data:
        page_id = row[0]
        page_url = row[1]
        page_dict[page_id]=page_url
        print(page_id)
        print(page_url)
def get_unique_users_list(page_id):
    query_string = "SELECT user_id FROM [datacafethailand:a19.page_post_user] where page_id='"+page_id+"' group by user_id limit 5"
    data = query(query_string)
    page_dict={}
    for row in data:
        print(row)
if __name__=="__main__":
    get_page_list()
    get_unique_users_list('129558990394402')
# query_job = client.run_async_query(str(uuid.uuid4()), """
#     #standardSQL
#     SELECT corpus AS title, COUNT(*) AS unique_words
#     FROM `publicdata.samples.shakespeare`
#     GROUP BY title
#     ORDER BY unique_words DESC
#     LIMIT 10""")

    

# query_job.begin()
# query_job.result()  # Wait for job to complete.
# destination_table = query_job.destination
# destination_table.reload()
# page_dict={}
# for row in destination_table.fetch_data():
#     page_id = row[0]
#     page_url = row[1]
#     page_dict[page_id]=page_url
#     print(page_id)
#     print(page_url)


    


