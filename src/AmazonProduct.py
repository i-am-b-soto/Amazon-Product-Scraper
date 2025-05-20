class AmazonProduct:
    _title = None
    _price = None
    _description = None
    _url = None

    def __init__(self, title, price, description=None, url=None):
        self._title = title
        self._price = price
        self._description = description
        self._url = url

    def to_json(self):
        return {"Title": self._title, "Price": self._price, 
                "Description": self._description, "url": self._url}