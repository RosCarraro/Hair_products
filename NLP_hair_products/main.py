import pandas as pd
import numpy as np

from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.transform import factor_cmap
# bokeh imports for server
from bokeh.layouts import row, column
from bokeh.models import Div
from bokeh.io import curdoc
import re

df = pd.read_csv("datasets/Plot_df.csv",index_col=0)
cols= ["#1f77b4","#fda000","#e55171","#44aa99","#332288","#e6a1eb","#0b672a","#f6d740","#bb2aa7","#6ab1d1","#5e0101","#3eba00"]
source = ColumnDataSource(df)

def get_ingredients(raw_ingredients):
   #raw_ingredients=soup.find(id="produto-texto-composicao").string
   ingredients=re.sub('\s{2,}',' ',raw_ingredients)
   ingredients=re.sub('\.|\\\\[a-zA-Z]','',ingredients) 
   ingredients_lower = ingredients.lower()
   ingredients_list=ingredients_lower.split(',') # tokenize ingredients
   ingredients_list=[re.sub('^[ \t]+|[ \t]+$','',ing) for ing in ingredients_list]
   return ingredients_list

# Initialize dictionary, list, and initial index
ingredient_idx = {}
corpus = []
idx = 0

# For loop for tokenization
for i,df_row in df.iterrows():   
   ingredients = get_ingredients(df_row['Ingredients'])
   corpus.append(ingredients)
   for ingredient in ingredients:
      if ingredient not in ingredient_idx:
            ingredient_idx[ingredient] = idx
            idx += 1

def scatter_plot(source):
   # Make a source and a scatter plot  
   tools = 'pan,wheel_zoom,tap,box_select,reset'
   plot = figure(x_axis_label = 'X', 
               y_axis_label = 'Y', 
               width = 500, height = 400,tools=tools)

   plot.circle(x = 'X', 
      y = 'Y', 
      source = source, 
      size = 10, nonselection_fill_alpha=0.3, legend_field="Product_type",
            color=factor_cmap('Product_type', cols, df.Product_type.unique()))

   # Create a HoverTool object
   hover = HoverTool(tooltips = [('Product', '@Product_name'), 
                                 ('Brand', '@Brand'), 
                                 ('Category', '@Product_type')])
   plot.add_tools(hover)
   plot.width=700
   plot.height=500
   plot.legend.location = 'bottom_right'
   plot.legend.background_fill_alpha = 0.5
   plot.legend.border_line_width = 3
   return plot

corpus_set=[set(c) for c in corpus]

# set up widgets
title = Div(text='', width_policy='fit')
common_ingr = Div(text='', width_policy='fit')
characterizing_ingr = Div(text='', width_policy='fit')

# call plot from previous cell
source = ColumnDataSource(df)
plot = scatter_plot(source)

# add a callback to a widget
def update(selected=None):
   title.text = 'Please select some products to compare their ingredients'

def update_ingredients(selected):
   #stats.text = str(data[[t1, t2, t1+'_returns', t2+'_returns']].describe())
   title.text = '<b>Common ingredients of selected products</b>:'
   data = [corpus_set[s] for s in selected]
   common_ingredients = set.intersection(*data)
   common_ingr.text=str(common_ingredients)
   characterizing_ingr.text='<b>Characterizing ingredients of each product</b>:<br>'
   for s in selected:
      characterizing_ingredients = corpus_set[s].difference(common_ingredients)
      characterizing_ingr.text += '<b>'+df.Product_name.iloc[s]+'</b>: '+str(characterizing_ingredients)+'<br>'

def selection_change(attrname, old, new):
   selected = source.selected.indices
   if selected:
      update_ingredients(selected)
   else:
      title.text = 'No products selected'
      common_ingr.text = ''
      characterizing_ingr.text = ''

source.selected.on_change('indices', selection_change)

# create a layout for everything
text_col=column(title,common_ingr,characterizing_ingr)
layout = row(plot,text_col)

# initialize
update()

    # add the layout to curdoc
curdoc().add_root(layout)