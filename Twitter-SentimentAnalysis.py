# Databricks notebook source
# MAGIC %md
# MAGIC # Huggingface Sentiment Analysis

# COMMAND ----------

# MAGIC %md
# MAGIC (pls ignore, internal use)
# MAGIC * [Twitter Stream S3](https://data-ai-lakehouse.cloud.databricks.com/?o=2847375137997282#notebook/3842290145331493/command/3842290145331494)
# MAGIC * [Pipeline](https://data-ai-lakehouse.cloud.databricks.com/?o=2847375137997282#joblist/pipelines/e5a33172-4c5c-459b-ab32-c9f3c720fcac)

# COMMAND ----------

!pip install transformers  emoji wordcloud

# COMMAND ----------

df = spark.read.format("delta").table("tweets_summer.silver")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Huggingface Sentiment Analysis

# COMMAND ----------

# MAGIC %md
# MAGIC 
# MAGIC for more details about [Hugging Face](https://huggingface.co/) on Databricks, check out the [Databricks blog posting](https://databricks.com/blog/2021/10/28/gpu-accelerated-sentiment-analysis-using-pytorch-and-huggingface-on-databricks.html)

# COMMAND ----------

from transformers import pipeline
import pandas as pd

tweets = df.toPandas()

# COMMAND ----------

# sentiment analysis is easy with huggingface on Databricks
#
# default model for analysis is "sentiment-analysis"
# but "finiteautomata/bertweet-base-sentiment-analysis" is even better tuned or tweets! 

#sentiment_pipeline = pipeline(model="finiteautomata/bertweet-base-sentiment-analysis")
sentiment_pipeline = pipeline(task="sentiment-analysis")

# COMMAND ----------

# MAGIC %md
# MAGIC Check it out! this is how SA works with a small, hard-coded list

# COMMAND ----------

sentiment_pipeline([" :-)",
                   "not good at all",
                   "I love the Lakehouses"
                   
                   ])

# COMMAND ----------

sentiments = sentiment_pipeline(tweets.text.to_list())

# COMMAND ----------

# add sentiments as new column to df
tweets = pd.concat([tweets, pd.DataFrame(sentiments)], axis=1)

# COMMAND ----------

# most positive tweets 
#pd.set_option('display.max_colwidth', None)  
tweets.query('label == "POSITIVE"').sort_values(by=['score'], ascending=False)[:15]

# COMMAND ----------

# most neg tweets 
# pd.set_option('display.max_colwidth', None)  

# tweets.query('label == "NEGATIVE"').sort_values(by=['score'], ascending=False)[:5].text

# COMMAND ----------

from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
 

# Wordcloud with positive tweets

stop_words = ["https", "RT","how"] + list(STOPWORDS)

x = tweets.query('label == "POS"').sort_values(by=['score'], ascending=False)[:100].text
positive_wordcloud = WordCloud(max_font_size=150, max_words=100, background_color="white", stopwords = stop_words).generate(str(x))
plt.figure()
plt.title("postive tweets")
plt.imshow(positive_wordcloud)
plt.axis("off")
plt.show()


# COMMAND ----------

# Let's count the number of tweets by sentiments
sentiment_counts = tweets.groupby(['label']).size()
print(sentiment_counts)

# visualize the sentiments
fig = plt.figure(figsize=(6,6), dpi=100)
ax = plt.subplot(111)
sentiment_counts.plot.pie(ax=ax, autopct='%1.1f%%',  fontsize=12, label="")

# COMMAND ----------

# MAGIC %md
# MAGIC 
# MAGIC ## Non-english Languages ...

# COMMAND ----------

# MAGIC %sql
# MAGIC 
# MAGIC select * from tweets_summer.languages where lang <> "en" sort by count desc

# COMMAND ----------

# MAGIC %md 
# MAGIC # Ressources

# COMMAND ----------

# MAGIC %md 
# MAGIC * Hugging Face with Databricks [blog](https://databricks.com/blog/2021/10/28/gpu-accelerated-sentiment-analysis-using-pytorch-and-huggingface-on-databricks.html)
# MAGIC * DAIS 2022 recording of this demo (tbd)
