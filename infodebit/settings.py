BOT_NAME = 'infodebit'

SPIDER_MODULES = ['infodebit.spiders']

ITEM_PIPELINES = {
    'scrapy_mongodb.MongoDBPipeline': 300,
    }

MONGODB_URI = 'mongodb://localhost:27017'
MONGODB_DATABASE = 'hydro'
MONGODB_COLLECTION = 'infodebit'
MONGODB_UNIQUE_KEY = 'hack'
