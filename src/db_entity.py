'''
Created on Sep 5, 2010

@author: axa
'''
from google.appengine.ext import db

class CounterLikeWord(db.Model):
    Creator = db.StringProperty()
    name  = db.StringProperty(required=True)
    value = db.IntegerProperty(required=True, default=0)


class CounterDislikeWord(db.Model):
    Creator = db.StringProperty()
    name  = db.StringProperty(required=True)
    value = db.IntegerProperty(required=True, default=0)


class Favorite(db.Model):
    Creator = db.StringProperty()
    Word = db.IntegerProperty(required=True)
    
    
class Words(db.Model):
    Created = db.DateTimeProperty(auto_now_add=True)
    Creator = db.StringProperty(required=True)
    Define = db.TextProperty(required=True)
    Display = db.BooleanProperty(default=True)
    Example = db.TextProperty()  
    ShareTo = db.StringListProperty()
    Source = db.StringListProperty()
    Tag = db.StringListProperty()
    Updated = db.DateTimeProperty(auto_now=True)
    Word = db.StringProperty(required=True)


class SearchPagingCounter(db.Model):
    name  = db.StringProperty(required=True)
    value = db.IntegerProperty(required=True, default=0)
        

if __name__ == '__main__':
    pass