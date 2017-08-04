from starwars_api.client import SWAPIClient
from starwars_api.exceptions import SWAPIClientError

api_client = SWAPIClient()


class BaseModel(object):

    def __init__(self, json_data):
        """
        Dynamically assign all attributes in `json_data` as instance
        attributes of the Model.
        """
        
        for key, value in json_data.items():
            setattr(self, key, value)
            
        

    @classmethod
    def get(cls, resource_id):
        """
        Returns an object of current Model requesting data to SWAPI using
        the api_client.
        """
        if cls.RESOURCE_NAME == 'people':
            return cls(api_client.get_people(resource_id))
        elif cls.RESOURCE_NAME == 'films':
            return cls(api_client.get_films(resource_id))
        
        
        

    @classmethod
    def all(cls):
        """
        Returns an iterable QuerySet of current Model. The QuerySet will be
        later in charge of performing requests to SWAPI for each of the
        pages while looping.
        """
        return eval(cls.__name__ + 'QuerySet()')
        


class People(BaseModel):
    """Representing a single person"""
    RESOURCE_NAME = 'people'

    def __init__(self, json_data):
        super(People, self).__init__(json_data)

    def __repr__(self):
        return 'Person: {0}'.format(self.name)


class Films(BaseModel):
    RESOURCE_NAME = 'films'

    def __init__(self, json_data):
        super(Films, self).__init__(json_data)

    def __repr__(self):
        return 'Film: {0}'.format(self.title)


class BaseQuerySet(object):

    def __init__(self):
        self._itemcount = 0
        self._pagecount = 1
        self.querydata = []
        self.totalcount = None
        
    def __iter__(self):
        self._itemcount = 0
        return self

    def __next__(self):
        """
        Must handle requests to next pages in SWAPI when objects in the current
        page were all consumed.
        """
        if self._itemcount >= len(self.querydata):
            try:
                self.getpage()
            except SWAPIClientError:
                raise StopIteration

        item = self.querydata[self._itemcount]
        
        self._itemcount += 1
        
        return item
       

    next = __next__
    
    
    def getpage(self):
        data = getattr(api_client, 'get_' + self.RESOURCE_NAME)(page=self._pagecount)
        self.totalcount = data['count']
        self.querydata.extend([eval(self.RESOURCE_NAME.title())(a) for a in data['results']]) 
        self._pagecount += 1
        
    def count(self):
        """
        Returns the total count of objects of current model.
        If the counter is not persisted as a QuerySet instance attr,
        a new request is performed to the API in order to get it.
        """
        if self.totalcount is None:
            self.getpage()
        return self.totalcount


class PeopleQuerySet(BaseQuerySet):
    RESOURCE_NAME = 'people'

    def __init__(self):
        super(PeopleQuerySet, self).__init__()

    def __repr__(self):
        return 'PeopleQuerySet: {0} objects'.format(str(len(self.objects)))


class FilmsQuerySet(BaseQuerySet):
    RESOURCE_NAME = 'films'

    def __init__(self):
        super(FilmsQuerySet, self).__init__()

    def __repr__(self):
        return 'FilmsQuerySet: {0} objects'.format(str(len(self.objects)))