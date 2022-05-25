-- Databricks notebook source
-- MAGIC %md
-- MAGIC # Delta Live Tables Twitter

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 
-- MAGIC ![Twitter Architecture Diagram](https://github.com/fmunz/dlt-l300/blob/main/twitterstream.png?raw=true)

-- COMMAND ----------

-- MAGIC %md
-- MAGIC * [Twitter Stream](https://data-ai-lakehouse.cloud.databricks.com/?o=2847375137997282#notebook/124654004282750)
-- MAGIC * [Pipeline](https://data-ai-lakehouse.cloud.databricks.com/?o=2847375137997282#joblist/pipelines/267b91c1-52f0-49e3-8b77-9a50b34f5d39/updates/10b2150e-b0a0-4116-9016-3b2595ea2ab9)
-- MAGIC * [Huggingface Sentiment Analysis](https://data-ai-lakehouse.cloud.databricks.com/?o=2847375137997282#notebook/2328309019401991)

-- COMMAND ----------

CREATE STREAMING LIVE TABLE bronze

COMMENT 'stream raw data from JSON files as is into bronze table
- we use autoloader for data ingestion of many small files
- Delta Live Tables performs maintenance tasks on tables every 24 hours. 
- By default, the system performs a full OPTIMIZE operation followed by VACUUM
- Streaming: +Ensures exactly-once processing of input rows
-            +Inputs are only read once

- note that the schema is detected automatically'

AS SELECT * FROM cloud_files(
  "dbfs:/data/twitter_dataeng2", "json"
)

-- COMMAND ----------

create or replace   live table silver 

(constraint valid_language expect (lang == "en") on violation drop row,
constraint valid_id expect (id != "") on violation drop row)

comment 'data is cleansed - other languages than EN are dropped'


as
  select id, geo, lang, text from  (live.bronze)

-- COMMAND ----------

-- CREATE OR REPLACE LIVE TABLE has same semantics as CREATE LIVE TABLE 
create or replace  streaming live table languages
comment 'table for statistics of different languages
that showed up in the pipeline' 

as
select lang, count(*) as count from  stream (live.bronze) group by lang order by count
