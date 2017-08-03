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
        resource = cls.__name__.lower()
        return cls(getattr(api_client, 'get_'+resource)(resource_id))

    @classmethod
    def all(cls):
        """
        Returns an iterable QuerySet of current Model. The QuerySet will be
        later in charge of performing requests to SWAPI for each of the
        pages while looping.
        """
        resource = cls.__name__
        Querysetclass = resource + 'QuerySet()'
        return eval(Querysetclass)
        


class People(BaseModel):
    """Representing a single person"""
    pass


class Films(BaseModel):
    """Representing a single film"""
    


class BaseQuerySet(object):

    def __init__(self):
        self.current_record = 0
        self.current_page = 0
        
        resource = type(self).__name__
        self.resource = resource.replace('QuerySet', '')
        self.method_name = "get_" + self.resource.lower()
        self._count = 0
        self.results =[]

    def __iter__(self):
        self.current_record = 0
        self.current_page = 1
        self._count = None
    
        return self.__class__()

    def __next__(self):
        """
        Must handle requests to next pages in SWAPI when objects in the current
        page were all consumed.
        """
        while True:
            if self.current_record + 1 > len(self.results):
                try:
                    self.get_next()
                except SWAPIClientError:
                    raise StopIteration()
        element = self.results[self.current_record]
        self.current_record+=1
        return element

    next = __next__
    
    def get_next(self):
        self.current_page += 1
        
        call = getattr(api_client, self.method_name)
        json_data = call(**{'[page': self.current_page})
        if self.current_page == 1:
            self._count = json_data['count']
        dicts = json_data['results']
        
        for item in dicts:
            elem = eval(self.resource)(item)
            self.results.append(elem)
            
        
    def count(self):
        """
        Returns the total count of objects of current model.
        If the counter is not persisted as a QuerySet instance attr,
        a new request is performed to the API in order to get it.
        """
        if not self._count:
            call = getattr(api_client, self.method_name)
            json_data = call(page=1)
            self._count = json_data['count']
            return self._count
        else:
            return self._count


class PeopleQuerySet(BaseQuerySet):
    pass


class FilmsQuerySet(BaseQuerySet):
    pass
