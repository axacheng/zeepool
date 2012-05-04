'''
Created on Sep 5, 2010

@author: axa
'''
from google.appengine.ext import db


class Words(db.Model):
    Created = db.DateTimeProperty(auto_now_add=True)
    Updated = db.DateTimeProperty(auto_now=True)
    Creator = db.StringProperty(required=True)
    Word = db.StringProperty(required=True)
    Define = db.TextProperty(required=True)
    Example = db.TextProperty()
    Tag = db.StringListProperty()


class CounterLikeWord(db.Model):
    name  = db.StringProperty(required=True)
    value = db.IntegerProperty(required=True, default=0)


class CounterDislikeWord(db.Model):
    name  = db.StringProperty(required=True)
    value = db.IntegerProperty(required=True, default=0)
    

class Comment(db.Model):
    Word = db.ReferenceProperty(Words, collection_name='comment')
    User = db.StringProperty(required=True)
    Define = db.TextProperty()
    Example = db.TextProperty()
    Eastablish = db.DateTimeProperty(auto_now_add=True)

    
if __name__ == '__main__':
    pass