import dash
from dash import dcc, html, Input, Output, dash_table
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from PIL import Image
from dash.dependencies import Input, Output
from collections import Counter

#Reading the scraped data from CSV
df = pd.read_csv("1000.csv")
#Sorting data by Author and making hyperlink
df = df.sort_values("Author")
for i in df:
    df['clickable'] = "["+ df['Title'] + "](" + df['Link']+")"
df = df.reset_index()
#Adding index
df['id'] = df.index+1
#Making frequency column from languages
df_freq = df.groupby("Language").size().reset_index(name="Count")

# Dash App Starts Here
app = dash.Dash(__name__)

#WordCloud Maker Function
def draw_wordcloud(subjects_column):
#Convert Subjects Coloumn to string
    all_subjects = subjects_column.dropna().astype(str).tolist()
#Cleaning Subject Column and splitting to one list
    cleaned_subjects = []
    for subject in all_subjects:
        subject = ' '.join(subject.split()).strip()
        subject=subject.strip()
        subject = subject.replace("'","")
        subject = subject.replace("[","")
        subject = subject.replace("]","")
        subject = subject.replace('"',"")
        #subject = subject.replace(' ',"_")
        subject = subject.replace("-","")
        cleaned_subjects.append(subject)
    
#Splitting list to string coloumn of subjects
    flat_subjects = [subject for sublist in cleaned_subjects for subject in sublist.split(',')]

#Generate frequency of Subjects
    subject_freq = Counter(flat_subjects)
#Generate wordcloud
    wordcloud = WordCloud(width=800, height=400, max_words=100, background_color='white').generate_from_frequencies(subject_freq)
#Save WorldCloud Image
    wordcloud.to_file("subject.png")
    image_path = 'subject.png'
#Use PIL library to load image
    pil_img = Image.open("subject.png")

#Updating wordcloud layout
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
#Return the Wordcloud
    return pil_img

#Dashapp Layout
app.layout = html.Div([
    html.H1("Gutenberg Book Project", style={'text-align': 'center'}),

# Dropdown for language selection
    dcc.Dropdown(
    id='dropdown',
    options=[{"label": i, "value": i} for i in df['Language'].unique()],
    value = ["English","Spanish","French","Italian","Russian","Japanese","Chinese","Tagalog","Portuguese","Middle English","Latin","Old English","Arabic","German"],
    multi=True,
    placeholder="Select languages",
    ),
html.H1("Bar Chart of Languages", style={'text-align': 'center'}),
# Barchart
    dcc.Graph(
    id='bar_chart',
        figure=px.bar(
        df_freq,
        x="Language", y="Count",
        color="Language",
                     )
    ),

# WordCloud
    html.Div([
        html.H1("Word Cloud of Top 100 Subjects", style={'text-align': 'center'}),
        html.Img(id='wordcloud', style={'height': '50%', 'width': '50%', 'align':'center', 'display': 'block', 'margin': '0 auto'})
    ]),

# DataTable
    html.Div([
        html.H1("Gutenberg Book Table", style={'text-align': 'center'}),
        dash_table.DataTable(df.to_dict('records'), id="table",
            columns=[
                {"name": "Id", "id": "id"},
                {"name": "Title", "id": "clickable", "presentation": "markdown"},
                {"name": "Author", "id": "Author"},
                {"name": "Language", "id": "Language"}
            ],
#Filter options for dashtable
                page_size=10,
                page_current=0,
                filter_action='native', 
                sort_action='native',  
                sort_mode='multi',  
                style_table={'overflowX': 'auto'},
                style_cell={'textAlign': 'left'},

        )
    ])
])

#Callback for interactive options
@app.callback(
    [Output('bar_chart', 'figure'),
     Output('table', 'data'),
     Output('wordcloud', 'src')],
      Input('dropdown', 'value')
)
#Function to send dropdown selection as filtered coloumn of data by language selected
def update_visuals(selected_languages):
# Filter data based on selected languages

#If no language selected use the initial dataframe and frequency generated
    if len(selected_languages) == 0:
        filtered_df = df
        filtered_freq = df_freq
#Else filter the dataframe by languages selected and make a new frequency column
    else:
        filtered_df = df[df["Language"].isin(selected_languages)]
        filtered_freq = filtered_df.groupby("Language").size().reset_index(name="Count")

#Update bar chart with filtered dataframe
    fig = px.bar(
        filtered_freq,
        x="Language", y="Count",
        color="Language",
    )
    fig.update_layout(xaxis={'categoryorder': 'total descending'})

## Update dashtable with filtered dataframe, update index coloum and hyperlink
    table_data = filtered_df[["Title", "Author", "Language", "Link"]].reset_index()
    table_data["id"] = table_data.index + 1
    table_data["clickable"] = "[" + table_data["Title"] + "](" + table_data["Link"] + ")"
    table_data = table_data.to_dict('records')

#Update wordcloud with filtered dataframe
    wordcloud_img = draw_wordcloud(filtered_df['Subject'])

#Return the barchart, dashtable and wordcloud
    return fig, table_data, wordcloud_img

#Runt the app on localhost server
if __name__ == '__main__':
    app.run_server(debug=True)
