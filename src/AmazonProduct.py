class AmazonProduct:
    _title = None
    _price = None
    _description = None
    _url = None

    def __init__(self, title="N/A", price="N/A", description=None, url=None):
        self._title = title
        self._price = price
        self._description = description
        self._url = url

    def fix_url(self):
        ref_index = self._url.find('/ref=')
        if ref_index != -1:
            self._url = self._url[:ref_index]        

    def to_json(self):
        return {"Title": self._title, "Price": self._price, 
                "Description": self._description, "url": self._url}