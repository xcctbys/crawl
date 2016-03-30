# Storage Designment

## Functions

- mysql orm
- mongo orm


## How to define mysql model?

You must inherit `BaseModel`. You can use all standard apis from Django 1.8.

### Save Example

Define class `Job`

    class Job(BaseModel):
        (STATUS_ON, STATUS_OFF) = range(1, 3)
	    STATUS_CHOICES = (
	        (STATUS_ON, u"启用"),
	        (STATUS_OFF, u"下线"),
	    )
	    name = models.CharField(max_length=128)
	    info = models.CharField(max_length=1024)
	    customer = models.CharField(max_length=128, blank=True, null=True)
	    status = models.IntegerField(default=STATUS_ON, choices=STATUS_CHOICES)
	    add_datetime = models.DateTimeField(auto_now_add=True)


give some value and save
    
    job = Job()
    job.name = "beijing"
    job.save()
    
table job will have a row with name is beijing.


### Update Example

    job = Job()
    job.name = "a"
    job.save()
    
    job.name = "b"
    job.save()



## how to define mongodb model?

You must inherit `BaseDocument`. We use `mongoengine` as basic, you can use standard apis from it.

    from mongoengine import *
    
    
	class Choice(BaseEmbeddedDocument):
	    choice_text = StringField(max_length=200)
	    votes = IntField(default=0)
	    
    
	class Poll(BsseDocument):
	    question = StringField(max_length=200)
	    pub_date = DateTimeField(help_text='date published')
	    choices = ListField(EmbeddedDocumentField(Choice))
	
	    meta = {
	        'indexes': [
	            'question', 
	            ('pub_date', '+question')
	        ]
	    }
	    
translate to mongodb

	{
	    "_id" : ObjectId("5483165de50c050005e4b29f"),
	    "question" : "What's up?",
	    "pub_date" :  ISODate("2013-04-14T11:06:21.922Z"),
	    "choices" : [
	        {
	            "choice_text" : "Not much",
	            "votes" : 0
	        },
	        {
	            "choice_text" : "Just hacking again",
	            "votes" : 1
	        }
	    ],
	}
	    

querying and updateing
	
	from yourproject.models import Poll, Choice
	
	poll = Poll.objects(question__contains="What").first()
	choice = Choice(choice_text="I'm at DjangoCon.fi", votes=23)
	poll.choices.append(choice)
	poll.save()
	
	print poll.question

Setting indexes

	class Poll(Document):
	    question = StringField(max_length=200)
	    pub_date = DateTimeField(help_text='date published')
	    choices = ListField(EmbeddedDocumentField(Choice))
	
	    meta = {
	        'indexes': [
	            'question', 
	            ('pub_date', '+question')
	        ]
	    }


## How to Setting

### Mysql 

We only use one mysql server. 
	
	DATABASES = {
	    'default': {
	        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
	        'NAME': 'clawer',                      # Or path to database file if using sqlite3.
	        'USER': 'cacti',                      # Not used with sqlite3.
	        'PASSWORD': 'cacti',                  # Not used with sqlite3.
	        'HOST': '10.100.80.50',                      # Set to empty string for localhost. Not used with sqlite3.
	        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
	    }
	}
	    
## MongoDB

    MongoDBS = {
        'default': {
            'username': "",
            'password': '',
            'host': '',
        },
        'log': {
            'username': "",
            'password': '',
            'host': '',
        },
        'source': {
            'username': "",
            'password': '',
            'host': '',
        },
        'structure': {
            'username': "",
            'password': '',
            'host': '',
        }
    }
    
- default: default mongodb server
- log: store all log, include generate log, analysis log etc
- source: data from source. For example website www.51job.com
- structure: after analysis, output structured data

